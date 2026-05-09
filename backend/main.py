"""
Ground Control Station — FastAPI application entry point.
"""

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from legacy_stats import router as legacy_stats_router
from robot_client import robot, RobotConnectionError
from database import init_db, log_mission, get_connection
from auth import hash_password, verify_password, create_token, verify_token

#  Feature Flags
ENABLE_ADVANCED_STATS = os.getenv("FF_ADVANCED_STATS", "false").lower() == "true"

# Configuration
ROBOT_API_URL = os.getenv("ROBOT_API_URL", "http://robot-api:5000")
LOG_LEVEL = os.getenv("LOG_LEVEL", "info")

#  Logging
logging.basicConfig(level=LOG_LEVEL.upper())
logger = logging.getLogger(__name__)


# Lifespan
@asynccontextmanager
async def lifespan(app):
    """Initialise database on startup."""
    init_db()
    logger.info("Database ready.")
    yield


#  App factory
app = FastAPI(
    title="Ground Control Station",
    description="CMP9134 — Robot Management System",
    version="1.0.0",
    lifespan=lifespan,
)

#  CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#  Routers
app.include_router(legacy_stats_router)


#  Health check
@app.get("/health", include_in_schema=False)
def health():
    return {"status": "ok"}


#  Robot status
@app.get("/api/status")
async def get_status():
    """Return current robot status."""
    try:
        return await robot.get_status()
    except RobotConnectionError as exc:
        logger.warning("Could not reach robot API: %s", exc)
        return {"error": str(exc)}


#  Robot control
@app.post("/api/move")
async def move_robot(x: int, y: int):
    """Send a move command to the robot."""
    try:
        return await robot.move(x, y)
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))


@app.post("/api/reset")
async def reset_robot():
    """Reset the robot to its starting position."""
    try:
        return await robot.reset()
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))


#  Auth routes
@app.post("/api/register")
def register(username: str, password: str, role: str = "viewer"):
    """Register a new user."""
    if role not in ("viewer", "commander"):
        raise HTTPException(status_code=400, detail="Role must be viewer or commander")
    conn = get_connection()
    existing = conn.execute(
        "SELECT id FROM users WHERE username = ?", (username,)
    ).fetchone()
    if existing:
        conn.close()
        raise HTTPException(status_code=400, detail="Username already exists")
    conn.execute(
        "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
        (username, hash_password(password), role),
    )
    conn.commit()
    conn.close()
    return {"message": f"User {username} created with role {role}"}


@app.post("/api/login")
def login(username: str, password: str):
    """Login and get a token."""
    conn = get_connection()
    user = conn.execute(
        "SELECT * FROM users WHERE username = ?", (username,)
    ).fetchone()
    conn.close()
    if not user or not verify_password(password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_token(username, user["role"])
    return {"token": token, "role": user["role"], "username": username}


@app.get("/api/logs")
def get_logs(token: str):
    """Get mission logs - any authenticated user can view."""
    user = verify_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    conn = get_connection()
    logs = conn.execute(
        "SELECT * FROM mission_logs ORDER BY timestamp DESC LIMIT 50"
    ).fetchall()
    conn.close()
    return {"logs": [dict(row) for row in logs]}


#  Secure robot control (RBAC)
@app.post("/api/move/secure")
async def move_robot_secure(x: int, y: int, token: str):
    """Move robot - Commander only."""
    user = verify_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    if user["role"] != "commander":
        raise HTTPException(status_code=403, detail="Commanders only")
    try:
        result = await robot.move(x, y)
        log_mission(user["username"], "MOVE", f"x={x}, y={y}", str(result))
        return result
    except Exception as e:
        log_mission(user["username"], "MOVE_FAILED", f"x={x}, y={y}", str(e))
        raise HTTPException(status_code=503, detail=str(e))


@app.post("/api/reset/secure")
async def reset_robot_secure(token: str):
    """Reset robot - Commander only."""
    user = verify_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    if user["role"] != "commander":
        raise HTTPException(status_code=403, detail="Commanders only")
    try:
        result = await robot.reset()
        log_mission(user["username"], "RESET", "robot reset", str(result))
        return result
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))

    # Feature Flag Route


@app.get("/api/experimental_stats")
def get_experimental_stats():
    """Advanced stats endpoint — controlled by feature flag FF_ADVANCED_STATS."""
    if not ENABLE_ADVANCED_STATS:
        raise HTTPException(status_code=404, detail="Feature not yet available.")
    return {"status": "success", "data": "Advanced mission statistics enabled!"}

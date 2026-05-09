# backend/legacy_stats.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

MISSION_RULES = {
    1: ("recon", 10),
    2: ("transport", 5),
}
MAX_SCORE = 100


class MissionInput(BaseModel):
    """Pydantic model for mission stats input — FastAPI validates automatically."""

    type: int
    dist: float
    batt: float
    payload_weight: float = 0


def _compute_base_score(distance: float, battery: float, multiplier: float) -> float:
    """Compute base mission score."""
    if distance <= 0 or battery <= 0:
        return 0
    return (distance * multiplier) / battery


def _cap_score(score: float) -> float:
    """Cap score at maximum value."""
    return min(score, MAX_SCORE)


@router.post("/api/mission_stats")
def calc_stats(data: MissionInput):
    """Calculate mission statistics and score."""
    mission = MISSION_RULES.get(data.type)
    if mission is None:
        raise HTTPException(status_code=400, detail="Invalid mission type")

    status, multiplier = mission
    score = _compute_base_score(data.dist, data.batt, multiplier)

    if status == "transport" and data.payload_weight > 50 and score > 0:
        score = score - (data.payload_weight * 0.1)

    score = _cap_score(score)

    # Parameterised query — prevents SQL injection
    query = "INSERT INTO stats (mission, score) VALUES (?, ?)"
    print(f"[DB LOG] Would execute: {query} with ({status}, {score})")

    return {"status": "success", "mission": status, "final_score": round(score, 2)}

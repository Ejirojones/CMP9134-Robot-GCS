"""
Robot API client scaffold.
"""

from __future__ import annotations

import logging
import os
from typing import Any

import httpx

ROBOT_API_URL = os.getenv("ROBOT_API_URL", "http://robot-api:5000")

logger = logging.getLogger(__name__)


class RobotConnectionError(Exception):
    """Raised when a request to the robot API fails."""


class RobotClient:
    """Minimal async HTTP client for the Virtual Robot API."""

    def __init__(self, base_url: str = ROBOT_API_URL) -> None:
        self._base = base_url.rstrip("/")

    async def get_status(self) -> dict[str, Any]:
        """Fetch current robot status (position, battery, state)."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self._base}/api/status", timeout=5.0)
                response.raise_for_status()
                return response.json()
        except Exception as exc:
            raise RobotConnectionError(f"Robot unreachable: {exc}") from exc

    async def move(self, x: int, y: int) -> dict[str, Any]:
        """Send move command with retry logic for chaos monkey."""
        last_error = None
        for attempt in range(3):
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{self._base}/api/move", json={"x": x, "y": y}, timeout=10.0
                    )
                    response.raise_for_status()
                    return response.json()
            except Exception as exc:
                last_error = exc
                logger.warning("Move attempt %d failed: %s", attempt + 1, exc)
        raise RobotConnectionError(f"Move failed after 3 attempts: {last_error}")

    async def reset(self) -> dict[str, Any]:
        """Reset robot with retry logic for chaos monkey."""
        last_error = None
        for attempt in range(3):
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{self._base}/api/reset", timeout=10.0
                    )
                    response.raise_for_status()
                    return response.json()
            except Exception as exc:
                last_error = exc
                logger.warning("Reset attempt %d failed: %s", attempt + 1, exc)
        raise RobotConnectionError(f"Reset failed after 3 attempts: {last_error}")


# Module-level singleton used by main.py
robot = RobotClient()

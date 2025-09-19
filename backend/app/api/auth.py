from __future__ import annotations

import httpx
from fastapi import APIRouter, Depends, Header, HTTPException

from app.config import SUPABASE_URL
from app.dependencies.supabase import get_supabase_client

router = APIRouter()


async def get_current_user(
    authorization: str = Header(None),
    client: httpx.AsyncClient = Depends(get_supabase_client),
):
    """Validate JWT Token with Supabase."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid Authorization Header")

    if not SUPABASE_URL:
        raise HTTPException(status_code=500, detail="Supabase URL is not configured")

    token = authorization.split("Bearer ", 1)[1].strip()
    if not token:
        raise HTTPException(status_code=401, detail="Invalid Authorization Header")

    try:
        response = await client.get(
            f"{SUPABASE_URL}/auth/v1/user",
            headers={"Authorization": f"Bearer {token}"},
        )
    except httpx.RequestError as exc:  # pragma: no cover - network failure
        raise HTTPException(status_code=503, detail="Unable to reach Supabase") from exc

    if response.status_code != 200:
        raise HTTPException(status_code=401, detail="Invalid Token")

    return response.json()


@router.get("/me")
async def get_user(user: dict = Depends(get_current_user)):
    """Returns authenticated user data."""
    return user

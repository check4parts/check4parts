"""FastAPI dependencies related to the ASG integration."""

from __future__ import annotations

from typing import Any, AsyncGenerator, Dict, Optional

from fastapi import Request

from app.adapters.asg_adapter import ASGAdapter


def _normalise_value(value: Optional[Any]) -> Optional[str]:
    if isinstance(value, str):
        trimmed = value.strip()
        return trimmed or None
    return None


async def _extract_body_credentials(request: Request) -> Dict[str, Optional[str]]:
    try:
        payload = await request.json()
    except Exception:  # pragma: no cover - body may be empty or malformed
        return {"login": None, "password": None}

    if not isinstance(payload, dict):
        return {"login": None, "password": None}

    login = _normalise_value(payload.get("login"))
    password = _normalise_value(payload.get("password"))
    return {"login": login, "password": password}


async def get_asg_adapter(request: Request) -> AsyncGenerator[ASGAdapter, None]:
    """Provide a configured :class:`ASGAdapter` for request handlers."""

    login = _normalise_value(request.headers.get("x-asg-login"))
    password = _normalise_value(request.headers.get("x-asg-password"))

    if not login or not password:
        body_credentials = await _extract_body_credentials(request)
        login = login or body_credentials["login"]
        password = password or body_credentials["password"]

    token: Optional[str] = None
    auth_header = request.headers.get("authorization")
    if isinstance(auth_header, str) and auth_header.lower().startswith("bearer "):
        token = _normalise_value(auth_header.split(" ", 1)[1])

    adapter = ASGAdapter(login=login, password=password, token=token)

    request.state.asg_credentials = {"login": login, "password": password, "token": token}

    async with adapter as session:
        yield session


__all__ = ["get_asg_adapter"]

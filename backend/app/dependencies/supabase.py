"""Supabase-specific FastAPI dependencies."""

from __future__ import annotations

from typing import Optional

import httpx

SUPABASE_TIMEOUT = httpx.Timeout(10.0)
_supabase_client: Optional[httpx.AsyncClient] = None


def _create_client() -> httpx.AsyncClient:
    return httpx.AsyncClient(timeout=SUPABASE_TIMEOUT)


async def get_supabase_client() -> httpx.AsyncClient:
    """Return a shared :class:`httpx.AsyncClient` instance for Supabase calls."""

    global _supabase_client
    if _supabase_client is None:
        _supabase_client = _create_client()
    return _supabase_client


__all__ = ["get_supabase_client", "SUPABASE_TIMEOUT"]

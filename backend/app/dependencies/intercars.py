"""FastAPI dependencies related to InterCars integrations."""

import os
from typing import AsyncGenerator

from dotenv import load_dotenv
from fastapi import HTTPException

from app.adapters.intercars_adapter import IntercarsAdapter
from app.services.token_cache import InMemoryTokenCache

load_dotenv()

_token_cache = InMemoryTokenCache()


async def get_intercars_adapter() -> AsyncGenerator[IntercarsAdapter, None]:
    """Provide an :class:`IntercarsAdapter` seeded with configured credentials."""

    client_id = os.getenv("INTERCARS_CLIENT_ID")
    client_secret = os.getenv("INTERCARS_CLIENT_SECRET")

    if not client_id or not client_secret:
        raise HTTPException(
            status_code=500,
            detail="InterCars credentials are not configured in the environment.",
        )

    adapter = IntercarsAdapter(
        client_id=client_id,
        client_secret=client_secret,
        token_cache=_token_cache,
    )

    async with adapter as session:
        yield session


def reset_intercars_token_cache() -> None:
    """Clear cached tokens (primarily for testing)."""

    _token_cache.clear_all()


def get_intercars_token_cache() -> InMemoryTokenCache:
    """Expose the shared token cache instance."""

    return _token_cache


__all__ = [
    "get_intercars_adapter",
    "get_intercars_token_cache",
    "reset_intercars_token_cache",
]

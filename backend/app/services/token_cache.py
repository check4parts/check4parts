"""Token caching utilities for InterCars API access tokens."""

from __future__ import annotations
"""Token caching utilities for InterCars API access tokens."""

import asyncio
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional, Protocol, Tuple


@dataclass
class CachedToken:
    """Represents an access token cached for reuse."""

    access_token: str
    refresh_token: Optional[str]
    expires_at: datetime


class TokenCacheProtocol(Protocol):
    """Minimal protocol required by :class:`IntercarsAdapter`."""

    async def get(self, client_id: str, client_secret: str) -> Optional[CachedToken]:
        """Return cached token data for the credential pair if available."""

    async def set(
        self,
        client_id: str,
        client_secret: str,
        token: CachedToken,
    ) -> None:
        """Persist token data for the credential pair."""

    async def clear(self, client_id: str, client_secret: str) -> None:
        """Remove cached token data for the credential pair."""


class InMemoryTokenCache(TokenCacheProtocol):
    """Thread-safe in-memory cache for access and refresh tokens."""

    def __init__(self) -> None:
        self._cache: Dict[Tuple[str, str], CachedToken] = {}
        self._lock = asyncio.Lock()

    async def get(self, client_id: str, client_secret: str) -> Optional[CachedToken]:
        cache_key = (client_id, client_secret)
        async with self._lock:
            cached = self._cache.get(cache_key)
            if not cached:
                return None

            if cached.expires_at <= datetime.utcnow():
                self._cache.pop(cache_key, None)
                return None

            return cached

    async def set(self, client_id: str, client_secret: str, token: CachedToken) -> None:
        cache_key = (client_id, client_secret)
        async with self._lock:
            self._cache[cache_key] = token

    async def clear(self, client_id: str, client_secret: str) -> None:
        cache_key = (client_id, client_secret)
        async with self._lock:
            self._cache.pop(cache_key, None)

    def clear_all(self) -> None:
        """Utility helper primarily intended for tests."""

        self._cache.clear()


__all__ = [
    "CachedToken",
    "TokenCacheProtocol",
    "InMemoryTokenCache",
]

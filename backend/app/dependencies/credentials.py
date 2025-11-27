from typing import AsyncGenerator

from app.services.credentials import DEFAULT_CREDENTIAL_STORE, ClientCredentialStore


async def get_credential_store() -> AsyncGenerator[ClientCredentialStore, None]:
    yield DEFAULT_CREDENTIAL_STORE


__all__ = ["get_credential_store"]

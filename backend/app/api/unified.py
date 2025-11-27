"""Unified search/products fan-out endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Path
from pydantic import BaseModel, Field

from app.api.auth import get_current_user
from app.dependencies.credentials import get_credential_store
from app.services.credentials import (
    ClientCredentialStore,
    InvalidCredentialError,
    UnknownSupplierError,
)
from app.services.unified_catalog import (
    UnifiedProductsRequest,
    UnifiedSearchRequest,
    unified_products,
    unified_search,
)

router = APIRouter(prefix="/space", tags=["Unified Catalog"])


class SupplierCredentialPayload(BaseModel):
    credentials: dict = Field(default_factory=dict)


def _client_id_from_user(user: dict) -> str:
    for key in ("id", "user_id", "sub"):
        if user.get(key):
            return str(user[key])
    raise HTTPException(status_code=400, detail="Unable to determine client id")


@router.post("/search")
async def search_space(
    request: UnifiedSearchRequest,
    user: dict = Depends(get_current_user),
    credential_store: ClientCredentialStore = Depends(get_credential_store),
):
    """Search across enabled suppliers using a BM Parts–like response shape."""

    client_id = _client_id_from_user(user)
    return await unified_search(
        request, client_id=client_id, credential_store=credential_store
    )


@router.post("/products")
async def products_space(
    request: UnifiedProductsRequest,
    user: dict = Depends(get_current_user),
    credential_store: ClientCredentialStore = Depends(get_credential_store),
):
    """Fetch product details from multiple suppliers while tolerating partial failures."""

    client_id = _client_id_from_user(user)
    return await unified_products(
        request, client_id=client_id, credential_store=credential_store
    )


@router.post("/credentials/{supplier}")
async def store_supplier_credentials(
    payload: SupplierCredentialPayload,
    supplier: str = Path(..., description="Supplier identifier"),
    user: dict = Depends(get_current_user),
    credential_store: ClientCredentialStore = Depends(get_credential_store),
):
    """Persist credentials for the authenticated client and supplier."""

    client_id = _client_id_from_user(user)
    try:
        credential_store.set_credentials(client_id, supplier, payload.credentials)
    except UnknownSupplierError as exc:  # pragma: no cover - simple mapping
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except InvalidCredentialError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {"supplier": supplier, "stored": True}


@router.get("/credentials")
async def list_supplier_credentials(
    user: dict = Depends(get_current_user),
    credential_store: ClientCredentialStore = Depends(get_credential_store),
):
    """Return credential availability per supplier without revealing secrets."""

    client_id = _client_id_from_user(user)
    return {"credentials": credential_store.supplier_status(client_id)}


"""Unified search/products fan-out endpoints."""

from fastapi import APIRouter, Depends

from app.api.auth import get_current_user
from app.services.unified_catalog import (
    UnifiedProductsRequest,
    UnifiedSearchRequest,
    unified_products,
    unified_search,
)

router = APIRouter(prefix="/space", tags=["Unified Catalog"])


@router.post("/search")
async def search_space(
    request: UnifiedSearchRequest,
    user: dict = Depends(get_current_user),  # noqa: ARG001 - validation side effect
):
    """Search across enabled suppliers using a BM Parts–like response shape."""

    return await unified_search(request, client_id=user.get("id"))


@router.post("/products")
async def products_space(
    request: UnifiedProductsRequest,
    user: dict = Depends(get_current_user),  # noqa: ARG001 - validation side effect
):
    """Fetch product details from multiple suppliers while tolerating partial failures."""

    return await unified_products(request, client_id=user.get("id"))


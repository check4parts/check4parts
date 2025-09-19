"""Aggregated search endpoints fan out to multiple providers."""

from __future__ import annotations

import asyncio
from typing import Any, Awaitable, Callable, Dict

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, ValidationError

from app.adapters.bm_parts_adapter import BMPartsAdapter, BMPartsAdapterError
from app.api.auth import get_current_user

router = APIRouter(prefix="/search", tags=["Aggregated Search"])


class ProviderSearchOptions(BaseModel):
    """Container for provider-specific search options."""

    name: str = Field(..., description="Provider key to query")
    options: Dict[str, Any] = Field(
        default_factory=dict,
        description="Provider specific options forwarded to the adapter",
    )


class AggregatedSearchRequest(BaseModel):
    """Request payload for executing a multi-provider product search."""

    query: str = Field(..., min_length=1, description="User supplied search term")
    providers: list[ProviderSearchOptions] = Field(
        ..., min_items=1, description="Providers that should participate in the search"
    )


class BMPartsSearchConfig(BaseModel):
    include_crosses: bool = False
    include_additional: bool = False
    filters: Dict[str, Any] = Field(default_factory=dict)


async def _search_bm_parts(query: str, options: Dict[str, Any]) -> Any:
    try:
        config = BMPartsSearchConfig.model_validate(options or {})
    except ValidationError as exc:
        raise HTTPException(
            status_code=422,
            detail={"message": "Invalid BM Parts search options", "errors": exc.errors()},
        ) from exc

    async with BMPartsAdapter() as adapter:
        return await adapter.search_products_enhanced(
            query,
            include_crosses=config.include_crosses,
            include_additional=config.include_additional,
            **config.filters,
        )


PROVIDER_HANDLERS: Dict[str, Callable[[str, Dict[str, Any]], Awaitable[Any]]] = {
    "bm-parts": _search_bm_parts,
}


async def _execute_provider(
    query: str, provider: ProviderSearchOptions
) -> Dict[str, Any]:
    handler = PROVIDER_HANDLERS.get(provider.name)
    if not handler:
        return {
            "provider": provider.name,
            "success": False,
            "error": {
                "status_code": 400,
                "detail": {"message": f"Unsupported provider '{provider.name}'"},
            },
        }

    try:
        data = await handler(query, provider.options)
        return {"provider": provider.name, "success": True, "data": data}
    except BMPartsAdapterError as exc:
        return {
            "provider": provider.name,
            "success": False,
            "error": {"status_code": exc.status_code, "detail": exc.detail},
        }
    except HTTPException as exc:
        return {
            "provider": provider.name,
            "success": False,
            "error": {"status_code": exc.status_code, "detail": exc.detail},
        }
    except Exception as exc:  # pragma: no cover - defensive programming
        return {
            "provider": provider.name,
            "success": False,
            "error": {
                "status_code": 500,
                "detail": {"message": "Unexpected adapter error", "error": str(exc)},
            },
        }


@router.post("/products")
async def aggregated_search(
    request: AggregatedSearchRequest,
    user: dict = Depends(get_current_user),  # noqa: ARG001 - validation side effect
):
    """Perform a multi-provider product search in a single request."""

    tasks = [_execute_provider(request.query, provider) for provider in request.providers]
    results = await asyncio.gather(*tasks)
    return {"query": request.query, "results": results}


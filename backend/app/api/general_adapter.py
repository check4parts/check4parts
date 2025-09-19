from __future__ import annotations

import asyncio
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel, Field

from app.adapters import adapter_registry
from app.adapters.base import AdapterError
from app.api.auth import get_current_user

router = APIRouter()


class AggregatedSearchRequest(BaseModel):
    """Describe the payload for aggregated adapter searches."""

    query: str = Field("", description="Search query forwarded to each provider")
    providers: List[str] = Field(
        default_factory=list,
        description="Optional list of provider identifiers. If omitted, all providers are used.",
    )
    provider_params: Dict[str, Dict[str, Any]] = Field(
        default_factory=dict,
        description="Optional dictionary of per-provider parameter overrides.",
    )


@router.get("/bmparts/data")
async def get_bm_parts_data(user: dict = Depends(get_current_user)) -> Dict[str, Any]:
    """Fetch data from BM Parts (Requires Authentication)."""

    adapter = adapter_registry["bmparts"]
    return adapter.fetch_data()


@router.post("/search", status_code=status.HTTP_200_OK)
async def aggregated_search(
    request: AggregatedSearchRequest,
    user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """Fan out the search request to all requested providers."""

    del user  # Authentication handled via dependency; suppress unused variable lint.

    if not adapter_registry:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="No providers configured")

    requested_providers = request.providers or list(adapter_registry.keys())

    missing = [name for name in requested_providers if name not in adapter_registry]
    if missing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": "Unknown providers requested", "providers": missing},
        )

    async def dispatch(provider_name: str) -> Dict[str, Any]:
        adapter = adapter_registry[provider_name]
        params = request.provider_params.get(provider_name, {})
        try:
            result = await run_in_threadpool(adapter.search, request.query, **params)
            return {"provider": provider_name, "data": result}
        except AdapterError as exc:
            return {"provider": provider_name, "error": str(exc)}

    responses = await asyncio.gather(*(dispatch(name) for name in requested_providers))

    aggregated: Dict[str, Any] = {}
    for entry in responses:
        provider_name = entry["provider"]
        if "data" in entry:
            aggregated[provider_name] = entry["data"]
        else:
            aggregated[provider_name] = {"error": entry.get("error", "Unknown error")}

    return {"results": aggregated}

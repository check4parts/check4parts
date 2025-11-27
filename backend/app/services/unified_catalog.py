"""Helpers for orchestrating supplier search and product lookups.

This module builds a unified abstraction over the various supplier adapters. It
fan-outs requests, normalises payloads to a BM Parts–like shape, and
coalesces partial failures into metadata instead of raising.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Awaitable, Callable, Dict

from fastapi import HTTPException
from pydantic import BaseModel, Field

from app.adapters.asg_adapter import ASGAdapter, ASGAPIError
from app.adapters.bm_parts_adapter import BMPartsAdapter, BMPartsAdapterError
from app.adapters.omega_adapter import OmegaAdapter, OmegaAPIError
from app.adapters.uniqtrade_adapter import UniqTradeAPIError, UniqTradeAdapter
from app.services.credentials import ClientCredentialStore, DEFAULT_CREDENTIAL_STORE

logger = logging.getLogger(__name__)


class SupplierConfig(BaseModel):
    """Supplier selector with optional adapter-specific options."""

    name: str
    options: Dict[str, Any] = Field(default_factory=dict)


class UnifiedSearchRequest(BaseModel):
    """Payload for the unified search endpoint."""

    query: str = Field(..., min_length=1)
    suppliers: list[str] | None = None
    supplier_options: Dict[str, Dict[str, Any]] = Field(default_factory=dict)


class SupplierProductRequest(BaseModel):
    """Product detail request scoped to a specific supplier."""

    supplier: str
    product_id: str
    options: Dict[str, Any] = Field(default_factory=dict)


class UnifiedProductsRequest(BaseModel):
    """Payload for fetching product details from multiple suppliers."""

    products: list[SupplierProductRequest]


class SupplierResult(BaseModel):
    """Outcome for a single supplier call."""

    supplier: str
    success: bool
    products: list[Dict[str, Any]] = Field(default_factory=list)
    raw: Any | None = None
    error: Dict[str, Any] | None = None


SUPPORTED_SUPPLIERS = ["bm-parts", "asg", "omega", "uniqtrade"]


def _normalise_part(supplier: str, product: Dict[str, Any]) -> Dict[str, Any]:
    """Return a BM Parts–like ``part`` payload for a supplier product."""

    raw_id = product.get("id")
    normalised_uuid: str | None
    if product.get("uuid"):
        normalised_uuid = product.get("uuid")
    elif raw_id is not None:
        normalised_uuid = str(raw_id)
    else:
        normalised_uuid = None

    return {
        "uuid": normalised_uuid,
        "name": product.get("name") or product.get("title") or product.get("description"),
        "code": product.get("code")
        or product.get("article")
        or product.get("sku")
        or product.get("oem"),
        "description": product.get("description"),
        "image": product.get("image") or product.get("photo") or product.get("picture"),
        "brand": product.get("brand") or product.get("producer") or product.get("manufacturer"),
        "details": product.get("details"),
        "crosses": product.get("crosses"),
        "additional": product.get("additional"),
        "supplier": supplier,
    }


def _normalise_rests(product: Dict[str, Any]) -> list[Dict[str, Any]]:
    """Return BM Parts–style ``rests`` entries when present."""

    if isinstance(product.get("rests"), list):
        return product["rests"]

    quantity = (
        product.get("quantity")
        or product.get("qty")
        or product.get("available")
        or product.get("rest")
    )
    price = product.get("price") or product.get("cost") or product.get("amount")
    delivery_time = product.get("delivery_time") or product.get("delivery")

    if quantity is None and price is None and delivery_time is None:
        return []

    provider_payload = product.get("provider") or {}
    warehouse_payload = product.get("warehouse") or {}

    return [
        {
            "provider": provider_payload,
            "warehouse": warehouse_payload,
            "quantity": quantity,
            "delivery_time": delivery_time,
            "price": price,
        }
    ]


def _extract_products_from_response(raw: Any) -> list[Dict[str, Any]]:
    """Best-effort extraction of product collections from heterogeneous payloads."""

    if isinstance(raw, list):
        return [p for p in raw if isinstance(p, dict)]

    if not isinstance(raw, dict):
        return []

    for key in ("products", "items", "data", "result", "list"):
        value = raw.get(key)
        if isinstance(value, list):
            return [p for p in value if isinstance(p, dict)]

    # Some APIs return mapping keyed by identifier
    if raw and all(isinstance(v, dict) for v in raw.values()):
        return list(raw.values())

    return []


def _normalise_supplier_payload(supplier: str, raw: Any) -> list[Dict[str, Any]]:
    """Transform a supplier payload into BM Parts–shaped product entries."""

    products: list[Dict[str, Any]] = []
    for product in _extract_products_from_response(raw):
        products.append(
            {
                "part": _normalise_part(supplier, product),
                "rests": _normalise_rests(product),
                "supplier": supplier,
                "raw": product,
            }
        )

    return products


async def _call_handler(
    supplier: str,
    handler: Callable[[], Awaitable[Any]],
) -> SupplierResult:
    try:
        raw = await handler()
        return SupplierResult(
            supplier=supplier,
            success=True,
            raw=raw,
            products=_normalise_supplier_payload(supplier, raw),
        )
    except (BMPartsAdapterError, ASGAPIError, OmegaAPIError, UniqTradeAPIError) as exc:
        logger.warning("%s supplier call failed: %s", supplier, exc)
        status_code = getattr(exc, "status_code", 500)
        detail = getattr(exc, "detail", None) or getattr(exc, "details", None) or {
            "message": str(exc)
        }
        return SupplierResult(
            supplier=supplier,
            success=False,
            error={"status_code": status_code, "detail": detail},
        )
    except HTTPException as exc:
        logger.warning("%s supplier HTTP error: %s", supplier, exc)
        return SupplierResult(
            supplier=supplier,
            success=False,
            error={"status_code": exc.status_code, "detail": exc.detail},
        )
    except Exception as exc:  # pragma: no cover - defensive logging
        logger.exception("Unexpected supplier failure for %s", supplier)
        return SupplierResult(
            supplier=supplier,
            success=False,
            error={"status_code": 500, "detail": {"message": str(exc)}},
        )


async def _search_bm_parts(query: str, options: Dict[str, Any]) -> Any:
    include_crosses = bool(options.get("include_crosses"))
    include_additional = bool(options.get("include_additional"))
    filters = options.get("filters") or {}

    async with BMPartsAdapter(token=options.get("token")) as adapter:
        return await adapter.search_products_enhanced(
            query,
            include_crosses=include_crosses,
            include_additional=include_additional,
            **filters,
        )


async def _search_asg(query: str, options: Dict[str, Any]) -> Any:
    adapter = ASGAdapter(
        login=options.get("login"),
        password=options.get("password"),
        token=options.get("token"),
    )

    async with adapter as session:
        return await session.search_products(
            query,
            category_id=options.get("category_id"),
            page=options.get("page", 1),
            per_page=options.get("per_page", 20),
        )


async def _search_omega(query: str, options: Dict[str, Any]) -> Any:
    adapter = OmegaAdapter(key=options.get("key"))
    async with adapter as session:
        return await session.search_products(
            query,
            rest=int(options.get("rest", 0)),
            from_index=int(options.get("from", 0)),
            count=int(options.get("count", 20)),
        )


async def _search_uniqtrade(query: str, options: Dict[str, Any]) -> Any:
    adapter = UniqTradeAdapter(
        email=options.get("email"),
        password=options.get("password"),
        browser_fingerprint=options.get("fingerprint"),
    )

    async with adapter as session:
        return await session.search_by_oem(query, include_info=True, language=options.get("language"))


SEARCH_HANDLERS: dict[str, Callable[[str, Dict[str, Any]], Awaitable[Any]]] = {
    "bm-parts": _search_bm_parts,
    "asg": _search_asg,
    "omega": _search_omega,
    "uniqtrade": _search_uniqtrade,
}


async def unified_search(
    request: UnifiedSearchRequest,
    *,
    client_id: str | None = None,
    credential_store: ClientCredentialStore | None = None,
) -> Dict[str, Any]:
    """Execute a cross-supplier product search."""

    store = credential_store or DEFAULT_CREDENTIAL_STORE
    requested_suppliers = request.suppliers or SUPPORTED_SUPPLIERS
    tasks: list[Awaitable[SupplierResult]] = []
    attempted_suppliers: list[str] = []
    skipped_suppliers: list[Dict[str, Any]] = []

    for supplier in requested_suppliers:
        options = request.supplier_options.get(supplier, {})
        merged_options = store.resolve_credentials(client_id, supplier, options)
        if merged_options is None:
            skipped_suppliers.append(
                {
                    "supplier": supplier,
                    "reason": "missing_credentials",
                }
            )
            continue

        handler = SEARCH_HANDLERS.get(supplier)
        attempted_suppliers.append(supplier)
        if not handler:
            tasks.append(
                _call_handler(
                    supplier,
                    lambda s=supplier: (_ for _ in ()).throw(
                        HTTPException(
                            status_code=400,
                            detail={"message": f"Unsupported supplier '{s}'"},
                        )
                    ),
                )
            )
            continue

        tasks.append(
            _call_handler(
                supplier, lambda h=handler, o=merged_options: h(request.query, o)
            )
        )

    results = await asyncio.gather(*tasks)
    products = [product for result in results for product in result.products]
    failed = [
        {"supplier": result.supplier, "error": result.error}
        for result in results
        if not result.success and result.error
    ]

    return {
        "query": request.query,
        "products": products,
        "meta": {
            "requested_suppliers": requested_suppliers,
            "attempted_suppliers": attempted_suppliers,
            "skipped_suppliers": skipped_suppliers,
            "failed_suppliers": failed,
            "partial_failure": bool(failed),
        },
    }


async def _product_bm_parts(product_id: str, options: Dict[str, Any]) -> Any:
    async with BMPartsAdapter(token=options.get("token")) as adapter:
        return await adapter.get_product_details(product_id)


async def _product_asg(product_id: str, options: Dict[str, Any]) -> Any:
    adapter = ASGAdapter(
        login=options.get("login"),
        password=options.get("password"),
        token=options.get("token"),
    )
    async with adapter as session:
        return await session.get_product_details(product_id)


async def _product_omega(product_id: str, options: Dict[str, Any]) -> Any:
    adapter = OmegaAdapter(key=options.get("key"))
    async with adapter as session:
        return await session.search_brand(product_id, options.get("brand", ""))


async def _product_uniqtrade(product_id: str, options: Dict[str, Any]) -> Any:
    adapter = UniqTradeAdapter(
        email=options.get("email"),
        password=options.get("password"),
        browser_fingerprint=options.get("fingerprint"),
    )
    async with adapter as session:
        return await session.get_detail_info(product_id)


PRODUCT_HANDLERS: dict[str, Callable[[str, Dict[str, Any]], Awaitable[Any]]] = {
    "bm-parts": _product_bm_parts,
    "asg": _product_asg,
    "omega": _product_omega,
    "uniqtrade": _product_uniqtrade,
}


async def unified_products(
    request: UnifiedProductsRequest,
    *,
    client_id: str | None = None,
    credential_store: ClientCredentialStore | None = None,
) -> Dict[str, Any]:
    """Fetch product details from multiple suppliers concurrently."""

    store = credential_store or DEFAULT_CREDENTIAL_STORE
    tasks: list[Awaitable[SupplierResult]] = []
    skipped: list[Dict[str, Any]] = []
    attempted_suppliers: list[str] = []

    for product in request.products:
        merged_options = store.resolve_credentials(
            client_id, product.supplier, product.options
        )
        if merged_options is None:
            skipped.append(
                {
                    "supplier": product.supplier,
                    "product_id": product.product_id,
                    "reason": "missing_credentials",
                }
            )
            continue

        handler = PRODUCT_HANDLERS.get(product.supplier)
        attempted_suppliers.append(product.supplier)
        if not handler:
            tasks.append(
                _call_handler(
                    product.supplier,
                    lambda s=product.supplier: (_ for _ in ()).throw(
                        HTTPException(
                            status_code=400,
                            detail={"message": f"Unsupported supplier '{s}'"},
                        )
                    ),
                )
            )
            continue

        tasks.append(
            _call_handler(
                product.supplier,
                lambda h=handler, p=product, o=merged_options: h(
                    p.product_id, o
                ),
            )
        )

    results = await asyncio.gather(*tasks)
    products = [product for result in results for product in result.products]
    failed = [
        {"supplier": result.supplier, "error": result.error}
        for result in results
        if not result.success and result.error
    ]

    return {
        "products": products,
        "meta": {
            "attempted_suppliers": attempted_suppliers,
            "skipped_suppliers": skipped,
            "failed_suppliers": failed,
            "partial_failure": bool(failed),
        },
    }


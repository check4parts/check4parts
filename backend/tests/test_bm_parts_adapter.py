import asyncio
import sys
from pathlib import Path
from unittest.mock import AsyncMock

import httpx
import pytest

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.adapters.bm_parts_adapter import BMPartsAdapter, BMPartsAdapterError  # noqa: E402


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.mark.anyio("asyncio")
async def test_fetch_http_error_includes_payload():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(400, json={"error": "invalid"})

    transport = httpx.MockTransport(handler)
    client = httpx.AsyncClient(transport=transport)

    async with BMPartsAdapter(client=client) as adapter:
        with pytest.raises(BMPartsAdapterError) as exc_info:
            await adapter.fetch("/test")

    await client.aclose()

    error = exc_info.value
    assert error.status_code == 400
    assert isinstance(error.detail, dict)
    assert error.detail["error"] == "invalid"


@pytest.mark.anyio("asyncio")
async def test_fetch_request_error_retries_and_raises(monkeypatch: pytest.MonkeyPatch):
    attempts = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1
        raise httpx.ConnectTimeout("timeout", request=request)

    transport = httpx.MockTransport(handler)
    client = httpx.AsyncClient(transport=transport)

    async def fake_sleep(_: float) -> None:
        pass

    monkeypatch.setattr(asyncio, "sleep", fake_sleep)

    async with BMPartsAdapter(client=client) as adapter:
        adapter.MAX_RETRIES = 2
        with pytest.raises(BMPartsAdapterError) as exc_info:
            await adapter.fetch("/test")

    await client.aclose()

    assert attempts == 2
    error = exc_info.value
    assert error.status_code == 502
    assert "Failed to communicate" in error.detail["message"]


@pytest.mark.anyio("asyncio")
async def test_search_products_enhanced_skips_failed_enrichment():
    adapter = BMPartsAdapter()
    adapter.search_products = AsyncMock(
        return_value={"products": [{"uuid": "prod-1", "name": "Part"}]}
    )
    adapter.get_product_crosses = AsyncMock(
        side_effect=BMPartsAdapterError(status_code=500, detail={"error": "boom"})
    )
    adapter.get_product_additional = AsyncMock()

    result = await adapter.search_products_enhanced(
        "query", include_crosses=True, include_additional=True
    )

    product = result["products"][0]
    assert "crosses" not in product
    assert "additional" not in product
    adapter.get_product_additional.assert_not_awaited()


@pytest.mark.anyio("asyncio")
async def test_search_products_enhanced_adds_enrichments_on_success():
    adapter = BMPartsAdapter()
    adapter.search_products = AsyncMock(
        return_value={"products": [{"uuid": "prod-1", "name": "Part"}]}
    )
    adapter.get_product_crosses = AsyncMock(return_value=[{"id": "cross"}])
    adapter.get_product_additional = AsyncMock(return_value=[{"id": "extra"}])

    result = await adapter.search_products_enhanced(
        "query", include_crosses=True, include_additional=True
    )

    product = result["products"][0]
    assert product.get("crosses") == [{"id": "cross"}]
    assert product.get("additional") == [{"id": "extra"}]

import sys
from pathlib import Path

from typing import Dict, Optional

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.api.uniqtrade import router  # noqa: E402


app = FastAPI()
app.include_router(router)


client = TestClient(app)


class DummyResponse:
    def __init__(
        self, content: bytes = b"test", headers: Optional[Dict[str, str]] = None
    ):
        self.content = content
        self.headers = headers or {"content-type": "text/plain"}


class DummyAdapter:
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def search_by_oem(self, oem, include_info, language):
        return {
            "oem": oem,
            "include_info": include_info,
            "language": language,
        }

    async def search_by_oem_and_brand(self, oem, brand, include_info, language):
        return {
            "oem": oem,
            "brand": brand,
            "include_info": include_info,
            "language": language,
        }

    async def get_order_details(self, order_id, language):
        return {"id": order_id, "language": language}

    async def get_pricelist_export_params(self, language):
        return {"language": language}

    async def request_pricelist_export(self, *args, **kwargs):
        return {"requested": True, "params": kwargs}

    async def get_pricelist_status(self, pricelist_id, language):
        return {"id": pricelist_id, "status": "done"}

    async def get_pricelists(self, language):
        return {"items": []}

    async def download_pricelist(self, token, language):
        return DummyResponse()

    async def delete_pricelist(self, pricelist_id, language):
        return {"deleted": pricelist_id}

    async def add_to_cart(self, detail_id, quantity, language):
        return {"detail_id": detail_id, "quantity": quantity}

    async def get_brands(self, language):
        return {"brands": []}

    async def get_storages(self, all_storages, point_id, language):
        return {"storages": [], "all": all_storages, "point": point_id}

    async def get_accounting_numbers_by_order(self, order_code, language):
        return {"order_code": order_code}

    async def get_order_by_accounting_number(self, accounting_number, language):
        return {"accounting_number": accounting_number}


@pytest.fixture(autouse=True)
def _mock_adapter(monkeypatch):
    monkeypatch.setattr("app.api.uniqtrade.UniqTradeAdapter", DummyAdapter)


def test_search_by_oem_endpoint():
    response = client.get(
        "/uniqtrade/search/products/ABC123",
        params={"info": 1, "language": "ru"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "oem": "ABC123",
        "include_info": True,
        "language": "ru",
    }


def test_search_by_oem_and_brand_endpoint():
    response = client.get(
        "/uniqtrade/search/products/ABC123/brand/ACME",
        params={"info": 0},
    )

    assert response.status_code == 200
    assert response.json() == {
        "oem": "ABC123",
        "brand": "ACME",
        "include_info": False,
        "language": "ua",
    }


def test_get_order_details_endpoint():
    response = client.get("/uniqtrade/orders/1")
    payload = response.json()

    assert response.status_code == 200
    assert payload["id"] == 1
    assert payload["language"] == "ua"


def test_pricelist_endpoints_flow():
    params_response = client.get("/uniqtrade/pricelists/export-params")
    export_response = client.post(
        "/uniqtrade/pricelists/export-request",
        json={
            "format": "xlsx",
            "visible_brands_id": [1],
            "in_stock": True,
            "show_scancode": False,
            "utr_article": False,
        },
    )
    status_response = client.get("/uniqtrade/pricelists/5/status")
    list_response = client.get("/uniqtrade/pricelists")
    delete_response = client.delete("/uniqtrade/pricelists/5")
    download_response = client.get("/uniqtrade/pricelists/download/token")

    assert params_response.status_code == 200
    assert params_response.json() == {"language": "ua"}
    assert export_response.status_code == 200
    assert export_response.json()["requested"] is True
    assert status_response.json()["status"] == "done"
    assert list_response.json()["items"] == []
    assert delete_response.json()["deleted"] == 5
    assert download_response.status_code == 200
    assert download_response.content == b"test"


def test_miscellaneous_endpoints():
    add_response = client.post(
        "/uniqtrade/cart/add", json={"detail_id": 10, "quantity": 2}
    )
    brands_response = client.get("/uniqtrade/brands")
    storages_response = client.get(
        "/uniqtrade/storages", params={"all_storages": True, "point_id": 7}
    )
    accounting_order_response = client.get(
        "/uniqtrade/accounting/by-order/ORDER1"
    )
    accounting_number_response = client.get(
        "/uniqtrade/accounting/by-number/ACC1"
    )

    assert add_response.json() == {"detail_id": 10, "quantity": 2}
    assert brands_response.json() == {"brands": []}
    assert storages_response.json()["all"] is True
    assert accounting_order_response.json()["order_code"] == "ORDER1"
    assert accounting_number_response.json()["accounting_number"] == "ACC1"

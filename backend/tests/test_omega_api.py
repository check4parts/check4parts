import importlib
import sys
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from fastapi.routing import APIRoute

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.api import omega  # noqa: E402


app = FastAPI()
app.include_router(omega.router)


client = TestClient(app)


MUTATING_GET_ROUTES = {
    "/omega/basket/add-product",
    "/omega/basket/remove-product",
    "/omega/claims/kind-claims",
    "/omega/claims/discount",
    "/omega/claims/addresses",
    "/omega/contact/get-contacts",
    "/omega/contact/get-contact-details",
    "/omega/expense/get-expense-document",
    "/omega/expense/get-expense-document-list",
    "/omega/expense/get-expense-document-details",
}


def _load_omega_router(monkeypatch: pytest.MonkeyPatch, flag_value: str | None) -> FastAPI:
    if flag_value is None:
        monkeypatch.delenv("ENABLE_MUTATING_GET_ROUTES", raising=False)
    else:
        monkeypatch.setenv("ENABLE_MUTATING_GET_ROUTES", flag_value)

    config_module = importlib.import_module("app.config")
    omega_module = importlib.import_module("app.api.omega")
    importlib.reload(config_module)
    importlib.reload(omega_module)

    test_app = FastAPI()
    test_app.include_router(omega_module.router)
    return test_app


def test_add_product_to_basket_rejects_zero_count(monkeypatch: pytest.MonkeyPatch):
    call_tracker = {}

    class DummyAdapter:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            call_tracker["entered"] = True
            return self

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            call_tracker["exited"] = True

        async def add_product_to_basket(self, product_id: int, count: int):
            call_tracker["called"] = True

    monkeypatch.setattr(omega, "OmegaAdapter", DummyAdapter)

    response = client.post(
        "/omega/basket/add-product", json={"product_id": 123, "count": 0}
    )

    assert response.status_code == 422
    assert "entered" not in call_tracker


def test_mutating_get_routes_disabled_by_default(monkeypatch: pytest.MonkeyPatch):
    test_app = _load_omega_router(monkeypatch, None)

    get_routes = {
        route.path
        for route in test_app.router.routes
        if isinstance(route, APIRoute) and "GET" in route.methods
    }

    assert MUTATING_GET_ROUTES.isdisjoint(get_routes)


def test_mutating_get_routes_can_be_reenabled(monkeypatch: pytest.MonkeyPatch):
    test_app = _load_omega_router(monkeypatch, "true")

    get_routes = {
        route.path
        for route in test_app.router.routes
        if isinstance(route, APIRoute) and "GET" in route.methods
    }

    assert MUTATING_GET_ROUTES.issubset(get_routes)

    for route in test_app.router.routes:
        if (
            isinstance(route, APIRoute)
            and route.path in MUTATING_GET_ROUTES
            and "GET" in route.methods
        ):
            assert route.deprecated is True

    # Reset modules back to the default state to avoid side effects on other tests
    _load_omega_router(monkeypatch, None)

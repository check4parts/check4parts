import sys
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.adapters.asg_adapter import ASGAdapter
from app.api.asg import router


@pytest.fixture
def asg_client():
    app = FastAPI()
    app.include_router(router)
    with TestClient(app) as client:
        yield client


def test_create_order_requires_id_or_sku(asg_client):
    response = asg_client.post(
        "/asg/orders/create",
        json={"products": [{"quantity": 1}], "test": False},
    )

    assert response.status_code == 422
    detail = response.json()["detail"]
    assert any(
        "Either 'id' or 'sku' must be provided for a product item." in error.get("msg", "")
        for error in detail
    ), detail
def _configure_token_hooks(storage):
    async def load_hook(cache_key: str):
        return storage.get(cache_key)

    async def save_hook(cache_key: str, token):
        if token is None:
            storage.pop(cache_key, None)
        else:
            storage[cache_key] = token

    ASGAdapter.configure_token_persistence(
        load_hook=load_hook,
        save_hook=save_hook,
    )


def test_login_persists_token(monkeypatch, asg_client):
    storage = {}
    _configure_token_hooks(storage)

    async def fake_make_request(self, method, endpoint, **kwargs):
        assert endpoint == "/auth/login"
        assert method == "POST"
        return {"access_token": "token-login", "expires_in": 3600}

    monkeypatch.setattr(ASGAdapter, "_make_request", fake_make_request)

    response = asg_client.post(
        "/asg/login", json={"login": "demo", "password": "secret"}
    )

    assert response.status_code == 200
    assert response.json()["access_token"] == "token-login"

    adapter = ASGAdapter(login="demo", password="secret")
    cache_key = adapter._credential_key  # noqa: SLF001 - test helper
    assert cache_key in storage
    assert storage[cache_key].token == "token-login"


def test_refresh_updates_cached_token(monkeypatch, asg_client):
    storage = {}
    _configure_token_hooks(storage)

    async def fake_make_request(self, method, endpoint, **kwargs):
        if endpoint == "/auth/login":
            return {"access_token": "token-login", "expires_in": 3600}
        if endpoint == "/auth/refresh":
            return {"access_token": "token-refresh", "expires_in": 3600}
        raise AssertionError(f"Unexpected endpoint {endpoint}")

    monkeypatch.setattr(ASGAdapter, "_make_request", fake_make_request)

    login_payload = {"login": "demo", "password": "secret"}
    login_response = asg_client.post("/asg/login", json=login_payload)
    assert login_response.status_code == 200

    refresh_response = asg_client.post(
        "/asg/refresh",
        headers={"X-ASG-Login": "demo", "X-ASG-Password": "secret"},
    )

    assert refresh_response.status_code == 200
    assert refresh_response.json()["access_token"] == "token-refresh"

    adapter = ASGAdapter(login="demo", password="secret")
    cache_key = adapter._credential_key  # noqa: SLF001 - test helper
    assert storage[cache_key].token == "token-refresh"


def test_authenticated_call_reuses_cache(monkeypatch, asg_client):
    storage = {}
    _configure_token_hooks(storage)

    calls = []

    async def fake_make_request(self, method, endpoint, **kwargs):
        if endpoint == "/auth/login":
            calls.append("login")
            return {"access_token": "token-login", "expires_in": 3600}
        if endpoint == "/auth/me":
            calls.append("me")
            assert self._access_token == "token-login"
            return {"user": {"id": 1}}
        raise AssertionError(f"Unexpected endpoint {endpoint}")

    monkeypatch.setattr(ASGAdapter, "_make_request", fake_make_request)

    asg_client.post("/asg/login", json={"login": "demo", "password": "secret"})

    response = asg_client.post(
        "/asg/me", headers={"X-ASG-Login": "demo", "X-ASG-Password": "secret"}
    )

    assert response.status_code == 200
    assert response.json() == {"user": {"id": 1}}
    assert calls == ["login", "me"]

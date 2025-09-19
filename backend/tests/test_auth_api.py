import sys
from pathlib import Path
from typing import Any, Dict

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).resolve().parents[1]))

import app.api.auth as auth_module
from app.api.auth import router
from app.dependencies.supabase import get_supabase_client


class DummyResponse:
    def __init__(self, status_code: int, payload: Dict[str, Any]):
        self.status_code = status_code
        self._payload = payload

    def json(self) -> Dict[str, Any]:
        return self._payload


class DummySupabaseClient:
    def __init__(self, response: DummyResponse):
        self._response = response
        self.requests = []

    async def get(self, url: str, *, headers: Dict[str, str]):
        self.requests.append((url, headers))
        return self._response


@pytest.fixture
def auth_app(monkeypatch):
    app = FastAPI()
    app.include_router(router, prefix="/auth")

    monkeypatch.setattr(auth_module, "SUPABASE_URL", "https://supabase.test")

    yield app


def test_auth_me_returns_user(auth_app):
    dummy_response = DummyResponse(200, {"id": "user-123"})
    dummy_client = DummySupabaseClient(dummy_response)

    async def override_client():
        return dummy_client

    auth_app.dependency_overrides[get_supabase_client] = override_client

    with TestClient(auth_app) as client:
        response = client.get(
            "/auth/me",
            headers={"Authorization": "Bearer demo-token"},
        )

    assert response.status_code == 200
    assert response.json() == {"id": "user-123"}
    assert dummy_client.requests == [
        ("https://supabase.test/auth/v1/user", {"Authorization": "Bearer demo-token"})
    ]


def test_auth_me_invalid_token(auth_app):
    dummy_response = DummyResponse(401, {"message": "invalid"})
    dummy_client = DummySupabaseClient(dummy_response)

    async def override_client():
        return dummy_client

    auth_app.dependency_overrides[get_supabase_client] = override_client

    with TestClient(auth_app) as client:
        response = client.get(
            "/auth/me",
            headers={"Authorization": "Bearer expired-token"},
        )

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid Token"}


def test_auth_me_missing_authorization_header(auth_app):
    with TestClient(auth_app) as client:
        response = client.get("/auth/me")

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid Authorization Header"}

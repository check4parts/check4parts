import sys
from datetime import datetime, timedelta
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.adapters.intercars_adapter import IntercarsAdapter  # noqa: E402
from app.api.intercars import router  # noqa: E402
from app.dependencies.intercars import reset_intercars_token_cache  # noqa: E402


class RecordingAdapter(IntercarsAdapter):
    """IntercarsAdapter stub that records authentication and requests."""

    auth_calls = 0
    recorded_requests = []
    last_credentials = None

    async def _authenticate(self):
        type(self).auth_calls += 1
        type(self).last_credentials = (self._client_id, self._client_secret)
        self._access_token = "token-123"
        self._refresh_token = "refresh-456"
        self._token_expires_at = datetime.utcnow() + timedelta(hours=1)
        await self._store_token_in_cache()
        return {
            "access_token": self._access_token,
            "refresh_token": self._refresh_token,
            "expires_in": 3600,
        }

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        params=None,
        json_data=None,
        require_auth: bool = True,
    ):
        if require_auth:
            await self._ensure_authenticated()

        payload = {
            "method": method,
            "endpoint": endpoint,
            "params": params,
            "json": json_data,
            "token": self._access_token,
        }
        type(self).recorded_requests.append(payload)

        if endpoint == "inventory/quote":
            return {"items": []}
        if endpoint == "delivery/metadata":
            return {"deliveries": []}
        if endpoint == "invoice/metadata":
            return {"invoices": []}

        return {}


def test_intercars_endpoints_use_configured_credentials(monkeypatch):
    monkeypatch.setenv("INTERCARS_CLIENT_ID", "test-client-id")
    monkeypatch.setenv("INTERCARS_CLIENT_SECRET", "test-client-secret")
    reset_intercars_token_cache()

    RecordingAdapter.auth_calls = 0
    RecordingAdapter.recorded_requests = []
    RecordingAdapter.last_credentials = None
    monkeypatch.setattr(
        "app.dependencies.intercars.IntercarsAdapter",
        RecordingAdapter,
    )

    app = FastAPI()
    app.include_router(router)

    client = TestClient(app)

    response = client.post(
        "/intercars/inventory/quote",
        json={"lines": [{"sku": "ABC123", "quantity": 1}]},
    )
    assert response.status_code == 200
    assert response.json() == {"items": []}

    response = client.get(
        "/intercars/delivery/search",
        params={
            "creation_date_from": "2024-01-01T00:00:00Z",
            "creation_date_to": "2024-01-02T00:00:00Z",
            "offset": 1,
            "limit": 20,
        },
    )
    assert response.status_code == 200
    assert response.json() == {"deliveries": []}

    response = client.get(
        "/intercars/invoice/search",
        params={
            "issue_date_from": "2024-01-01T00:00:00Z",
            "issue_date_to": "2024-01-02T00:00:00Z",
            "offset": 1,
            "limit": 20,
        },
    )
    assert response.status_code == 200
    assert response.json() == {"invoices": []}

    assert RecordingAdapter.auth_calls == 1
    assert RecordingAdapter.last_credentials == ("test-client-id", "test-client-secret")
    assert [req["endpoint"] for req in RecordingAdapter.recorded_requests] == [
        "inventory/quote",
        "delivery/metadata",
        "invoice/metadata",
    ]
    assert all(req["token"] == "token-123" for req in RecordingAdapter.recorded_requests)

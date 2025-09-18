import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.api.intercars import router  # noqa: E402


class DummyIntercarsAdapter:
    last_payload = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def submit_requisition(self, payload):
        type(self).last_payload = payload
        return {"status": "ok"}


def test_submit_requisition_accepts_camel_case(monkeypatch):
    app = FastAPI()
    app.include_router(router)

    client = TestClient(app)

    monkeypatch.setattr(
        "app.api.intercars.IntercarsAdapter", DummyIntercarsAdapter
    )

    payload = {
        "lines": [
            {
                "sku": "ABC123",
                "requiredQuantity": 2,
                "unitPriceNet": 10.5,
                "unitPriceGross": 12.6,
            }
        ],
        "customNumber": "CUST-1",
    }

    response = client.post("/intercars/sales/requisition", json=payload)

    assert response.status_code == 200
    assert DummyIntercarsAdapter.last_payload == payload

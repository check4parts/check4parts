import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.api.intercars import get_intercars_adapter, router  # noqa: E402


class DummyIntercarsAdapter:
    last_payload = None

    async def submit_requisition(self, payload):
        type(self).last_payload = payload
        return {"status": "ok"}


async def _provide_dummy_adapter():
    yield DummyIntercarsAdapter()


def test_submit_requisition_accepts_camel_case():
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_intercars_adapter] = _provide_dummy_adapter

    client = TestClient(app)

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

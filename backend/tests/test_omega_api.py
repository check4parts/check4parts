import sys
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.api import omega  # noqa: E402


app = FastAPI()
app.include_router(omega.router)


client = TestClient(app)


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

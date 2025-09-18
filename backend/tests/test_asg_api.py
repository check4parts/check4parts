import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.api.asg import router


app = FastAPI()
app.include_router(router)


client = TestClient(app)


def test_create_order_requires_id_or_sku():
    response = client.post(
        "/asg/orders/create",
        json={"products": [{"quantity": 1}], "test": False},
    )

    assert response.status_code == 422
    detail = response.json()["detail"]
    assert any(
        "Either 'id' or 'sku' must be provided for a product item." in error.get("msg", "")
        for error in detail
    ), detail

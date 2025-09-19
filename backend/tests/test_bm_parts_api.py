import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.api.bm_parts import router  # noqa: E402


app = FastAPI()
app.include_router(router)


client = TestClient(app)


def test_change_product_requires_to_product_uuid():
    payload = {
        "cart_uuid": "cart-uuid",
        "from_product_uuid": "product-a",
    }
    response = client.post("/bm-parts/change_product/", json=payload)
    assert response.status_code == 422
    detail = response.json()["detail"]
    assert any(error.get("loc", [])[-1] == "to_product_uuid" for error in detail)


def test_add_cart_product_schema_requires_quantity():
    response = client.post(
        "/bm-parts/shopping/cart/test-cart/product",
        json={"product_uuid": "product-uuid"},
    )

    assert response.status_code == 422
    detail = response.json()["detail"]
    assert any(error.get("loc", [])[-1] == "quantity" for error in detail)


def test_delete_reserves_requires_orders_list():
    response = client.request(
        "DELETE", "/bm-parts/reserves/", json={"orders": "not-a-list"}
    )

    assert response.status_code == 422
    detail = response.json()["detail"]
    assert any("orders" in error.get("loc", []) for error in detail)


def test_cart_product_openapi_schema_contains_examples():
    schema = app.openapi()
    path_item = schema["paths"]["/bm-parts/shopping/cart/{cart_uuid}/product"]
    schema_ref = path_item["post"]["requestBody"]["content"]["application/json"]["schema"]

    if "$ref" in schema_ref:
        component_name = schema_ref["$ref"].split("/")[-1]
        post_schema = schema["components"]["schemas"][component_name]
    else:
        post_schema = schema_ref

    assert set(post_schema["required"]) == {"product_uuid", "quantity"}
    example = post_schema["example"]
    assert example["quantity"] == 2
    assert "product_uuid" in example


def test_delete_reserves_openapi_schema_contains_example():
    schema = app.openapi()
    schema_ref = schema["paths"]["/bm-parts/reserves/"]["delete"]["requestBody"][
        "content"
    ]["application/json"]["schema"]

    if "$ref" in schema_ref:
        component_name = schema_ref["$ref"].split("/")[-1]
        delete_schema = schema["components"]["schemas"][component_name]
    else:
        delete_schema = schema_ref

    assert delete_schema["type"] == "object"
    assert "orders" in delete_schema["required"]
    assert isinstance(delete_schema["example"]["orders"], list)

from typing import Optional, List

from fastapi import APIRouter, Request
from pydantic import BaseModel

from app.adapters.bm_parts_adapter import BMPartsAdapter

router = APIRouter(prefix="/bm_parts", tags=["BM Parts"])


class ReservedProductsUUIDRequest(BaseModel):
    reserves_uuid: list[str]


class CartsWarehousesRequest(BaseModel):
    cart_uuid: str
    warehouses: list[str]


@router.get("/profile/me/")
async def get_bm_parts_profile():
    adapter = BMPartsAdapter()
    return await adapter.get_profile()


@router.get("/aggregations/advertisements/")
async def get_aggregations_advertisements():
    adapter = BMPartsAdapter()
    return await adapter.get_aggregations_advertisements()


@router.get("/aggregations/end_nodes/")
async def get_aggregations_end_nodes():
    adapter = BMPartsAdapter()
    return await adapter.get_aggregations_end_nodes()


@router.get("/aggregations/brands/")
async def get_aggregations_brands():
    adapter = BMPartsAdapter()
    return await adapter.get_aggregations_brands()


@router.get("/aggregations/nodes/")
async def get_aggregations_nodes():
    adapter = BMPartsAdapter()
    return await adapter.get_aggregations_nodes()


@router.get("/aggregations/cars/")
async def get_aggregations_cars():
    adapter = BMPartsAdapter()
    return await adapter.get_aggregations_cars()


@router.get("/search/history/")
async def get_search_history():
    adapter = BMPartsAdapter()
    return await adapter.get_search_history()


@router.get("/search/suggest/")
async def get_search_suggestions(q: str, products_as: str = "obj"):
    adapter = BMPartsAdapter()
    return await adapter.get_search_suggestions(q, products_as)


@router.get("/search/groups/")
async def get_product_groups():
    adapter = BMPartsAdapter()
    return await adapter.get_product_groups()


@router.get("/search/products/")
async def search_products(q: str, request: Request):
    adapter = BMPartsAdapter()
    filters = dict(request.query_params)

    filters.pop("q", None)

    return await adapter.search_products(q, **filters)


@router.get("/models_by_brand/{car_name}")
async def get_models_by_brand(car_name: str):
    adapter = BMPartsAdapter()
    return await adapter.get_models_by_brand(car_name)


@router.get("/engines_by_model/{car_name}/{model_name}")
async def get_engines_by_model(car_name: str, model_name: str):
    adapter = BMPartsAdapter()
    return await adapter.get_engines_by_model(car_name, model_name)


@router.get("/group_filters/{group_path}")  # TODO: to test
async def get_group_filters(group_path: str):
    adapter = BMPartsAdapter()
    return await adapter.get_group_filters(group_path)


@router.post("/reserved_products_detailed/")
async def get_reserved_products_detailed(request: ReservedProductsUUIDRequest):
    adapter = BMPartsAdapter()
    return await adapter.get_reserved_products_detailed(request.reserves_uuid)


@router.post("/reserved_products/")
async def get_reserved_products(request: ReservedProductsUUIDRequest):
    adapter = BMPartsAdapter()
    return await adapter.get_reserved_products(request.reserves_uuid)


@router.post("/reserve_order/")
async def reserve_order(order_uuid: str, comment: str, warehouse_uuid: str):
    adapter = BMPartsAdapter()
    return await adapter.reserve_order(order_uuid, comment, warehouse_uuid)


@router.get("/carts/count/")
async def get_bm_parts_carts_count():
    adapter = BMPartsAdapter()
    return await adapter.get_carts_count()


@router.post("/bm_parts/carts/union/")
async def post_bm_parts_union_carts(carts_array: list):
    adapter = BMPartsAdapter()
    return await adapter.union_carts(carts_array)


@router.post("/bm_parts/change_product/")
async def post_bm_parts_change_product_in_cart(
    cart_uuid: str, from_product_uuid: str, to_product_uuid: str
):
    adapter = BMPartsAdapter()
    return await adapter.change_product_in_cart(
        cart_uuid, from_product_uuid, to_product_uuid
    )


@router.post("/cart_products/")
async def get_bm_parts_cart_products(request: CartsWarehousesRequest):
    adapter = BMPartsAdapter()
    return await adapter.get_cart_products(request.cart_uuid, request.warehouses)


@router.post("/bm_parts/change_owner/")
async def post_bm_parts_change_cart_owner(cart_uuid: str, client_uuid: str):
    adapter = BMPartsAdapter()
    return await adapter.change_cart_owner(cart_uuid, client_uuid)


@router.get("/reserves/")
async def get_bm_parts_reserves(response_fields: str = "all"):
    adapter = BMPartsAdapter()
    return await adapter.get_reserves(response_fields)


@router.delete("/bm_parts/reserves/")
async def delete_bm_parts_reserves(orders: list):
    adapter = BMPartsAdapter()
    return await adapter.delete_reserves(orders)


@router.get("/shopping/carts/")
async def get_bm_parts_carts():
    adapter = BMPartsAdapter()
    return await adapter.get_carts()


@router.post("/bm_parts/shopping/carts/")
async def create_bm_parts_cart(name: str, products: list = None):
    adapter = BMPartsAdapter()
    return await adapter.create_cart(name, products)


@router.post("/bm_parts/shopping/cart/{cart_uuid}/product/{product_uuid}/{quantity}")
async def add_product_to_bm_parts_cart(
    cart_uuid: str, product_uuid: str, quantity: int
):
    adapter = BMPartsAdapter()
    return await adapter.add_product_to_cart(cart_uuid, product_uuid, quantity)


@router.put("/bm_parts/shopping/cart/{cart_uuid}/product/{product_uuid}/{quantity}")
async def update_product_in_bm_parts_cart(
    cart_uuid: str, product_uuid: str, quantity: int
):
    adapter = BMPartsAdapter()
    return await adapter.update_product_quantity_in_cart(
        cart_uuid, product_uuid, quantity
    )


@router.delete("/bm_parts/shopping/cart/{cart_uuid}/product/{product_uuid}")
async def delete_product_from_bm_parts_cart(cart_uuid: str, product_uuid: str):
    adapter = BMPartsAdapter()
    return await adapter.delete_product_from_cart(cart_uuid, product_uuid)


@router.delete("/bm_parts/shopping/cart/")
async def delete_bm_parts_cart(cart_uuid: str):
    adapter = BMPartsAdapter()
    return await adapter.delete_cart(cart_uuid)


@router.get("/shopping/cart/{cart_uuid}")
async def get_bm_parts_cart(cart_uuid: str):
    adapter = BMPartsAdapter()
    return await adapter.get_cart(cart_uuid)


@router.post("/bm_parts/shopping/cart/{cart_uuid}")
async def update_bm_parts_cart(
    cart_uuid: str, name: str = None, owner_uuid: str = None
):
    adapter = BMPartsAdapter()
    return await adapter.update_cart(cart_uuid, name, owner_uuid)


@router.get("/product/{product_uuid}/in_waiting/")
async def get_in_waiting(product_uuid: str):
    adapter = BMPartsAdapter()
    return await adapter.get_in_waiting(product_uuid)


@router.get("/product/{product_uuid}/in_stocks/")
async def get_in_stocks(product_uuid: str, id_type: str = None):
    adapter = BMPartsAdapter()
    return await adapter.get_in_stocks(product_uuid, id_type)


@router.get("/product/{product_uuid}/prices/")
async def get_prices(product_uuid: str, id_type: str = None):
    adapter = BMPartsAdapter()
    return await adapter.get_prices(product_uuid, id_type)


@router.get("/product/{product_uuid}/price/")
async def get_price(product_uuid: str, currency: str = "UAH", id_type: str = None):
    adapter = BMPartsAdapter()
    return await adapter.get_price(product_uuid, currency, id_type)


@router.get("/product/{product_uuid}/")
async def get_product_info(
    product_uuid: str,
    warehouses: str = "all",
    currency: str = "UAH",
    id_type: str = None,
    products_as: str = "obj",
):
    adapter = BMPartsAdapter()
    return await adapter.get_product_info(
        product_uuid, warehouses, currency, id_type, products_as
    )


@router.get("/detection_cases/")
async def get_detection_cases():
    adapter = BMPartsAdapter()
    return await adapter.get_detection_cases()


@router.get("/reclamations/")
async def get_reclamations(page: int = 1, per_page: int = 10, direction: str = "desc"):
    adapter = BMPartsAdapter()
    return await adapter.get_reclamations(page, per_page, direction)


@router.post("/bm_parts/reclamation/")
async def create_reclamation(data: dict):
    adapter = BMPartsAdapter()
    return await adapter.create_reclamation(data)


@router.get("/returns/")
async def get_returns(page: int = 1, per_page: int = 10, direction: str = "desc"):
    adapter = BMPartsAdapter()
    return await adapter.get_returns(page, per_page, direction)


@router.get("/sold_products/")
async def get_sold_products(
    page: int = 1,
    per_page: int = 10,
    direction: str = "desc",
    reason: str = "returns",
    q: str = None,
):
    adapter = BMPartsAdapter()
    return await adapter.get_sold_products(page, per_page, direction, reason, q)


@router.delete("/bm_parts/returns/products/{uuid}")
async def delete_product_return(uuid: str):
    adapter = BMPartsAdapter()
    return await adapter.delete_product_return(uuid)


@router.get("/returns/products/")
async def get_return_products():
    adapter = BMPartsAdapter()
    return await adapter.get_return_products()


@router.post("/bm_parts/returns/request/")
async def create_return_request(request_data: dict):
    adapter = BMPartsAdapter()
    return await adapter.create_return_request(request_data)


@router.get("/returns/causes/")
async def get_return_causes():
    adapter = BMPartsAdapter()
    return await adapter.get_return_causes()


@router.post("/bm_parts/returns/notify/")
async def notify_return(text: str):
    adapter = BMPartsAdapter()
    return await adapter.notify_return(text)

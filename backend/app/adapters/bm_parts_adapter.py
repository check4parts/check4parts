import asyncio
from typing import Any, Optional

import httpx
from fastapi import HTTPException

from app.config import BM_PARTS_TOKEN


class BMPartsAdapterError(HTTPException):
    """HTTP error raised when the BM Parts upstream returns an error."""

    def __init__(
        self,
        status_code: int,
        detail: Any | None = None,
        message: str | None = None,
        headers: Optional[dict[str, str]] = None,
    ) -> None:
        fallback_message = message or "BM Parts API request failed"
        detail_payload = detail if detail is not None else {"message": fallback_message}
        super().__init__(status_code=status_code, detail=detail_payload, headers=headers)
        self.message = fallback_message


class BMPartsAdapter:
    BASE_URL = "https://api.bm.parts"
    REQUEST_TIMEOUT = 30.0
    MAX_RETRIES = 3
    RETRY_BACKOFF = 1.0

    def __init__(self, client: httpx.AsyncClient | None = None) -> None:
        self.token = BM_PARTS_TOKEN
        self.headers: dict[str, str] = {}
        if BM_PARTS_TOKEN:
            self.headers["Authorization"] = BM_PARTS_TOKEN
        self._client: httpx.AsyncClient | None = client
        self._owns_client = client is None

    async def __aenter__(self) -> "BMPartsAdapter":
        if not self._client:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(self.REQUEST_TIMEOUT),
                limits=httpx.Limits(max_connections=10, max_keepalive_connections=5),
            )
            self._owns_client = True
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        if self._client and self._owns_client:
            await self._client.aclose()
        self._client = None

    async def _get_client(self) -> httpx.AsyncClient:
        if not self._client:
            await self.__aenter__()
        assert self._client is not None
        return self._client

    async def fetch(
        self, endpoint: str, params: dict | None = None, method: str = "GET", data: dict | None = None
    ) -> Any:
        client = await self._get_client()
        url = f"{self.BASE_URL}{endpoint}"

        for attempt in range(self.MAX_RETRIES):
            try:
                response = await client.request(
                    method,
                    url,
                    params=params,
                    json=data,
                    headers=self.headers,
                )
                response.raise_for_status()
                try:
                    return response.json()
                except ValueError as exc:
                    raise BMPartsAdapterError(
                        status_code=502,
                        detail={
                            "message": "Invalid response payload from BM Parts API",
                            "response_text": response.text,
                        },
                    ) from exc
            except httpx.HTTPStatusError as exc:
                raise BMPartsAdapterError(
                    status_code=exc.response.status_code,
                    detail=self._extract_error_detail(exc.response),
                    message="BM Parts API responded with an error",
                ) from exc
            except httpx.RequestError as exc:
                if attempt < self.MAX_RETRIES - 1:
                    await asyncio.sleep(self.RETRY_BACKOFF * (2**attempt))
                    continue
                raise BMPartsAdapterError(
                    status_code=502,
                    detail={
                        "message": "Failed to communicate with BM Parts API",
                        "error": str(exc),
                    },
                ) from exc

    def _extract_error_detail(self, response: httpx.Response) -> Any:
        try:
            return response.json()
        except ValueError:
            return {"message": response.text or "Unknown error"}

    async def get_profile(self):
        endpoint = "/profile/me"
        return await self.fetch(endpoint)

    async def get_aggregations_advertisements(self):
        endpoint = "/search/products/aggregations/advertisements"
        return await self.fetch(endpoint)

    async def get_aggregations_end_nodes(self):
        endpoint = "/search/products/aggregations/end_nodes"
        return await self.fetch(endpoint)

    async def get_aggregations_brands(self):
        endpoint = "/search/products/aggregations/brands"
        return await self.fetch(endpoint)

    async def get_aggregations_nodes(self):
        endpoint = "/search/products/aggregations/nodes"
        return await self.fetch(endpoint)

    async def get_aggregations_cars(self):
        endpoint = "/search/products/aggregations/cars"
        return await self.fetch(endpoint)

    async def get_search_history(self):
        endpoint = "/search/products/history"
        return await self.fetch(endpoint)

    async def get_search_suggestions(self, query: str, products_as: str = "obj"):
        endpoint = "/search/products/suggest"
        return await self.fetch(endpoint, {"q": query, "products_as": products_as})

    async def get_product_groups(self):
        endpoint = "/search/products/groups"
        return await self.fetch(endpoint)

    async def search_products(self, query: str, **filters):
        endpoint = "/search/products"
        params = {"q": query, **filters}
        return await self.fetch(endpoint, params)

    async def get_product_details(self, product_uuid: str):
        endpoint = f"/products/{product_uuid}"
        return await self.fetch(endpoint)

    async def get_product_crosses(self, product_uuid: str):
        endpoint = f"/products/{product_uuid}/crosses"
        return await self.fetch(endpoint)

    async def get_product_additional(self, product_uuid: str):
        endpoint = f"/products/{product_uuid}/additional"
        return await self.fetch(endpoint)

    async def get_car_models(self, car_name: str):
        endpoint = f"/search/products/aggregations/car/{car_name}/models"
        return await self.fetch(endpoint)

    async def get_car_engines(self, car_name: str, model_name: str):
        endpoint = f"/search/products/aggregations/car/{car_name}/model/{model_name}"
        return await self.fetch(endpoint)

    async def get_group_filters(self, group_path: str):
        endpoint = f"/search/products/groups/{group_path}/filters"
        return await self.fetch(endpoint)

    async def get_search_suggests(self, query: str, products_as: str = "obj"):
        endpoint = "/search/suggests"
        return await self.fetch(endpoint, {"q": query, "products_as": products_as})

    async def search_products_enhanced(
        self,
        query: str,
        include_crosses: bool = False,
        include_additional: bool = False,
        **filters,
    ):
        basic_results = await self.search_products(query, **filters)

        if not (include_crosses or include_additional):
            return basic_results

        if "products" in basic_results:
            products_data = basic_results["products"]

            if isinstance(products_data, dict):
                products_list = list(products_data.items())
            else:
                products_list = [
                    (str(i), product) for i, product in enumerate(products_data)
                ]

            for product_id, product_data in products_list:
                product_uuid = product_data.get("uuid")

                if product_uuid:
                    try:
                        if include_crosses:
                            crosses_data = await self.get_product_crosses(product_uuid)
                            if crosses_data:
                                product_data["crosses"] = crosses_data

                        if include_additional:
                            additional_data = await self.get_product_additional(
                                product_uuid
                            )
                            if additional_data:
                                product_data["additional"] = additional_data

                    except BMPartsAdapterError:
                        continue

        return basic_results

    async def get_warehouse_stocks(
        self, product_uuid: str, warehouse_ids: list[str] = None
    ):
        params = {"uuid": product_uuid}
        if warehouse_ids:
            params["warehouses"] = warehouse_ids

        endpoint = "/products/stocks"
        return await self.fetch(endpoint, params)

    async def get_product_prices(self, product_uuid: str, currency: str = None):
        params = {"uuid": product_uuid}
        if currency:
            params["currency"] = currency

        endpoint = "/products/prices"
        return await self.fetch(endpoint, params)

    async def search_by_vin(self, vin: str):
        endpoint = "/search/suggests"
        return await self.fetch(endpoint, {"q": vin})

    async def get_delivery_options(self, product_uuid: str, warehouse_id: str = None):
        params = {"uuid": product_uuid}
        if warehouse_id:
            params["warehouse"] = warehouse_id

        endpoint = "/products/delivery"
        return await self.fetch(endpoint, params)

    async def search_suggestions(self, query: str, products_as: str = "obj"):
        endpoint = "/search/suggests"
        params = {"q": query, "products_as": products_as}
        return await self.fetch(endpoint, params)

    async def get_models_by_brand(self, car_name: str):
        endpoint = f"/search/products/aggregations/car/{car_name}/models"
        return await self.fetch(endpoint)

    async def get_engines_by_model(self, car_name: str, model_name: str):
        endpoint = f"/search/products/aggregations/car/{car_name}/model/{model_name}"
        return await self.fetch(endpoint)

    async def get_group_filters(self, group_path: str):
        endpoint = f"/search/products/groups/{group_path}/filters"
        return await self.fetch(endpoint)

    async def get_reserved_products_detailed(self, reserves_uuid: list[str]):
        endpoint = "/shopping/reserve/products/detailed"
        json_data = {"reserves_uuid": reserves_uuid}
        return await self.fetch(endpoint, method="POST", data=json_data)

    async def get_reserved_products(self, reserves_uuid: list[str]):
        endpoint = "/shopping/reserve/products"
        json_data = {"reserves_uuid": reserves_uuid}
        return await self.fetch(endpoint, method="POST", data=json_data)

    async def reserve_order(self, order_uuid: str, comment: str, warehouse_uuid: str):
        endpoint = "/shopping/reserve/process"
        json_data = {
            "order_uuid": order_uuid,
            "comment": comment,
            "warehouse_uuid": warehouse_uuid,
        }
        return await self.fetch(endpoint, method="POST", data=json_data)

    async def get_carts_count(self):
        endpoint = "/shopping/carts/count"
        return await self.fetch(endpoint)

    async def union_carts(self, carts_array: list):
        endpoint = "/shopping/carts/union"
        data = {"carts_array": carts_array}
        return await self.fetch(endpoint, method="POST", data=data)

    async def change_product_in_cart(
        self, cart_uuid: str, from_product_uuid: str, to_product_uuid: str
    ):
        endpoint = "/shopping/change_product"
        data = {
            "cart_uuid": cart_uuid,
            "from": from_product_uuid,
            "to": to_product_uuid,
        }
        return await self.fetch(endpoint, method="POST", data=data)

    async def get_cart_products(self, cart_uuid: str, warehouses: list[str] = None):
        endpoint = "/shopping/cart_products"
        json_data = {"cart_uuid": cart_uuid, "warehouses": warehouses}
        return await self.fetch(endpoint, method="POST", data=json_data)

    async def change_cart_owner(self, cart_uuid: str, client_uuid: str):
        endpoint = "/shopping/change_owner"
        data = {"cart_uuid": cart_uuid, "client_uuid": client_uuid}
        return await self.fetch(endpoint, method="POST", data=data)

    async def get_reserves(self, response_fields: str = "all"):
        endpoint = "/shopping/reserves"
        params = {"response_fields": response_fields}
        return await self.fetch(endpoint, params=params)

    async def delete_reserves(self, orders: list[str]):
        endpoint = "/shopping/reserves"
        data = {"orders": orders}
        return await self.fetch(endpoint, method="DELETE", data=data)

    async def get_carts(self):
        endpoint = "/shopping/carts"
        return await self.fetch(endpoint)

    async def create_cart(self, name: str, products: list = None):
        endpoint = "/shopping/carts"
        data = {"name": name, "products": products or []}
        return await self.fetch(endpoint, method="POST", data=data)

    async def add_product_to_cart(
        self, cart_uuid: str, product_uuid: str, quantity: int
    ):
        endpoint = f"/shopping/cart/{cart_uuid}/product"
        data = {"product_uuid": product_uuid, "quantity": quantity}
        return await self.fetch(endpoint, method="POST", data=data)

    async def update_product_quantity_in_cart(
        self, cart_uuid: str, product_uuid: str, quantity: int
    ):
        endpoint = f"/shopping/cart/{cart_uuid}/product"
        data = {"product_uuid": product_uuid, "quantity": quantity}
        return await self.fetch(endpoint, method="PUT", data=data)

    async def delete_product_from_cart(self, cart_uuid: str, product_uuid: str):
        endpoint = f"/shopping/cart/{cart_uuid}/product"
        data = {"product_uuid": product_uuid}
        return await self.fetch(endpoint, method="DELETE", data=data)

    async def delete_cart(self, cart_uuid: str):
        endpoint = f"/shopping/cart/{cart_uuid}"
        return await self.fetch(endpoint, method="DELETE")

    async def get_cart(self, cart_uuid: str):
        endpoint = f"/shopping/cart/{cart_uuid}"
        return await self.fetch(endpoint)

    async def update_cart(
        self, cart_uuid: str, name: str = None, owner_uuid: str = None
    ):
        endpoint = f"/shopping/cart/{cart_uuid}"
        data = {"name": name, "owner_uuid": owner_uuid}
        return await self.fetch(endpoint, method="POST", data=data)

    async def get_in_waiting(self, product_uuid: str):
        endpoint = f"/product/{product_uuid}/in_waiting"
        return await self.fetch(endpoint)

    async def get_in_stocks(self, product_uuid: str, id_type: str = "id"):
        endpoint = f"/product/{product_uuid}/in_stocks"
        params = {"id_type": id_type} if id_type is not None else None
        return await self.fetch(endpoint, params=params)

    async def get_prices(self, product_uuid: str, id_type: str = "id"):
        endpoint = f"/product/{product_uuid}/prices"
        params = {"id_type": id_type} if id_type is not None else None
        return await self.fetch(endpoint, params=params)

    async def get_price(
        self, product_uuid: str, currency: str = "UAH", id_type: str = "id"
    ):
        endpoint = f"/product/{product_uuid}/price"
        params = {"currency": currency}
        if id_type is not None:
            params["id_type"] = id_type
        return await self.fetch(endpoint, params=params)

    async def get_product_info(
        self,
        product_uuid: str,
        warehouses: str = "all",
        currency: str = "UAH",
        id_type: str = None,
        products_as: str = "obj",
    ):
        endpoint = f"/product/{product_uuid}"
        params = {
            "warehouses": warehouses,
            "currency": currency,
            "id_type": id_type if id_type is not None else None,
            "products_as": products_as,
        }
        return await self.fetch(endpoint, params=params)

    async def get_detection_cases(self):
        endpoint = "/return_products/detection_cases"
        return await self.fetch(endpoint)

    async def get_reclamations(
        self, page: int = 1, per_page: int = 10, direction: str = "desc"
    ):
        endpoint = "/return_products/reclamations"
        params = {"page": page, "per_page": per_page, "direction": direction}
        return await self.fetch(endpoint, params)

    async def create_reclamation(self, data: dict):
        endpoint = "/return_products/reclamation"
        return await self.fetch(endpoint, method="POST", data=data)

    async def get_returns(
        self, page: int = 1, per_page: int = 10, direction: str = "desc"
    ):
        endpoint = "/return_products/returns"
        params = {"page": page, "per_page": per_page, "direction": direction}
        return await self.fetch(endpoint, params)

    async def get_sold_products(
        self,
        page: int = 1,
        per_page: int = 10,
        direction: str = "desc",
        reason: str = "returns",
        q: str = None,
    ):
        endpoint = "/return_products/sold"
        params = {
            "page": page,
            "per_page": per_page,
            "direction": direction,
            "reason": reason,
            "q": q,
        }
        return await self.fetch(endpoint, params)

    async def delete_product_return(self, uuid: str):
        endpoint = f"/return_products/returns/{uuid}"
        return await self.fetch(endpoint, method="DELETE")

    async def get_return_products(self):
        endpoint = "/returns/products"
        return await self.fetch(endpoint)

    async def create_return_request(self, data: dict):
        endpoint = "/returns/request"
        return await self.fetch(endpoint, data=data, method="POST")

    async def get_return_causes(self):
        endpoint = "/returns/causes"
        return await self.fetch(endpoint)

    async def notify_return(self, text: str):
        endpoint = "/returns/notify"
        payload = {"text": text}
        return await self.fetch(endpoint, data=payload, method="POST")

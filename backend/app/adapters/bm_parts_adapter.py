import httpx
from fastapi import HTTPException

from app.config import BM_PARTS_TOKEN


class BMPartsAdapter:
    BASE_URL = "https://api.bm.parts"

    def __init__(self):
        self.token = BM_PARTS_TOKEN
        self.headers = {
            "Authorization": BM_PARTS_TOKEN,
        }

    async def fetch(
        self, endpoint: str, params: dict = None, method: str = "GET", data: dict = None
    ):
        async with httpx.AsyncClient() as client:
            if method == "GET":
                response = await client.get(
                    f"{self.BASE_URL}{endpoint}", params=params, headers=self.headers
                )
            elif method == "POST":
                response = await client.post(
                    f"{self.BASE_URL}{endpoint}",
                    json=data,
                    params=params,
                    headers=self.headers,
                )
            elif method == "PUT":
                response = await client.put(
                    f"{self.BASE_URL}{endpoint}",
                    json=data,
                    params=params,
                    headers=self.headers,
                )
            elif method == "DELETE":
                response = await client.delete(
                    f"{self.BASE_URL}{endpoint}", params=params, headers=self.headers
                )

            response.raise_for_status()
            return response.json()

    async def get_profile(self):
        url = f"{self.BASE_URL}/profile/me"
        headers = {"Authorization": self.token}
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code, detail=response.json()
                )
            return response.json()

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

    async def delete_reserves(self, orders: list):
        endpoint = "/shopping/reserves"
        params = {"orders": ",".join(orders)}
        return await self.fetch(endpoint, method="DELETE", params=params)

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
        endpoint = f"/shopping/cart/{cart_uuid}/product/{product_uuid}/{quantity}"
        return await self.fetch(endpoint, method="POST")

    async def update_product_quantity_in_cart(
        self, cart_uuid: str, product_uuid: str, quantity: int
    ):
        endpoint = f"/shopping/cart/{cart_uuid}/product/{product_uuid}/{quantity}"
        return await self.fetch(endpoint, method="PUT")

    async def delete_product_from_cart(self, cart_uuid: str, product_uuid: str):
        endpoint = f"/shopping/cart/{cart_uuid}/product/{product_uuid}"
        return await self.fetch(endpoint, method="DELETE")

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

    async def create_return_request(self, params: dict):
        endpoint = "/returns/request"
        return await self.fetch(endpoint, params=params, method="POST")

    async def get_return_causes(self):
        endpoint = "/returns/causes"
        return await self.fetch(endpoint)

    async def notify_return(self, text: str):
        endpoint = "/returns/notify"
        return await self.fetch(endpoint, params={"text": text}, method="POST")

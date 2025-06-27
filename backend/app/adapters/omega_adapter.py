import httpx
from fastapi import HTTPException
# from app.config import OMEGA_TOKEN


class OmegaAdapter:
    BASE_URL = "https://api.omega.com"

    def __init__(self):
        # self.token = OMEGA_TOKEN
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

    async def fetch(
            self,
            endpoint: str,
            params: dict = None,
            method: str = "GET",
            data: dict = None
    ):
        url = f"{self.BASE_URL}{endpoint}"

        async with httpx.AsyncClient() as client:
            if method == "GET":
                response = await client.get(url, params=params, headers=self.headers)
            elif method == "POST":
                response = await client.post(
                    url, json=data, params=params, headers=self.headers
                )
            elif method == "PUT":
                response = await client.put(
                    url, json=data, params=params, headers=self.headers
                )
            elif method == "DELETE":
                response = await client.delete(url, params=params, headers=self.headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

        if response.status_code >= 400:
            raise HTTPException(
                status_code=response.status_code,
                detail=response.json()
            )

        return response.json()

    async def login(self, username: str, password: str):
        url = f"{self.BASE_URL}/auth/login"
        headers = {
            "Content-Type": "application/json",
        }
        data = {
            "username": username,
            "password": password
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=data, headers=headers)

            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=response.json()
                )

        result = response.json()
        self.token = result.get("access_token") or result.get("token")
        self.headers["Authorization"] = f"Bearer {self.token}"

        return result

    async def logout(self):
        return await self.fetch("/auth/logout", method="POST")

    async def me(self):
        return await self.fetch("/auth/me", method="GET")

    async def refresh_token(self):
        return await self.fetch("/auth/refresh", method="POST")

    async def get_orders(self, page: int = 1, limit: int = 50):
        params = {"page": page, "limit": limit}
        return await self.fetch("/orders", method="GET", params=params)

    async def create_order(self, products: list[dict], **kwargs):
        payload = {
            "products": products,
            **kwargs
        }
        return await self.fetch("/orders", method="POST", data=payload)

    async def get_order(self, order_id: str):
        return await self.fetch(f"/orders/{order_id}", method="GET")

    async def update_order(self, order_id: str, data: dict):
        return await self.fetch(f"/orders/{order_id}", method="PUT", data=data)

    async def cancel_order(self, order_id: str):
        return await self.fetch(f"/orders/{order_id}/cancel", method="POST")

    async def get_products(self, category: str = None, page: int = 1, limit: int = 50):
        params = {"page": page, "limit": limit}
        if category:
            params["category"] = category
        return await self.fetch("/products", method="GET", params=params)

    async def get_product(self, product_id: str):
        return await self.fetch(f"/products/{product_id}", method="GET")

    async def get_prices(self, filter_props: dict = None, page: int = 1, limit: int = 50):
        params = {"page": page, "limit": limit}
        data = {"filter": filter_props or {}}
        return await self.fetch("/prices", method="POST", data=data, params=params)

    async def get_categories(self):
        return await self.fetch("/categories", method="GET")

    async def get_inventory(self, product_ids: list[str] = None):
        data = {"product_ids": product_ids} if product_ids else {}
        return await self.fetch("/inventory", method="POST", data=data)

    async def create_basket(self, products: list[dict]):
        payload = {"products": products}
        return await self.fetch("/basket", method="POST", data=payload)

    async def get_basket(self, basket_id: str):
        return await self.fetch(f"/basket/{basket_id}", method="GET")

    async def update_basket(self, basket_id: str, products: list[dict]):
        payload = {"products": products}
        return await self.fetch(f"/basket/{basket_id}", method="PUT", data=payload)
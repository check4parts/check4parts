import httpx
from fastapi import HTTPException

from app.config import ASG_TOKEN


class ASGAdapter:
    BASE_URL = "https://online.asg.ua/api"

    def __init__(self):
        self.token = ASG_TOKEN
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

    async def fetch(
        self, endpoint: str, params: dict = None, method: str = "GET", data: dict = None
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
                    status_code=response.status_code, detail=response.json()
                )
            return response.json()

    async def login(self, login: str, password: str):
        url = f"{self.BASE_URL}/auth/login"
        headers = {
            "Content-Type": "application/json",
            # "X-Asg-Header": x_asg_header,
        }
        data = {"login": login, "password": password}
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=data, headers=headers)
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code, detail=response.json()
                )
            result = response.json()
            self.token = result.get("access_token")
            self.headers["Authorization"] = f"Bearer {self.token}"
            return result

    async def logout(self):
        return await self.fetch("/auth/logout", method="POST")

    async def me(self):
        return await self.fetch("/auth/me", method="POST")

    async def refresh_token(self):
        return await self.fetch("/auth/refresh", method="POST")

    async def get_orders(self):
        return await self.fetch("/orders/all", method="POST")

    async def create_order(self, products: list[dict], test: str = "0"):
        payload = {"test": test, "products": products}
        return await self.fetch("/orders/store", method="POST", data=payload)

    async def cancel_order(self, order_id: int):
        return await self.fetch(f"/orders/cancel/{order_id}", method="POST")

    async def get_prices(self, filter_props: dict = None, page: int = 1):
        params = {"page": page}
        data = {"filter": filter_props or {}}
        return await self.fetch("/prices", method="POST", data=data, params=params)

    async def get_categories(self):
        return await self.fetch("/categories", method="POST")

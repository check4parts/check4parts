import httpx
from fastapi import HTTPException


class IntercarsAdapter:
    BASE_URL = "https://api.intercars.com"

    def __init__(self):
        self.token = None
        self.headers = {}

    async def fetch(
        self, endpoint: str, method: str = "GET", params: dict = None, data: dict = None
    ):
        async with httpx.AsyncClient() as client:
            url = f"{self.BASE_URL}{endpoint}"

            if method == "GET":
                response = await client.get(url, headers=self.headers, params=params)
            elif method == "POST":
                response = await client.post(url, headers=self.headers, json=data)
            elif method == "PUT":
                response = await client.put(url, headers=self.headers, json=data)
            elif method == "DELETE":
                response = await client.delete(url, headers=self.headers, params=params)

            response.raise_for_status()
            return response.json()

    async def authorize(self, client_id: str, client_secret: str):
        endpoint = "/api/token"
        data = {
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{self.BASE_URL}{endpoint}", data=data)
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code, detail=response.json()
                )

            result = response.json()
            self.token = result["access_token"]
            self.headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
            }
            return result

    async def inventory_quote(self, lines: list[dict]):
        endpoint = "/inventory/1.0.0/inventory/quote"
        return await self.fetch(endpoint, method="POST", data={"lines": lines})

    async def get_stock_balance(
        self, skus: list[str], locations: list[str] = None, ship_to: str = None
    ):
        endpoint = "/inventory/1.0.0/inventory/stock"
        params = {"sku": ",".join(skus)}

        if locations:
            params["location"] = ",".join(locations)
        if ship_to:
            params["shipTo"] = ship_to

        return await self.fetch(endpoint, method="GET", params=params)

    async def inventory_stock(self, skus: list[str], location: str):
        endpoint = "/inventory/1.0.0/inventory/stock"
        params = {"location": location}
        data = {"sku": ",".join(skus)}
        return await self.fetch(endpoint, method="POST", params=params, data=data)

    async def search_deliveries(
        self,
        creation_date_from: str,
        creation_date_to: str,
        offset: int = 1,
        limit: int = 20,
    ):
        endpoint = "/delivery"
        params = {
            "creationDateFrom": creation_date_from,
            "creationDateTo": creation_date_to,
            "offset": offset,
            "limit": limit,
        }
        return await self.fetch(endpoint, method="GET", params=params)

    async def get_delivery(self, delivery_id: str):
        endpoint = f"/delivery/{delivery_id}"
        return await self.fetch(endpoint, method="GET")

    async def search_invoice(
        self,
        creation_date_from: str,
        creation_date_to: str,
        offset: int = 1,
        limit: int = 20,
    ):
        endpoint = "/invoice"
        params = {
            "issueDateFrom": creation_date_from,
            "issueDateTo": creation_date_to,
            "offset": offset,
            "limit": limit,
        }
        return await self.fetch(endpoint, method="GET", params=params)

    async def get_invoice(self, invoice_id: str):
        endpoint = f"/invoice/{invoice_id}"
        return await self.fetch(endpoint, method="GET")

    async def get_requisition(self, requisition_id: str):
        endpoint = f"/sales/requisition/{requisition_id}"
        return await self.fetch(endpoint, method="GET")

    async def submit_requisition(self, requisition_data: dict):
        endpoint = "/sales/requisition"
        return await self.fetch(endpoint, method="POST", data=requisition_data)

    async def cancel_requisition(self, requisition_id: str, ship_to: str = None):
        endpoint = f"/sales/requisition/{requisition_id}/cancel"
        params = {"shipTo": ship_to} if ship_to else None
        return await self.fetch(endpoint, method="POST", params=params)

    async def search_order(
        self,
        creation_date_from: str,
        creation_date_to: str,
        offset: int = 1,
        limit: int = 20,
    ):
        endpoint = "/sales/requisition"
        params = {
            "creationDateFrom": creation_date_from,
            "creationDateTo": creation_date_to,
            "offset": offset,
            "limit": limit,
        }
        return await self.fetch(endpoint, method="GET", params=params)

    async def get_order(self, order_id: str):
        endpoint = f"/sales/order/{order_id}"
        return await self.fetch(endpoint, method="GET")

    async def customer(self):
        endpoint = "/customer"
        return await self.fetch(endpoint, method="GET")

    async def customer_finances(self):
        endpoint = "/customer/finances"
        return await self.fetch(endpoint, method="GET")

    async def calculate_item_price(self, lines: list[dict]):
        endpoint = "/pricing/quote"
        return await self.fetch(endpoint, method="POST", data={"lines": lines})

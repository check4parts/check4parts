import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin
import httpx

logger = logging.getLogger(__name__)


class IntercarsAPIError(Exception):
    def __init__(
        self, status_code: int, message: str, details: Optional[Dict[str, Any]] = None
    ):
        self.status_code = status_code
        self.message = message
        self.details = details or {}
        super().__init__(f"InterCars API Error {status_code}: {message}")


class IntercarsAdapter:
    BASE_URL = "https://webapi.intercars.eu"
    TOKEN_ENDPOINT = "/v1/oauth2/token"
    API_VERSION = "v1"

    REQUEST_TIMEOUT = 30.0
    MAX_RETRIES = 3
    RETRY_BACKOFF = 1.0
    TOKEN_BUFFER_SECONDS = 300

    def __init__(self, client_id: str = None, client_secret: str = None):
        self._client_id = client_id
        self._client_secret = client_secret
        self._access_token: Optional[str] = None
        self._token_expires_at: Optional[datetime] = None
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self):
        self._client = httpx.AsyncClient(
            timeout=httpx.Timeout(self.REQUEST_TIMEOUT),
            limits=httpx.Limits(max_connections=10, max_keepalive_connections=5),
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._client:
            await self._client.aclose()

    @property
    def _is_token_valid(self) -> bool:
        if not self._access_token or not self._token_expires_at:
            return False
        return (
            datetime.utcnow() + timedelta(seconds=self.TOKEN_BUFFER_SECONDS)
            < self._token_expires_at
        )

    async def _get_client(self) -> httpx.AsyncClient:
        if not self._client:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(self.REQUEST_TIMEOUT),
                limits=httpx.Limits(max_connections=10, max_keepalive_connections=5),
            )
        return self._client

    async def _ensure_authenticated(self) -> None:
        if not self._is_token_valid:
            if not self._client_id or not self._client_secret:
                raise IntercarsAPIError(401, "Authentication credentials not provided")
            await self._authenticate()

    async def _authenticate(self) -> Dict[str, Any]:
        if not self._client_id or not self._client_secret:
            raise IntercarsAPIError(
                401, "Client ID and secret are required for authentication"
            )

        client = await self._get_client()
        url = urljoin(self.BASE_URL, self.TOKEN_ENDPOINT)

        data = {
            "grant_type": "client_credentials",
            "client_id": self._client_id,
            "client_secret": self._client_secret,
        }

        try:
            response = await client.post(url, data=data)
            await self._handle_response_errors(response)

            result = response.json()
            self._access_token = result.get("access_token")

            if not self._access_token:
                raise IntercarsAPIError(
                    401, "No access token received from authentication"
                )

            expires_in = result.get("expires_in", 3600)
            self._token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in)

            logger.info("Successfully authenticated with InterCars API")
            return result

        except httpx.RequestError as e:
            logger.error(f"Network error during authentication: {e}")
            raise IntercarsAPIError(
                500, f"Network error during authentication: {str(e)}"
            )

    async def _handle_response_errors(self, response: httpx.Response) -> None:
        if response.is_success:
            return

        try:
            error_data = response.json()
        except (ValueError, TypeError):
            error_data = {"error": response.text}

        error_message = (
            error_data.get("error_description")
            or error_data.get("message")
            or "Unknown error"
        )

        if response.status_code == 401:
            self._access_token = None
            self._token_expires_at = None

        raise IntercarsAPIError(response.status_code, error_message, error_data)

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        require_auth: bool = True,
    ) -> Dict[str, Any]:

        if require_auth:
            await self._ensure_authenticated()

        client = await self._get_client()
        url = urljoin(self.BASE_URL, f"/{self.API_VERSION}/{endpoint.lstrip('/')}")

        headers = {"Content-Type": "application/json"}
        if require_auth and self._access_token:
            headers["Authorization"] = f"Bearer {self._access_token}"

        for attempt in range(self.MAX_RETRIES):
            try:
                if method.upper() == "GET":
                    response = await client.get(url, params=params, headers=headers)
                elif method.upper() == "POST":
                    response = await client.post(
                        url, params=params, json=json_data, headers=headers
                    )
                elif method.upper() == "PUT":
                    response = await client.put(
                        url, params=params, json=json_data, headers=headers
                    )
                elif method.upper() == "DELETE":
                    response = await client.delete(url, params=params, headers=headers)
                else:
                    raise IntercarsAPIError(400, f"Unsupported HTTP method: {method}")

                await self._handle_response_errors(response)
                return response.json()

            except IntercarsAPIError as e:
                if e.status_code == 401 and attempt < self.MAX_RETRIES - 1:
                    logger.warning("Token expired, re-authenticating...")
                    await self._authenticate()
                    continue
                raise
            except httpx.RequestError as e:
                if attempt < self.MAX_RETRIES - 1:
                    wait_time = self.RETRY_BACKOFF * (2**attempt)
                    logger.warning(
                        f"Request failed (attempt {attempt + 1}), retrying in {wait_time}s: {e}"
                    )
                    await asyncio.sleep(wait_time)
                    continue
                raise IntercarsAPIError(
                    500, f"Network error after {self.MAX_RETRIES} attempts: {str(e)}"
                )

    async def authenticate(self, client_id: str, client_secret: str) -> Dict[str, Any]:
        self._client_id = client_id
        self._client_secret = client_secret
        return await self._authenticate()

    async def inventory_quote(self, lines: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not lines:
            raise IntercarsAPIError(400, "Lines cannot be empty")

        return await self._make_request(
            "POST", "inventory/quote", json_data={"lines": lines}
        )

    async def get_stock_balance(
        self,
        skus: List[str],
        locations: Optional[List[str]] = None,
        ship_to: Optional[str] = None,
    ) -> Dict[str, Any]:
        if not skus:
            raise IntercarsAPIError(400, "SKUs cannot be empty")

        params = {"sku": ",".join(skus)}
        if locations:
            params["location"] = ",".join(locations)
        if ship_to:
            params["shipTo"] = ship_to

        return await self._make_request("GET", "inventory/stock", params=params)

    async def inventory_stock(self, skus: List[str], location: str) -> Dict[str, Any]:
        if not skus:
            raise IntercarsAPIError(400, "SKUs cannot be empty")
        if not location:
            raise IntercarsAPIError(400, "Location cannot be empty")

        return await self._make_request(
            "POST",
            "inventory/stock",
            params={"location": location},
            json_data={"sku": ",".join(skus)},
        )

    async def search_deliveries(
        self,
        creation_date_from: str,
        creation_date_to: str,
        offset: int = 1,
        limit: int = 20,
    ) -> Dict[str, Any]:
        self._validate_date_range(creation_date_from, creation_date_to)
        self._validate_pagination(offset, limit)

        params = {
            "creationDateFrom": creation_date_from,
            "creationDateTo": creation_date_to,
            "offset": offset,
            "limit": limit,
        }
        return await self._make_request("GET", "delivery/metadata", params=params)

    async def get_delivery(self, delivery_id: str) -> Dict[str, Any]:
        if not delivery_id or not delivery_id.strip():
            raise IntercarsAPIError(400, "Delivery ID cannot be empty")

        return await self._make_request("GET", f"delivery/{delivery_id.strip()}")

    async def search_invoices(
        self, issue_date_from: str, issue_date_to: str, offset: int = 1, limit: int = 20
    ) -> Dict[str, Any]:
        self._validate_date_range(issue_date_from, issue_date_to)
        self._validate_pagination(offset, limit)

        params = {
            "issueDateFrom": issue_date_from,
            "issueDateTo": issue_date_to,
            "offset": offset,
            "limit": limit,
        }
        return await self._make_request("GET", "invoice/metadata", params=params)

    async def get_invoice(self, invoice_id: str) -> Dict[str, Any]:
        if not invoice_id or not invoice_id.strip():
            raise IntercarsAPIError(400, "Invoice ID cannot be empty")

        return await self._make_request("GET", f"invoice/{invoice_id.strip()}")

    async def get_requisition(self, requisition_id: str) -> Dict[str, Any]:
        if not requisition_id or not requisition_id.strip():
            raise IntercarsAPIError(400, "Requisition ID cannot be empty")

        return await self._make_request(
            "GET", f"sales/requisition/{requisition_id.strip()}"
        )

    async def submit_requisition(
        self, requisition_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        if not requisition_data:
            raise IntercarsAPIError(400, "Requisition data cannot be empty")

        if "lines" not in requisition_data or not requisition_data["lines"]:
            raise IntercarsAPIError(400, "Requisition must contain at least one line")

        return await self._make_request(
            "POST", "sales/requisition", json_data=requisition_data
        )

    async def cancel_requisition(
        self, requisition_id: str, ship_to: Optional[str] = None
    ) -> Dict[str, Any]:
        if not requisition_id or not requisition_id.strip():
            raise IntercarsAPIError(400, "Requisition ID cannot be empty")

        params = {"shipTo": ship_to} if ship_to else None
        return await self._make_request(
            "POST", f"sales/requisition/{requisition_id.strip()}/cancel", params=params
        )

    async def search_orders(
        self,
        creation_date_from: str,
        creation_date_to: str,
        offset: int = 1,
        limit: int = 20,
    ) -> Dict[str, Any]:
        self._validate_date_range(creation_date_from, creation_date_to)
        self._validate_pagination(offset, limit)

        params = {
            "creationDateFrom": creation_date_from,
            "creationDateTo": creation_date_to,
            "offset": offset,
            "limit": limit,
        }
        return await self._make_request(
            "GET", "sales/requisition/metadata", params=params
        )

    async def get_order(self, order_id: str) -> Dict[str, Any]:
        if not order_id or not order_id.strip():
            raise IntercarsAPIError(400, "Order ID cannot be empty")

        return await self._make_request("GET", f"sales/order/{order_id.strip()}")

    async def get_customer(self) -> Dict[str, Any]:
        return await self._make_request("GET", "customer")

    async def get_customer_finances(self) -> Dict[str, Any]:
        return await self._make_request("GET", "customer/finances")

    async def calculate_item_price(self, lines: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not lines:
            raise IntercarsAPIError(400, "Lines cannot be empty")

        return await self._make_request(
            "POST", "pricing/quote", json_data={"lines": lines}
        )

    def _validate_date_range(self, date_from: str, date_to: str) -> None:
        if not date_from or not date_to:
            raise IntercarsAPIError(400, "Both date_from and date_to are required")

        try:
            from_date = datetime.fromisoformat(date_from.replace("Z", "+00:00"))
            to_date = datetime.fromisoformat(date_to.replace("Z", "+00:00"))

            if from_date > to_date:
                raise IntercarsAPIError(400, "date_from cannot be later than date_to")

        except (ValueError, TypeError) as e:
            raise IntercarsAPIError(400, f"Invalid date format: {str(e)}")

    def _validate_pagination(self, offset: int, limit: int) -> None:
        if offset < 1:
            raise IntercarsAPIError(400, "Offset must be at least 1")
        if limit < 1 or limit > 100:
            raise IntercarsAPIError(400, "Limit must be between 1 and 100")

    async def close(self) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None

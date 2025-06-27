import asyncio
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urljoin

import httpx

from app.config import ASG_TOKEN

logger = logging.getLogger(__name__)


class ASGAPIError(Exception):
    def __init__(
        self, status_code: int, message: str, details: Optional[Dict[str, Any]] = None
    ):
        self.status_code = status_code
        self.message = message
        self.details = details or {}
        super().__init__(f"ASG API Error {status_code}: {message}")


class ASGAdapter:
    BASE_URL = "https://api-online.asg.ua/api"
    AUTH_SALT = "JHBds9328*(&Y"

    REQUEST_TIMEOUT = 30.0
    MAX_RETRIES = 3
    RETRY_BACKOFF = 1.0
    TOKEN_BUFFER_SECONDS = 300

    def __init__(self, login: str = None, password: str = None, token: str = None):
        self._login = login
        self._password = password
        self._access_token = token or ASG_TOKEN
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

    def _generate_auth_header(self, login: str, password: str) -> str:
        auth_string = f"{login}{self.AUTH_SALT}{password}"
        return hashlib.sha256(auth_string.encode()).hexdigest()

    @property
    def _is_token_valid(self) -> bool:
        if not self._access_token:
            return False
        if not self._token_expires_at:
            return True
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

    async def _handle_response_errors(self, response: httpx.Response) -> None:
        if response.is_success:
            return

        try:
            error_data = response.json()
        except (ValueError, TypeError):
            error_data = {"error": response.text}

        error_message = (
            error_data.get("message")
            or error_data.get("error")
            or error_data.get("detail")
            or "Unknown error"
        )

        if response.status_code == 401:
            self._access_token = None
            self._token_expires_at = None

        raise ASGAPIError(response.status_code, error_message, error_data)

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        require_auth: bool = True,
        use_asg_header: bool = False,
    ) -> Dict[str, Any]:

        client = await self._get_client()
        url = urljoin(self.BASE_URL, endpoint.lstrip("/"))

        headers = {"Content-Type": "application/json"}

        if require_auth and self._access_token:
            headers["Authorization"] = f"Bearer {self._access_token}"

        if use_asg_header and self._login and self._password:
            headers["X-ASG-Header"] = self._generate_auth_header(
                self._login, self._password
            )

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
                    raise ASGAPIError(400, f"Unsupported HTTP method: {method}")

                await self._handle_response_errors(response)

                try:
                    return response.json()
                except (ValueError, TypeError):
                    return {"success": True, "data": response.text}

            except ASGAPIError as e:
                if (
                    e.status_code == 401
                    and attempt < self.MAX_RETRIES - 1
                    and self._login
                    and self._password
                ):
                    logger.warning("Token expired, attempting re-authentication...")
                    try:
                        await self._authenticate()
                        continue
                    except Exception as auth_error:
                        logger.error(f"Re-authentication failed: {auth_error}")
                raise
            except httpx.RequestError as e:
                if attempt < self.MAX_RETRIES - 1:
                    wait_time = self.RETRY_BACKOFF * (2**attempt)
                    logger.warning(
                        f"Request failed (attempt {attempt + 1}), retrying in {wait_time}s: {e}"
                    )
                    await asyncio.sleep(wait_time)
                    continue
                raise ASGAPIError(
                    500, f"Network error after {self.MAX_RETRIES} attempts: {str(e)}"
                )

    async def _authenticate(self) -> Dict[str, Any]:
        if not self._login or not self._password:
            raise ASGAPIError(401, "Login credentials are required for authentication")

        auth_data = {"login": self._login, "password": self._password}

        result = await self._make_request(
            "POST",
            "/auth/login",
            json_data=auth_data,
            require_auth=False,
            use_asg_header=True,
        )

        self._access_token = result.get("access_token")
        if not self._access_token:
            raise ASGAPIError(401, "No access token received from authentication")

        expires_in = result.get("expires_in", 3600)
        self._token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in)

        logger.info("Successfully authenticated with ASG API")
        return result

    async def login(self, login: str, password: str) -> Dict[str, Any]:
        if not login or not login.strip():
            raise ASGAPIError(400, "Login cannot be empty")
        if not password or not password.strip():
            raise ASGAPIError(400, "Password cannot be empty")

        self._login = login.strip()
        self._password = password.strip()
        return await self._authenticate()

    async def logout(self) -> Dict[str, Any]:
        try:
            result = await self._make_request("POST", "/auth/logout")
            self._access_token = None
            self._token_expires_at = None
            return result
        except ASGAPIError:
            self._access_token = None
            self._token_expires_at = None
            raise

    async def get_me(self) -> Dict[str, Any]:
        return await self._make_request("POST", "/auth/me")

    async def refresh_token(self) -> Dict[str, Any]:
        result = await self._make_request("POST", "/auth/refresh")

        new_token = result.get("access_token")
        if new_token:
            self._access_token = new_token
            expires_in = result.get("expires_in", 3600)
            self._token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in)

        return result

    async def get_orders(self) -> Dict[str, Any]:
        return await self._make_request("POST", "/orders/all")

    async def create_order(
        self, products: List[Dict[str, Any]], test: bool = False
    ) -> Dict[str, Any]:
        if not products:
            raise ASGAPIError(400, "Products list cannot be empty")

        for i, product in enumerate(products):
            if not isinstance(product, dict):
                raise ASGAPIError(400, f"Product at index {i} must be a dictionary")
            if "id" not in product and "sku" not in product:
                raise ASGAPIError(
                    400, f"Product at index {i} must have 'id' or 'sku' field"
                )
            if "quantity" not in product:
                raise ASGAPIError(
                    400, f"Product at index {i} must have 'quantity' field"
                )

            try:
                quantity = int(product["quantity"])
                if quantity <= 0:
                    raise ASGAPIError(
                        400, f"Product at index {i} quantity must be positive"
                    )
            except (ValueError, TypeError):
                raise ASGAPIError(
                    400, f"Product at index {i} quantity must be a valid number"
                )

        payload = {"test": "1" if test else "0", "products": products}
        return await self._make_request("POST", "/orders/store", json_data=payload)

    async def cancel_order(self, order_id: Union[int, str]) -> Dict[str, Any]:
        if not order_id:
            raise ASGAPIError(400, "Order ID cannot be empty")

        try:
            order_id_int = int(order_id)
            if order_id_int <= 0:
                raise ASGAPIError(400, "Order ID must be a positive integer")
        except (ValueError, TypeError):
            raise ASGAPIError(400, "Order ID must be a valid integer")

        return await self._make_request("POST", f"/orders/cancel/{order_id_int}")

    async def get_prices(
        self, filter_props: Optional[Dict[str, Any]] = None, page: int = 1
    ) -> Dict[str, Any]:
        if page < 1:
            raise ASGAPIError(400, "Page number must be at least 1")
        if page > 10000:
            raise ASGAPIError(400, "Page number cannot exceed 10000")

        params = {"page": page}
        json_data = {"filter": filter_props or {}}

        return await self._make_request(
            "POST", "/prices", params=params, json_data=json_data
        )

    async def get_categories(self) -> Dict[str, Any]:
        return await self._make_request("POST", "/categories")

    async def search_products(
        self,
        query: str,
        category_id: Optional[int] = None,
        page: int = 1,
        per_page: int = 20,
    ) -> Dict[str, Any]:
        if not query or not query.strip():
            raise ASGAPIError(400, "Search query cannot be empty")
        if page < 1:
            raise ASGAPIError(400, "Page number must be at least 1")
        if per_page < 1 or per_page > 100:
            raise ASGAPIError(400, "Per page must be between 1 and 100")

        filters = {"search": query.strip()}
        if category_id is not None:
            try:
                category_id_int = int(category_id)
                if category_id_int > 0:
                    filters["category_id"] = category_id_int
            except (ValueError, TypeError):
                raise ASGAPIError(400, "Category ID must be a valid integer")

        params = {"page": page, "per_page": per_page}
        json_data = {"filter": filters}

        return await self._make_request(
            "POST", "/prices", params=params, json_data=json_data
        )

    async def get_product_details(self, product_id: Union[int, str]) -> Dict[str, Any]:
        if not product_id:
            raise ASGAPIError(400, "Product ID cannot be empty")

        try:
            product_id_int = int(product_id)
            if product_id_int <= 0:
                raise ASGAPIError(400, "Product ID must be a positive integer")
        except (ValueError, TypeError):
            raise ASGAPIError(400, "Product ID must be a valid integer")

        filters = {"id": product_id_int}
        json_data = {"filter": filters}

        return await self._make_request("POST", "/prices", json_data=json_data)

    async def close(self) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None

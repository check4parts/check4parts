import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin

import httpx

from app.config import UNIQTRADE_EMAIL, UNIQTRADE_PASSWORD, UNIQTRADE_FINGERPRINT

logger = logging.getLogger(__name__)


class UniqTradeAPIError(Exception):
    """Represents HTTP level failures originating from UniqTrade."""

    def __init__(
        self, status_code: int, message: str, details: Optional[Dict[str, Any]] = None
    ):
        self.status_code = status_code
        self.message = message
        self.details = details or {}
        super().__init__(f"UniqTrade API Error {status_code}: {message}")


class UniqTradeAdapter:
    """Client for UniqTrade's REST API handling authentication and retries."""

    BASE_URL = "https://order24-api.utr.ua"

    REQUEST_TIMEOUT = 30.0
    MAX_RETRIES = 3
    RETRY_BACKOFF = 1.0

    def __init__(
        self, email: str = None, password: str = None, browser_fingerprint: str = None
    ):
        self._email = email or UNIQTRADE_EMAIL
        self._password = password or UNIQTRADE_PASSWORD
        self._browser_fingerprint = browser_fingerprint or UNIQTRADE_FINGERPRINT

        if not self._email or not self._password:
            raise UniqTradeAPIError(401, "UniqTrade credentials are required")
        if not self._browser_fingerprint:
            raise UniqTradeAPIError(401, "Browser fingerprint is required")

        self._client: Optional[httpx.AsyncClient] = None
        self._token: Optional[str] = None
        self._refresh_token: Optional[str] = None
        self._token_expires_at: Optional[datetime] = None

    async def __aenter__(self):
        self._client = httpx.AsyncClient(
            timeout=httpx.Timeout(self.REQUEST_TIMEOUT),
            limits=httpx.Limits(max_connections=10, max_keepalive_connections=5),
        )
        await self._ensure_authenticated()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._client:
            await self._client.aclose()

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

        if response.status_code == 412:
            error_message = (
                "Invalid credentials. Please check your login data and try again."
            )
        elif response.status_code == 401:
            error_message = error_data.get("message") or "Authentication error"
        else:
            error_message = (
                error_data.get("message")
                or error_data.get("error")
                or f"HTTP {response.status_code} error"
            )

        raise UniqTradeAPIError(response.status_code, error_message, error_data)

    def _is_token_expired(self) -> bool:
        """Check if current token is expired or about to expire (within 5 minutes)"""
        if not self._token or not self._token_expires_at:
            return True
        return datetime.now() >= (self._token_expires_at - timedelta(minutes=5))

    async def _login(self) -> Dict[str, Any]:
        """Perform login to get JWT tokens"""
        client = await self._get_client()
        url = urljoin(self.BASE_URL, "/api/login_check")

        headers = {"Content-Type": "application/json"}
        json_data = {
            "email": self._email,
            "password": self._password,
            "browser_fingerprint": self._browser_fingerprint,
        }

        for attempt in range(self.MAX_RETRIES):
            try:
                response = await client.post(url, json=json_data, headers=headers)
                await self._handle_response_errors(response)

                auth_data = response.json()
                self._token = auth_data["token"]
                self._refresh_token = auth_data["refresh_token"]

                # Parse expires_at timestamp
                expires_str = auth_data["expires_at"]
                self._token_expires_at = datetime.strptime(
                    expires_str, "%Y-%m-%d %H:%M:%S"
                )

                logger.info("Successfully authenticated with UniqTrade API")
                return auth_data

            except UniqTradeAPIError:
                raise
            except httpx.RequestError as e:
                if attempt < self.MAX_RETRIES - 1:
                    wait_time = self.RETRY_BACKOFF * (2**attempt)
                    logger.warning(
                        f"Login request failed (attempt {attempt + 1}), retrying in {wait_time}s: {e}"
                    )
                    await asyncio.sleep(wait_time)
                    continue
                raise UniqTradeAPIError(
                    500,
                    f"Network error during login after {self.MAX_RETRIES} attempts: {str(e)}",
                )

    async def _refresh_auth_token(self) -> Dict[str, Any]:
        """Refresh expired JWT token using refresh token"""
        if not self._refresh_token:
            raise UniqTradeAPIError(401, "No refresh token available")

        client = await self._get_client()
        url = urljoin(self.BASE_URL, "/api/token/refresh")

        headers = {"Content-Type": "application/json"}
        json_data = {
            "refresh_token": self._refresh_token,
            "browser_fingerprint": self._browser_fingerprint,
        }

        for attempt in range(self.MAX_RETRIES):
            try:
                response = await client.post(url, json=json_data, headers=headers)
                await self._handle_response_errors(response)

                auth_data = response.json()
                self._token = auth_data["token"]
                self._refresh_token = auth_data["refresh_token"]

                expires_str = auth_data["expires_at"]
                self._token_expires_at = datetime.strptime(
                    expires_str, "%Y-%m-%d %H:%M:%S"
                )

                logger.info("Successfully refreshed UniqTrade API token")
                return auth_data

            except UniqTradeAPIError as e:
                if e.status_code == 401:
                    logger.warning("Refresh token invalid, attempting full login")
                    return await self._login()
                raise
            except httpx.RequestError as e:
                if attempt < self.MAX_RETRIES - 1:
                    wait_time = self.RETRY_BACKOFF * (2**attempt)
                    logger.warning(
                        f"Token refresh failed (attempt {attempt + 1}), retrying in {wait_time}s: {e}"
                    )
                    await asyncio.sleep(wait_time)
                    continue
                raise UniqTradeAPIError(
                    500,
                    f"Network error during token refresh after {self.MAX_RETRIES} attempts: {str(e)}",
                )

    async def _ensure_authenticated(self) -> None:
        """Ensure we have a valid authentication token"""
        if self._is_token_expired():
            if self._refresh_token:
                try:
                    await self._refresh_auth_token()
                except UniqTradeAPIError:
                    await self._login()
            else:
                await self._login()

    async def _make_authenticated_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        language: str = "ua",
        return_raw: bool = False,
    ) -> Any:
        """Make authenticated request with automatic token refresh"""
        await self._ensure_authenticated()

        client = await self._get_client()
        url = urljoin(self.BASE_URL, endpoint.lstrip("/"))

        headers = {"Authorization": f"Bearer {self._token}", "Language": language}

        for attempt in range(self.MAX_RETRIES):
            try:
                method_upper = method.upper()
                if method_upper == "GET":
                    response = await client.get(url, params=params, headers=headers)
                elif method_upper == "POST":
                    response = await client.post(
                        url, params=params, json=json_data, headers=headers
                    )
                elif method_upper == "DELETE":
                    response = await client.delete(
                        url, params=params, json=json_data, headers=headers
                    )
                else:
                    raise UniqTradeAPIError(400, f"Unsupported HTTP method: {method}")

                if response.status_code == 401:
                    error_data = {}
                    try:
                        error_data = response.json()
                    except (ValueError, TypeError):
                        pass

                    if "Expired JWT Token" in str(error_data.get("message", "")):
                        logger.info("Token expired during request, refreshing...")
                        await self._refresh_auth_token()
                        headers["Authorization"] = f"Bearer {self._token}"
                        if method_upper == "GET":
                            response = await client.get(
                                url, params=params, headers=headers
                            )
                        elif method_upper == "POST":
                            response = await client.post(
                                url, params=params, json=json_data, headers=headers
                            )
                        elif method_upper == "DELETE":
                            response = await client.delete(
                                url, params=params, json=json_data, headers=headers
                            )
                        else:
                            raise UniqTradeAPIError(
                                400, f"Unsupported HTTP method: {method}"
                            )

                await self._handle_response_errors(response)

                if return_raw:
                    return response

                try:
                    return response.json()
                except (ValueError, TypeError):
                    return {"data": response.text}

            except UniqTradeAPIError:
                raise
            except httpx.RequestError as e:
                if attempt < self.MAX_RETRIES - 1:
                    wait_time = self.RETRY_BACKOFF * (2**attempt)
                    logger.warning(
                        f"Request failed (attempt {attempt + 1}), retrying in {wait_time}s: {e}"
                    )
                    await asyncio.sleep(wait_time)
                    continue
                raise UniqTradeAPIError(
                    500, f"Network error after {self.MAX_RETRIES} attempts: {str(e)}"
                )

    def _validate_positive_int(self, value: int, field_name: str) -> int:
        if not isinstance(value, int) or value <= 0:
            raise UniqTradeAPIError(400, f"{field_name} must be a positive integer")
        return value

    def _validate_non_empty_string(self, value: str, field_name: str) -> str:
        if not value or not value.strip():
            raise UniqTradeAPIError(400, f"{field_name} cannot be empty")
        return value.strip()

    async def search_by_oem(
        self, oem: str, include_info: bool = False, language: str = "ua"
    ) -> Dict[str, Any]:
        """
        Search for parts by OEM/article number

        Args:
            oem: Part article/OEM number
            include_info: Whether to include additional info (images, characteristics)
            language: Response language ('ua' or 'ru')
        """
        oem = self._validate_non_empty_string(oem, "OEM")

        endpoint = f"/api/search/{oem}"
        params = {}
        if include_info:
            params["info"] = "1"

        return await self._make_authenticated_request(
            "GET", endpoint, params=params, language=language
        )

    async def search_by_oem_and_brand(
        self, oem: str, brand: str, include_info: bool = False, language: str = "ua"
    ) -> Dict[str, Any]:
        """
        Search for parts by OEM/article number and brand

        Args:
            oem: Part article/OEM number
            brand: Brand name or external code
            include_info: Whether to include additional info (images, characteristics)
            language: Response language ('ua' or 'ru')
        """
        oem = self._validate_non_empty_string(oem, "OEM")
        brand = self._validate_non_empty_string(brand, "Brand")

        endpoint = f"/api/search/{oem}"
        params = {"brand": brand}
        if include_info:
            params["info"] = "1"

        return await self._make_authenticated_request(
            "GET", endpoint, params=params, language=language
        )

    async def get_detail_applicability(
        self, detail_id: int, language: str = "ua"
    ) -> Dict[str, Any]:
        """
        Get part applicability information by detail ID

        Args:
            detail_id: Detail ID from search results
            language: Response language ('ua' or 'ru')
        """
        if not isinstance(detail_id, int):
            raise UniqTradeAPIError(400, "Detail ID must be an integer")

        endpoint = f"/api/applicability/{detail_id}"
        return await self._make_authenticated_request(
            "GET", endpoint, language=language
        )

    async def get_detail_info(
        self, detail_id: int, language: str = "ua"
    ) -> Dict[str, Any]:
        """
        Get detailed information about a part by detail ID

        Args:
            detail_id: Detail ID from search results
            language: Response language ('ua' or 'ru')
        """
        if not isinstance(detail_id, int):
            raise UniqTradeAPIError(400, "Detail ID must be an integer")

        endpoint = f"/api/detail/{detail_id}"
        return await self._make_authenticated_request(
            "GET", endpoint, language=language
        )

    async def get_detail_characteristics(
        self, detail_id: int, language: str = "ua"
    ) -> Dict[str, Any]:
        """
        Get part characteristics by detail ID

        Args:
            detail_id: Detail ID from search results
            language: Response language ('ua' or 'ru')
        """
        if not isinstance(detail_id, int):
            raise UniqTradeAPIError(400, "Detail ID must be an integer")

        endpoint = f"/api/characteristics/{detail_id}"
        return await self._make_authenticated_request(
            "GET", endpoint, language=language
        )

    async def batch_search(
        self, search_items: List[Dict[str, Any]], language: str = "ua"
    ) -> Dict[str, Any]:
        """
        Batch search for multiple parts in a single request

        Args:
            search_items: List of search items, each containing either:
                         - {"id": detail_id} for search by internal ID
                         - {"oem": "article", "brand": "brand_name"} for search by OEM+brand
            language: Response language ('ua' or 'ru')
        """
        if not isinstance(search_items, list) or not search_items:
            raise UniqTradeAPIError(400, "Search items must be a non-empty list")

        json_data = {"details": search_items}
        return await self._make_authenticated_request(
            "POST", "/api/search", json_data=json_data, language=language
        )

    async def search_analogs(
        self, brand: str, oem: str, language: str = "ua"
    ) -> Dict[str, Any]:
        """
        Search for part analogs by brand and OEM

        Args:
            brand: Brand name
            oem: Part article/OEM number
            language: Response language ('ua' or 'ru')
        """
        brand = self._validate_non_empty_string(brand, "Brand")
        oem = self._validate_non_empty_string(oem, "OEM")

        endpoint = f"/api/analogs/{brand}/{oem}"
        return await self._make_authenticated_request(
            "GET", endpoint, language=language
        )

    async def get_delivery_points(self, language: str = "ua") -> Dict[str, Any]:
        """
        Get list of available delivery points

        Args:
            language: Response language ('ua' or 'ru')
        """
        return await self._make_authenticated_request(
            "GET", "/api/delivery-points", language=language
        )

    async def get_transporters(
        self, date: str, point_id: int, language: str = "ua"
    ) -> Dict[str, Any]:
        """
        Get list of available transporters for specific date and delivery point

        Args:
            date: Delivery date in YYYY-MM-DD format
            point_id: Delivery point ID from get_delivery_points
            language: Response language ('ua' or 'ru')
        """
        if not isinstance(point_id, int):
            raise UniqTradeAPIError(400, "Point ID must be an integer")

        # Validate date format
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            raise UniqTradeAPIError(400, "Date must be in YYYY-MM-DD format")

        endpoint = f"/api/transporters/{date}/{point_id}"
        return await self._make_authenticated_request(
            "GET", endpoint, language=language
        )

    async def get_delivery_options(
        self,
        date: str,
        point_id: int,
        transporter_id: int,
        storage_ids: List[int],
        language: str = "ua",
    ) -> Dict[str, Any]:
        """
        Get delivery options for specified date, point, and transporter

        Args:
            date: Delivery date in YYYY-MM-DD format
            point_id: Delivery point ID
            transporter_id: Transporter ID
            storage_ids: List of storage IDs
            language: Response language ('ua' or 'ru')
        """
        # Validate date format
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            raise UniqTradeAPIError(400, "Date must be in YYYY-MM-DD format")

        if not storage_ids:
            raise UniqTradeAPIError(400, "Storage IDs list cannot be empty")

        endpoint = f"/api/deliveries/{date}/{point_id}/{transporter_id}"
        json_data = {"storages": storage_ids}

        return await self._make_authenticated_request(
            "POST", endpoint, json_data=json_data, language=language
        )

    async def create_order(
        self, orders: List[Dict[str, Any]], language: str = "ua"
    ) -> Dict[str, Any]:
        """
        Create new order(s)

        Args:
            orders: List of order dictionaries with required fields:
                - comment: Order comment
                - delivery: Delivery option ID
                - deliveryDate: Delivery date (YYYY-MM-DD)
                - deliveryPoint: Delivery point ID
                - items: List of items with detail, quantity, storage
                - paymentType: 'nal' or 'beznal'
                - withoutDocument: Boolean
            language: Response language ('ua' or 'ru')
        """
        if not orders:
            raise UniqTradeAPIError(400, "Orders list cannot be empty")

        required_fields = [
            "delivery",
            "deliveryDate",
            "deliveryPoint",
            "items",
            "paymentType",
        ]
        for i, order in enumerate(orders):
            for field in required_fields:
                if field not in order:
                    raise UniqTradeAPIError(
                        400, f"Missing required field '{field}' in order {i}"
                    )

            try:
                datetime.strptime(order["deliveryDate"], "%Y-%m-%d")
            except ValueError:
                raise UniqTradeAPIError(
                    400, f"deliveryDate must be in YYYY-MM-DD format in order {i}"
                )

            if order["paymentType"] not in ["nal", "beznal"]:
                raise UniqTradeAPIError(
                    400, f"paymentType must be 'nal' or 'beznal' in order {i}"
                )

            if not order.get("items"):
                raise UniqTradeAPIError(400, f"Items list cannot be empty in order {i}")

            for j, item in enumerate(order["items"]):
                item_required_fields = ["detail", "quantity", "storage"]
                for field in item_required_fields:
                    if field not in item:
                        raise UniqTradeAPIError(
                            400,
                            f"Missing required field '{field}' in item {j} of order {i}",
                        )

        endpoint = "/api/order/accept"

        return await self._make_authenticated_request(
            "POST", endpoint, json_data=orders, language=language
        )

    async def get_order_list(
        self,
        start_date: str,
        page: Optional[int] = None,
        limit: Optional[int] = None,
        mode: str = "period",
        detail_id: Optional[int] = None,
        language: str = "ua",
    ) -> Dict[str, Any]:
        """
        Get list of orders from specified start date to current date

        Args:
            start_date: Start date for order search (YYYY-MM-DD)
            page: Page number for pagination
            limit: Number of items per page
            mode: Search mode (default: "period")
            detail_id: Filter orders containing specific detail ID
            language: Response language ('ua' or 'ru')
        """
        try:
            datetime.strptime(start_date, "%Y-%m-%d")
        except ValueError:
            raise UniqTradeAPIError(400, "Start date must be in YYYY-MM-DD format")

        if detail_id:
            endpoint = f"/api/order-list/{start_date}/{detail_id}"
        else:
            endpoint = f"/api/order-list/{start_date}"

        params = {}
        if page is not None:
            params["page"] = page
        if limit is not None:
            params["limit"] = limit
        if mode:
            params["mode"] = mode

        return await self._make_authenticated_request(
            "GET", endpoint, params=params, language=language
        )

    async def get_order_details(
        self, order_id: int, language: str = "ua"
    ) -> Dict[str, Any]:
        order_id = self._validate_positive_int(order_id, "Order ID")
        endpoint = f"/api/order/{order_id}"
        return await self._make_authenticated_request(
            "GET", endpoint, language=language
        )

    async def get_pricelist_export_params(
        self, language: str = "ua"
    ) -> Dict[str, Any]:
        endpoint = "/api/pricelist/params"
        return await self._make_authenticated_request(
            "GET", endpoint, language=language
        )

    async def request_pricelist_export(
        self,
        export_format: str,
        visible_brands_id: Optional[List[int]] = None,
        categories_id: Optional[List[int]] = None,
        models_id: Optional[List[str]] = None,
        in_stock: bool = True,
        show_scancode: bool = False,
        utr_article: bool = False,
        language: str = "ua",
    ) -> Dict[str, Any]:
        export_format = self._validate_non_empty_string(export_format, "Format").lower()
        allowed_formats = {"xlsx", "txt", "csv"}
        if export_format not in allowed_formats:
            raise UniqTradeAPIError(
                400,
                "Invalid export format. Allowed values: xlsx, txt, csv",
            )

        for name, value in {
            "visible_brands_id": visible_brands_id,
            "categories_id": categories_id,
        }.items():
            if value is not None:
                if not isinstance(value, list) or not all(
                    isinstance(item, int) for item in value
                ):
                    raise UniqTradeAPIError(
                        400, f"{name} must be a list of integers"
                    )

        if models_id is not None:
            if not isinstance(models_id, list) or not all(
                isinstance(item, str) and item.strip() for item in models_id
            ):
                raise UniqTradeAPIError(
                    400, "models_id must be a list of non-empty strings"
                )

        if not isinstance(in_stock, bool):
            raise UniqTradeAPIError(400, "in_stock must be a boolean value")
        if not isinstance(show_scancode, bool):
            raise UniqTradeAPIError(400, "show_scancode must be a boolean value")
        if not isinstance(utr_article, bool):
            raise UniqTradeAPIError(400, "utr_article must be a boolean value")

        json_data: Dict[str, Any] = {
            "format": export_format,
            "in_stock": in_stock,
            "show_scancode": show_scancode,
            "utr_article": utr_article,
        }

        if visible_brands_id:
            json_data["visible_brands_id"] = visible_brands_id
        if categories_id:
            json_data["categories_id"] = categories_id
        if models_id:
            json_data["models_id"] = [model.strip() for model in models_id]

        endpoint = "/api/pricelist/export"
        return await self._make_authenticated_request(
            "POST", endpoint, json_data=json_data, language=language
        )

    async def get_pricelist_status(
        self, pricelist_id: int, language: str = "ua"
    ) -> Dict[str, Any]:
        pricelist_id = self._validate_positive_int(pricelist_id, "Pricelist ID")
        endpoint = f"/api/pricelist/status/{pricelist_id}"
        return await self._make_authenticated_request(
            "GET", endpoint, language=language
        )

    async def get_pricelists(self, language: str = "ua") -> Dict[str, Any]:
        endpoint = "/api/pricelist"
        return await self._make_authenticated_request(
            "GET", endpoint, language=language
        )

    async def download_pricelist(
        self, token: str, language: str = "ua"
    ) -> httpx.Response:
        token = self._validate_non_empty_string(token, "Pricelist token")
        endpoint = f"/api/pricelist/download/{token}"
        return await self._make_authenticated_request(
            "GET", endpoint, language=language, return_raw=True
        )

    async def delete_pricelist(
        self, pricelist_id: int, language: str = "ua"
    ) -> Dict[str, Any]:
        pricelist_id = self._validate_positive_int(pricelist_id, "Pricelist ID")
        endpoint = f"/api/pricelist/{pricelist_id}"
        return await self._make_authenticated_request(
            "DELETE", endpoint, language=language
        )

    async def add_to_cart(
        self, detail_id: int, quantity: int, language: str = "ua"
    ) -> Dict[str, Any]:
        detail_id = self._validate_positive_int(detail_id, "Detail ID")
        quantity = self._validate_positive_int(quantity, "Quantity")

        json_data = {"detail_id": detail_id, "quantity": quantity}
        endpoint = "/api/cart/add"
        return await self._make_authenticated_request(
            "POST", endpoint, json_data=json_data, language=language
        )

    async def get_brands(self, language: str = "ua") -> Dict[str, Any]:
        endpoint = "/api/brands"
        return await self._make_authenticated_request(
            "GET", endpoint, language=language
        )

    async def get_storages(
        self,
        all_storages: bool = False,
        point_id: Optional[int] = None,
        language: str = "ua",
    ) -> Dict[str, Any]:
        if point_id is not None and not isinstance(point_id, int):
            raise UniqTradeAPIError(400, "point_id must be an integer if provided")

        params: Dict[str, Any] = {}
        if all_storages:
            params["all"] = 1
        if point_id is not None:
            params["point_id"] = point_id

        endpoint = "/api/storages"
        return await self._make_authenticated_request(
            "GET", endpoint, params=params, language=language
        )

    async def get_accounting_numbers_by_order(
        self, order_code: str, language: str = "ua"
    ) -> Dict[str, Any]:
        order_code = self._validate_non_empty_string(order_code, "Order code")
        endpoint = f"/api/accounting/order/{order_code}"
        return await self._make_authenticated_request(
            "GET", endpoint, language=language
        )

    async def get_order_by_accounting_number(
        self, accounting_number: str, language: str = "ua"
    ) -> Dict[str, Any]:
        accounting_number = self._validate_non_empty_string(
            accounting_number, "Accounting number"
        )
        endpoint = f"/api/accounting/{accounting_number}"
        return await self._make_authenticated_request(
            "GET", endpoint, language=language
        )

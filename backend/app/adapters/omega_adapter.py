import asyncio
import logging
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin
from datetime import datetime

import httpx

from app.config import OMEGA_KEY

logger = logging.getLogger(__name__)


class OmegaAPIError(Exception):
    """Raised when the Omega API returns an error response."""

    def __init__(
        self, status_code: int, message: str, details: Optional[Dict[str, Any]] = None
    ):
        self.status_code = status_code
        self.message = message
        self.details = details or {}
        super().__init__(f"Omega API Error {status_code}: {message}")


class OmegaAdapter:
    """Async wrapper around the Omega REST API with retry handling."""

    BASE_URL = "https://public.omega.page"

    REQUEST_TIMEOUT = 30.0
    MAX_RETRIES = 3
    RETRY_BACKOFF = 1.0

    def __init__(self, key: str = None):
        self._key = key or OMEGA_KEY
        if not self._key:
            raise OmegaAPIError(401, "Omega API key is required")
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
            or f"HTTP {response.status_code} error"
        )

        raise OmegaAPIError(response.status_code, error_message, error_data)

    async def _validate_omega_response(self, data: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(data, dict):
            raise OmegaAPIError(500, "Invalid response format from Omega API")

        success = data.get("Success")
        if success is False:
            errors = data.get("Errors", [])
            if errors and isinstance(errors, list) and len(errors) > 0:
                first_error = errors[0]
                if isinstance(first_error, dict):
                    error_msg = (
                        first_error.get("Description")
                        or first_error.get("Error")
                        or "API returned error"
                    )
                else:
                    error_msg = str(first_error)
            else:
                error_msg = "API request failed"
            raise OmegaAPIError(400, error_msg, {"errors": errors})

        return data

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        client = await self._get_client()
        url = urljoin(self.BASE_URL, endpoint.lstrip("/"))

        headers = {"Content-Type": "application/json"}

        if json_data is None:
            json_data = {}
        json_data["Key"] = self._key

        for attempt in range(self.MAX_RETRIES):
            try:
                if method.upper() == "GET":
                    response = await client.get(url, params=params, headers=headers)
                elif method.upper() == "POST":
                    response = await client.post(
                        url, params=params, json=json_data, headers=headers
                    )
                else:
                    raise OmegaAPIError(400, f"Unsupported HTTP method: {method}")

                await self._handle_response_errors(response)

                try:
                    response_data = response.json()
                    return await self._validate_omega_response(response_data)
                except (ValueError, TypeError):
                    return {"Success": True, "Data": response.text}

            except OmegaAPIError:
                raise
            except httpx.RequestError as e:
                if attempt < self.MAX_RETRIES - 1:
                    wait_time = self.RETRY_BACKOFF * (2**attempt)
                    logger.warning(
                        f"Request failed (attempt {attempt + 1}), retrying in {wait_time}s: {e}"
                    )
                    await asyncio.sleep(wait_time)
                    continue
                raise OmegaAPIError(
                    500, f"Network error after {self.MAX_RETRIES} attempts: {str(e)}"
                )

    def _validate_date_format(self, date_str: str, field_name: str) -> str:
        try:
            datetime.strptime(date_str, "%d.%m.%Y")
            return date_str
        except ValueError:
            raise OmegaAPIError(400, f"{field_name} must be in DD.MM.YYYY format")

    def _validate_non_empty_string(self, value: str, field_name: str) -> str:
        if not value or not value.strip():
            raise OmegaAPIError(400, f"{field_name} cannot be empty")
        return value.strip()

    async def get_account(self) -> Dict[str, Any]:
        return await self._make_request("POST", "/public/api/v1.0/profile/account")

    async def add_product_to_basket(
        self, product_id: int, count: int
    ) -> Dict[str, Any]:
        if not isinstance(product_id, int):
            raise OmegaAPIError(400, "Product ID must be an integer")
        if not isinstance(count, int) or count == 0:
            raise OmegaAPIError(400, "Count must be a non-zero integer")

        json_data = {"ProductId": product_id, "Count": count}
        return await self._make_request(
            "POST", "/public/api/v1.0/basket/addProduct", json_data=json_data
        )

    async def add_product_list_to_basket(
        self, product_list: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        if not product_list:
            raise OmegaAPIError(400, "Product list cannot be empty")

        for i, product in enumerate(product_list):
            if not isinstance(product, dict):
                raise OmegaAPIError(400, f"Product at index {i} must be a dictionary")
            if "ProductId" not in product:
                raise OmegaAPIError(
                    400, f"Product at index {i} must have 'ProductId' field"
                )
            if "Count" not in product:
                raise OmegaAPIError(
                    400, f"Product at index {i} must have 'Count' field"
                )

            try:
                product_id = int(product["ProductId"])
                count = int(product["Count"])
                if count == 0:
                    raise OmegaAPIError(
                        400, f"Product at index {i} count cannot be zero"
                    )
            except (ValueError, TypeError):
                raise OmegaAPIError(
                    400, f"Product at index {i} has invalid ProductId or Count"
                )

        json_data = {"ProductList": product_list}
        return await self._make_request(
            "POST", "/public/api/v1.0/basket/addProductList", json_data=json_data
        )

    async def remove_product_from_basket(self, product_id: int) -> Dict[str, Any]:
        if not isinstance(product_id, int):
            raise OmegaAPIError(400, "Product ID must be an integer")

        json_data = {"ProductId": product_id}
        return await self._make_request(
            "POST",
            "/public/api/v1.0/basket/removeProductFromBasket",
            json_data=json_data,
        )

    async def get_basket(self) -> Dict[str, Any]:
        return await self._make_request("POST", "/public/api/v1.0/basket/getBasket")

    async def clear_basket(self) -> Dict[str, Any]:
        return await self._make_request("POST", "/public/api/v1.0/basket/clear")

    # Claims endpoints
    async def get_kind_claims(self, product_id: str, doc_id: str) -> Dict[str, Any]:
        product_id = self._validate_non_empty_string(product_id, "Product ID")
        doc_id = self._validate_non_empty_string(doc_id, "Document ID")

        json_data = {"ProductId": product_id, "DocId": doc_id}
        return await self._make_request(
            "POST", "/public/api/v1.0/claims/getKindClaims", json_data=json_data
        )

    async def check_claim_kind(
        self, doc_id: str, kind_id: str, product_id: str
    ) -> Dict[str, Any]:
        doc_id = self._validate_non_empty_string(doc_id, "Document ID")
        kind_id = self._validate_non_empty_string(kind_id, "Kind ID")
        product_id = self._validate_non_empty_string(product_id, "Product ID")

        json_data = {
            "DocId": doc_id,
            "KindId": kind_id,
            "ProductId": product_id,
        }
        return await self._make_request(
            "POST", "/public/api/v1.0/claims/checkClaimKind", json_data=json_data
        )

    async def get_discount(
        self, product_id: str, doc_id: str, type_id: str
    ) -> Dict[str, Any]:
        product_id = self._validate_non_empty_string(product_id, "Product ID")
        doc_id = self._validate_non_empty_string(doc_id, "Document ID")
        type_id = self._validate_non_empty_string(type_id, "Type ID")

        json_data = {
            "ProductId": product_id,
            "DocId": doc_id,
            "TypeId": type_id,
        }
        return await self._make_request(
            "POST", "/public/api/v1.0/claims/getDiscount", json_data=json_data
        )

    async def get_contacts(self) -> Dict[str, Any]:
        return await self._make_request("POST", "/public/api/v1.0/claims/getContacts")

    async def upload_photo(
        self, product_id: Optional[str], data: str, file_name: str
    ) -> Dict[str, Any]:
        data = self._validate_non_empty_string(data, "Image data")
        file_name = self._validate_non_empty_string(file_name, "File name")

        if not file_name.lower().endswith(".jpg"):
            raise OmegaAPIError(400, "File must be a JPEG (.jpg) image")

        json_data = {
            "ProductId": product_id.strip() if product_id else "",
            "Data": data,
            "FileName": file_name,
        }
        return await self._make_request(
            "POST", "/public/api/v1.0/claims/uploadPhoto", json_data=json_data
        )

    async def get_addresses(self, kind: int) -> Dict[str, Any]:
        if not isinstance(kind, int):
            raise OmegaAPIError(400, "Kind must be an integer")

        json_data = {"Kind": kind}
        return await self._make_request(
            "POST", "/public/api/v1.0/claims/getAddresses", json_data=json_data
        )

    async def create_claim(
        self,
        doc_id: str,
        products: List[Dict[str, Any]],
        comment: Optional[str] = None,
        contact_id: Optional[str] = None,
        phone_id: Optional[str] = None,
        address_key: Optional[str] = None,
        photos: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        doc_id = self._validate_non_empty_string(doc_id, "Document ID")

        if not products:
            raise OmegaAPIError(400, "Products list cannot be empty")

        for i, product in enumerate(products):
            if not isinstance(product, dict):
                raise OmegaAPIError(400, f"Product at index {i} must be a dictionary")

            required_fields = ["ProductId", "DocId", "KindId"]
            for field in required_fields:
                if field not in product or not str(product[field]).strip():
                    raise OmegaAPIError(
                        400, f"Product at index {i} must have non-empty '{field}' field"
                    )

            if "YearVehicle" in product:
                try:
                    year = int(product["YearVehicle"])
                    if year < 1000 or year > 9999:
                        raise OmegaAPIError(
                            400,
                            f"Product at index {i} YearVehicle must be between 1000 and 9999",
                        )
                except (ValueError, TypeError):
                    raise OmegaAPIError(
                        400, f"Product at index {i} YearVehicle must be a valid integer"
                    )

            if "ReadyForDiscount" in product:
                try:
                    discount = int(product["ReadyForDiscount"])
                    if discount not in [0, 1]:
                        raise OmegaAPIError(
                            400, f"Product at index {i} ReadyForDiscount must be 0 or 1"
                        )
                except (ValueError, TypeError):
                    raise OmegaAPIError(
                        400, f"Product at index {i} ReadyForDiscount must be 0 or 1"
                    )

        json_data = {
            "DocId": doc_id,
            "Products": products,
        }

        if comment:
            json_data["Comment"] = comment.strip()
        if contact_id:
            json_data["ContactId"] = contact_id.strip()
        if phone_id:
            json_data["PhoneId"] = phone_id.strip()
        if address_key:
            json_data["AddressKey"] = address_key.strip()
        if photos:
            json_data["Photos"] = [
                photo.strip() for photo in photos if photo and photo.strip()
            ]

        return await self._make_request(
            "POST", "/public/api/v1.0/claims/createClaim", json_data=json_data
        )

    async def get_claims_list(self) -> Dict[str, Any]:
        return await self._make_request("POST", "/public/api/v1.0/claims/getClaimsList")

    async def download_refund_documents(self) -> Dict[str, Any]:
        return await self._make_request(
            "POST", "/public/api/v1.0/claims/downloadRefundDocuments"
        )

    async def get_contact_list(self, customer_id: str) -> Dict[str, Any]:
        customer_id = self._validate_non_empty_string(customer_id, "Customer ID")

        json_data = {"CustomerId": customer_id}
        return await self._make_request(
            "POST", "/public/api/v1.0/contact/getContacts", json_data=json_data
        )

    async def add_contact(
        self,
        customer_id: str,
        first_name: str,
        second_name: str,
        last_name: str,
        phone: Optional[str] = None,
    ) -> Dict[str, Any]:
        customer_id = self._validate_non_empty_string(customer_id, "Customer ID")
        first_name = self._validate_non_empty_string(first_name, "First name")
        second_name = self._validate_non_empty_string(second_name, "Second name")
        last_name = self._validate_non_empty_string(last_name, "Last name")

        contact_model = {
            "FirstName": first_name,
            "SecondName": second_name,
            "LastName": last_name,
        }

        if phone:
            phone = phone.strip()
            if phone:
                contact_model["Phone"] = phone

        json_data = {"CustomerId": customer_id, "ContactModel": contact_model}
        return await self._make_request(
            "POST", "/public/api/v1.0/contact/addContact", json_data=json_data
        )

    async def edit_contact(
        self, contact_id: str, first_name: str, second_name: str, last_name: str
    ) -> Dict[str, Any]:
        contact_id = self._validate_non_empty_string(contact_id, "Contact ID")
        first_name = self._validate_non_empty_string(first_name, "First name")
        second_name = self._validate_non_empty_string(second_name, "Second name")
        last_name = self._validate_non_empty_string(last_name, "Last name")

        json_data = {
            "ContactModel": {
                "Id": contact_id,
                "FirstName": first_name,
                "SecondName": second_name,
                "LastName": last_name,
            }
        }
        return await self._make_request(
            "POST", "/public/api/v1.0/contact/editContact", json_data=json_data
        )

    async def remove_contact(self, contact_id: str) -> Dict[str, Any]:
        contact_id = self._validate_non_empty_string(contact_id, "Contact ID")

        json_data = {"ContactId": contact_id}
        return await self._make_request(
            "POST", "/public/api/v1.0/contact/removeContact", json_data=json_data
        )

    async def add_contact_phone(self, contact_id: str, phone: str) -> Dict[str, Any]:
        contact_id = self._validate_non_empty_string(contact_id, "Contact ID")
        phone = self._validate_non_empty_string(phone, "Phone")

        json_data = {"ContactId": contact_id, "Phone": phone}
        return await self._make_request(
            "POST", "/public/api/v1.0/contact/addContactPhone", json_data=json_data
        )

    async def remove_contact_phone(self, contact_id: str, phone: str) -> Dict[str, Any]:
        contact_id = self._validate_non_empty_string(contact_id, "Contact ID")
        phone = self._validate_non_empty_string(phone, "Phone")

        json_data = {"ContactId": contact_id, "Phone": phone}
        return await self._make_request(
            "POST", "/public/api/v1.0/contact/removeContactPhone", json_data=json_data
        )

    async def get_contact_details(self, contact_id: str) -> Dict[str, Any]:
        contact_id = self._validate_non_empty_string(contact_id, "Contact ID")

        json_data = {"ContactId": contact_id}
        return await self._make_request(
            "POST", "/public/api/v1.0/contact/getContactDetails", json_data=json_data
        )

    async def get_expense_document(self, doc_id: str) -> Dict[str, Any]:
        doc_id = self._validate_non_empty_string(doc_id, "Document ID")

        json_data = {"DocId": doc_id}
        return await self._make_request(
            "POST", "/public/api/v1.0/expense/getExpenseDocument", json_data=json_data
        )

    async def get_expense_document_list(
        self, start_date: str, end_date: str
    ) -> Dict[str, Any]:
        start_date = self._validate_date_format(start_date, "Start date")
        end_date = self._validate_date_format(end_date, "End date")

        try:
            start_dt = datetime.strptime(start_date, "%d.%m.%Y")
            end_dt = datetime.strptime(end_date, "%d.%m.%Y")
            if start_dt > end_dt:
                raise OmegaAPIError(400, "Start date cannot be after end date")
        except ValueError:
            raise OmegaAPIError(400, "Invalid date format")

        json_data = {"StartDate": start_date, "EndDate": end_date}
        return await self._make_request(
            "POST",
            "/public/api/v1.0/expense/getExpenseDocumentList",
            json_data=json_data,
        )

    async def get_expense_document_details(self, doc_id: str) -> Dict[str, Any]:
        doc_id = self._validate_non_empty_string(doc_id, "Document ID")

        json_data = {"DocId": doc_id}
        return await self._make_request(
            "POST",
            "/public/api/v1.0/expense/getExpenseDocumentDetails",
            json_data=json_data,
        )

    async def add_invoice(self) -> Dict[str, Any]:
        return await self._make_request("POST", "/public/api/v1.0/invoice8/addInvoice")

    async def reserve_invoice(self, doc_id: str) -> Dict[str, Any]:
        doc_id = self._validate_non_empty_string(doc_id, "Document ID")

        json_data = {"DocId": doc_id}
        return await self._make_request(
            "POST", "/public/api/v1.0/invoice8/reserveInvoice", json_data=json_data
        )

    async def cod_invoice(self, doc_id: str, summ_cod: str) -> Dict[str, Any]:
        doc_id = self._validate_non_empty_string(doc_id, "Document ID")
        summ_cod = self._validate_non_empty_string(summ_cod, "COD Sum")

        json_data = {"DocId": doc_id, "SummCod": summ_cod}
        return await self._make_request(
            "POST", "/public/api/v1.0/invoice8/codInvoice", json_data=json_data
        )

    async def ready_invoice(self, doc_id: str) -> Dict[str, Any]:
        doc_id = self._validate_non_empty_string(doc_id, "Document ID")

        json_data = {"DocId": doc_id}
        return await self._make_request(
            "POST", "/public/api/v1.0/invoice8/readyInvoice", json_data=json_data
        )

    async def add_product_to_invoice(
        self, doc_id: str, prod_id: int, count: int
    ) -> Dict[str, Any]:
        doc_id = self._validate_non_empty_string(doc_id, "Document ID")
        if not isinstance(prod_id, int):
            raise OmegaAPIError(400, "Product ID must be an integer")
        if not isinstance(count, int) or count == 0:
            raise OmegaAPIError(400, "Count must be a non-zero integer")

        json_data = {"DocId": doc_id, "ProdId": prod_id, "Count": count}
        return await self._make_request(
            "POST", "/public/api/v1.0/invoice8/addProductToInvoice", json_data=json_data
        )

    async def move_products_from_basket_to_invoice(self, doc_id: str) -> Dict[str, Any]:
        doc_id = self._validate_non_empty_string(doc_id, "Document ID")

        json_data = {"DocId": doc_id}
        return await self._make_request(
            "POST",
            "/public/api/v1.0/invoice8/moveProductsFromBasketToInvoice",
            json_data=json_data,
        )

    async def get_invoice_list(self) -> Dict[str, Any]:
        return await self._make_request(
            "POST", "/public/api/v1.0/invoice8/getListInvoice"
        )

    async def get_invoice(self, doc_id: str) -> Dict[str, Any]:
        doc_id = self._validate_non_empty_string(doc_id, "Document ID")

        json_data = {"DocId": doc_id}
        return await self._make_request(
            "POST", "/public/api/v1.0/invoice8/getInvoice", json_data=json_data
        )

    async def get_customers(self) -> Dict[str, Any]:
        return await self._make_request(
            "POST", "/public/api/v1.0/invoice8/getCustomers"
        )

    async def set_invoice_customer(
        self, customer_id: str, doc_id: str
    ) -> Dict[str, Any]:
        customer_id = self._validate_non_empty_string(customer_id, "Customer ID")
        doc_id = self._validate_non_empty_string(doc_id, "Document ID")

        json_data = {"CustomerId": customer_id, "DocId": doc_id}
        return await self._make_request(
            "POST", "/public/api/v1.0/invoice8/setInvoiceCustomer", json_data=json_data
        )

    async def get_contracts(self, customer_id: str) -> Dict[str, Any]:
        customer_id = self._validate_non_empty_string(customer_id, "Customer ID")

        json_data = {"CustomerId": customer_id}
        return await self._make_request(
            "POST", "/public/api/v1.0/invoice8/getContracts", json_data=json_data
        )

    async def set_invoice_contract(
        self, contract_id: str, doc_id: str
    ) -> Dict[str, Any]:
        contract_id = self._validate_non_empty_string(contract_id, "Contract ID")
        doc_id = self._validate_non_empty_string(doc_id, "Document ID")

        json_data = {"ContractId": contract_id, "DocId": doc_id}
        return await self._make_request(
            "POST", "/public/api/v1.0/invoice8/setInvoiceContract", json_data=json_data
        )

    async def get_warehouses(
        self,
        customer_id: str,
        shipment_type_id: Optional[str] = None,
        delivery_address_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        customer_id = self._validate_non_empty_string(customer_id, "Customer ID")

        json_data = {"CustomerId": customer_id}
        if shipment_type_id:
            json_data["ShipmentTypeId"] = shipment_type_id.strip()
        if delivery_address_id:
            json_data["DeliveryAddressId"] = delivery_address_id.strip()

        return await self._make_request(
            "POST", "/public/api/v1.0/invoice8/getWarehouses", json_data=json_data
        )

    async def set_invoice_warehouse(
        self, warehouse_id: str, doc_id: str
    ) -> Dict[str, Any]:
        warehouse_id = self._validate_non_empty_string(warehouse_id, "Warehouse ID")
        doc_id = self._validate_non_empty_string(doc_id, "Document ID")

        json_data = {"WarehouseId": warehouse_id, "DocId": doc_id}
        return await self._make_request(
            "POST", "/public/api/v1.0/invoice8/setInvoiceWarehouse", json_data=json_data
        )

    async def get_shipment_types(self) -> Dict[str, Any]:
        return await self._make_request(
            "POST", "/public/api/v1.0/invoice8/getShipmentTypes"
        )

    async def get_plain_settings(self) -> Dict[str, Any]:
        return await self._make_request(
            "POST", "/public/api/v1.0/invoice8/getPlainSettings"
        )

    async def set_plain_shipment(
        self, doc_id: str, address_id: str, route_id: str
    ) -> Dict[str, Any]:
        doc_id = self._validate_non_empty_string(doc_id, "Document ID")
        address_id = self._validate_non_empty_string(address_id, "Address ID")
        route_id = self._validate_non_empty_string(route_id, "Route ID")

        json_data = {"DocId": doc_id, "AddressId": address_id, "RouteId": route_id}
        return await self._make_request(
            "POST", "/public/api/v1.0/invoice8/setPlainShipment", json_data=json_data
        )

    async def get_self_delivery_settings(self, doc_id: str) -> Dict[str, Any]:
        doc_id = self._validate_non_empty_string(doc_id, "Document ID")

        json_data = {"DocId": doc_id}
        return await self._make_request(
            "POST",
            "/public/api/v1.0/invoice8/getSelfDeliverySettings",
            json_data=json_data,
        )

    async def set_self_delivery_shipment(self, doc_id: str) -> Dict[str, Any]:
        doc_id = self._validate_non_empty_string(doc_id, "Document ID")

        json_data = {"DocId": doc_id}
        return await self._make_request(
            "POST",
            "/public/api/v1.0/invoice8/setSelfDeliveryShipment",
            json_data=json_data,
        )

    async def get_courier_delivery_settings(self, doc_id: str) -> Dict[str, Any]:
        doc_id = self._validate_non_empty_string(doc_id, "Document ID")

        json_data = {"DocId": doc_id}
        return await self._make_request(
            "POST",
            "/public/api/v1.0/invoice8/getCourierDeliverySettings",
            json_data=json_data,
        )

    async def get_courier_towns(self, doc_id: str, delivery_id: str) -> Dict[str, Any]:
        doc_id = self._validate_non_empty_string(doc_id, "Document ID")
        delivery_id = self._validate_non_empty_string(delivery_id, "Delivery ID")

        json_data = {"DocId": doc_id, "DeliveryId": delivery_id}
        return await self._make_request(
            "POST", "/public/api/v1.0/invoice8/getCourierTowns", json_data=json_data
        )

    async def get_courier_addresses(
        self, doc_id: str, delivery_id: str, town_id: str
    ) -> Dict[str, Any]:
        doc_id = self._validate_non_empty_string(doc_id, "Document ID")
        delivery_id = self._validate_non_empty_string(delivery_id, "Delivery ID")
        town_id = self._validate_non_empty_string(town_id, "Town ID")

        json_data = {"DocId": doc_id, "DeliveryId": delivery_id, "TownId": town_id}
        return await self._make_request(
            "POST", "/public/api/v1.0/invoice8/getCourierAddresses", json_data=json_data
        )

    async def set_courier_shipment(
        self,
        doc_id: str,
        delivery_type_id: str,
        service_type_id: str,
        town_id: str,
        address_id: str,
        contact_person_id: str,
        drop_shipping: bool = False,
        consignee: Optional[str] = None,
    ) -> Dict[str, Any]:
        doc_id = self._validate_non_empty_string(doc_id, "Document ID")
        delivery_type_id = self._validate_non_empty_string(
            delivery_type_id, "Delivery Type ID"
        )
        service_type_id = self._validate_non_empty_string(
            service_type_id, "Service Type ID"
        )
        town_id = self._validate_non_empty_string(town_id, "Town ID")
        address_id = self._validate_non_empty_string(address_id, "Address ID")
        contact_person_id = self._validate_non_empty_string(
            contact_person_id, "Contact Person ID"
        )

        json_data = {
            "DocId": doc_id,
            "DeliveryTypeId": delivery_type_id,
            "ServiceTypeId": service_type_id,
            "TownId": town_id,
            "AddressId": address_id,
            "ContactPersonId": contact_person_id,
            "DropShipping": drop_shipping,
        }

        if consignee:
            json_data["Consignee"] = consignee.strip()

        return await self._make_request(
            "POST", "/public/api/v1.0/invoice8/setCourierShipment", json_data=json_data
        )

    async def get_consignee_by_okpo(self, okpo: str, phone: str) -> Dict[str, Any]:
        okpo = self._validate_non_empty_string(okpo, "OKPO")
        phone = self._validate_non_empty_string(phone, "Phone")

        json_data = {"OKPO": okpo, "Phone": phone}
        return await self._make_request(
            "POST", "/public/api/v1.0/invoice8/getConsigneeByOkpo", json_data=json_data
        )

    async def get_basket_rests(self) -> Dict[str, Any]:
        return await self._make_request(
            "POST", "/public/api/v1.0/invoice8/getBasketRests"
        )

    async def get_rests(self, rests: List[int]) -> Dict[str, Any]:
        if not rests:
            raise OmegaAPIError(400, "Rests list cannot be empty")

        for i, rest in enumerate(rests):
            if not isinstance(rest, int):
                raise OmegaAPIError(400, f"Rest at index {i} must be an integer")

        json_data = {"Rests": rests}
        return await self._make_request(
            "POST", "/public/api/v1.0/invoice8/getRests", json_data=json_data
        )

    async def get_contract_sro(self) -> Dict[str, Any]:
        return await self._make_request(
            "POST", "/public/api/v1.0/invoice8/getContractSRO"
        )

    async def delete_item_from_invoice(
        self, doc_id: str, product_id: int
    ) -> Dict[str, Any]:
        doc_id = self._validate_non_empty_string(doc_id, "Document ID")
        if not isinstance(product_id, int):
            raise OmegaAPIError(400, "Product ID must be an integer")

        json_data = {"DocId": doc_id, "ProductId": product_id}
        return await self._make_request(
            "POST",
            "/public/api/v1.0/invoice8/deleteItemFromInvoice",
            json_data=json_data,
        )

    async def update_products_quantity(
        self, doc_id: str, products: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        doc_id = self._validate_non_empty_string(doc_id, "Document ID")

        if not products:
            raise OmegaAPIError(400, "Products list cannot be empty")

        for i, product in enumerate(products):
            if not isinstance(product, dict):
                raise OmegaAPIError(400, f"Product at index {i} must be a dictionary")
            if "ProductId" not in product:
                raise OmegaAPIError(
                    400, f"Product at index {i} must have 'ProductId' field"
                )
            if "Count" not in product:
                raise OmegaAPIError(
                    400, f"Product at index {i} must have 'Count' field"
                )

        json_data = {"DocId": doc_id, "Products": products}
        return await self._make_request(
            "POST",
            "/public/api/v1.0/invoice8/updateProductsQuantity",
            json_data=json_data,
        )

    async def delete_invoice(self, doc_id: str) -> Dict[str, Any]:
        doc_id = self._validate_non_empty_string(doc_id, "Document ID")

        json_data = {"DocId": doc_id}
        return await self._make_request(
            "POST", "/public/api/v1.0/invoice8/deleteInvoice", json_data=json_data
        )

    async def get_planned_delivery_address(self) -> Dict[str, Any]:
        return await self._make_request(
            "POST", "/public/api/v1.0/invoice8/getPlannedDeliveryAddress"
        )

    async def get_prices(self) -> Dict[str, Any]:
        return await self._make_request("POST", "/public/api/v1.0/price/getPrices")

    async def enqueue_price(self, price_id: int) -> Dict[str, Any]:
        if not isinstance(price_id, int):
            raise OmegaAPIError(400, "Price ID must be an integer")

        json_data = {"Id": price_id}
        return await self._make_request(
            "POST", "/public/api/v1.0/price/enqueuePrice", json_data=json_data
        )

    async def download_price(self, price_id: int) -> Dict[str, Any]:
        if not isinstance(price_id, int):
            raise OmegaAPIError(400, "Price ID must be an integer")

        json_data = {"Id": price_id}
        return await self._make_request(
            "POST", "/public/api/v1.0/price/downloadPrice", json_data=json_data
        )

    # Receivables endpoints
    async def get_receivables_data(self, date_to: str) -> Dict[str, Any]:
        date_to = self._validate_date_format(date_to, "DateTo")
        json_data = {"DateTo": date_to}
        return await self._make_request(
            "POST",
            "/public/api/v1.0/receivables/getReceivablesData",
            json_data=json_data,
        )

    # Search endpoints
    async def search_products(
        self,
        search_phrase: str,
        rest: int = 0,
        from_index: int = 0,
        count: int = 20,
    ) -> Dict[str, any]:
        search_phrase = self._validate_non_empty_string(search_phrase, "SearchPhrase")
        if not isinstance(rest, int) or rest < 0:
            raise OmegaAPIError(400, "Rest must be a non-negative integer")
        if not isinstance(from_index, int) or from_index < 0:
            raise OmegaAPIError(400, "From index must be a non-negative integer")
        if not isinstance(count, int) or count <= 0:
            raise OmegaAPIError(400, "Count must be a positive integer")

        json_data = {
            "SearchPhrase": search_phrase,
            "Rest": rest,
            "From": from_index,
            "Count": count,
        }
        return await self._make_request(
            "POST", "/public/api/v1.0/product/search", json_data=json_data
        )

    async def search_brand(
        self, code: str, brand: str, rest: int = 0
    ) -> Dict[str, Any]:
        code = self._validate_non_empty_string(code, "Code")
        brand = self._validate_non_empty_string(brand, "Brand")
        if not isinstance(rest, int) or rest < 0:
            raise OmegaAPIError(400, "Rest must be a non-negative integer")

        json_data = {"Code": code, "Brand": brand, "Rest": rest}
        return await self._make_request(
            "POST", "/public/api/v1.0/product/searchBrand", json_data=json_data
        )

    async def search_brand_by_id(
        self, code: str, brand_id: int, rest: int = 0
    ) -> Dict[str, Any]:
        code = self._validate_non_empty_string(code, "Code")
        if not isinstance(brand_id, int):
            raise OmegaAPIError(400, "Brand ID must be an integer")
        if not isinstance(rest, int) or rest < 0:
            raise OmegaAPIError(400, "Rest must be a non-negative integer")

        json_data = {"Code": code, "BrandId": brand_id, "Rest": rest}
        return await self._make_request(
            "POST", "/public/api/v1.0/product/searchBrandById", json_data=json_data
        )

    async def search_product_id_list(
        self, product_id_list: List[int]
    ) -> Dict[str, Any]:
        if not isinstance(product_id_list, list) or not product_id_list:
            raise OmegaAPIError(400, "Product ID list cannot be empty")

        for product_id in product_id_list:
            if not isinstance(product_id, int):
                raise OmegaAPIError(400, "All product IDs must be integers")

        json_data = {"ProductIdList": [str(pid) for pid in product_id_list]}
        return await self._make_request(
            "POST", "/public/api/v1.0/product/searchProductIdList", json_data=json_data
        )

    async def search_product_card_list(
        self, product_card_list: List[str]
    ) -> Dict[str, Any]:
        if not isinstance(product_card_list, list) or not product_card_list:
            raise OmegaAPIError(400, "Product card list cannot be empty")

        for card in product_card_list:
            if not isinstance(card, str) or not card.strip():
                raise OmegaAPIError(400, "All product cards must be non-empty strings")

        json_data = {"ProductCardList": product_card_list}
        return await self._make_request(
            "POST",
            "/public/api/v1.0/product/searchProductCardList",
            json_data=json_data,
        )

    async def get_product_details(self, product_id_list: List[int]) -> Dict[str, Any]:
        if not isinstance(product_id_list, list) or not product_id_list:
            raise OmegaAPIError(400, "Product ID list cannot be empty")

        for product_id in product_id_list:
            if not isinstance(product_id, int):
                raise OmegaAPIError(400, "All product IDs must be integers")

        json_data = {"ProductIdList": product_id_list}
        return await self._make_request(
            "POST", "/public/api/v1.0/product/details", json_data=json_data
        )

    async def get_images_info(self) -> Dict[str, Any]:
        return await self._make_request("POST", "/public/api/v1.0/product/imagesInfo")

    async def get_product_image(self, product_id: int, number: int) -> Dict[str, Any]:
        if not isinstance(product_id, int):
            raise OmegaAPIError(400, "Product ID must be an integer")
        if not isinstance(number, int) or number < 0:
            raise OmegaAPIError(400, "Number must be a non-negative integer")

        json_data = {"ProductId": product_id, "Number": number}
        return await self._make_request(
            "POST", "/public/api/v1.0/product/image", json_data=json_data
        )

    async def get_pricelist_paged(self, product_id: int, number: int) -> Dict[str, Any]:
        if not isinstance(product_id, int):
            raise OmegaAPIError(400, "Product ID must be an integer")
        if not isinstance(number, int) or number < 1:
            raise OmegaAPIError(400, "Number must be a positive integer")

        json_data = {"ProductId": product_id, "Number": number}
        return await self._make_request(
            "POST", "/public/api/v1.0/product/pricelist/paged", json_data=json_data
        )

    async def get_tecdoc_crosses(self, product_id: int) -> Dict[str, Any]:
        if not isinstance(product_id, int):
            raise OmegaAPIError(400, "Product ID must be an integer")

        json_data = {"ProductId": product_id}
        return await self._make_request(
            "POST", "/public/api/v1.0/product/getTecDocCrosses", json_data=json_data
        )

    async def get_all_crosses(self, product_id: int) -> Dict[str, Any]:
        if not isinstance(product_id, int):
            raise OmegaAPIError(400, "Product ID must be an integer")

        json_data = {"ProductId": product_id}
        return await self._make_request(
            "POST", "/public/api/v1.0/product/getAllCrosses", json_data=json_data
        )

    async def get_brands(
        self, page_index: int = 0, page_size: int = 100, rest: int = 0
    ) -> Dict[str, Any]:
        if not isinstance(page_index, int) or page_index < 0:
            raise OmegaAPIError(400, "Page index must be a non-negative integer")
        if not isinstance(page_size, int) or page_size <= 0:
            raise OmegaAPIError(400, "Page size must be a positive integer")
        if not isinstance(rest, int) or rest < 0:
            raise OmegaAPIError(400, "Rest must be a non-negative integer")

        json_data = {"PageIndex": page_index, "PageSize": page_size, "Rest": rest}
        return await self._make_request(
            "POST", "/public/api/v1.0/product/getBrands", json_data=json_data
        )

    async def get_lamps(
        self, filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        json_data = filters or {}
        return await self._make_request(
            "POST", "/public/api/v1.0/searchcatalog/getLamps", json_data=json_data
        )

    async def get_lamps_filters(self) -> Dict[str, Any]:
        return await self._make_request(
            "POST", "/public/api/v1.0/searchcatalog/getLampsFilters"
        )

    async def get_road_map(
        self, filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        json_data = filters or {}
        return await self._make_request(
            "POST", "/public/api/v1.0/searchcatalog/getRoadMap", json_data=json_data
        )

    async def get_bearings(
        self, filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        json_data = filters or {}
        return await self._make_request(
            "POST", "/public/api/v1.0/searchcatalog/getBearings", json_data=json_data
        )

    async def get_accessories(
        self, filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        json_data = filters or {}
        return await self._make_request(
            "POST", "/public/api/v1.0/searchcatalog/getAccessories", json_data=json_data
        )

    async def get_accessories_filters(self) -> Dict[str, Any]:
        return await self._make_request(
            "POST", "/public/api/v1.0/searchcatalog/getAccessoriesFilters"
        )

    async def get_garage_equipment(
        self, filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        json_data = filters or {}
        return await self._make_request(
            "POST",
            "/public/api/v1.0/searchcatalog/getGarageEquipment",
            json_data=json_data,
        )

    async def close(self) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None

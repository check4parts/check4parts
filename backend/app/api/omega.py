import logging
from typing import List, Optional, Dict, Any

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from app.adapters.omega_adapter import OmegaAdapter, OmegaAPIError

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/omega", tags=["omega"])


class BasketProductItem(BaseModel):
    product_id: int = Field(..., description="Product ID")
    count: int = Field(..., gt=0, description="Product count must be positive")


class AddProductRequest(BaseModel):
    product_id: int = Field(..., description="Product ID")
    count: int = Field(..., description="Product count (can be negative to reduce)")


class AddProductListRequest(BaseModel):
    product_list: List[BasketProductItem] = Field(
        ..., min_items=1, description="List of products to add"
    )


class RemoveProductRequest(BaseModel):
    product_id: int = Field(..., description="Product ID to remove")


class ClaimProductBase(BaseModel):
    product_id: str = Field(..., description="Product ID")
    doc_id: str = Field(..., description="Document ID")
    kind_id: str = Field(..., description="Kind of claim")
    text: Optional[str] = Field(None, description="Claim text")
    quantity: Optional[str] = Field(None, description="Quantity")
    sum_claim: Optional[float] = Field(None, ge=0, description="Claim sum")
    vin: Optional[str] = Field(None, description="VIN number for hidden defects")
    car_mark: Optional[str] = Field(None, description="Car mark for hidden defects")
    car_model: Optional[str] = Field(None, description="Car model for hidden defects")
    year_vehicle: Optional[int] = Field(
        None, ge=1000, le=9999, description="Vehicle year for hidden defects"
    )
    ready_for_discount: Optional[int] = Field(
        None, ge=0, le=1, description="Ready for discount (0 or 1)"
    )


class CreateClaimRequest(BaseModel):
    doc_id: str = Field(..., description="Document ID")
    comment: Optional[str] = Field(None, description="Claim comment")
    contact_id: Optional[str] = Field(None, description="Contact ID")
    phone_id: Optional[str] = Field(None, description="Phone ID")
    address_key: Optional[str] = Field(None, description="Address key")
    products: List[ClaimProductBase] = Field(
        ..., min_items=1, description="List of products for claim"
    )
    photos: Optional[List[str]] = Field(
        None, description="List of photo reference keys"
    )


class UploadPhotoRequest(BaseModel):
    product_id: Optional[str] = Field(None, description="Product ID")
    data: str = Field(..., description="Base64 encoded image data")
    file_name: str = Field(..., description="File name with .jpg extension")


class GetKindClaimsRequest(BaseModel):
    product_id: str = Field(..., description="Product ID")
    doc_id: str = Field(..., description="Document ID")


class CheckClaimKindRequest(BaseModel):
    doc_id: str = Field(..., description="Document ID")
    kind_id: str = Field(..., description="Kind ID")
    product_id: str = Field(..., description="Product ID")


class GetDiscountRequest(BaseModel):
    product_id: str = Field(..., description="Product ID")
    doc_id: str = Field(..., description="Document ID")
    type_id: str = Field(..., description="Type ID")


class GetAddressesRequest(BaseModel):
    kind: int = Field(..., description="Address kind")


class GetContactListRequest(BaseModel):
    customer_id: str = Field(..., description="Customer ID")


class AddContactRequest(BaseModel):
    customer_id: str = Field(..., description="Customer ID")
    first_name: str = Field(..., description="First name")
    second_name: str = Field(..., description="Second name")
    last_name: str = Field(..., description="Last name")
    phone: Optional[str] = Field(None, description="Phone number")


class EditContactRequest(BaseModel):
    contact_id: str = Field(..., description="Contact ID")
    first_name: str = Field(..., description="First name")
    second_name: str = Field(..., description="Second name")
    last_name: str = Field(..., description="Last name")


class RemoveContactRequest(BaseModel):
    contact_id: str = Field(..., description="Contact ID")


class AddContactPhoneRequest(BaseModel):
    contact_id: str = Field(..., description="Contact ID")
    phone: str = Field(..., description="Phone number")


class RemoveContactPhoneRequest(BaseModel):
    contact_id: str = Field(..., description="Contact ID")
    phone: str = Field(..., description="Phone number")


class GetContactDetailsRequest(BaseModel):
    contact_id: str = Field(..., description="Contact ID")


class GetExpenseDocumentRequest(BaseModel):
    doc_id: str = Field(..., description="Document ID")


class GetExpenseDocumentListRequest(BaseModel):
    start_date: str = Field(..., description="Start date in DD.MM.YYYY format")
    end_date: str = Field(..., description="End date in DD.MM.YYYY format")


class GetExpenseDocumentDetailsRequest(BaseModel):
    doc_id: str = Field(..., description="Document ID")


class ReserveInvoiceRequest(BaseModel):
    doc_id: str = Field(..., description="Document ID")


class CodInvoiceRequest(BaseModel):
    doc_id: str = Field(..., description="Document ID")
    summ_cod: str = Field(..., description="COD sum")


class ReadyInvoiceRequest(BaseModel):
    doc_id: str = Field(..., description="Document ID")


class AddProductToInvoiceRequest(BaseModel):
    doc_id: str = Field(..., description="Document ID")
    prod_id: int = Field(..., description="Product ID")
    count: int = Field(..., gt=0, description="Product count must be positive")


class MoveProductsFromBasketToInvoiceRequest(BaseModel):
    doc_id: str = Field(..., description="Document ID")


class GetInvoiceRequest(BaseModel):
    doc_id: str = Field(..., description="Document ID")


class SetInvoiceCustomerRequest(BaseModel):
    customer_id: str = Field(..., description="Customer ID")
    doc_id: str = Field(..., description="Document ID")


class GetContractsRequest(BaseModel):
    customer_id: str = Field(..., description="Customer ID")


class SetInvoiceContractRequest(BaseModel):
    contract_id: str = Field(..., description="Contract ID")
    doc_id: str = Field(..., description="Document ID")


class GetWarehousesRequest(BaseModel):
    customer_id: str = Field(..., description="Customer ID")
    shipment_type_id: Optional[str] = Field(None, description="Shipment type ID")
    delivery_address_id: Optional[str] = Field(None, description="Delivery address ID")


class SetInvoiceWarehouseRequest(BaseModel):
    warehouse_id: str = Field(..., description="Warehouse ID")
    doc_id: str = Field(..., description="Document ID")


class DocIdRequest(BaseModel):
    doc_id: str


class SetPlainShipmentRequest(BaseModel):
    doc_id: str
    address_id: str
    route_id: str


class CourierTownsRequest(BaseModel):
    doc_id: str
    delivery_id: str


class CourierAddressesRequest(BaseModel):
    doc_id: str
    delivery_id: str
    town_id: str


class SetCourierShipmentRequest(BaseModel):
    doc_id: str
    delivery_type_id: str
    service_type_id: str
    town_id: str
    address_id: str
    contact_person_id: str
    drop_shipping: bool = False
    consignee: Optional[str] = None


class ConsigneeByOkpoRequest(BaseModel):
    okpo: str
    phone: str


class GetRestsRequest(BaseModel):
    rests: List[int]


class DeleteItemFromInvoiceRequest(BaseModel):
    doc_id: str
    product_id: int


class UpdateProductsQuantityRequest(BaseModel):
    doc_id: str
    products: List[Dict[str, Any]]


class PriceRequest(BaseModel):
    price_id: int = Field(..., description="Price ID")


class ReceivablesRequest(BaseModel):
    date_to: str = Field(..., description="Date in DD.MM.YYYY format")


class SearchRequest(BaseModel):
    search_phrase: str = Field(..., description="Search phrase")
    rest: int = Field(0, ge=0, description="Rest filter")
    from_index: int = Field(0, ge=0, description="Starting index")
    count: int = Field(20, gt=0, description="Number of results")


class SearchBrandRequest(BaseModel):
    code: str = Field(..., description="Product code")
    brand: str = Field(..., description="Brand name")
    rest: int = Field(0, ge=0, description="Rest filter")


class SearchBrandByIdRequest(BaseModel):
    code: str = Field(..., description="Product code")
    brand_id: int = Field(..., description="Brand ID")
    rest: int = Field(0, ge=0, description="Rest filter")


class ProductIdListRequest(BaseModel):
    product_id_list: List[int] = Field(..., description="List of product IDs")


class ProductCardListRequest(BaseModel):
    product_card_list: List[str] = Field(..., description="List of product cards")


class ProductImageRequest(BaseModel):
    product_id: int = Field(..., description="Product ID")
    number: int = Field(..., ge=0, description="Image number")


class PricelistPagedRequest(BaseModel):
    product_id: int = Field(..., description="Product ID")
    number: int = Field(..., gt=0, description="Page number")


class ProductIdRequest(BaseModel):
    product_id: int = Field(..., description="Product ID")


class BrandsRequest(BaseModel):
    page_index: int = Field(0, ge=0, description="Page index")
    page_size: int = Field(100, gt=0, description="Page size")
    rest: int = Field(0, ge=0, description="Rest filter")


class FiltersRequest(BaseModel):
    filters: Optional[Dict[str, Any]] = Field(None, description="Optional filters")


async def handle_api_errors(func, *args, **kwargs):
    try:
        return await func(*args, **kwargs)
    except OmegaAPIError as e:
        logger.error(f"Omega API error: {e}")
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Unexpected error in Omega adapter: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/profile/account")
async def get_account():
    async with OmegaAdapter() as adapter:
        return await handle_api_errors(adapter.get_account)


@router.post("/basket/add-product")
async def add_product_to_basket(request: AddProductRequest):
    async with OmegaAdapter() as adapter:
        return await handle_api_errors(
            adapter.add_product_to_basket, request.product_id, request.count
        )


@router.post("/basket/add-product-list")
async def add_product_list_to_basket(request: AddProductListRequest):
    async with OmegaAdapter() as adapter:
        products_data = [
            {"ProductId": item.product_id, "Count": item.count}
            for item in request.product_list
        ]
        return await handle_api_errors(
            adapter.add_product_list_to_basket, products_data
        )


@router.post("/basket/remove-product")
async def remove_product_from_basket(request: RemoveProductRequest):
    async with OmegaAdapter() as adapter:
        return await handle_api_errors(
            adapter.remove_product_from_basket, request.product_id
        )


@router.post("/basket/get")
async def get_basket():
    async with OmegaAdapter() as adapter:
        return await handle_api_errors(adapter.get_basket)


@router.post("/basket/clear")
async def clear_basket():
    async with OmegaAdapter() as adapter:
        return await handle_api_errors(adapter.clear_basket)


@router.post("/claims/kind-claims")
async def get_kind_claims(request: GetKindClaimsRequest):
    async with OmegaAdapter() as adapter:
        return await handle_api_errors(
            adapter.get_kind_claims, request.product_id, request.doc_id
        )


@router.post("/claims/check-claim-kind")
async def check_claim_kind(request: CheckClaimKindRequest):
    async with OmegaAdapter() as adapter:
        return await handle_api_errors(
            adapter.check_claim_kind,
            request.doc_id,
            request.kind_id,
            request.product_id,
        )


@router.post("/claims/discount")
async def get_discount(request: GetDiscountRequest):
    async with OmegaAdapter() as adapter:
        return await handle_api_errors(
            adapter.get_discount, request.product_id, request.doc_id, request.type_id
        )


@router.post("/claims/contacts")
async def get_contacts():
    async with OmegaAdapter() as adapter:
        return await handle_api_errors(adapter.get_contacts)


@router.post("/claims/upload-photo")
async def upload_photo(request: UploadPhotoRequest):
    async with OmegaAdapter() as adapter:
        return await handle_api_errors(
            adapter.upload_photo, request.product_id, request.data, request.file_name
        )


@router.post("/claims/addresses")
async def get_addresses(request: GetAddressesRequest):
    async with OmegaAdapter() as adapter:
        return await handle_api_errors(adapter.get_addresses, request.kind)


@router.post("/claims/create")
async def create_claim(request: CreateClaimRequest):
    async with OmegaAdapter() as adapter:
        products_data = []
        for product in request.products:
            product_dict = {
                "ProductId": product.product_id,
                "DocId": product.doc_id,
                "KindId": product.kind_id,
            }

            if product.text:
                product_dict["Text"] = product.text
            if product.quantity:
                product_dict["Quantity"] = product.quantity
            if product.sum_claim is not None:
                product_dict["SumClaim"] = product.sum_claim

            if product.vin:
                product_dict["Vin"] = product.vin
            if product.car_mark:
                product_dict["CarMark"] = product.car_mark
            if product.car_model:
                product_dict["CarModel"] = product.car_model
            if product.year_vehicle:
                product_dict["YearVehicle"] = product.year_vehicle
            if product.ready_for_discount is not None:
                product_dict["ReadyForDiscount"] = product.ready_for_discount

            products_data.append(product_dict)

        return await handle_api_errors(
            adapter.create_claim,
            request.doc_id,
            products_data,
            request.comment,
            request.contact_id,
            request.phone_id,
            request.address_key,
            request.photos,
        )


@router.post("/claims/list")
async def get_claims_list():
    async with OmegaAdapter() as adapter:
        return await handle_api_errors(adapter.get_claims_list)


@router.post("/claims/download-refund-documents")
async def download_refund_documents():
    async with OmegaAdapter() as adapter:
        return await handle_api_errors(adapter.download_refund_documents)


# Contact endpoints
@router.post("/contact/get-contacts")
async def get_contact_list(request: GetContactListRequest):
    async with OmegaAdapter() as adapter:
        return await handle_api_errors(adapter.get_contact_list, request.customer_id)


@router.post("/contact/add-contact")
async def add_contact(request: AddContactRequest):
    async with OmegaAdapter() as adapter:
        return await handle_api_errors(
            adapter.add_contact,
            request.customer_id,
            request.first_name,
            request.second_name,
            request.last_name,
            request.phone,
        )


@router.post("/contact/edit-contact")
async def edit_contact(request: EditContactRequest):
    async with OmegaAdapter() as adapter:
        return await handle_api_errors(
            adapter.edit_contact,
            request.contact_id,
            request.first_name,
            request.second_name,
            request.last_name,
        )


@router.post("/contact/remove-contact")
async def remove_contact(request: RemoveContactRequest):
    async with OmegaAdapter() as adapter:
        return await handle_api_errors(adapter.remove_contact, request.contact_id)


@router.post("/contact/add-contact-phone")
async def add_contact_phone(request: AddContactPhoneRequest):
    async with OmegaAdapter() as adapter:
        return await handle_api_errors(
            adapter.add_contact_phone, request.contact_id, request.phone
        )


@router.post("/contact/remove-contact-phone")
async def remove_contact_phone(request: RemoveContactPhoneRequest):
    async with OmegaAdapter() as adapter:
        return await handle_api_errors(
            adapter.remove_contact_phone, request.contact_id, request.phone
        )


@router.post("/contact/get-contact-details")
async def get_contact_details(request: GetContactDetailsRequest):
    async with OmegaAdapter() as adapter:
        return await handle_api_errors(adapter.get_contact_details, request.contact_id)


# Expense document endpoints
@router.post("/expense/get-expense-document")
async def get_expense_document(request: GetExpenseDocumentRequest):
    async with OmegaAdapter() as adapter:
        return await handle_api_errors(adapter.get_expense_document, request.doc_id)


@router.post("/expense/get-expense-document-list")
async def get_expense_document_list(request: GetExpenseDocumentListRequest):
    async with OmegaAdapter() as adapter:
        return await handle_api_errors(
            adapter.get_expense_document_list, request.start_date, request.end_date
        )


@router.post("/expense/get-expense-document-details")
async def get_expense_document_details(request: GetExpenseDocumentDetailsRequest):
    async with OmegaAdapter() as adapter:
        return await handle_api_errors(
            adapter.get_expense_document_details, request.doc_id
        )


@router.get("/basket/add-product")
async def add_product_to_basket_query(
    product_id: int = Query(..., description="Product ID"),
    count: int = Query(..., gt=0, description="Product count must be positive"),
):
    async with OmegaAdapter() as adapter:
        return await handle_api_errors(adapter.add_product_to_basket, product_id, count)


@router.get("/basket/remove-product")
async def remove_product_from_basket_query(
    product_id: int = Query(..., description="Product ID to remove"),
):
    async with OmegaAdapter() as adapter:
        return await handle_api_errors(adapter.remove_product_from_basket, product_id)


@router.get("/claims/kind-claims")
async def get_kind_claims_query(
    product_id: str = Query(..., description="Product ID"),
    doc_id: str = Query(..., description="Document ID"),
):
    async with OmegaAdapter() as adapter:
        return await handle_api_errors(adapter.get_kind_claims, product_id, doc_id)


@router.get("/claims/discount")
async def get_discount_query(
    product_id: str = Query(..., description="Product ID"),
    doc_id: str = Query(..., description="Document ID"),
    type_id: str = Query(..., description="Type ID"),
):
    async with OmegaAdapter() as adapter:
        return await handle_api_errors(
            adapter.get_discount, product_id, doc_id, type_id
        )


@router.get("/claims/addresses")
async def get_addresses_query(
    kind: int = Query(..., description="Address kind"),
):
    async with OmegaAdapter() as adapter:
        return await handle_api_errors(adapter.get_addresses, kind)


@router.get("/contact/get-contacts")
async def get_contact_list_query(
    customer_id: str = Query(..., description="Customer ID"),
):
    async with OmegaAdapter() as adapter:
        return await handle_api_errors(adapter.get_contact_list, customer_id)


@router.get("/contact/get-contact-details")
async def get_contact_details_query(
    contact_id: str = Query(..., description="Contact ID"),
):
    async with OmegaAdapter() as adapter:
        return await handle_api_errors(adapter.get_contact_details, contact_id)


@router.get("/expense/get-expense-document")
async def get_expense_document_query(
    doc_id: str = Query(..., description="Document ID"),
):
    async with OmegaAdapter() as adapter:
        return await handle_api_errors(adapter.get_expense_document, doc_id)


@router.get("/expense/get-expense-document-list")
async def get_expense_document_list_query(
    start_date: str = Query(..., description="Start date in DD.MM.YYYY format"),
    end_date: str = Query(..., description="End date in DD.MM.YYYY format"),
):
    async with OmegaAdapter() as adapter:
        return await handle_api_errors(
            adapter.get_expense_document_list, start_date, end_date
        )


@router.get("/expense/get-expense-document-details")
async def get_expense_document_details_query(
    doc_id: str = Query(..., description="Document ID"),
):
    async with OmegaAdapter() as adapter:
        return await handle_api_errors(adapter.get_expense_document_details, doc_id)


@router.post("/invoice/add")
async def add_invoice():
    async with OmegaAdapter() as adapter:
        return await handle_api_errors(adapter.add_invoice)


@router.post("/invoice/reserve")
async def reserve_invoice(request: ReserveInvoiceRequest):
    async with OmegaAdapter() as adapter:
        return await handle_api_errors(adapter.reserve_invoice, request.doc_id)


@router.post("/invoice/cod")
async def cod_invoice(request: CodInvoiceRequest):
    async with OmegaAdapter() as adapter:
        return await handle_api_errors(
            adapter.cod_invoice, request.doc_id, request.summ_cod
        )


@router.post("/invoice/ready")
async def ready_invoice(request: ReadyInvoiceRequest):
    async with OmegaAdapter() as adapter:
        return await handle_api_errors(adapter.ready_invoice, request.doc_id)


@router.post("/invoice/add-product")
async def add_product_to_invoice(request: AddProductToInvoiceRequest):
    async with OmegaAdapter() as adapter:
        return await handle_api_errors(
            adapter.add_product_to_invoice,
            request.doc_id,
            request.prod_id,
            request.count,
        )


@router.post("/invoice/move-products-from-basket")
async def move_products_from_basket_to_invoice(
    request: MoveProductsFromBasketToInvoiceRequest,
):
    async with OmegaAdapter() as adapter:
        return await handle_api_errors(
            adapter.move_products_from_basket_to_invoice, request.doc_id
        )


@router.post("/invoice/list")
async def get_invoice_list():
    async with OmegaAdapter() as adapter:
        return await handle_api_errors(adapter.get_invoice_list)


@router.post("/invoice/get")
async def get_invoice(request: GetInvoiceRequest):
    async with OmegaAdapter() as adapter:
        return await handle_api_errors(adapter.get_invoice, request.doc_id)


@router.post("/invoice/customers")
async def get_customers():
    async with OmegaAdapter() as adapter:
        return await handle_api_errors(adapter.get_customers)


@router.post("/invoice/set-customer")
async def set_invoice_customer(request: SetInvoiceCustomerRequest):
    async with OmegaAdapter() as adapter:
        return await handle_api_errors(
            adapter.set_invoice_customer, request.customer_id, request.doc_id
        )


@router.post("/invoice/contracts")
async def get_contracts(request: GetContractsRequest):
    async with OmegaAdapter() as adapter:
        return await handle_api_errors(adapter.get_contracts, request.customer_id)


@router.post("/invoice/set-contract")
async def set_invoice_contract(request: SetInvoiceContractRequest):
    async with OmegaAdapter() as adapter:
        return await handle_api_errors(
            adapter.set_invoice_contract, request.contract_id, request.doc_id
        )


@router.post("/invoice/warehouses")
async def get_warehouses(request: GetWarehousesRequest):
    async with OmegaAdapter() as adapter:
        return await handle_api_errors(
            adapter.get_warehouses,
            request.customer_id,
            request.shipment_type_id,
            request.delivery_address_id,
        )


@router.post("/invoice/set-warehouse")
async def set_invoice_warehouse(request: SetInvoiceWarehouseRequest):
    async with OmegaAdapter() as adapter:
        return await handle_api_errors(
            adapter.set_invoice_warehouse, request.warehouse_id, request.doc_id
        )


@router.post("/invoice8/shipment-types")
async def get_shipment_types():
    async with OmegaAdapter() as adapter:
        return await handle_api_errors(adapter.get_shipment_types)


@router.post("/invoice8/plain-settings")
async def get_plain_settings():
    async with OmegaAdapter() as adapter:
        return await handle_api_errors(adapter.get_plain_settings)


@router.post("/invoice8/set-plain-shipment")
async def set_plain_shipment(request: SetPlainShipmentRequest):
    async with OmegaAdapter() as adapter:
        return await handle_api_errors(
            adapter.set_plain_shipment,
            request.doc_id,
            request.address_id,
            request.route_id,
        )


@router.post("/invoice8/self-delivery-settings")
async def get_self_delivery_settings(request: DocIdRequest):
    async with OmegaAdapter() as adapter:
        return await handle_api_errors(
            adapter.get_self_delivery_settings, request.doc_id
        )


@router.post("/invoice8/set-self-delivery-shipment")
async def set_self_delivery_shipment(request: DocIdRequest):
    async with OmegaAdapter() as adapter:
        return await handle_api_errors(
            adapter.set_self_delivery_shipment, request.doc_id
        )


@router.post("/invoice8/courier-delivery-settings")
async def get_courier_delivery_settings(request: DocIdRequest):
    async with OmegaAdapter() as adapter:
        return await handle_api_errors(
            adapter.get_courier_delivery_settings, request.doc_id
        )


@router.post("/invoice8/courier-towns")
async def get_courier_towns(request: CourierTownsRequest):
    async with OmegaAdapter() as adapter:
        return await handle_api_errors(
            adapter.get_courier_towns, request.doc_id, request.delivery_id
        )


@router.post("/invoice8/courier-addresses")
async def get_courier_addresses(request: CourierAddressesRequest):
    async with OmegaAdapter() as adapter:
        return await handle_api_errors(
            adapter.get_courier_addresses,
            request.doc_id,
            request.delivery_id,
            request.town_id,
        )


@router.post("/invoice8/set-courier-shipment")
async def set_courier_shipment(request: SetCourierShipmentRequest):
    async with OmegaAdapter() as adapter:
        return await handle_api_errors(
            adapter.set_courier_shipment,
            request.doc_id,
            request.delivery_type_id,
            request.service_type_id,
            request.town_id,
            request.address_id,
            request.contact_person_id,
            request.drop_shipping,
            request.consignee,
        )


@router.post("/invoice8/consignee-by-okpo")
async def get_consignee_by_okpo(request: ConsigneeByOkpoRequest):
    async with OmegaAdapter() as adapter:
        return await handle_api_errors(
            adapter.get_consignee_by_okpo, request.okpo, request.phone
        )


@router.post("/invoice8/basket-rests")
async def get_basket_rests():
    async with OmegaAdapter() as adapter:
        return await handle_api_errors(adapter.get_basket_rests)


@router.post("/invoice8/rests")
async def get_rests(request: GetRestsRequest):
    async with OmegaAdapter() as adapter:
        return await handle_api_errors(adapter.get_rests, request.rests)


@router.post("/invoice8/contract-sro")
async def get_contract_sro():
    async with OmegaAdapter() as adapter:
        return await handle_api_errors(adapter.get_contract_sro)


@router.post("/invoice8/delete-item")
async def delete_item_from_invoice(request: DeleteItemFromInvoiceRequest):
    async with OmegaAdapter() as adapter:
        return await handle_api_errors(
            adapter.delete_item_from_invoice, request.doc_id, request.product_id
        )


@router.post("/invoice8/update-products-quantity")
async def update_products_quantity(request: UpdateProductsQuantityRequest):
    async with OmegaAdapter() as adapter:
        return await handle_api_errors(
            adapter.update_products_quantity, request.doc_id, request.products
        )


@router.post("/invoice8/delete-invoice")
async def delete_invoice(request: DocIdRequest):
    async with OmegaAdapter() as adapter:
        return await handle_api_errors(adapter.delete_invoice, request.doc_id)


@router.post("/invoice8/planned-delivery-address")
async def get_planned_delivery_address():
    async with OmegaAdapter() as adapter:
        return await handle_api_errors(adapter.get_planned_delivery_address)


@router.post("/price/list")
async def get_prices() -> Dict[str, Any]:
    async with OmegaAdapter() as adapter:
        return await handle_api_errors(adapter.get_prices)


@router.post("/price/enqueue")
async def enqueue_price(request: PriceRequest) -> Dict[str, Any]:
    async with OmegaAdapter() as adapter:
        return await handle_api_errors(adapter.enqueue_price, request.price_id)


@router.post("/price/download")
async def download_price(request: PriceRequest) -> Dict[str, Any]:
    async with OmegaAdapter() as adapter:
        return await handle_api_errors(adapter.download_price, request.price_id)


# Receivables endpoints
@router.post("/receivables/data")
async def get_receivables_data(request: ReceivablesRequest) -> Dict[str, Any]:
    async with OmegaAdapter() as adapter:
        return await handle_api_errors(adapter.get_receivables_data, request.date_to)


# Search endpoints
@router.post("/search/products")
async def search_products(request: SearchRequest) -> Dict[str, Any]:
    async with OmegaAdapter() as adapter:
        return await handle_api_errors(
            adapter.search_products,
            request.search_phrase,
            request.rest,
            request.from_index,
            request.count,
        )


@router.post("/product/search-brand")
async def search_brand(request: SearchBrandRequest) -> Dict[str, Any]:
    async with OmegaAdapter() as adapter:
        return await handle_api_errors(
            adapter.search_brand, request.code, request.brand, request.rest
        )


@router.post("/product/search-brand-by-id")
async def search_brand_by_id(request: SearchBrandByIdRequest) -> Dict[str, Any]:
    async with OmegaAdapter() as adapter:
        return await handle_api_errors(
            adapter.search_brand_by_id, request.code, request.brand_id, request.rest
        )


@router.post("/product/search-product-id-list")
async def search_product_id_list(request: ProductIdListRequest) -> Dict[str, Any]:
    async with OmegaAdapter() as adapter:
        return await handle_api_errors(
            adapter.search_product_id_list, request.product_id_list
        )


@router.post("/product/search-product-card-list")
async def search_product_card_list(request: ProductCardListRequest) -> Dict[str, Any]:
    async with OmegaAdapter() as adapter:
        return await handle_api_errors(
            adapter.search_product_card_list, request.product_card_list
        )


# Product endpoints
@router.post("/product/details")
async def get_product_details(request: ProductIdListRequest) -> Dict[str, Any]:
    async with OmegaAdapter() as adapter:
        return await handle_api_errors(
            adapter.get_product_details, request.product_id_list
        )


@router.post("/product/images-info")
async def get_images_info() -> Dict[str, Any]:
    async with OmegaAdapter() as adapter:
        return await handle_api_errors(adapter.get_images_info)


@router.post("/product/image")
async def get_product_image(request: ProductImageRequest) -> Dict[str, Any]:
    async with OmegaAdapter() as adapter:
        return await handle_api_errors(
            adapter.get_product_image, request.product_id, request.number
        )


@router.post("/product/pricelist-paged")
async def get_pricelist_paged(request: PricelistPagedRequest) -> Dict[str, Any]:
    async with OmegaAdapter() as adapter:
        return await handle_api_errors(
            adapter.get_pricelist_paged, request.product_id, request.number
        )


@router.post("/product/tecdoc-crosses")
async def get_tecdoc_crosses(request: ProductIdRequest) -> Dict[str, Any]:
    async with OmegaAdapter() as adapter:
        return await handle_api_errors(adapter.get_tecdoc_crosses, request.product_id)


@router.post("/product/all-crosses")
async def get_all_crosses(request: ProductIdRequest) -> Dict[str, Any]:
    async with OmegaAdapter() as adapter:
        return await handle_api_errors(adapter.get_all_crosses, request.product_id)


@router.post("/product/brands")
async def get_brands(request: BrandsRequest) -> Dict[str, Any]:
    async with OmegaAdapter() as adapter:
        return await handle_api_errors(
            adapter.get_brands, request.page_index, request.page_size, request.rest
        )


@router.post("/searchcatalog/lamps")
async def get_lamps(request: FiltersRequest):
    async with OmegaAdapter() as adapter:
        return await handle_api_errors(adapter.get_lamps, request.filters)


@router.post("/searchcatalog/lamps-filters")
async def get_lamps_filters():
    async with OmegaAdapter() as adapter:
        return await handle_api_errors(adapter.get_lamps_filters)


@router.post("/searchcatalog/road-map")
async def get_road_map(request: FiltersRequest):
    async with OmegaAdapter() as adapter:
        return await handle_api_errors(adapter.get_road_map, request.filters)


@router.post("/searchcatalog/bearings")
async def get_bearings(request: FiltersRequest):
    async with OmegaAdapter() as adapter:
        return await handle_api_errors(adapter.get_bearings, request.filters)


@router.post("/searchcatalog/accessories")
async def get_accessories(request: FiltersRequest):
    async with OmegaAdapter() as adapter:
        return await handle_api_errors(adapter.get_accessories, request.filters)


@router.post("/searchcatalog/accessories-filters")
async def get_accessories_filters():
    async with OmegaAdapter() as adapter:
        return await handle_api_errors(adapter.get_accessories_filters)


@router.post("/searchcatalog/garage-equipment")
async def get_garage_equipment(request: FiltersRequest):
    async with OmegaAdapter() as adapter:
        return await handle_api_errors(adapter.get_garage_equipment, request.filters)

from typing import List, Optional

from fastapi import APIRouter, Query
from pydantic import BaseModel

from app.adapters.intercars_adapter import IntercarsAdapter

router = APIRouter()


class InventoryLine(BaseModel):
    sku: str
    quantity: int


class InventoryQuoteRequest(BaseModel):
    lines: List[InventoryLine]


class InventoryStockRequest(BaseModel):
    skus: List[str]
    location: str


class DeliverySearchRequest(BaseModel):
    creation_date_from: str
    creation_date_to: str
    offset: int = 1
    limit: int = 20


class RequisitionLine(BaseModel):
    sku: str
    requiredQuantity: int
    unitPriceNet: float
    unitPriceGross: float


class SubmitRequisitionRequest(BaseModel):
    lines: List[RequisitionLine]
    customNumber: Optional[str] = None
    deliveryMethod: Optional[str] = None
    shipTo: Optional[str] = None
    deferredPayment: Optional[bool] = None
    comments: Optional[str] = None


class CancelRequisitionRequest(BaseModel):
    requisition_id: str
    ship_to: str = None


class CalculateItemPriceRequest(BaseModel):
    lines: List[InventoryLine]


@router.post("/intercars/authorize/")
async def authorize(client_id: str, client_secret: str):
    adapter = IntercarsAdapter()
    return await adapter.authorize(client_id, client_secret)


@router.post("/intercars/inventory/quote/")
async def inventory_quote(request: InventoryQuoteRequest):
    adapter = IntercarsAdapter()
    return await adapter.inventory_quote([line.dict() for line in request.lines])


@router.get("/intercars/inventory/stock/")
async def get_stock_balance(
    sku: List[str] = Query(...),
    location: Optional[List[str]] = Query(None),
    ship_to: Optional[str] = Query(None),
):
    adapter = IntercarsAdapter()
    return await adapter.get_stock_balance(
        skus=sku, locations=location, ship_to=ship_to
    )


@router.post("/intercars/inventory/stock/")
async def inventory_stock(request: InventoryStockRequest):
    adapter = IntercarsAdapter()
    response = await adapter.inventory_stock(request.skus, request.location)
    return response


@router.get("/intercars/delivery/search/")
async def search_deliveries(request: DeliverySearchRequest):
    adapter = IntercarsAdapter()
    deliveries = await adapter.search_deliveries(
        creation_date_from=request.creation_date_from,
        creation_date_to=request.creation_date_to,
        offset=request.offset,
        limit=request.limit,
    )
    return deliveries


@router.get("/intercars/delivery/{delivery_id}")
async def get_delivery(delivery_id: str):
    adapter = IntercarsAdapter()
    delivery_details = await adapter.get_delivery(delivery_id)
    return delivery_details


@router.post("/intercars/invoice")
async def search_invoice(request: DeliverySearchRequest):
    adapter = IntercarsAdapter()
    invoices = await adapter.search_invoice(
        creation_date_from=request.creation_date_from,
        creation_date_to=request.creation_date_to,
        offset=request.offset,
        limit=request.limit,
    )
    return invoices


@router.get("/intercars/invoice/{invoice_id}")
async def get_invoice(invoice_id: str):
    adapter = IntercarsAdapter()
    return await adapter.get_invoice(invoice_id)


@router.get("/intercars/requisition/{requisition_id}")
async def get_requisition(requisition_id: str):
    adapter = IntercarsAdapter()
    return await adapter.get_requisition(requisition_id)


@router.post("/intercars/sales/requisition/")
async def submit_requisition(request: SubmitRequisitionRequest):
    adapter = IntercarsAdapter()
    requisition_payload = request.dict(exclude_none=True)
    return await adapter.submit_requisition(requisition_payload)


@router.post("/intercars/requisition/cancel/")
async def cancel_requisition(request: CancelRequisitionRequest):
    adapter = IntercarsAdapter()
    return await adapter.cancel_requisition(request.requisition_id, request.ship_to)


@router.get("/intercars/sales/requisition")
async def search_order(request: DeliverySearchRequest):
    adapter = IntercarsAdapter()
    return await adapter.search_order(
        creation_date_from=request.creation_date_from,
        creation_date_to=request.creation_date_to,
        offset=request.offset,
        limit=request.limit,
    )


@router.get("/intercars/sales/order/{order_id}")
async def get_order(order_id: str):
    adapter = IntercarsAdapter()
    return await adapter.get_order(order_id)


@router.get("/intercars/customer/")
async def get_customer():
    adapter = IntercarsAdapter()
    return await adapter.customer()


@router.get("/intercars/customer/finances/")
async def get_customer_finances():
    adapter = IntercarsAdapter()
    return await adapter.customer_finances()


@router.post("/intercars/pricing/quote/")
async def calculate_item_price(request: CalculateItemPriceRequest):
    adapter = IntercarsAdapter()
    return await adapter.calculate_item_price([line.dict() for line in request.lines])

import io
import logging
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel, Field
from starlette.responses import StreamingResponse

from app.adapters.uniqtrade_adapter import UniqTradeAdapter, UniqTradeAPIError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/uniqtrade", tags=["uniqtrade"])


class SearchRequest(BaseModel):
    oem: str
    brand: Optional[str] = None
    include_info: bool = False
    language: str = "ua"


class BatchSearchItem(BaseModel):
    id: Optional[int] = None
    oem: Optional[str] = None
    brand: Optional[str] = None


class BatchSearchRequest(BaseModel):
    details: List[BatchSearchItem]
    language: str = "ua"


class DeliveryOptionsRequest(BaseModel):
    date: str = Field(..., description="Delivery date in YYYY-MM-DD format")
    point_id: int = Field(..., description="Delivery point ID")
    transporter_id: int = Field(..., description="Transporter ID")
    storage_ids: List[int] = Field(..., description="List of storage IDs")
    language: str = Field("ua", description="Response language (ua/ru)")


class OrderItem(BaseModel):
    detail: int = Field(..., description="Product ID")
    quantity: int = Field(..., gt=0, description="Quantity")
    storage: int = Field(..., description="Storage ID")


class OrderRequest(BaseModel):
    comment: Optional[str] = Field(None, description="Order comment")
    delivery: int = Field(..., description="Delivery option ID")
    deliveryDate: str = Field(..., description="Delivery date in YYYY-MM-DD format")
    deliveryPoint: int = Field(..., description="Delivery point ID")
    items: List[OrderItem] = Field(..., min_items=1, description="List of order items")
    paymentType: str = Field(
        ..., pattern="^(nal|beznal)$", description="Payment type: nal or beznal"
    )
    withoutDocument: bool = Field(False, description="Order without document")


class CreateOrderRequest(BaseModel):
    orders: List[OrderRequest] = Field(..., min_items=1, description="List of orders")
    language: str = Field("ua", description="Response language (ua/ru)")


class OrderListRequest(BaseModel):
    start_date: str = Field(..., description="Start date in YYYY-MM-DD format")
    page: Optional[int] = Field(None, gt=0, description="Page number")
    limit: Optional[int] = Field(
        None, gt=0, le=100, description="Items per page (max 100)"
    )
    mode: str = Field("period", description="Search mode")
    detail_id: Optional[int] = Field(None, description="Filter by specific detail ID")
    language: str = Field("ua", description="Response language (ua/ru)")


class PricelistExportRequest(BaseModel):
    format: str = Field(..., description="Export format (xlsx, txt, csv)")
    visible_brands_id: Optional[List[int]] = Field(
        None, description="List of brand IDs"
    )
    categories_id: Optional[List[int]] = Field(None, description="List of category IDs")
    models_id: Optional[List[str]] = Field(None, description="List of model names")
    in_stock: bool = Field(True, description="Include only items in stock")
    show_scancode: bool = Field(False, description="Include barcode field")
    utr_article: bool = Field(False, description="Include UniqTrade article field")
    language: str = Field("ua", description="Response language (ua/ru)")


class AddToCartRequest(BaseModel):
    detail_id: int = Field(..., description="Product detail ID")
    quantity: int = Field(..., gt=0, description="Quantity to add")
    language: str = Field("ua", description="Response language (ua/ru)")


async def handle_api_errors(func, *args, **kwargs):
    """Helper function to handle API errors consistently"""
    try:
        result = await func(*args, **kwargs)
        return {"success": True, "data": result}
    except UniqTradeAPIError as e:
        logger.error(f"UniqTrade API error: {e}")
        return {
            "success": False,
            "error": {
                "code": e.status_code,
                "message": e.message,
                "details": e.details,
            },
        }
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return {
            "success": False,
            "error": {
                "code": 500,
                "message": "Internal server error",
                "details": {"exception": str(e)},
            },
        }


@router.get("/search/products/{oem}")
async def search_by_oem(
    oem: str,
    info: Optional[int] = Query(
        None, description="Include additional info (1 for yes)"
    ),
    language: str = Query("ua", description="Response language (ua/ru)"),
):
    """
    Search for auto parts by OEM/article number

    Args:
        oem: Part article/OEM number
        info: Include additional information like images (1 or 0)
        language: Response language ('ua' or 'ru')
    """
    async with UniqTradeAdapter() as adapter:
        include_info = info == 1 if info is not None else False
        return await handle_api_errors(
            adapter.search_by_oem, oem, include_info, language
        )


@router.post("/search/products")
async def search_parts(request: SearchRequest):
    """
    Search for auto parts with flexible parameters

    Body:
        oem: Part article/OEM number (required)
        brand: Brand name or external code (optional)
        include_info: Include additional information like images
        language: Response language ('ua' or 'ru')
    """
    async with UniqTradeAdapter() as adapter:
        if request.brand:
            return await handle_api_errors(
                adapter.search_by_oem_and_brand,
                request.oem,
                request.brand,
                request.include_info,
                request.language,
            )
        else:
            return await handle_api_errors(
                adapter.search_by_oem,
                request.oem,
                request.include_info,
                request.language,
            )


@router.get("/search/products/{oem}/brand/{brand}")
async def search_by_oem_and_brand(
    oem: str,
    brand: str,
    info: Optional[int] = Query(
        None, description="Include additional info (1 for yes)"
    ),
    language: str = Query("ua", description="Response language (ua/ru)"),
):
    """
    Search for auto parts by OEM/article number and brand

    Args:
        oem: Part article/OEM number
        brand: Brand name or external code
        info: Include additional information like images (1 or 0)
        language: Response language ('ua' or 'ru')
    """
    async with UniqTradeAdapter() as adapter:
        include_info = info == 1 if info is not None else False
        return await handle_api_errors(
            adapter.search_by_oem_and_brand, oem, brand, include_info, language
        )


@router.get("/detail/{detail_id}/applicability")
async def get_detail_applicability(
    detail_id: int, language: str = Query("ua", description="Response language (ua/ru)")
):
    """
    Get part applicability information by detail ID

    Args:
        detail_id: Detail ID from search results
        language: Response language ('ua' or 'ru')
    """
    async with UniqTradeAdapter() as adapter:
        return await handle_api_errors(
            adapter.get_detail_applicability, detail_id, language
        )


@router.get("/detail/{detail_id}")
async def get_detail_info(
    detail_id: int, language: str = Query("ua", description="Response language (ua/ru)")
):
    """
    Get detailed information about a part by detail ID

    Args:
        detail_id: Detail ID from search results
        language: Response language ('ua' or 'ru')
    """
    async with UniqTradeAdapter() as adapter:
        return await handle_api_errors(adapter.get_detail_info, detail_id, language)


@router.get("/detail/{detail_id}/characteristics")
async def get_detail_characteristics(
    detail_id: int, language: str = Query("ua", description="Response language (ua/ru)")
):
    """
    Get part characteristics by detail ID

    Args:
        detail_id: Detail ID from search results
        language: Response language ('ua' or 'ru')
    """
    async with UniqTradeAdapter() as adapter:
        return await handle_api_errors(
            adapter.get_detail_characteristics, detail_id, language
        )


@router.post("/search/batch")
async def batch_search(request: BatchSearchRequest):
    """
    Batch search for multiple parts in a single request

    Body:
        details: List of search items, each containing either:
                 - {"id": detail_id} for search by internal ID
                 - {"oem": "article", "brand": "brand_name"} for search by OEM+brand
        language: Response language ('ua' or 'ru')
    """
    async with UniqTradeAdapter() as adapter:
        search_items = []
        for item in request.details:
            search_dict = {}
            if item.id is not None:
                search_dict["id"] = item.id
            if item.oem is not None:
                search_dict["oem"] = item.oem
            if item.brand is not None:
                search_dict["brand"] = item.brand
            search_items.append(search_dict)

        return await handle_api_errors(
            adapter.batch_search, search_items, request.language
        )


@router.get("/analogs/{brand}/{oem}")
async def search_analogs(
    brand: str,
    oem: str,
    language: str = Query("ua", description="Response language (ua/ru)"),
):
    """
    Search for part analogs by brand and OEM

    Args:
        brand: Brand name
        oem: Part article/OEM number
        language: Response language ('ua' or 'ru')
    """
    async with UniqTradeAdapter() as adapter:
        return await handle_api_errors(adapter.search_analogs, brand, oem, language)


@router.get("/delivery-points")
async def get_delivery_points(
    language: str = Query("ua", description="Response language (ua/ru)")
):
    """
    Get list of available delivery points

    Args:
        language: Response language ('ua' or 'ru')
    """
    async with UniqTradeAdapter() as adapter:
        return await handle_api_errors(adapter.get_delivery_points, language)


@router.get("/transporters/{date}/{point_id}")
async def get_transporters(
    date: str,
    point_id: int,
    language: str = Query("ua", description="Response language (ua/ru)"),
):
    """
    Get list of available transporters for specific date and delivery point

    Args:
        date: Delivery date in YYYY-MM-DD format (e.g., 2016-09-30)
        point_id: Delivery point ID from get_delivery_points
        language: Response language ('ua' or 'ru')
    """
    async with UniqTradeAdapter() as adapter:
        return await handle_api_errors(
            adapter.get_transporters, date, point_id, language
        )


@router.post("/delivery-options")
async def get_delivery_options(request: DeliveryOptionsRequest):
    """
    Get available delivery options for specified parameters

    Args:
        request: DeliveryOptionsRequest with date, point_id, transporter_id, and storage_ids

    Returns:
        List of available delivery options or error message
    """
    async with UniqTradeAdapter() as adapter:
        return await handle_api_errors(
            adapter.get_delivery_options,
            request.date,
            request.point_id,
            request.transporter_id,
            request.storage_ids,
            request.language,
        )


@router.post("/orders")
async def create_order(request: CreateOrderRequest):
    """
    Create new order(s)

    Args:
        request: CreateOrderRequest with list of orders to create

    Returns:
        Created order details or error message
    """
    async with UniqTradeAdapter() as adapter:
        # Convert Pydantic models to dicts
        orders_data = [order.dict() for order in request.orders]
        return await handle_api_errors(
            adapter.create_order, orders_data, request.language
        )


@router.get("/orders")
async def get_order_list(
    start_date: str = Query(..., description="Start date in YYYY-MM-DD format"),
    page: Optional[int] = Query(None, gt=0, description="Page number"),
    limit: Optional[int] = Query(None, gt=0, le=100, description="Items per page"),
    mode: str = Query("period", description="Search mode"),
    detail_id: Optional[int] = Query(None, description="Filter by detail ID"),
    language: str = Query("ua", description="Response language (ua/ru)"),
):
    """
    Get list of orders from start date to current date

    Args:
        start_date: Start date for search period
        page: Page number for pagination
        limit: Number of items per page
        mode: Search mode
        detail_id: Filter orders containing specific detail
        language: Response language

    Returns:
        List of orders or error message
    """
    async with UniqTradeAdapter() as adapter:
        return await handle_api_errors(
            adapter.get_order_list, start_date, page, limit, mode, detail_id, language
        )


@router.get("/orders/{order_id}")
async def get_order_details(
    order_id: int, language: str = Query("ua", description="Response language (ua/ru)")
):
    """
    Get detailed information about specific order

    Args:
        order_id: Order ID
        language: Response language

    Returns:
        Order details or error message
    """
    async with UniqTradeAdapter() as adapter:
        return await handle_api_errors(adapter.get_order_details, order_id, language)


@router.get("/pricelists/export-params")
async def get_pricelist_export_params(
    language: str = Query("ua", description="Response language (ua/ru)")
):
    """
    Get available parameters for pricelist export

    Args:
        language: Response language

    Returns:
        Available formats, brands, models, and categories
    """
    async with UniqTradeAdapter() as adapter:
        return await handle_api_errors(adapter.get_pricelist_export_params, language)


@router.post("/pricelists/export-request")
async def request_pricelist_export(request: PricelistExportRequest):
    """
    Request pricelist export generation

    Args:
        request: PricelistExportRequest with export parameters

    Returns:
        Pricelist generation task details
    """
    async with UniqTradeAdapter() as adapter:
        return await handle_api_errors(
            adapter.request_pricelist_export,
            request.format,
            request.visible_brands_id,
            request.categories_id,
            request.models_id,
            request.in_stock,
            request.show_scancode,
            request.utr_article,
            request.language,
        )


@router.get("/pricelists/{pricelist_id}/status")
async def get_pricelist_status(
    pricelist_id: int,
    language: str = Query("ua", description="Response language (ua/ru)"),
):
    """
    Check pricelist generation status

    Args:
        pricelist_id: Pricelist ID
        language: Response language

    Returns:
        Pricelist status (in queue/complete)
    """
    async with UniqTradeAdapter() as adapter:
        return await handle_api_errors(
            adapter.get_pricelist_status, pricelist_id, language
        )


@router.get("/pricelists")
async def get_pricelists(
    language: str = Query("ua", description="Response language (ua/ru)")
):
    """
    Get list of user's pricelists

    Args:
        language: Response language

    Returns:
        List of user's pricelists
    """
    async with UniqTradeAdapter() as adapter:
        return await handle_api_errors(adapter.get_pricelists, language)


@router.get("/pricelists/download/{token}")
async def download_pricelist(
    token: str, language: str = Query("ua", description="Response language (ua/ru)")
):
    """
    Download pricelist file

    Args:
        token: Pricelist token
        language: Response language

    Returns:
        File download stream
    """
    async with UniqTradeAdapter() as adapter:
        try:
            response = await adapter.download_pricelist(token, language)

            filename = "pricelist.csv"
            if "content-disposition" in response.headers:
                content_disp = response.headers["content-disposition"]
                if "filename=" in content_disp:
                    filename = content_disp.split("filename=")[1].strip('"')

            return StreamingResponse(
                io.BytesIO(response.content),
                media_type=response.headers.get(
                    "content-type", "application/octet-stream"
                ),
                headers={"Content-Disposition": f"attachment; filename={filename}"},
            )

        except UniqTradeAPIError as e:
            raise HTTPException(status_code=e.status_code, detail=e.message)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


@router.delete("/pricelists/{pricelist_id}")
async def delete_pricelist(
    pricelist_id: int,
    language: str = Query("ua", description="Response language (ua/ru)"),
):
    """
    Delete pricelist

    Args:
        pricelist_id: Pricelist ID
        language: Response language

    Returns:
        Deletion confirmation or error message
    """
    async with UniqTradeAdapter() as adapter:
        return await handle_api_errors(adapter.delete_pricelist, pricelist_id, language)


@router.post("/cart/add")
async def add_to_cart(request: AddToCartRequest):
    """
    Add item to shopping cart

    Args:
        request: AddToCartRequest with detail_id and quantity

    Returns:
        Cart item details or error message
    """
    async with UniqTradeAdapter() as adapter:
        return await handle_api_errors(
            adapter.add_to_cart, request.detail_id, request.quantity, request.language
        )


@router.get("/brands")
async def get_brands(
    language: str = Query("ua", description="Response language (ua/ru)")
):
    """
    Get list of available brands

    Args:
        language: Response language

    Returns:
        List of brands
    """
    async with UniqTradeAdapter() as adapter:
        return await handle_api_errors(adapter.get_brands, language)


@router.get("/storages")
async def get_storages(
    all_storages: bool = Query(False, description="Get all storages"),
    point_id: Optional[int] = Query(None, description="Filter by delivery point ID"),
    language: str = Query("ua", description="Response language (ua/ru)"),
):
    """
    Get list of storages

    Args:
        all_storages: Get all storages instead of only accessible ones
        point_id: Filter by delivery point for priority sorting
        language: Response language

    Returns:
        List of storages
    """
    async with UniqTradeAdapter() as adapter:
        return await handle_api_errors(
            adapter.get_storages, all_storages, point_id, language
        )


@router.get("/accounting/by-order/{order_code}")
async def get_accounting_numbers_by_order(
    order_code: str,
    language: str = Query("ua", description="Response language (ua/ru)"),
):
    """
    Get accounting document numbers by order code

    Args:
        order_code: Order code (e.g., УЯТ555556)
        language: Response language

    Returns:
        List of accounting documents
    """
    async with UniqTradeAdapter() as adapter:
        return await handle_api_errors(
            adapter.get_accounting_numbers_by_order, order_code, language
        )


@router.get("/accounting/by-number/{accounting_number}")
async def get_order_by_accounting_number(
    accounting_number: str,
    language: str = Query("ua", description="Response language (ua/ru)"),
):
    """
    Get order by accounting document number

    Args:
        accounting_number: Accounting document number (e.g., 75196)
        language: Response language

    Returns:
        Order information
    """
    async with UniqTradeAdapter() as adapter:
        return await handle_api_errors(
            adapter.get_order_by_accounting_number, accounting_number, language
        )

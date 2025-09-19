import logging
from typing import Any, Dict, List, Optional, Union

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field, model_validator

from app.adapters.asg_adapter import ASGAdapter, ASGAPIError
from app.dependencies.asg import get_asg_adapter

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/asg", tags=["asg"])


class LoginRequest(BaseModel):
    login: str = Field(..., min_length=1, description="User login")
    password: str = Field(..., min_length=1, description="User password")


class ProductItem(BaseModel):
    id: Optional[int] = Field(None, description="Product ID")
    sku: Optional[str] = Field(None, description="Product SKU")
    quantity: int = Field(..., gt=0, description="Quantity must be positive")
    price: Optional[float] = Field(None, ge=0, description="Product price")

    class Config:
        validate_assignment = True

    @model_validator(mode="after")
    def validate_id_or_sku(cls, product: "ProductItem") -> "ProductItem":
        if product.id is None and not (product.sku and product.sku.strip()):
            raise ValueError("Either 'id' or 'sku' must be provided for a product item.")
        return product


class CreateOrderRequest(BaseModel):
    products: List[ProductItem] = Field(
        ..., min_items=1, description="List of products to order"
    )
    test: bool = Field(False, description="Test mode flag")


class PriceFilters(BaseModel):
    search: Optional[str] = Field(None, description="Search query")
    category_id: Optional[int] = Field(None, gt=0, description="Category ID")
    brand_id: Optional[int] = Field(None, gt=0, description="Brand ID")
    min_price: Optional[float] = Field(None, ge=0, description="Minimum price")
    max_price: Optional[float] = Field(None, ge=0, description="Maximum price")
    in_stock: Optional[bool] = Field(None, description="Filter by stock availability")


class GetPricesRequest(BaseModel):
    filter: Optional[PriceFilters] = Field(None, description="Price filters")
    page: int = Field(1, ge=1, le=10000, description="Page number")


class SearchProductsRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Search query")
    category_id: Optional[int] = Field(None, gt=0, description="Category ID filter")
    page: int = Field(1, ge=1, description="Page number")
    per_page: int = Field(20, ge=1, le=100, description="Items per page")


def _format_error_detail(
    status_code: int, message: str, details: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    return {
        "success": False,
        "error": {
            "code": status_code,
            "message": message,
            "details": details or {},
        },
    }


async def handle_api_errors(func, *args, **kwargs):
    try:
        return await func(*args, **kwargs)
    except ASGAPIError as e:
        logger.error(f"ASG API error: {e}")
        raise HTTPException(
            status_code=e.status_code,
            detail=_format_error_detail(e.status_code, e.message, e.details),
        ) from e
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Unexpected error in ASG adapter")
        raise HTTPException(
            status_code=500,
            detail=_format_error_detail(
                500, "Internal server error", {"exception": str(e)}
            ),
        ) from e


@router.post("/login")
async def login(
    request: LoginRequest,
    adapter: ASGAdapter = Depends(get_asg_adapter),
):
    return await handle_api_errors(adapter.login, request.login, request.password)


@router.post("/logout")
async def logout(adapter: ASGAdapter = Depends(get_asg_adapter)):
    return await handle_api_errors(adapter.logout)


@router.post("/me")
async def get_me(adapter: ASGAdapter = Depends(get_asg_adapter)):
    return await handle_api_errors(adapter.get_me)


@router.post("/refresh")
async def refresh_token(adapter: ASGAdapter = Depends(get_asg_adapter)):
    return await handle_api_errors(adapter.refresh_token)


@router.post("/orders")
async def list_orders(adapter: ASGAdapter = Depends(get_asg_adapter)):
    return await handle_api_errors(adapter.get_orders)


@router.post("/orders/create")
async def create_order(
    request: CreateOrderRequest,
    adapter: ASGAdapter = Depends(get_asg_adapter),
):
    products_data = [product.dict(exclude_none=True) for product in request.products]
    return await handle_api_errors(
        adapter.create_order, products_data, request.test
    )


@router.post("/orders/{order_id}/cancel")
async def cancel_order(
    order_id: Union[int, str],
    adapter: ASGAdapter = Depends(get_asg_adapter),
):
    if not order_id:
        raise HTTPException(status_code=400, detail="Order ID cannot be empty")

    return await handle_api_errors(adapter.cancel_order, order_id)


@router.post("/prices")
async def get_prices(
    request: GetPricesRequest,
    adapter: ASGAdapter = Depends(get_asg_adapter),
):
    filter_dict = request.filter.dict(exclude_none=True) if request.filter else None
    return await handle_api_errors(adapter.get_prices, filter_dict, request.page)


@router.get("/prices")
async def get_prices_query(
    page: int = Query(1, ge=1, le=10000, description="Page number"),
    search: Optional[str] = Query(None, description="Search query"),
    category_id: Optional[int] = Query(None, gt=0, description="Category ID"),
    brand_id: Optional[int] = Query(None, gt=0, description="Brand ID"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price"),
    in_stock: Optional[bool] = Query(None, description="Filter by stock availability"),
    adapter: ASGAdapter = Depends(get_asg_adapter),
):
    if max_price is not None and min_price is not None and max_price < min_price:
        raise HTTPException(
            status_code=400, detail="max_price cannot be less than min_price"
        )

    filters = {}
    if search:
        filters["search"] = search
    if category_id is not None:
        filters["category_id"] = category_id
    if brand_id is not None:
        filters["brand_id"] = brand_id
    if min_price is not None:
        filters["min_price"] = min_price
    if max_price is not None:
        filters["max_price"] = max_price
    if in_stock is not None:
        filters["in_stock"] = in_stock

    return await handle_api_errors(
        adapter.get_prices, filters if filters else None, page
    )


@router.post("/categories")
async def get_categories(adapter: ASGAdapter = Depends(get_asg_adapter)):
    return await handle_api_errors(adapter.get_categories)


@router.post("/products/search")
async def search_products(
    request: SearchProductsRequest,
    adapter: ASGAdapter = Depends(get_asg_adapter),
):
    return await handle_api_errors(
        adapter.search_products,
        request.query,
        request.category_id,
        request.page,
        request.per_page,
    )


@router.get("/search/products")
async def search_products_query(
    query: str = Query(..., min_length=1, description="Search query"),
    category_id: Optional[int] = Query(None, gt=0, description="Category ID filter"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    adapter: ASGAdapter = Depends(get_asg_adapter),
):
    return await handle_api_errors(
        adapter.search_products, query, category_id, page, per_page
    )


@router.get("/products/{product_id}")
async def get_product_details(
    product_id: Union[int, str],
    adapter: ASGAdapter = Depends(get_asg_adapter),
):
    if not product_id:
        raise HTTPException(status_code=400, detail="Product ID cannot be empty")

    return await handle_api_errors(adapter.get_product_details, product_id)


@router.post("/products/{product_id}")
async def get_product_details_post(
    product_id: Union[int, str],
    adapter: ASGAdapter = Depends(get_asg_adapter),
):
    if not product_id:
        raise HTTPException(status_code=400, detail="Product ID cannot be empty")

    return await handle_api_errors(adapter.get_product_details, product_id)

import logging
from typing import List, Optional, Union

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field, field_validator

from app.adapters.asg_adapter import ASGAdapter, ASGAPIError

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

    @field_validator("id", "sku", mode="before")
    def validate_product_identifier(self, v, info):
        values = info.data
        if not v and not values.get("id") and not values.get("sku"):
            raise ValueError("Either 'id' or 'sku' must be provided")
        return v

    class Config:
        validate_assignment = True


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

    @field_validator("max_price")
    def validate_price_range(self, v, info):
        values = info.data
        if v is not None and values.get("min_price") is not None:
            if v < values["min_price"]:
                raise ValueError("max_price cannot be less than min_price")
        return v


class GetPricesRequest(BaseModel):
    filter: Optional[PriceFilters] = Field(None, description="Price filters")
    page: int = Field(1, ge=1, le=10000, description="Page number")


class SearchProductsRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Search query")
    category_id: Optional[int] = Field(None, gt=0, description="Category ID filter")
    page: int = Field(1, ge=1, description="Page number")
    per_page: int = Field(20, ge=1, le=100, description="Items per page")


async def handle_api_errors(func, *args, **kwargs):
    try:
        return await func(*args, **kwargs)
    except ASGAPIError as e:
        logger.error(f"ASG API error: {e}")
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Unexpected error in ASG adapter: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/login")
async def login(request: LoginRequest):
    async with ASGAdapter() as adapter:
        return await handle_api_errors(adapter.login, request.login, request.password)


@router.post("/logout")
async def logout():
    async with ASGAdapter() as adapter:
        return await handle_api_errors(adapter.logout)


@router.post("/me")
async def get_me():
    async with ASGAdapter() as adapter:
        return await handle_api_errors(adapter.get_me)


@router.post("/refresh")
async def refresh_token():
    async with ASGAdapter() as adapter:
        return await handle_api_errors(adapter.refresh_token)


@router.post("/orders")
async def list_orders():
    async with ASGAdapter() as adapter:
        return await handle_api_errors(adapter.get_orders)


@router.post("/orders/create")
async def create_order(request: CreateOrderRequest):
    async with ASGAdapter() as adapter:
        products_data = [
            product.dict(exclude_none=True) for product in request.products
        ]
        return await handle_api_errors(
            adapter.create_order, products_data, request.test
        )


@router.post("/orders/{order_id}/cancel")
async def cancel_order(order_id: Union[int, str]):
    if not order_id:
        raise HTTPException(status_code=400, detail="Order ID cannot be empty")

    async with ASGAdapter() as adapter:
        return await handle_api_errors(adapter.cancel_order, order_id)


@router.post("/prices")
async def get_prices(request: GetPricesRequest):
    async with ASGAdapter() as adapter:
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

    async with ASGAdapter() as adapter:
        return await handle_api_errors(
            adapter.get_prices, filters if filters else None, page
        )


@router.post("/categories")
async def get_categories():
    async with ASGAdapter() as adapter:
        return await handle_api_errors(adapter.get_categories)


@router.post("/products/search")
async def search_products(request: SearchProductsRequest):
    async with ASGAdapter() as adapter:
        return await handle_api_errors(
            adapter.search_products,
            request.query,
            request.category_id,
            request.page,
            request.per_page,
        )


@router.get("/products/search")
async def search_products_query(
    query: str = Query(..., min_length=1, description="Search query"),
    category_id: Optional[int] = Query(None, gt=0, description="Category ID filter"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
):
    async with ASGAdapter() as adapter:
        return await handle_api_errors(
            adapter.search_products, query, category_id, page, per_page
        )


@router.get("/products/{product_id}")
async def get_product_details(product_id: Union[int, str]):
    if not product_id:
        raise HTTPException(status_code=400, detail="Product ID cannot be empty")

    async with ASGAdapter() as adapter:
        return await handle_api_errors(adapter.get_product_details, product_id)


@router.post("/products/{product_id}")
async def get_product_details_post(product_id: Union[int, str]):
    if not product_id:
        raise HTTPException(status_code=400, detail="Product ID cannot be empty")

    async with ASGAdapter() as adapter:
        return await handle_api_errors(adapter.get_product_details, product_id)

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from pydantic import BaseModel
from app.adapters.omega_adapter import OmegaAdapter

router = APIRouter(prefix="/omega", tags=["Omega"])


class LoginRequest(BaseModel):
    username: str
    password: str


class ProductItem(BaseModel):
    product_id: str
    quantity: int
    price: Optional[float] = None


class CreateOrderRequest(BaseModel):
    products: List[ProductItem]
    test_mode: Optional[bool] = False
    notes: Optional[str] = None


class CreateBasketRequest(BaseModel):
    products: List[ProductItem]


class UpdateOrderRequest(BaseModel):
    products: Optional[List[ProductItem]] = None
    status: Optional[str] = None
    notes: Optional[str] = None


@router.post("/login/")
async def login_omega_user(request: LoginRequest):
    adapter = OmegaAdapter()
    try:
        return await adapter.login(
            username=request.username,
            password=request.password
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/logout/")
async def logout_omega_user():
    adapter = OmegaAdapter()
    try:
        return await adapter.logout()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/me/")
async def get_current_user():
    adapter = OmegaAdapter()
    try:
        return await adapter.me()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/refresh/")
async def refresh_token():
    adapter = OmegaAdapter()
    try:
        return await adapter.refresh_token()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/orders/")
async def list_orders(
        page: int = Query(1, ge=1, description="Page number"),
        limit: int = Query(50, ge=1, le=100, description="Items per page")
):
    adapter = OmegaAdapter()
    try:
        return await adapter.get_orders(page=page, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/orders/")
async def create_order(request: CreateOrderRequest):
    adapter = OmegaAdapter()
    try:
        products = [item.dict() for item in request.products]

        additional_params = {}
        if request.test_mode is not None:
            additional_params["test_mode"] = request.test_mode
        if request.notes:
            additional_params["notes"] = request.notes

        return await adapter.create_order(
            products=products,
            **additional_params
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/orders/{order_id}")
async def get_order(order_id: str):
    adapter = OmegaAdapter()
    try:
        return await adapter.get_order(order_id=order_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/orders/{order_id}")
async def update_order(order_id: str, request: UpdateOrderRequest):
    adapter = OmegaAdapter()
    try:
        update_data = {}
        if request.products:
            update_data["products"] = [item.dict() for item in request.products]
        if request.status:
            update_data["status"] = request.status
        if request.notes:
            update_data["notes"] = request.notes

        return await adapter.update_order(order_id=order_id, data=update_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/orders/{order_id}/cancel")
async def cancel_order(order_id: str):
    adapter = OmegaAdapter()
    try:
        return await adapter.cancel_order(order_id=order_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/products/")
async def list_products(
        category: Optional[str] = Query(None, description="Filter by category"),
        page: int = Query(1, ge=1, description="Page number"),
        limit: int = Query(50, ge=1, le=100, description="Items per page")
):
    adapter = OmegaAdapter()
    try:
        return await adapter.get_products(
            category=category,
            page=page,
            limit=limit
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/products/{product_id}")
async def get_product(product_id: str):
    adapter = OmegaAdapter()
    try:
        return await adapter.get_product(product_id=product_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/categories/")
async def list_categories():
    adapter = OmegaAdapter()
    try:
        return await adapter.get_categories()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/prices/")
async def get_prices(
        filter_props: Optional[dict] = None,
        page: int = Query(1, ge=1, description="Page number"),
        limit: int = Query(50, ge=1, le=100, description="Items per page")
):
    adapter = OmegaAdapter()
    try:
        return await adapter.get_prices(
            filter_props=filter_props,
            page=page,
            limit=limit
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/inventory/")
async def get_inventory(product_ids: Optional[List[str]] = None):
    adapter = OmegaAdapter()
    try:
        return await adapter.get_inventory(product_ids=product_ids)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/basket/")
async def create_basket(request: CreateBasketRequest):
    adapter = OmegaAdapter()
    try:
        products = [item.dict() for item in request.products]
        return await adapter.create_basket(products=products)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/basket/{basket_id}")
async def get_basket(basket_id: str):
    adapter = OmegaAdapter()
    try:
        return await adapter.get_basket(basket_id=basket_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/basket/{basket_id}")
async def update_basket(basket_id: str, request: CreateBasketRequest):
    adapter = OmegaAdapter()
    try:
        products = [item.dict() for item in request.products]
        return await adapter.update_basket(basket_id=basket_id, products=products)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

from fastapi import APIRouter

from app.adapters.asg_adapter import ASGAdapter

router = APIRouter(prefix="/asg", tags=["ASG"])


@router.post("/asg/login/")
async def login_asg_user():
    adapter = ASGAdapter()
    return await adapter.login(
        login="43420m",
        password="PASRdQBz7EpUq#",
    )


@router.post("/asg/logout/")
async def logout_asg_user():
    adapter = ASGAdapter()
    return await adapter.logout()


@router.post("/asg/me/")
async def get_me():
    adapter = ASGAdapter()
    return await adapter.me()


@router.post("/asg/refresh/")
async def refresh_token():
    adapter = ASGAdapter()
    return await adapter.refresh_token()


@router.post("/asg/orders/")
async def list_orders():
    adapter = ASGAdapter()
    return await adapter.get_orders()


@router.post("/asg/orders/create/")
async def create_order(products: list[dict]):
    adapter = ASGAdapter()
    return await adapter.create_order(products=products)


@router.post("/asg/orders/{order_id}/cancel/")
async def cancel_order(order_id: int):
    adapter = ASGAdapter()
    return await adapter.cancel_order(order_id)


@router.post("/asg/prices/")
async def get_prices(page: int, filter_props: dict):
    adapter = ASGAdapter()
    return await adapter.get_prices(filter_props=filter_props, page=page)


@router.post("/asg/categories/")
async def get_categories():
    adapter = ASGAdapter()
    return await adapter.get_categories()

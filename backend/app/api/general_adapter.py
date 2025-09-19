from fastapi import APIRouter, Depends
from app.adapters.bm_parts_adapter import BMPartsAdapter
from app.api.auth import get_current_user

router = APIRouter()

bm_parts_adapter = BMPartsAdapter()


@router.get("/bmparts/data")
async def get_bm_parts_data(user: dict = Depends(get_current_user)):
    """Fetch data from BM Parts (Requires Authentication)"""
    return bm_parts_adapter.fetch_data()

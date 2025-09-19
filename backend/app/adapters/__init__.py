from __future__ import annotations

from typing import Dict

from app.adapters.base import BaseAdapter
from app.adapters.bm_parts_adapter import BMPartsAdapter

adapter_registry: Dict[str, BaseAdapter] = {
    "bmparts": BMPartsAdapter(),
}

__all__ = ["adapter_registry", "BaseAdapter", "BMPartsAdapter"]

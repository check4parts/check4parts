from __future__ import annotations

from typing import Any, Dict, Optional

from app.adapters.base import AdapterError, BaseAdapter
from app.config import BMPARTS_API_KEY, BMPARTS_BASE_URL


class BMPartsAdapter(BaseAdapter):
    """Adapter responsible for communicating with the BM Parts API."""

    def __init__(self, *, base_url: Optional[str] = None, api_key: Optional[str] = None) -> None:
        headers: Dict[str, str] = {}
        resolved_api_key = api_key or BMPARTS_API_KEY
        if resolved_api_key:
            headers["Authorization"] = f"Bearer {resolved_api_key}"

        super().__init__(
            base_url=base_url or BMPARTS_BASE_URL or "",
            default_headers=headers,
        )

    def fetch_data(self, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Retrieve a generic payload from the provider."""

        if not self.base_url:
            return {"error": "BM Parts base URL is not configured"}

        context = self.prepare_request("GET", params=params)
        try:
            response = self.request(context)
            return response.json()
        except AdapterError as exc:
            return {"error": "Failed to fetch data", "details": str(exc)}

    def search(self, query: str, **kwargs: Any) -> Dict[str, Any]:  # type: ignore[override]
        """Execute a search request against the BM Parts API."""

        params: Dict[str, Any] = kwargs.get("params", {}).copy()
        if query:
            params.setdefault("q", query)

        return self.fetch_data(params=params)

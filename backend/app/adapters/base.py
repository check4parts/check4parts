from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

import requests


class AdapterError(Exception):
    """Base exception for adapter-related failures."""


@dataclass
class RequestContext:
    """Represents metadata required to execute an HTTP request."""

    method: str
    url: str
    headers: Dict[str, str]
    params: Optional[Dict[str, Any]] = None
    json: Optional[Dict[str, Any]] = None
    data: Optional[Any] = None
    timeout: Optional[float] = None


class BaseAdapter:
    """Shared abstraction for adapters that communicate with external APIs."""

    def __init__(
        self,
        *,
        base_url: str,
        default_headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.default_headers = default_headers or {}
        self.timeout = timeout

    def build_url(self, path: str = "") -> str:
        """Create a fully qualified URL using the adapter base URL."""

        if not path:
            return self.base_url
        return f"{self.base_url}/{path.lstrip('/')}"

    def prepare_request(
        self,
        method: str,
        *,
        path: str = "",
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        data: Optional[Any] = None,
        timeout: Optional[float] = None,
    ) -> RequestContext:
        """Compose a :class:`RequestContext` with merged headers."""

        merged_headers = {**self.default_headers, **(headers or {})}
        return RequestContext(
            method=method,
            url=self.build_url(path),
            headers=merged_headers,
            params=params,
            json=json,
            data=data,
            timeout=timeout or self.timeout,
        )

    def request(self, context: RequestContext) -> requests.Response:
        """Execute an HTTP request and surface consistent adapter errors."""

        try:
            response = requests.request(
                context.method,
                context.url,
                headers=context.headers,
                params=context.params,
                json=context.json,
                data=context.data,
                timeout=context.timeout,
            )
            response.raise_for_status()
            return response
        except requests.RequestException as exc:  # pragma: no cover - thin wrapper
            raise AdapterError(str(exc)) from exc

    def search(self, query: str, **_: Any) -> Dict[str, Any]:
        """Search the provider for the given query.

        Subclasses must override this method to implement provider-specific
        behavior.
        """

        raise NotImplementedError

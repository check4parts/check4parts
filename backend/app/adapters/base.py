"""Shared abstractions for talking to external provider APIs."""

from __future__ import annotations

import asyncio
from typing import Any, Dict, Optional, Type
from urllib.parse import urljoin

import httpx
from fastapi import HTTPException


class ExternalAPIError(HTTPException):
    """Base error raised when an upstream provider call fails."""

    provider: str

    def __init__(
        self,
        provider: str,
        *,
        status_code: int,
        detail: Any | None = None,
        message: str | None = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> None:
        fallback_message = message or f"{provider} API request failed"
        detail_payload = detail if detail is not None else {"message": fallback_message}
        super().__init__(status_code=status_code, detail=detail_payload, headers=headers)
        self.provider = provider
        self.message = fallback_message


class ExternalAPIAdapter:
    """Helper that wraps common HTTP client behaviour for adapters."""

    BASE_URL = ""
    REQUEST_TIMEOUT = 30.0
    MAX_RETRIES = 3
    RETRY_BACKOFF = 1.0
    PROVIDER_NAME = "External"
    ERROR_CLS: Type[ExternalAPIError] = ExternalAPIError

    def __init__(
        self,
        *,
        client: httpx.AsyncClient | None = None,
        default_headers: Optional[Dict[str, str]] = None,
    ) -> None:
        self._client: httpx.AsyncClient | None = client
        self._owns_client = client is None
        self._default_headers = default_headers or {}

    async def __aenter__(self) -> "ExternalAPIAdapter":
        if not self._client:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(self.REQUEST_TIMEOUT),
                limits=httpx.Limits(max_connections=10, max_keepalive_connections=5),
            )
            self._owns_client = True
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:  # pragma: no cover - passthrough
        await self.aclose()

    async def aclose(self) -> None:
        if self._client and self._owns_client:
            await self._client.aclose()
        self._client = None

    async def _get_client(self) -> httpx.AsyncClient:
        if not self._client:
            await self.__aenter__()
        assert self._client is not None
        return self._client

    def build_headers(self) -> Dict[str, str]:
        """Return the default headers that should accompany each request."""

        return dict(self._default_headers)

    async def request(
        self,
        method: str,
        endpoint: str,
        *,
        params: Dict[str, Any] | None = None,
        json: Dict[str, Any] | None = None,
        headers: Dict[str, str] | None = None,
    ) -> Any:
        client = await self._get_client()
        url = urljoin(self.BASE_URL.rstrip("/") + "/", endpoint.lstrip("/"))
        request_headers = self.build_headers()
        if headers:
            request_headers.update(headers)

        for attempt in range(self.MAX_RETRIES):
            try:
                response = await client.request(
                    method,
                    url,
                    params=params,
                    json=json,
                    headers=request_headers,
                )
                response.raise_for_status()
                return self._decode_response(response)
            except httpx.HTTPStatusError as exc:
                raise self.ERROR_CLS(
                    self.PROVIDER_NAME,
                    status_code=exc.response.status_code,
                    detail=self._extract_error_detail(exc.response),
                    message=f"{self.PROVIDER_NAME} API responded with an error",
                ) from exc
            except httpx.RequestError as exc:
                if attempt < self.MAX_RETRIES - 1:
                    await asyncio.sleep(self.RETRY_BACKOFF * (2**attempt))
                    continue
                raise self.ERROR_CLS(
                    self.PROVIDER_NAME,
                    status_code=502,
                    detail={
                        "message": f"Failed to communicate with {self.PROVIDER_NAME} API",
                        "error": str(exc),
                    },
                    message=f"Failed to communicate with {self.PROVIDER_NAME} API",
                ) from exc

    def _decode_response(self, response: httpx.Response) -> Any:
        try:
            return response.json()
        except ValueError as exc:
            raise self.ERROR_CLS(
                self.PROVIDER_NAME,
                status_code=502,
                detail={
                    "message": f"Invalid response payload from {self.PROVIDER_NAME} API",
                    "response_text": response.text,
                },
            ) from exc

    def _extract_error_detail(self, response: httpx.Response) -> Any:
        try:
            return response.json()
        except ValueError:
            return {"message": response.text or "Unknown error"}


import asyncio

import pytest

from app.services import unified_catalog as uc
from app.services.credentials import ClientCredentialStore, DEFAULT_RULES, InvalidCredentialError


def test_invalid_credentials_rejected():
    store = ClientCredentialStore(DEFAULT_RULES, {})

    with pytest.raises(InvalidCredentialError):
        store.set_credentials("c1", "bm-parts", {})


def test_resolve_credentials_uses_defaults():
    store = ClientCredentialStore(DEFAULT_RULES, {"bm-parts": {"token": "abc"}})

    resolved = store.resolve_credentials("c1", "bm-parts", {})

    assert resolved == {"token": "abc"}


def test_unified_search_skips_missing_credentials(monkeypatch):
    store = ClientCredentialStore(DEFAULT_RULES, {})

    async def fake_handler(query: str, options: dict):
        return {"products": [{"uuid": "1", "name": "test"}]}

    monkeypatch.setattr(
        uc,
        "SEARCH_HANDLERS",
        {"bm-parts": fake_handler, "omega": fake_handler},
    )

    request = uc.UnifiedSearchRequest(
        query="abc", suppliers=["bm-parts", "omega"], supplier_options={}
    )
    result = asyncio.run(
        uc.unified_search(request, client_id="c1", credential_store=store)
    )

    assert result["products"] == []
    assert result["meta"]["attempted_suppliers"] == []
    assert {entry["supplier"] for entry in result["meta"]["skipped_suppliers"]} == {
        "bm-parts",
        "omega",
    }

    store.set_credentials("c1", "bm-parts", {"token": "abc"})

    result = asyncio.run(
        uc.unified_search(request, client_id="c1", credential_store=store)
    )

    assert len(result["products"]) == 1
    assert result["meta"]["attempted_suppliers"] == ["bm-parts"]
    assert result["meta"]["skipped_suppliers"]

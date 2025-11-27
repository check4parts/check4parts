import pytest

from app.services import unified_catalog
from app.services.supplier_credentials import SupplierCredentialManager
from app.services.unified_catalog import UnifiedSearchRequest, unified_search


@pytest.fixture
def anyio_backend():
    return "asyncio"


def test_manager_stores_credentials_per_client():
    manager = SupplierCredentialManager()
    manager.set_credentials("client-a", "omega", {"key": "123"})
    manager.set_credentials("client-b", "omega", {"key": "456"})

    assert manager.get_credentials("client-a", "omega") == {"key": "123"}
    assert manager.get_credentials("client-b", "omega") == {"key": "456"}


@pytest.mark.parametrize(
    "supplier, credentials, expected",
    [
        ("bm-parts", {}, False),
        ("bm-parts", {"token": "t"}, True),
        ("asg", {"token": "t"}, True),
        ("asg", {"login": "l", "password": "p"}, True),
        ("asg", {"login": "l"}, False),
        (
            "uniqtrade",
            {"email": "e", "password": "p", "fingerprint": "f"},
            True,
        ),
        ("uniqtrade", {"email": "e", "password": "p"}, False),
    ],
)
def test_required_credentials_validation(supplier, credentials, expected):
    manager = SupplierCredentialManager()
    assert manager.has_required_credentials(supplier, credentials) is expected


def test_effective_credentials_merge_and_persist():
    manager = SupplierCredentialManager(
        default_credentials={"omega": {"key": "default"}}
    )

    merged = manager.get_effective_credentials(
        "omega", client_id="client-1", overrides={"key": "override"}
    )

    # Override wins over default and is persisted for the client
    assert merged == {"key": "override"}
    assert manager.get_credentials("client-1", "omega") == {"key": "override"}

    # Subsequent calls can read from the stored value
    reused = manager.get_effective_credentials("omega", client_id="client-1")
    assert reused == {"key": "override"}


@pytest.mark.anyio
async def test_unified_search_skips_unconfigured_suppliers(monkeypatch):
    async def fake_handler(query, options):  # pragma: no cover - not executed
        return {"products": []}

    monkeypatch.setitem(unified_catalog.SEARCH_HANDLERS, "omega", fake_handler)

    manager = SupplierCredentialManager()
    request = UnifiedSearchRequest(query="q", suppliers=["omega"])

    response = await unified_search(
        request, client_id="client-x", credential_manager=manager
    )

    assert response["products"] == []
    assert response["meta"]["skipped_suppliers"] == ["omega"]


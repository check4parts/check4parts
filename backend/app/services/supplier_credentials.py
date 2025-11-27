"""Credential routing and storage for supplier API integrations."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Mapping, MutableMapping, Optional

from app.config import (
    ASG_TOKEN,
    BM_PARTS_TOKEN,
    INTERCARS_CLIENT_ID,
    INTERCARS_CLIENT_SECRET,
    OMEGA_KEY,
    UNIQTRADE_EMAIL,
    UNIQTRADE_FINGERPRINT,
    UNIQTRADE_PASSWORD,
)


def _clean_payload(payload: Mapping[str, Any]) -> Dict[str, Any]:
    """Return a shallow copy of ``payload`` without falsy values."""

    return {key: value for key, value in payload.items() if value}


@dataclass
class SupplierCredentialManager:
    """Simple in-memory registry of client credentials per supplier."""

    default_credentials: Mapping[str, Mapping[str, Any]] = field(default_factory=dict)
    _store: MutableMapping[str, Dict[str, Dict[str, Any]]] = field(
        default_factory=dict, init=False
    )

    REQUIRED_FIELDS: Mapping[str, tuple[tuple[str, ...], ...]] = field(
        default_factory=lambda: {
            # BM Parts requires the Authorization token.
            "bm-parts": (("token",),),
            # ASG accepts either a bearer token or login/password pair.
            "asg": (("token",), ("login", "password")),
            # Omega expects a single API key field.
            "omega": (("key",),),
            # UniqTrade requires the full credential set.
            "uniqtrade": (("email", "password", "fingerprint"),),
            # InterCars uses OAuth client credentials.
            "intercars": (("client_id", "client_secret"),),
        }
    )

    def _get_store_for_client(self, client_id: str) -> Dict[str, Dict[str, Any]]:
        return self._store.setdefault(client_id, {})

    def set_credentials(
        self, client_id: str, supplier: str, credentials: Mapping[str, Any]
    ) -> None:
        """Persist credentials for a supplier/client pair."""

        cleaned = _clean_payload(credentials)
        if not cleaned:
            return
        client_store = self._get_store_for_client(client_id)
        client_store[supplier] = cleaned

    def get_credentials(self, client_id: str, supplier: str) -> Dict[str, Any]:
        """Return stored credentials or an empty mapping."""

        return dict(self._store.get(client_id, {}).get(supplier, {}))

    def _default_credentials(self, supplier: str) -> Dict[str, Any]:
        return dict(self.default_credentials.get(supplier, {}))

    def get_effective_credentials(
        self,
        supplier: str,
        *,
        client_id: Optional[str] = None,
        overrides: Optional[Mapping[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Merge default credentials, stored client data, and request overrides."""

        result: Dict[str, Any] = {}
        result.update(self._default_credentials(supplier))
        if client_id:
            result.update(self.get_credentials(client_id, supplier))
        if overrides:
            result.update(_clean_payload(overrides))
        if client_id and overrides:
            self.set_credentials(client_id, supplier, result)
        return result

    def has_required_credentials(
        self, supplier: str, credentials: Mapping[str, Any]
    ) -> bool:
        """Validate that the credentials contain one of the required field sets."""

        required_sets = self.REQUIRED_FIELDS.get(supplier)
        if not required_sets:
            return True

        for field_group in required_sets:
            if all(credentials.get(field) for field in field_group):
                return True
        return False

    def clear_client(self, client_id: str) -> None:
        """Remove all stored credentials for a client (primarily for tests)."""

        self._store.pop(client_id, None)


DEFAULT_CREDENTIAL_MANAGER = SupplierCredentialManager(
    default_credentials={
        "bm-parts": {"token": BM_PARTS_TOKEN},
        "asg": {"token": ASG_TOKEN},
        "omega": {"key": OMEGA_KEY},
        "uniqtrade": {
            "email": UNIQTRADE_EMAIL,
            "password": UNIQTRADE_PASSWORD,
            "fingerprint": UNIQTRADE_FINGERPRINT,
        },
        "intercars": {
            "client_id": INTERCARS_CLIENT_ID,
            "client_secret": INTERCARS_CLIENT_SECRET,
        },
    }
)


__all__ = ["SupplierCredentialManager", "DEFAULT_CREDENTIAL_MANAGER"]

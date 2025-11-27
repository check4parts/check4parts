"""Credential routing and validation for supplier integrations."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, Mapping

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


@dataclass(frozen=True)
class SupplierCredentialRule:
    """Validation rules for an individual supplier."""

    name: str
    required: Iterable[str] = field(default_factory=set)
    any_of: Iterable[Iterable[str]] = field(default_factory=list)

    def is_valid(self, credentials: Mapping[str, Any] | None) -> bool:
        """Return ``True`` when the credentials satisfy the rule set."""

        if not credentials:
            return False

        def _has_all(fields: Iterable[str]) -> bool:
            return all(bool(credentials.get(field)) for field in fields)

        if self.required and not _has_all(self.required):
            return False

        if self.any_of:
            return any(_has_all(group) for group in self.any_of)

        return bool(credentials)


class CredentialStoreError(ValueError):
    """Base class for credential store failures."""


class UnknownSupplierError(CredentialStoreError):
    """Raised when attempting to store credentials for an unsupported supplier."""


class InvalidCredentialError(CredentialStoreError):
    """Raised when credentials do not satisfy a supplier's rule set."""


class ClientCredentialStore:
    """In-memory registry of supplier credentials per client."""

    def __init__(
        self,
        rules: Mapping[str, SupplierCredentialRule],
        defaults: Mapping[str, Dict[str, Any]] | None = None,
    ) -> None:
        self._rules = dict(rules)
        self._defaults = {k: v for k, v in (defaults or {}).items() if v}
        self._store: dict[str, dict[str, Dict[str, Any]]] = {}

    def set_credentials(
        self, client_id: str, supplier: str, credentials: Mapping[str, Any]
    ) -> None:
        if supplier not in self._rules:
            raise UnknownSupplierError(f"Unsupported supplier '{supplier}'")

        rule = self._rules[supplier]
        if not rule.is_valid(credentials):
            raise InvalidCredentialError(
                f"Credentials for '{supplier}' are incomplete or invalid"
            )

        self._store.setdefault(client_id, {})[supplier] = dict(credentials)

    def get_credentials(self, client_id: str, supplier: str) -> Dict[str, Any] | None:
        return self._store.get(client_id, {}).get(supplier) or self._defaults.get(
            supplier
        )

    def resolve_credentials(
        self,
        client_id: str | None,
        supplier: str,
        request_options: Mapping[str, Any] | None = None,
    ) -> Dict[str, Any] | None:
        """Merge defaults, stored credentials, and request overrides.

        Returns ``None`` when the final payload does not satisfy the supplier
        rule set.
        """

        if supplier not in self._rules:
            return None

        merged: dict[str, Any] = {}
        merged.update(self._defaults.get(supplier, {}))

        if client_id:
            merged.update(self._store.get(client_id, {}).get(supplier, {}))

        if request_options:
            merged.update(request_options)

        return merged if self._rules[supplier].is_valid(merged) else None

    def supplier_status(self, client_id: str | None) -> list[dict[str, Any]]:
        statuses: list[dict[str, Any]] = []
        for name, rule in self._rules.items():
            merged = self.resolve_credentials(client_id, name, {})
            statuses.append(
                {
                    "supplier": name,
                    "has_credentials": rule.is_valid(merged),
                }
            )
        return statuses


DEFAULT_RULES: dict[str, SupplierCredentialRule] = {
    "bm-parts": SupplierCredentialRule(name="bm-parts", required={"token"}),
    "asg": SupplierCredentialRule(
        name="asg", any_of=[{"token"}, {"login", "password"}]
    ),
    "omega": SupplierCredentialRule(name="omega", required={"key"}),
    "uniqtrade": SupplierCredentialRule(
        name="uniqtrade", required={"email", "password", "fingerprint"}
    ),
    "intercars": SupplierCredentialRule(
        name="intercars", required={"client_id", "client_secret"}
    ),
}


def _default_credentials_from_env() -> dict[str, Dict[str, Any]]:
    defaults: dict[str, Dict[str, Any]] = {}

    if BM_PARTS_TOKEN:
        defaults["bm-parts"] = {"token": BM_PARTS_TOKEN}

    if ASG_TOKEN:
        defaults["asg"] = {"token": ASG_TOKEN}

    if OMEGA_KEY:
        defaults["omega"] = {"key": OMEGA_KEY}

    if UNIQTRADE_EMAIL and UNIQTRADE_PASSWORD and UNIQTRADE_FINGERPRINT:
        defaults["uniqtrade"] = {
            "email": UNIQTRADE_EMAIL,
            "password": UNIQTRADE_PASSWORD,
            "fingerprint": UNIQTRADE_FINGERPRINT,
        }

    if INTERCARS_CLIENT_ID and INTERCARS_CLIENT_SECRET:
        defaults["intercars"] = {
            "client_id": INTERCARS_CLIENT_ID,
            "client_secret": INTERCARS_CLIENT_SECRET,
        }

    return defaults


DEFAULT_CREDENTIAL_STORE = ClientCredentialStore(
    rules=DEFAULT_RULES, defaults=_default_credentials_from_env()
)

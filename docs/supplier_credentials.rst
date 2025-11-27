Supplier credential routing
===========================

Supplier adapters require different authentication inputs. The backend consolidates
credential handling via ``SupplierCredentialManager`` in
``app.services.supplier_credentials``. It merges three sources in order:

1. Default credentials from environment variables (see :doc:`development`).
2. Values previously stored for the current authenticated client.
3. Per-request overrides sent inside ``supplier_options``.

When a client supplies overrides, the merged values are persisted for that client
so future calls do not need to repeat the secrets.

Required credential fields
--------------------------

The routing layer validates that at least one acceptable credential set is
present per supplier:

- ``bm-parts``: ``token``
- ``asg``: either ``token`` or a ``login``/``password`` pair
- ``omega``: ``key``
- ``uniqtrade``: ``email``, ``password``, and ``fingerprint``
- ``intercars``: ``client_id`` and ``client_secret`` (used by InterCars-specific
  routes)

If a supplier is missing its required fields after merging defaults and stored
values, the unified catalog services skip it and record the slug under
``meta.skipped_suppliers``.

Client-facing behaviour
-----------------------

- Requests against ``/space/search`` or ``/space/products`` only fan out to
  suppliers with valid credentials for the authenticated client.
- Missing or incomplete credentials never block other suppliers; they are simply
  skipped.
- Invalid or failing suppliers are surfaced separately in
  ``meta.failed_suppliers`` with status codes and details, so the frontend can
  inform the user without losing successful data from other providers.

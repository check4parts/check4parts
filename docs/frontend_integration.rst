Frontend integration for unified catalog
=======================================

The ``/space`` endpoints expose a consistent schema so the frontend can call
multiple suppliers without bespoke handling.

Authentication
--------------

All routes require the Supabase JWT in the ``Authorization`` header:
``Authorization: Bearer <supabase-jwt>``.

Search flow (``POST /space/search``)
------------------------------------

**Request body**

- ``query`` (string): required search term.
- ``suppliers`` (list[str], optional): supplier slugs (``bm-parts``, ``asg``,
  ``omega``, ``uniqtrade``). If omitted, all supported suppliers are queried.
- ``supplier_options`` (object, optional): per-supplier overrides (e.g.
  pagination for ASG, API keys for Omega).
- Credentials: suppliers without stored or inline credentials are skipped and
  reported in ``meta.skipped_suppliers``.

**Response shape**

- ``products``: list of entries with ``part`` (BM Parts-like fields), ``rests``
  availability, ``supplier`` slug, and ``raw`` provider payload.
- ``meta``: includes ``requested_suppliers``, ``attempted_suppliers``,
  ``skipped_suppliers`` when credentials are missing, ``failed_suppliers`` with
  ``status_code``/``detail``, and ``partial_failure`` boolean.

**Fetch example**

.. code-block:: javascript

   const response = await fetch("/space/search", {
     method: "POST",
     headers: {
       "Content-Type": "application/json",
       Authorization: `Bearer ${token}`,
     },
     body: JSON.stringify({
       query: "oil filter",
       suppliers: ["bm-parts", "omega"],
       supplier_options: { omega: { key: "<api-key>", count: 10 } },
     }),
   });
   const { products, meta } = await response.json();
   // meta.partial_failure can be surfaced to the user if true

Product details flow (``POST /space/products``)
-----------------------------------------------

**Request body**

- ``products`` (list): each item requires ``supplier`` and ``product_id``, plus
  optional ``options`` to fine-tune adapter behaviour.

**Response shape**

- ``products``: BM Parts-shaped product entries (``part``, ``rests``,
  ``supplier``, ``raw``)
- ``meta``: ``attempted_suppliers`` and ``skipped_suppliers`` mirrors search
  behaviour, alongside ``failed_suppliers`` and ``partial_failure``. Successful
  suppliers still return results even if others fail.

**Fetch example**

.. code-block:: javascript

   const response = await fetch("/space/products", {
     method: "POST",
     headers: {
       "Content-Type": "application/json",
       Authorization: `Bearer ${token}`,
     },
     body: JSON.stringify({
       products: [
         { supplier: "bm-parts", product_id: "123" },
         { supplier: "uniqtrade", product_id: "ABC", options: { language: "en" } },
       ],
     }),
   });
   const { products, meta } = await response.json();
   // handle meta.failed_suppliers to display warnings

Error handling
--------------

- Invalid suppliers yield ``error`` entries in ``meta.failed_suppliers`` with a
  ``400`` status code.
- Timeouts or upstream issues set ``partial_failure`` to ``true`` while still
  returning successful supplier data.
- Missing credentials do not count as failures but the supplier is omitted from
  attempts and listed in ``meta.skipped_suppliers``.

Managing credentials
--------------------

- Before issuing search/product calls, store client credentials per supplier
  using ``POST /space/credentials/{supplier}`` with the supplier-specific
  fields:

  - ``bm-parts``: ``token``
  - ``asg``: ``token`` *or* ``login`` + ``password``
  - ``omega``: ``key``
  - ``uniqtrade``: ``email``, ``password``, ``fingerprint``

- ``GET /space/credentials`` returns which suppliers have credentials for the
  authenticated user (values are not returned).

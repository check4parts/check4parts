System Architecture Overview
============================

Repository Layout
-----------------

The project is split into two main workspaces:

``backend/``
    FastAPI based integration layer that aggregates the provider APIs and exposes
    Check4Parts specific endpoints. The package entry point lives in
    :mod:`app.main` and wires together the provider routers from
    :mod:`app.api`.

``frontend/``
    Placeholder for the future client applications. The current effort focuses
    on the backend so the folder mainly contains scaffolding assets.


Backend Packages
----------------

``app/adapters``
    Adapter classes encapsulate low-level communication with each supplier API
    (BM Parts, InterCars, ASG, Omega, and UniqTrade). They are designed around
    ``httpx.AsyncClient`` instances with retry, timeout, and error handling
    logic. The adapters provide coroutine methods that map one-to-one to the
    upstream endpoints.

``app/api``
    FastAPI routers organised by provider. Each router converts HTTP requests
    into adapter calls, handles payload validation with Pydantic models, and
    exposes a consistent URL scheme (``/<provider-slug>/...``).

``app/dependencies``
    Dependency helpers that prepare adapter instances for request handlers. For
    example, :func:`app.dependencies.intercars.get_intercars_adapter` injects
    credentials and caches OAuth tokens, while :func:`app.dependencies.asg.get_asg_adapter`
    extracts login information from headers or bodies.

``app/services``
    Cross-cutting helpers that are reused by multiple adapters. Currently this
    hosts the token cache abstraction shared by InterCars routes.

``app/config.py``
    Centralises configuration read from environment variables (tokens, API
    keys, and feature toggles).


Runtime Flow
------------

1. :mod:`app.main` loads environment variables, creates the FastAPI
   application, and mounts the provider routers via the
   :data:`app.api.PROVIDER_REGISTRY` mapping.
2. Clients invoke URLs like ``/bm-parts/search/products`` or
   ``/omega/basket/add-product``. The corresponding router validates the request
   payload using the Pydantic models defined alongside each handler.
3. Route handlers depend on adapter factories (from ``app.dependencies``) to
   obtain ready-to-use HTTP clients with authentication state.
4. Adapter methods perform outbound HTTP calls, apply retries, translate errors
   into :class:`fastapi.HTTPException`, and return JSON payloads.
5. Responses are serialised back to the client using the default FastAPI JSON
   encoder.


Extending the System
--------------------

To add a new provider integration:

1. Implement a new adapter inside ``app/adapters`` modelled after the existing
   ones. Focus on providing coroutine methods that wrap each upstream endpoint
   and raise provider-specific exceptions.
2. Create a router module under ``app/api`` with request/response models and
   dependency injection of the adapter.
3. Register the router in ``app/api/__init__.py`` using a slug that matches the
   desired URL prefix.
4. Update the documentation under :doc:`api_reference` to include the new
   endpoints and sample payloads.


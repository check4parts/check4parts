# Backend Authentication Overview

## ASG flow

1. Clients authenticate by sending `POST /asg/login` with a JSON payload that
   includes `login` and `password`.
2. The `get_asg_adapter` dependency inspects the incoming request and
   configures an `ASGAdapter` instance with credentials gathered from:
   - The `Authorization` header (`Bearer <token>`).
   - The `X-ASG-Login` and `X-ASG-Password` headers.
   - The request body (for JSON payloads that contain `login` and `password`).
3. `ASGAdapter.login()` exchanges the credentials for a bearer token and caches
   the resulting `CachedCredentialToken` in memory keyed by the credential
   pair. The cache keeps the token until it expires or a 401 response is
   received.
4. Subsequent requests may either reuse the cached token by passing the same
   credentials (headers or body) or provide the bearer token in the
   `Authorization` header. When credentials are supplied, the dependency reloads
   any cached token before the handler executes, avoiding an extra login call.
5. `POST /asg/refresh` uses the cached credentials to exchange a new access
   token and updates the cache automatically. Any authenticated data request
   (for example `POST /asg/me`) will reuse the cached token if available.

### Token persistence hooks

`ASGAdapter` exposes `configure_token_persistence(load_hook=..., save_hook=...)`
so applications can persist cached tokens outside of process memory (for
example Redis). Hooks receive/return `CachedCredentialToken` instances and are
invoked whenever cached data is stored, loaded, or cleared. A simple example:

```python
from app.adapters.asg_adapter import ASGAdapter, CachedCredentialToken

_storage = {}


async def load_token(cache_key: str):
    raw = _storage.get(cache_key)
    return CachedCredentialToken.from_payload(raw) if raw else None


async def save_token(cache_key: str, token: CachedCredentialToken | None):
    if token is None:
        _storage.pop(cache_key, None)
    else:
        _storage[cache_key] = token.as_dict()


ASGAdapter.configure_token_persistence(
    load_hook=load_token,
    save_hook=save_token,
)
```

Clearing the persistence hooks or in-memory cache for testing can be done via
`ASGAdapter.configure_token_persistence()` and `ASGAdapter.clear_token_cache()`.

## Omega mutating GET routes

Historically the Omega adapter exposed basket, claim, contact, and expense
mutations as both `POST` and `GET` routes. Those `GET` variants have been
deprecated and are now disabled by default. Clients should migrate to the
existing `POST` endpoints, which remain unchanged.

For backwards compatibility you can temporarily re-enable the legacy `GET`
routes by setting the `ENABLE_MUTATING_GET_ROUTES` environment variable to a
truthy value (for example `1` or `true`) before starting the service. When
enabled, the routes are still marked as deprecated in the OpenAPI schema to
discourage new integrations from relying on them.

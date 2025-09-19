# Adapter Architecture

This project now exposes a shared abstraction for third-party parts providers. The key elements are:

- `app.adapters.base.BaseAdapter` centralizes HTTP handling, default headers, and error propagation for provider implementations.
- Each provider-specific adapter (for example, `BMPartsAdapter`) inherits from the base class, configures its authentication headers, and implements any search/fetch helpers it requires.
- `app.adapters.adapter_registry` maintains the set of initialized adapters that the API layer can query.

## Environment variables

Configure the BM Parts adapter with the following variables in your environment or `.env` file:

| Variable | Description |
| --- | --- |
| `BMPARTS_BASE_URL` | Base URL for the BM Parts API. |
| `BMPARTS_API_KEY` | Bearer token used to authenticate requests. |

## API endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/api/bmparts/data` | Returns the default BM Parts payload using the shared adapter abstraction. |
| `POST` | `/api/search` | Accepts a list of providers and fans the request out to each adapter, aggregating the results. |

### Aggregated search payload

```json
{
  "query": "alternator",
  "providers": ["bmparts"],
  "provider_params": {
    "bmparts": {
      "params": {"category": "electrical"}
    }
  }
}
```

When `providers` is omitted, all configured adapters are queried. Per-provider overrides allow the frontend to add query-string parameters or JSON bodies required by each provider.

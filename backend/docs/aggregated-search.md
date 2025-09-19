# Aggregated Search API

The aggregated search endpoint allows the frontend to fan out a single
request to multiple providers. Each provider executes its native search
routine and the backend merges the responses into a consistent payload.

## Endpoint

`POST /search/products`

### Authentication

Every request must include the Supabase bearer token in the `Authorization`
header. The endpoint reuses the shared `get_current_user` dependency, so no
additional provider-specific credentials are needed from the client.

### Request Body

```
{
  "query": "string",             // Required search phrase.
  "providers": [
    {
      "name": "bm-parts",       // Provider identifier.
      "options": {
        "include_crosses": true,
        "include_additional": false,
        "filters": { ... }       // Optional BM Parts query parameters.
      }
    }
  ]
}
```

### Response Shape

```
{
  "query": "string",
  "results": [
    {
      "provider": "bm-parts",
      "success": true,
      "data": { ... }            // Raw provider payload when successful.
    },
    {
      "provider": "omega",
      "success": false,
      "error": {
        "status_code": 400,
        "detail": {
          "message": "Unsupported provider 'omega'"
        }
      }
    }
  ]
}
```

Each entry in `results` contains the provider key, a `success` flag and either
`data` (on success) or `error` (on failure). A provider that is not yet
implemented returns a descriptive error payload without impacting the other
providers in the batch.

## Adding Providers

1. Implement or reuse an adapter that inherits from `ExternalAPIAdapter`.
2. Expose an async handler that accepts the `query` string and an `options`
   dictionary. The handler should return the upstream payload or raise a
   FastAPI `HTTPException`.
3. Register the handler in `PROVIDER_HANDLERS` inside
   `app/api/search.py`. The provider becomes instantly available to the
   aggregated search route.

This architecture keeps authentication shared while allowing each provider to
opt into the aggregated search experience with minimal boilerplate.

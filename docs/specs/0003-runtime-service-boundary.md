# Spec: Runtime Service Boundary

## Status

Verified

## Goal

Expose the verified deterministic finance workflows through a local FastAPI
ASGI service boundary before adding live providers, Telegram delivery,
persistence, Hermes Agent runtime integration, model routing, deployment, or
external service dependencies.

The service must preserve the public Python contracts and verified behavior from
`docs/specs/0001-finance-daily-market-brief.md` and
`docs/specs/0002-finance-entry-zone-strategy.md` while adding deterministic HTTP
request, response, and error contracts.

## Scenario

A developer imports the local ASGI app at `hermes_runtime.app:app` and exercises
it in process with a watchlist, explicit `as_of`, and a fixture payload.

For valid finance requests, the app routes directly to the matching verified
finance function and returns the exact deterministic markdown report inside a
structured JSON response.

Malformed HTTP request shapes return deterministic structured validation errors.
Finance-domain validation failures return deterministic structured domain
errors without stack traces. Unexpected internal exceptions return deterministic
structured internal errors without stack traces. Health and readiness checks
succeed without secrets, fixture files, live providers, model calls,
persistence, Telegram, or network access.

## In Scope

- A local FastAPI-only ASGI app.
- An importable app at `hermes_runtime.app:app`.
- `GET /health`.
- `GET /ready`.
- `POST /finance/daily-market-brief`.
- `POST /finance/entry-zone-strategy`.
- Deterministic request, success response, and error response schemas.
- HTTP error mapping for request validation, empty watchlists, finance-domain
  validation failures, and unexpected internal exceptions.
- Minimal dependency additions for FastAPI and in-process ASGI route tests.
- Regression preservation for existing verified finance behavior.
- The current single-user personal product assumption.

## Out Of Scope

- CLI interface.
- Uvicorn scripts, external server startup commands, deployment runners,
  Docker, AWS, or production runtime configuration.
- Telegram delivery.
- Hermes Agent runtime integration.
- Runtime finance subagent orchestration.
- Live providers, provider adapters, or fixture file loading inside handlers.
- Persistence, watchlist storage, scheduling, auth, or multi-user behavior.
- Model calls, OpenRouter gateway integration, or model-written synthesis.
- Brokerage integration, alerts, trade execution, order routing, or position
  sizing.
- Changes to the public finance APIs or deterministic report content from
  specs `0001` and `0002`.

## Contracts

### Runtime Interface

The implementation must create an importable local ASGI app:

```python
from hermes_runtime.app import app
```

The runtime package may be added under `src/hermes_runtime`. Dependency changes
are limited to FastAPI and the minimal in-process ASGI test dependency needed to
exercise the app.

The implementation must not add external server runners, deployment
configuration, auth middleware, provider configuration, model configuration,
persistence configuration, Telegram configuration, or runtime agent
orchestration.

### Endpoints

The service exposes these in-scope routes:

- `GET /health`
- `GET /ready`
- `POST /finance/daily-market-brief`
- `POST /finance/entry-zone-strategy`

`GET /health` returns `200` with:

```json
{
  "status": "ok"
}
```

`GET /ready` returns `200` with:

```json
{
  "status": "ready"
}
```

Readiness means only that the app imports and both finance POST route handlers
are registered. `/ready` must derive readiness from the app route table
containing both finance POST routes. It must not check secrets, fixture files,
network access, providers, databases, models, Telegram, deployment state, or
Hermes Agent runtime state.

Both finance POST endpoints accept a JSON object with:

```json
{
  "watchlist": ["NVDA", "AAPL"],
  "as_of": "2026-06-26T16:30:00-04:00",
  "fixture": {}
}
```

Unsupported extra request fields are request-validation errors.

`POST /finance/daily-market-brief` must pass `watchlist`, `as_of`, and
`fixture` directly to:

```python
generate_daily_market_brief(watchlist: list[str], as_of: str, fixture: dict) -> str
```

`POST /finance/entry-zone-strategy` must pass `watchlist`, `as_of`, and
`fixture` directly to:

```python
generate_entry_zone_strategy(watchlist: list[str], as_of: str, fixture: dict) -> str
```

Handlers must not load fixture files from disk. Tests may load fixture JSON and
send it as request payload.

### Success Response

Successful finance POST responses return `200` with:

```json
{
  "workflow": "daily_market_brief",
  "as_of": "2026-06-26T16:30:00-04:00",
  "report_markdown": "..."
}
```

Allowed `workflow` values are:

- `daily_market_brief`
- `entry_zone_strategy`

`workflow` is a finance endpoint enum, not a Hermes skill workflow or runtime
orchestration term. `as_of` echoes the request value. `report_markdown` is the
exact markdown string returned by the underlying finance function.

The runtime layer must not summarize, rewrite, stream, store, enrich, or
otherwise transform the returned report.

### Error Response

All service errors use this deterministic shape:

```json
{
  "error": {
    "type": "request_validation",
    "message": "...",
    "field": "watchlist"
  }
}
```

`field` may be omitted only when the error is not tied to a single request
field.

Malformed JSON, missing request fields, wrong field types, non-object request
bodies, or unsupported extra fields return `422` with
`type: "request_validation"`.

FastAPI or Pydantic validation errors must be normalized into the service error
envelope. Raw top-level `detail` arrays must not be returned.

Finance-domain validation failures from the verified finance functions,
including malformed fixtures, `as_of` mismatch, invalid timestamps, and invalid
fixture values, return `400` with `type: "domain_validation"`.

Empty watchlists return `400` with `type: "domain_validation"` at the HTTP
boundary, even if an underlying finance function would render a markdown
validation failure.

Unexpected internal exceptions return `500` with `type: "internal_error"`.
The response message must be `Internal runtime error.`. The response must be
deterministic and must not expose Python tracebacks, internal file paths,
secrets, environment values, dependency configuration, or raw exception object
representations.

The runtime maps `ValueError` raised by the verified finance functions during
request execution to `domain_validation`. All non-HTTP,
non-request-validation exceptions, including `AssertionError`, `TypeError`, and
unexpected dependency or runtime errors, map to `internal_error`.

Unsupported routes return `404` with `type: "not_found"`. Unsupported methods
return `405` with `type: "method_not_allowed"`. Both use the standard error
envelope and do not expose FastAPI's default `detail` shape.

### Finance Boundaries

The service must preserve the verified contracts from:

- `docs/specs/0001-finance-daily-market-brief.md`
- `docs/specs/0002-finance-entry-zone-strategy.md`

It must not mutate the supplied fixture, weaken research-only financial-advice
wording boundaries, introduce factual claims outside supplied fixtures, or
change the public Python APIs verified by `0001` and `0002`.

Visible degradation that the verified finance functions intentionally render as
markdown remains a successful report response. Only HTTP request-shape errors,
empty watchlists at the HTTP boundary, finance-domain validation failures, and
unexpected runtime failures are mapped to structured error responses.

## Failure Modes

- Missing, malformed, or non-object JSON request body.
- Missing request fields, wrong request field types, or unsupported extra body
  fields.
- Empty watchlist at the HTTP boundary.
- Finance-domain validation errors from existing verified workflows, including
  malformed fixtures, `as_of` mismatch, invalid timestamps, and invalid fixture
  values.
- Unsupported route or method.
- Unexpected internal exception.
- Health or readiness checks accidentally depending on secrets, files, network,
  providers, databases, models, Telegram, deployment state, or Hermes runtime.
- Runtime wrapper accidentally mutating fixtures or transforming finance
  markdown.

## Acceptance Criteria

- The implementation exposes an importable local ASGI app at
  `hermes_runtime.app:app`.
- `GET /health` returns `200` with `{"status": "ok"}` and requires no external
  dependency.
- `GET /ready` returns `200` with `{"status": "ready"}` based only on local app
  importability and finance route registration.
- `POST /finance/daily-market-brief` calls only
  `generate_daily_market_brief(...)` for finance report generation.
- `POST /finance/entry-zone-strategy` calls only
  `generate_entry_zone_strategy(...)` for finance report generation.
- Valid fixture payloads return `200` with `workflow`, echoed `as_of`, and exact
  `report_markdown`.
- Malformed JSON and request schema errors return deterministic `422`
  structured request-validation errors.
- Request validation errors use a top-level `error` object and do not expose a
  top-level `detail` response.
- Finance-domain validation failures return deterministic `400` structured
  domain-validation errors.
- Empty watchlists return deterministic `400` structured domain-validation
  errors at the HTTP boundary.
- Unexpected internal exceptions return deterministic `500` structured internal
  errors without stack traces.
- Unsupported routes return deterministic `404` structured not-found errors.
- Unsupported methods return deterministic `405` structured method-not-allowed
  errors.
- Existing `0001` and `0002` public Python APIs and regression tests remain
  valid.
- The service performs no network access, model calls, provider calls, Telegram
  calls, persistence, scheduling, auth, deployment behavior, fixture file
  loading inside handlers, or runtime subagent orchestration.

## Verification

- Add in-process ASGI route tests for `/health` and `/ready`.
- Assert both finance POST routes are registered and `/ready` derives readiness
  from the app route table without inspecting files, environment secrets,
  network, providers, databases, models, Telegram, deployment state, or Hermes
  runtime state.
- Add in-process ASGI route tests for valid daily market brief and entry-zone
  strategy POST requests.
- Assert successful POST responses include the expected `workflow`, echoed
  `as_of`, and exact markdown returned by the finance function.
- Add route tests for malformed JSON or schema errors as `422` structured
  request-validation errors.
- Assert request-validation responses use the top-level `error` envelope and do
  not return a top-level `detail` array.
- Add route tests for finance-domain validation errors as `400` structured
  domain-validation errors.
- Add route tests for empty watchlists as `400` structured domain-validation
  errors.
- Add route tests for unexpected internal exceptions as `500` structured
  internal errors without stack traces.
- Add route tests for unsupported routes as `404` structured not-found errors
  and unsupported methods as `405` structured method-not-allowed errors.
- Add route tests that send fixture data in the request body and monkeypatch the
  finance functions to assert handlers pass the payload through without opening
  fixture paths or calling repo fixture loaders.
- Keep the verified `0001` and `0002` finance tests in the regression baseline.
- Run `uv run pytest`.
- Run `uv run ruff check .`.

## Open Questions

None blocking for implementation.

Deferred to later specs:

- Whether a CLI should be added.
- Whether runtime responses should support formats beyond markdown.
- How this service boundary connects to Hermes Agent runtime integration.
- How this service boundary connects to Telegram delivery.

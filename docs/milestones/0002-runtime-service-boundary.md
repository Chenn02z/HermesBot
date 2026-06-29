# Milestone: Runtime Service Boundary

## Status

Verified

## Source

Split from the consolidated roadmap requirements handoff, which has been
decomposed and removed. This milestone was implemented and verified as the
local runtime boundary after the verified fixture-backed finance foundation.

## Goal

Define a local runtime boundary around the verified deterministic finance
functions before adding live providers, Telegram delivery, persistence, or
deployment.

This milestone makes the verified finance functions available through a local
FastAPI service boundary. It does not introduce runtime subagent orchestration
or external service dependencies.

## Scenario

The developer invokes a local in-process ASGI app with a watchlist, explicit
`as_of`, and fixture payload. The app routes the request to one of the verified
finance functions and returns the exact deterministic markdown report inside a
structured JSON response.

Invalid HTTP request shapes return deterministic structured validation errors.
Finance-domain validation failures return deterministic structured domain
errors without stack traces. Health and readiness checks succeed without
secrets, fixture files, live providers, model calls, persistence, Telegram, or
network access.

## In Scope

- A local FastAPI-only ASGI service boundary.
- An importable app at `hermes_runtime.app:app`.
- HTTP endpoints for the verified daily market brief and entry-zone strategy
  workflows.
- Deterministic request, success response, and error response schemas.
- Health and readiness endpoints that depend only on local importability and
  route registration.
- Minimal dependency additions for FastAPI and in-process ASGI route tests.
- The current single-user personal product assumption.

## Out Of Scope

- CLI interface.
- External server startup commands, uvicorn scripts, deployment runners, Docker,
  AWS, or production runtime configuration.
- Telegram delivery.
- Hermes Agent runtime integration.
- Runtime finance subagent orchestration.
- Live providers, provider adapters, or fixture file loading inside handlers.
- Persistence, watchlist storage, scheduling, auth, or multi-user behavior.
- Model calls, OpenRouter gateway integration, or model-written synthesis.
- Brokerage integration, alerts, trade execution, order routing, or position
  sizing.

## Contracts

### Runtime Interface

The milestone implements a local FastAPI-only ASGI app importable as:

```python
from hermes_runtime.app import app
```

In-scope dependency changes are limited to FastAPI and the minimal test
dependency needed to exercise the ASGI app in process. The implementation must
not add an external server runner, deployment configuration, auth middleware,
provider configuration, model configuration, persistence configuration, or
Telegram configuration.

### Endpoints

The service exposes:

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

Readiness means only that the app imports and both finance route handlers are
registered. It must not check secrets, files, network access, providers,
databases, models, Telegram, deployment state, or Hermes Agent runtime state.

Both POST endpoints accept this JSON body:

```json
{
  "watchlist": ["NVDA", "AAPL"],
  "as_of": "2026-06-26T16:30:00-04:00",
  "fixture": {}
}
```

The daily market brief endpoint must pass `watchlist`, `as_of`, and `fixture`
directly to:

```python
generate_daily_market_brief(watchlist: list[str], as_of: str, fixture: dict) -> str
```

The entry-zone strategy endpoint must pass `watchlist`, `as_of`, and `fixture`
directly to:

```python
generate_entry_zone_strategy(watchlist: list[str], as_of: str, fixture: dict) -> str
```

Runtime handlers must not load fixture files from disk. Tests may load fixture
JSON and send it as request payload.

### Success Response

Successful POST responses return `200` with:

```json
{
  "workflow": "daily_market_brief",
  "as_of": "2026-06-26T16:30:00-04:00",
  "report_markdown": "..."
}
```

For this milestone, `workflow` is a finance endpoint enum, not a Hermes skill
workflow or runtime orchestration term. Allowed values are:

- `daily_market_brief`
- `entry_zone_strategy`

`as_of` echoes the request value. `report_markdown` is the exact markdown string
returned by the underlying verified finance function. The runtime layer must
not summarize, rewrite, stream, store, enrich, or otherwise transform the
returned report.

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

- Malformed JSON, missing request fields, wrong field types, or extra
  unsupported body shapes return `422` with `type: "request_validation"`.
- Finance-domain validation failures from the verified finance functions,
  including malformed fixtures, `as_of` mismatch, invalid timestamps, and
  invalid fixture values, return `400` with `type: "domain_validation"`.
- Empty watchlists return `400` with `type: "domain_validation"` at the HTTP
  boundary, even if an underlying finance function would render a markdown
  validation failure.
- Unexpected internal exceptions return a deterministic structured error
  without stack traces.

### Finance Boundaries

The service layer must preserve the verified finance contracts from:

- `docs/specs/0001-finance-daily-market-brief.md`
- `docs/specs/0002-finance-entry-zone-strategy.md`

It must not mutate the supplied fixture, weaken research-only financial-advice
wording boundaries, introduce factual claims outside supplied fixtures, or
change the public Python APIs verified by `0001` and `0002`.

Visible degradation that the verified finance functions intentionally render as
markdown remains a successful report response. Only HTTP request-shape errors
and finance-domain validation failures are mapped to structured error
responses.

## Failure Modes

- Missing, malformed, or non-object JSON request body.
- Missing request fields, wrong request field types, or unsupported extra body
  shapes.
- Empty watchlist at the HTTP boundary.
- Finance-domain validation errors from existing verified workflows.
- Unsupported route or method.
- Unexpected internal exception.
- Health or readiness checks accidentally depending on secrets, files, network,
  providers, databases, models, Telegram, deployment state, or Hermes runtime.

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
- Malformed JSON and schema errors return deterministic `422` structured
  errors.
- Finance-domain validation failures return deterministic `400` structured
  errors.
- Empty watchlists return deterministic `400` structured domain errors at the
  HTTP boundary.
- Existing `0001` and `0002` public Python APIs and regression tests remain
  valid.
- The service performs no network access, model calls, provider calls, Telegram
  calls, persistence, scheduling, auth, deployment behavior, fixture file
  loading inside handlers, or runtime subagent orchestration.

## Verification

- Add FastAPI/TestClient or equivalent in-process ASGI tests for both valid
  finance POST routes.
- Add route tests for malformed JSON or schema errors as `422` structured
  request-validation errors.
- Add route tests for finance-domain validation errors as `400` structured
  domain-validation errors.
- Add route tests for empty watchlists as `400` structured domain-validation
  errors.
- Add route tests for `/health` and `/ready` proving no external dependency is
  required.
- Keep the verified `0001` and `0002` finance tests in the regression baseline.
- Run `uv run pytest`.
- Run `uv run ruff check .`.

## Open Questions

- None blocking for implementation.

Deferred to later specs:

- Whether a CLI should be added.
- Whether runtime responses should support formats beyond markdown.
- How this service boundary connects to Hermes Agent runtime integration.
- How this service boundary connects to Telegram delivery.

## Handoff

- Producer skill: `$hermes-spec`
- Intended consumer skill: `$hermes-dev-loop`
- Artifact path: `docs/milestones/0002-runtime-service-boundary.md`
- Status: Verified.
- Settled decisions: runtime boundary comes before live providers, Telegram,
  persistence, Hermes Agent runtime integration, model routing, and deployment;
  the first interface is a local FastAPI-only ASGI service at
  `hermes_runtime.app:app`; CLI is deferred.
- Unresolved blockers: none for implementation.
- Required next reads: `docs/milestones/0001-finance-agent-foundation.md`,
  `docs/specs/0001-finance-daily-market-brief.md`,
  `docs/specs/0002-finance-entry-zone-strategy.md`, and this milestone.
- Key contracts and acceptance criteria: expose `/health`, `/ready`,
  `/finance/daily-market-brief`, and `/finance/entry-zone-strategy`; accept
  request-body fixture payloads; return exact markdown in structured success
  responses; map request validation to deterministic `422` errors and
  finance-domain validation to deterministic `400` errors; preserve the verified
  finance APIs and exclusions.
- Verification: `docs/specs/0003-runtime-service-boundary.md` is Verified; the
  runtime app and in-process ASGI route tests exist in the current repo state.
- Remaining open questions: non-blocking follow-up specs for CLI, non-markdown
  response formats, Hermes Agent runtime integration, and Telegram delivery.
- Agent routing log: `spec-planner` used; `spec-griller` used; focused
  `$grill-with-docs` check performed by the main agent against the canonical
  docs and current repo shape.

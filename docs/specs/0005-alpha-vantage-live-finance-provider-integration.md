# Spec: AlphaVantage Live Finance Provider Integration

## Status

Draft

## Goal

Define the first live finance provider integration using AlphaVantage while
preserving the deterministic finance evidence boundary.

Live provider code must fetch AlphaVantage evidence, map it through the
accepted and verified finance evidence adapter contract, and then reuse the
existing deterministic finance report generators. This spec is intentionally
Draft until `docs/specs/0004-finance-evidence-provider-contract.md` is
Verified.

## Scenario

A developer calls a finance-layer live function for a watchlist and explicit
`as_of`. The function reads `ALPHAVANTAGE_API_KEY`, fetches AlphaVantage data
for the supported tickers and market context, groups the raw provider payloads,
maps them through the finance evidence adapter, and returns the deterministic
daily market brief or entry-zone strategy report.

If credentials are missing, the provider is unavailable, the API returns quota
or rate-limit information, a response is malformed, timestamps are stale or
ambiguous, or only partial evidence is available, live code returns a
deterministic failure or visible degradation path without invented evidence.

## In Scope

- AlphaVantage as the first live finance provider.
- Finance-layer importable live functions for both verified workflows.
- Environment-based live credential lookup using `ALPHAVANTAGE_API_KEY`.
- Fetching quote, market, news, and technical indicator evidence needed by the
  daily market brief and entry-zone strategy workflows.
- Grouping raw AlphaVantage response bodies into adapter payload groups.
- Passing all provider evidence through the verified finance evidence adapter.
- Fixture-backed tests using recorded or mocked AlphaVantage-shaped payloads.
- Optional local-only live smoke tests gated behind credentials and explicit
  opt-in.

## Out Of Scope

- Implementation before `docs/specs/0004-finance-evidence-provider-contract.md`
  is Verified.
- Additional live providers.
- Direct use of raw AlphaVantage payloads by report renderers.
- Changing the public daily market brief or entry-zone strategy APIs.
- Changing `hermes_runtime` routes, schemas, readiness checks, or runtime
  configuration.
- Telegram delivery, persistence, scheduling, auth, deployment, or multi-user
  behavior.
- Model calls, OpenRouter gateway integration, or model-written synthesis.
- Brokerage integration, alerts, trade execution, order routing, position
  sizing, or personalized financial advice.

## Contracts

### Dependency On Adapter Spec

This spec must remain Draft until
`docs/specs/0004-finance-evidence-provider-contract.md` is Verified. The live
provider implementation must consume the verified adapter API and result
contract rather than redefining adapter behavior locally.

### Provider And Credential

AlphaVantage is the only provider in scope. Live execution reads the API key
from `ALPHAVANTAGE_API_KEY`.

The API key must never be committed, logged, echoed in errors, included in
fixtures, embedded in generated reports, or exposed through diagnostics.
Module import and normal automated tests must not require the key.

### Public Finance-Layer API

The child implementation must expose importable live functions for both
verified workflows. Candidate function names are:

```python
generate_live_daily_market_brief(watchlist: list[str], as_of: str) -> str
generate_live_entry_zone_strategy(watchlist: list[str], as_of: str) -> str
```

The exact import paths remain open while this spec is Draft. The public surface
must stay inside the finance package boundary and must not add runtime HTTP
routes.

### Provider Payloads

The implementation must fetch raw AlphaVantage response bodies in production
code and group them into the payload keys required by the verified adapter
spec. Recorded or mocked AlphaVantage payloads are test-only inputs. Candidate
AlphaVantage endpoint functions include:

- `GLOBAL_QUOTE`
- `TIME_SERIES_DAILY`
- `NEWS_SENTIMENT`
- `SMA`
- `RSI`
- `ATR`

This endpoint list is not accepted implementation scope until this spec is
revised after adapter verification. The accepted version of this spec must name
the exact endpoint functions, response fields, timestamp mapping rules, and
payload-group keys used for each finance workflow.

### Runtime Boundary

This spec does not add, remove, or change any `hermes_runtime` route, request
schema, response schema, readiness behavior, or runtime configuration contract.
A later runtime milestone may decide whether live-provider behavior should be
exposed through HTTP endpoints.

### Test Policy

Normal `uv run pytest` must pass without live credentials and without network
access. Fixture-backed tests with recorded or mocked AlphaVantage-shaped
payloads are the baseline.

Optional live smoke tests may run only when `ALPHAVANTAGE_API_KEY` is set and
the developer supplies an explicit opt-in marker or environment flag.

### Failure Handling

Missing `ALPHAVANTAGE_API_KEY`, auth failures, provider quota or rate-limit
responses, timeouts, non-2xx HTTP responses, malformed JSON, provider error
payloads, missing expected fields, stale timestamps, invalid symbols, and
partial payloads must produce deterministic fetch or adapter failures.

Adapter `complete` results and adapter `partial` results with
validator-accepted fixtures proceed to the existing deterministic report
generator. Adapter `failed` results do not render a finance report.

The implementation must not invent prices, market context, news, indicators,
timestamps, sources, or symbol mappings. It must not retry implicitly unless a
future accepted revision defines bounded deterministic retry behavior.

## Failure Modes

- Missing `ALPHAVANTAGE_API_KEY`.
- Secret value appears in logs, errors, diagnostics, fixtures, or reports.
- Module import or normal tests require live credentials.
- Provider auth failure, quota or rate-limit response, timeout, non-2xx
  response, malformed JSON, or provider error payload.
- AlphaVantage response fields are missing, stale, future-dated, timezone-less,
  or incompatible with canonical finance timestamp requirements.
- Provider symbol does not match the requested normalized ticker.
- Partial payloads bypass adapter diagnostics.
- Live code passes raw provider payloads directly to report renderers.
- Runtime HTTP routes are changed by live provider work.
- Tests depend on network access by default.
- Live provider behavior weakens research-only finance wording boundaries.

## Acceptance Criteria

This spec is not yet accepted for implementation.

Before this spec can be marked Accepted:

- `docs/specs/0004-finance-evidence-provider-contract.md` is Verified.
- Exact AlphaVantage endpoint functions are named for daily market brief and
  entry-zone strategy evidence.
- Exact AlphaVantage response fields and payload-group keys are named.
- Timestamp mapping rules satisfy canonical ISO-8601 timezone-offset
  requirements from the verified finance specs.
- Exact import paths for the live finance-layer functions are named.
- The optional live smoke-test opt-in mechanism is named.
- The spec has been grilled again after the above details are settled.

Implementation acceptance criteria after acceptance:

- AlphaVantage is the only live provider target.
- Live finance functions cover both daily market brief and entry-zone strategy.
- Live functions read `ALPHAVANTAGE_API_KEY` only at execution time.
- Normal imports and normal tests do not require `ALPHAVANTAGE_API_KEY`.
- All AlphaVantage payloads pass through the verified adapter contract before
  deterministic report generation.
- No `hermes_runtime` endpoint, request schema, response schema, readiness
  behavior, or runtime configuration contract changes.
- Missing credentials, auth failures, quota/rate-limit responses, timeouts,
  stale data, invalid symbols, malformed payloads, and partial payloads are
  handled deterministically.
- Research-only wording remains enforced by the existing deterministic finance
  report generators.

## Verification

- Add fixture-backed tests for AlphaVantage-shaped payload grouping without live
  credentials.
- Add fixture-backed tests for both live finance workflow functions using
  recorded or mocked AlphaVantage responses.
- Add tests for missing credentials, auth failures, quota/rate-limit responses,
  timeouts, non-2xx responses, malformed JSON, provider error payloads, stale
  data, invalid symbols, and partial payloads.
- Add tests proving normal imports and normal test collection do not require
  `ALPHAVANTAGE_API_KEY`.
- Add optional local-only live smoke tests gated behind
  `ALPHAVANTAGE_API_KEY` and explicit opt-in.
- Keep verified finance, runtime, and adapter regression tests in the baseline.
- Run `uv run pytest` without requiring live credentials.
- Run `uv run ruff check .`.

## Open Questions

Blocking before this spec can be marked Accepted:

- Which exact AlphaVantage endpoint functions and response fields satisfy the
  canonical evidence needs for both verified finance workflows?
- How should AlphaVantage date-only daily and technical-indicator payloads map
  to canonical ISO-8601 datetimes with timezone offsets without inventing
  freshness?
- What are the final import paths for the live finance-layer functions?
- What explicit opt-in marker or environment flag should gate live smoke tests?

Deferred to later specs:

- Whether bounded deterministic retry behavior is worthwhile.
- Whether a later runtime milestone should expose live-provider behavior through
  HTTP endpoints.

## Handoff

- Producer skill: `$hermes-spec`
- Intended consumer skill: `$hermes-spec` for a later acceptance revision after
  `docs/specs/0004-finance-evidence-provider-contract.md` is Verified.
- Source milestone path:
  `docs/milestones/0004-live-finance-provider-integration.md`
- Artifact path:
  `docs/specs/0005-alpha-vantage-live-finance-provider-integration.md`
- Status: Draft.
- Settled decisions carried forward: AlphaVantage is the first live provider;
  `ALPHAVANTAGE_API_KEY` is the live credential name; live finance work remains
  finance-layer only; no `hermes_runtime` endpoint changes are included;
  normal tests must remain credential-free; optional local smoke tests require
  credentials and explicit opt-in.
- Unresolved blockers: adapter spec verification; exact endpoint and response
  field mapping; timestamp mapping rules; final import paths; live smoke-test
  opt-in marker.
- Verification expectations: fixture-backed AlphaVantage-shaped tests,
  provider failure tests, normal credential-free `uv run pytest`, optional
  local live smoke tests, and `uv run ruff check .`.
- Agent routing log: `spec-planner` used; `spec-griller` used.

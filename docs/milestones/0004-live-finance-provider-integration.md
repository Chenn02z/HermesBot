# Milestone: Live Finance Provider Integration

## Status

Accepted

## Source

Split from the consolidated roadmap requirements handoff, which has been
decomposed and removed. A 2026-06-29 `$hermes-requirements` acceptance run
settled AlphaVantage as the first live finance provider and removed the prior
provider-choice blocker.

## Goal

Integrate AlphaVantage as the first live finance provider after the
provider-neutral evidence adapter contract is accepted and verified.

Live provider evidence must pass through the accepted finance evidence adapter
boundary before deterministic report generation. Deterministic finance
functions remain the only report source of truth.

## Scope Boundary

- Fetch live quote, market, news, and strategy inputs from AlphaVantage only
  through finance-layer provider code.
- Cover both verified finance workflows: daily market brief and entry-zone
  strategy.
- Expose importable finance-layer live functions only.
- Reuse deterministic finance report generation after adapter validation.
- Keep live behavior optional and explicitly configured.
- Read the live credential from `ALPHAVANTAGE_API_KEY`.
- Exclude runtime HTTP route changes, brokerage, trade execution,
  personalized advice, Telegram delivery, scheduling, persistence, model calls,
  and deployment.

## Scenarios

- The developer calls an importable live daily market brief function with a
  supported watchlist and explicit `as_of`; the function fetches AlphaVantage
  evidence, maps it into canonical evidence through the accepted adapter
  contract, and renders a research-only report with the existing deterministic
  daily market brief function.
- The developer calls an importable live entry-zone strategy function with a
  supported watchlist and explicit `as_of`; the function fetches AlphaVantage
  evidence, maps it into canonical evidence through the accepted adapter
  contract, and renders a research-only report with the existing deterministic
  entry-zone strategy function.
- Missing credentials, provider outage, quota/rate-limit response, auth
  failure, timeout, stale data, invalid symbol, malformed payload, or partial
  data produces deterministic diagnostics or failure results without invented
  evidence.

## Contracts

### Dependency On `0003`

Implementation of this live provider milestone must not begin until
`docs/specs/0004-finance-evidence-provider-contract.md` is Verified. The live
provider spec may be drafted from this Accepted milestone, but live
implementation must wait for the adapter result, payload grouping, diagnostics,
and canonical fixture contracts to be verified.

### Provider Boundary

AlphaVantage is the first accepted live finance provider for this milestone.
The child spec must name the AlphaVantage endpoint functions it uses and map
their raw response bodies through the provider-neutral adapter layer. Candidate
endpoint functions include `GLOBAL_QUOTE`, `TIME_SERIES_DAILY`,
`NEWS_SENTIMENT`, `SMA`, `RSI`, and `ATR`; the child spec must narrow this list
to the minimum needed for the verified finance workflows.

Provider payloads must not bypass adapter validation. Live code must not pass
raw AlphaVantage payloads directly into report renderers.

### Public Finance-Layer API

The child spec must define importable finance-layer live functions for both
verified workflows. Candidate function names are:

```python
generate_live_daily_market_brief(watchlist: list[str], as_of: str) -> str
generate_live_entry_zone_strategy(watchlist: list[str], as_of: str) -> str
```

The exact import paths may be chosen in the child spec, but the public surface
must remain inside the finance package boundary.

This milestone does not add, remove, or change any `hermes_runtime` route,
request schema, response schema, readiness behavior, or runtime configuration
contract.

### Credentials And Test Policy

Live execution reads `ALPHAVANTAGE_API_KEY` from the environment. The key must
never be committed, logged, echoed in errors, included in fixtures, or embedded
in docs beyond the environment variable name.

Module import and normal automated tests must not require live credentials.
Fixture-backed tests are the required baseline. Optional local live smoke tests
may run only when `ALPHAVANTAGE_API_KEY` is set and an explicit opt-in marker or
environment flag is supplied by the developer.

### Failure Handling

Missing `ALPHAVANTAGE_API_KEY`, auth failures, provider quota/rate-limit
responses, timeouts, non-2xx HTTP responses, malformed JSON, provider error
payloads, missing expected fields, stale timestamps, invalid symbols, and
partial payloads must produce deterministic fetch or adapter failures.

The implementation must not invent prices, market context, news, indicators,
timestamps, sources, or symbol mappings to recover from provider failures. It
must not retry implicitly unless a child spec explicitly defines bounded,
deterministic retry behavior.

## Acceptance Criteria Candidates

- AlphaVantage is the only first live provider target for this milestone.
- The child spec covers both verified finance workflows.
- Importable finance-layer live functions fetch AlphaVantage evidence, map it
  through the accepted adapter contract, and call the existing deterministic
  report generators.
- No AlphaVantage payload bypasses adapter validation.
- No `hermes_runtime` endpoint, request schema, response schema, readiness
  behavior, or runtime configuration contract changes.
- `ALPHAVANTAGE_API_KEY` is the only accepted live credential name.
- Module import and normal `uv run pytest` do not require live credentials.
- Optional local live smoke tests are gated behind explicit credentials and
  explicit developer opt-in.
- Provider errors, quota/rate-limit responses, auth failures, timeouts, stale
  data, invalid symbols, malformed payloads, and partial payloads are handled
  deterministically.
- Research-only wording remains enforced by the existing deterministic finance
  report generators.

## Verification

- Add fixture-backed tests for AlphaVantage-shaped payload fetching and mapping
  behavior without live credentials.
- Add fixture-backed tests for both live finance workflow functions using
  recorded or mocked AlphaVantage responses.
- Add tests for missing credentials, auth failures, quota/rate-limit responses,
  timeouts, non-2xx responses, malformed JSON, provider error payloads, stale
  data, invalid symbols, and partial payloads.
- Add optional local-only live smoke tests gated behind
  `ALPHAVANTAGE_API_KEY` and explicit opt-in.
- Run `uv run pytest` without requiring live credentials.
- Run `uv run ruff check .`.

## Open Questions

None blocking for milestone acceptance.

Deferred to child specs:

- Exact AlphaVantage endpoints and payload keys required for each verified
  finance workflow.
- Exact import paths for the live finance-layer public functions.
- Whether bounded deterministic retry behavior is worthwhile.
- Whether a later runtime milestone should expose live-provider behavior through
  HTTP endpoints.

## Handoff

- Producer skill: `$hermes-requirements`
- Intended consumer skill: `$hermes-spec`.
- Artifact path: `docs/milestones/0004-live-finance-provider-integration.md`
- Status: Accepted.
- Settled decisions: AlphaVantage is the first live provider; live finance work
  is limited to finance-layer importable functions for daily market brief and
  entry-zone strategy; no `hermes_runtime` endpoint changes are included;
  `ALPHAVANTAGE_API_KEY` is the live credential name; normal tests remain
  credential-free; optional local smoke tests are credential-gated and require
  explicit opt-in.
- Unresolved blockers: none.
- Required next reads:
  `docs/milestones/0003-finance-evidence-provider-contract.md`, verified
  finance specs `0001` and `0002`,
  `docs/specs/0003-runtime-service-boundary.md`, and AlphaVantage official API
  documentation.
- Key contracts and acceptance criteria: fetch AlphaVantage evidence only in
  finance-layer provider code; map provider payloads through accepted adapters;
  cover both verified finance workflows; keep normal tests credential-free;
  preserve deterministic finance truth and research-only wording; prohibit
  runtime endpoint changes, models, Telegram, persistence, deployment, and
  brokerage behavior.
- Verification expectations: fixture-backed tests for both live workflow
  functions, provider failure tests, existing finance regression baseline,
  optional credential-gated live smoke tests, `uv run pytest`, and
  `uv run ruff check .`.
- Remaining open questions: exact AlphaVantage endpoint set, public live import
  paths, optional retry policy, and later runtime exposure are deferred to child
  specs.
- Agent routing log: `$hermes-requirements` used `spec-planner`,
  `spec-griller`, `$grill-with-docs`, and `doc-curator` during the 2026-06-29
  acceptance run.

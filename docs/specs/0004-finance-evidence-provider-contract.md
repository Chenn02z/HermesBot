# Spec: Finance Evidence Provider Contract

## Status

Accepted

## Goal

Add a finance-layer evidence adapter contract that maps static or recorded
provider-shaped payloads into the canonical fixture shapes consumed by the
verified deterministic finance workflows:

```python
generate_daily_market_brief(watchlist: list[str], as_of: str, fixture: dict) -> str
generate_entry_zone_strategy(watchlist: list[str], as_of: str, fixture: dict) -> str
```

The adapter layer must preserve provider provenance, timestamps, partial-data
diagnostics, and provider failures before report generation. Existing finance
report functions remain the report source of truth and must not change.

## Scenario

A developer supplies a watchlist, an explicit `as_of`, a provider label, and
recorded provider-shaped payloads grouped by evidence type. The adapter maps
the payloads into canonical JSON-compatible fixtures for the daily market brief
or entry-zone strategy workflow and returns a deterministic result containing
the fixture, status, provider metadata, and ordered diagnostics.

If provider payloads are malformed, partial, stale, future-dated, unsupported,
or inconsistent with the requested symbol, the adapter returns deterministic
diagnostics and omits invented evidence. When enough canonical evidence remains
for the verified finance workflow to degrade visibly, the adapter may return a
partial fixture that still passes existing finance validation.

## In Scope

- A new finance-layer module at `hermes_finance.evidence_adapters`.
- Importable adapter result and diagnostic types.
- Separate mapping functions for daily market brief and entry-zone strategy
  evidence.
- Static or recorded provider-shaped payloads supplied by callers or tests.
- Canonical fixture output for `docs/specs/0001-finance-daily-market-brief.md`.
- Canonical fixture output for `docs/specs/0002-finance-entry-zone-strategy.md`.
- Deterministic diagnostics for partial, stale, invalid, unsupported,
  malformed, provider-error, symbol-mismatch, missing-provenance, and skipped
  evidence cases.
- Fixture-backed adapter tests and integration-style tests through the existing
  finance report functions.
- Preservation of the current single-user personal product assumption.

## Out Of Scope

- Live network calls, provider SDKs, HTTP clients, provider credentials, or
  environment-based provider configuration.
- AlphaVantage-specific live fetch behavior.
- Modifying the public daily market brief or entry-zone strategy APIs.
- Changing `hermes_runtime` routes, schemas, readiness checks, or runtime
  configuration.
- Depending on `hermes_runtime` from the finance adapter layer.
- Telegram delivery, persistence, scheduling, auth, deployment, or multi-user
  behavior.
- Model calls, OpenRouter gateway integration, or model-written synthesis.
- Brokerage integration, alerts, trade execution, order routing, position
  sizing, or personalized financial advice.

## Contracts

### Public Adapter API

The implementation must expose these importable functions from
`hermes_finance.evidence_adapters`:

```python
from collections.abc import Mapping

map_daily_market_brief_evidence(
    watchlist: list[str],
    as_of: str,
    provider: str,
    payloads: Mapping[str, object],
) -> AdapterResult

map_entry_zone_strategy_evidence(
    watchlist: list[str],
    as_of: str,
    provider: str,
    payloads: Mapping[str, object],
) -> AdapterResult
```

The module must also expose `AdapterResult` and `AdapterDiagnostic`.

Adapter functions must not mutate caller-supplied payloads, load fixture files,
perform provider discovery, fetch live data, read credentials, import
`hermes_runtime`, call models, call Telegram, persist data, schedule work, or
touch brokerage systems.

### Payload Groups

`payloads` are verbatim recorded provider response bodies grouped by evidence
type. Provider-specific specs must name their exact raw response keys, but this
spec requires the adapter layer to accept these provider-neutral group names
when present:

- `market_context`
- `quotes`
- `ranges`
- `support_levels`
- `news`
- `moving_averages`
- `momentum`
- `range_52w`
- `support_resistance`
- `volatility`
- `volume`

Each payload group value must be either:

- a mapping from normalized requested ticker symbol to that symbol's raw
  provider response body;
- a mapping from market proxy symbol or label to that proxy's raw provider
  response body, for `market_context`; or
- a list of raw provider response bodies only when the evidence group is not
  symbol-specific, such as broad market notes.

For multi-symbol watchlists, symbol-specific evidence groups must preserve one
entry per normalized requested ticker when evidence exists. A provider-specific
spec may define nested raw response structure inside each group value, but it
must not require the provider-neutral adapter API to infer symbol ownership
from an unkeyed blob. Missing ticker keys are partial payloads and must produce
diagnostics.

Unknown payload groups must be ignored with a deterministic diagnostic rather
than treated as canonical evidence. Missing optional groups may produce partial
results only where the verified finance specs already define visible
degradation.

### Adapter Result

`AdapterResult` must carry:

- `fixture`: canonical JSON-compatible fixture data, or `None` when no valid
  fixture can be produced.
- `status`: one of `complete`, `partial`, or `failed`.
- `diagnostics`: an ordered list of `AdapterDiagnostic`.
- `provider`: the caller-supplied provider label.
- `as_of`: the caller-supplied `as_of`.

`AdapterDiagnostic` must carry:

- `type`: deterministic diagnostic type.
- `message`: deterministic human-readable message that does not include stack
  traces, secrets, raw exception representations, or provider credentials.
- `symbol`: affected normalized symbol when applicable.
- `field`: affected provider or canonical field when applicable.

Allowed diagnostic types are:

- `provider_error`
- `missing_field`
- `missing_provenance`
- `malformed_payload`
- `partial_payload`
- `stale_timestamp`
- `future_timestamp`
- `invalid_timestamp`
- `invalid_symbol`
- `unsupported_symbol`
- `symbol_mismatch`
- `skipped_evidence_group`
- `unknown_evidence_group`

Diagnostics may be empty only when `status` is `complete`.

### Canonical Fixture Output

Adapter-produced fixtures must be accepted by the existing finance validators
and public report functions without changing those APIs.

A daily market brief fixture must include the required top-level structure from
`0001` when a fixture is produced:

- top-level `as_of`
- `market_context.indices`
- top-level `tickers`

An entry-zone strategy fixture must include the required top-level structure
from `0002` when a fixture is produced:

- top-level `as_of`
- top-level `tickers`

The adapter may include optional canonical fields only when they are supported
by `0001` or `0002`. Missing required top-level fixture structure must produce
`fixture: None` and `status: failed`.

### Provenance, Symbols, And Freshness

Ticker normalization must match the verified finance specs: trim leading and
trailing whitespace and uppercase only.

Mapped canonical evidence must preserve source and timestamp metadata needed by
the verified finance freshness rules:

- `as_of` must exactly match the canonical fixture `as_of`.
- Provider timestamps mapped into canonical evidence must be valid ISO-8601
  datetimes with timezone offsets.
- Missing, malformed, stale, or future-dated timestamps must produce
  diagnostics.
- Canonical `source` fields must identify recorded provider provenance and must
  not claim live data for static or recorded fixtures.
- Provider symbols that do not match the requested normalized ticker must
  produce diagnostics instead of silent substitution.
- Inputs that the provider explicitly identifies as ambiguous, unsupported, or
  invalid for the requested normalized symbol must populate canonical
  `invalid_inputs` when the target verified finance spec supports that field.
  Provider symbol mismatches, malformed evidence, missing evidence, stale
  evidence, and provider errors remain diagnostics and must not be represented
  as `invalid_inputs` unless the provider explicitly classifies the requested
  symbol itself as ambiguous, unsupported, or invalid.

### Finance Boundaries

Adapters must preserve the finance boundaries from `0001` and `0002`.

They must not weaken research-only wording boundaries, introduce factual claims
outside supplied provider evidence, bypass existing finance validation, render
reports, or inject adapter diagnostics into finance report text.

## Failure Modes

- Malformed recorded provider payload.
- Provider error payload.
- Unknown or missing evidence group.
- Partial provider payload.
- Missing required quote, market, news, range, or strategy fields.
- Stale, missing, malformed, timezone-less, or future-dated timestamps.
- Unsupported, invalid, or ambiguous symbol.
- Provider symbol mismatch with the requested normalized ticker.
- Missing provider provenance or source metadata.
- Adapter diagnostics are lost before report generation.
- Adapter output bypasses existing finance validation.
- Adapter invents prices, market context, news, strategy indicators,
  timestamps, sources, or ticker mappings.
- Adapter introduces live network access, provider SDK calls, credential reads,
  model calls, Telegram behavior, runtime endpoint changes, persistence,
  scheduling, deployment behavior, or brokerage behavior.

## Acceptance Criteria

- `hermes_finance.evidence_adapters` exposes `AdapterResult`,
  `AdapterDiagnostic`, `map_daily_market_brief_evidence(...)`, and
  `map_entry_zone_strategy_evidence(...)`.
- Adapter tests map recorded quote, range, market context, and news payloads
  into a canonical `0001` fixture accepted by
  `generate_daily_market_brief(...)`.
- Adapter tests map recorded quote and technical indicator payloads into a
  canonical `0002` fixture accepted by
  `generate_entry_zone_strategy(...)`.
- Adapter results keep canonical fixture data, deterministic status, provider,
  `as_of`, and diagnostics separate.
- Complete mappings produce `status: complete` and no diagnostics.
- Partial mappings produce `status: partial`, a fixture only when existing
  finance validation can accept it, and at least one diagnostic.
- Failed mappings produce `status: failed`, `fixture: None`, and at least one
  diagnostic.
- Partial payloads, stale data, future timestamps, invalid symbols,
  unsupported symbols, provider error payloads, malformed payloads, unknown
  evidence groups, missing provenance, and provider symbol mismatches produce
  deterministic diagnostics.
- Source and timestamp metadata required by verified freshness rules are
  preserved in mapped canonical fixtures.
- Existing `0001`, `0002`, and runtime regression tests pass unchanged.
- The implementation performs no live network access, provider SDK calls,
  credential reads, model calls, Telegram calls, persistence, scheduling, auth,
  runtime endpoint changes, deployment behavior, brokerage behavior, trade
  execution, or position sizing.

## Verification

- Add static recorded-provider fixtures under `tests/fixtures/finance/`.
- Add adapter unit tests for successful `0001` fixture mapping.
- Add adapter unit tests for successful `0002` fixture mapping.
- Add adapter tests for partial payloads, stale timestamps, future timestamps,
  invalid symbols, unsupported symbols, provider error payloads, malformed
  payloads, unknown evidence groups, symbol mismatches, and missing provenance.
- Add integration-style tests that pass adapter-produced fixtures into
  `generate_daily_market_brief(...)` and
  `generate_entry_zone_strategy(...)`.
- Keep the verified `0001`, `0002`, and runtime tests in the regression
  baseline.
- Run `uv run pytest`.
- Run `uv run ruff check .`.

## Open Questions

None blocking for implementation.

Deferred to later specs:

- Exact provider-specific payload keys for AlphaVantage and future providers.
- Whether runtime endpoints should accept adapter-produced evidence directly or
  continue accepting only canonical fixture payloads.

## Handoff

- Producer skill: `$hermes-spec`
- Intended consumer skill: `$hermes-dev-loop`
- Source milestone path:
  `docs/milestones/0003-finance-evidence-provider-contract.md`
- Artifact path: `docs/specs/0004-finance-evidence-provider-contract.md`
- Status: Accepted.
- Settled decisions carried forward: provider-neutral finance evidence
  adapters remain finance-layer only; adapter output is canonical fixture data
  plus explicit diagnostics; deterministic finance functions remain the report
  source of truth; runtime endpoint changes are out of scope.
- Unresolved blockers: none.
- Verification expectations: adapter unit tests, adapter-to-finance integration
  tests, existing finance and runtime regression tests, `uv run pytest`, and
  `uv run ruff check .`.
- Agent routing log: `spec-planner` used; `spec-griller` used.

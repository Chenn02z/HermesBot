# Milestone: Finance Evidence Provider Contract

## Status

Draft

This draft is intentionally not Accepted yet. `0003` is sequenced after
`docs/milestones/0002-runtime-service-boundary.md`, and `0002` is Accepted but
not implemented in the current repo state. Implementation of this milestone
must not begin until `0002` reaches Verified and `0003` is explicitly moved to
Accepted, unless a later `$hermes-requirements` pass revises this sequencing
dependency.

## Source

Split from the consolidated roadmap requirements handoff, which has been
decomposed and removed. An earlier formalization pass turned the
requirements-level draft into a milestone contract while preserving the
dependency on `0002`.

## Goal

Define provider-neutral finance evidence adapter contracts that convert static
or recorded provider-shaped payloads into the validated fixture shapes consumed
by the verified deterministic finance functions:

```python
generate_daily_market_brief(watchlist: list[str], as_of: str, fixture: dict) -> str
generate_entry_zone_strategy(watchlist: list[str], as_of: str, fixture: dict) -> str
```

The adapter boundary must make provider provenance, timestamps, partial data,
and provider failures explicit before report generation. Deterministic finance
functions remain the only report source of truth.

## Scenario

A developer supplies recorded provider-shaped payloads for a watchlist and an
explicit `as_of`. The adapter layer maps the recorded quote, market context,
news, and technical indicator payloads into canonical JSON-compatible fixtures
that satisfy the verified `0001` and `0002` finance contracts. The developer can
then pass those canonical fixtures to the existing finance functions and receive
the same deterministic, research-only reports the fixture-backed foundation
already verifies.

If provider payloads are partial, stale, malformed, invalid for a requested
symbol, or contain provider error records, the adapter layer returns explicit
diagnostics and only uses canonical visible degradation where the verified
finance contracts already allow it. It must not invent prices, news, technical
indicators, timestamps, sources, or ticker interpretations to fill gaps.

## In Scope

- Provider-neutral adapter contracts for static or recorded provider-shaped
  quote, market context, news, and strategy evidence payloads.
- Canonical fixture output for
  `docs/specs/0001-finance-daily-market-brief.md`.
- Canonical fixture output for
  `docs/specs/0002-finance-entry-zone-strategy.md`.
- Explicit provenance metadata for mapped evidence, including provider name,
  provider symbol when available, provider timestamp, and canonical `source`
  strings.
- Structured adapter results for complete, partial, and failed mapping cases,
  with diagnostics for partial, stale, invalid symbol, unsupported symbol,
  provider error, symbol mismatch, and malformed payload cases.
- Fixture-backed verification using static recorded-provider payloads.
- Preservation of the current single-user personal product assumption.

## Out Of Scope

- Implementing or choosing the first live finance provider.
- Live network calls, provider SDKs, provider credentials, or environment-based
  provider configuration.
- Modifying the `0002` runtime service contract or adding runtime endpoints.
- Depending on `hermes_runtime` from the finance adapter layer.
- Telegram delivery.
- Hermes Agent runtime integration.
- Persistence, caching, watchlist storage, scheduling, auth, or multi-user
  behavior.
- Model calls, OpenRouter gateway integration, or model-written synthesis.
- Brokerage integration, alerts, trade execution, order routing, position
  sizing, or personalized financial advice.

## Contracts

### Dependency On `0002`

This milestone is sequenced after
`docs/milestones/0002-runtime-service-boundary.md`.

`0003` must not change the runtime service contract from `0002`. Any runtime
endpoint changes needed to consume adapter-produced evidence require a later
milestone or an explicit revision to the runtime milestone.

The adapter implementation, when later accepted, should live inside the finance
package boundary and must not import from `hermes_runtime`. Runtime code may
consume adapter-produced fixtures in later specs, but this milestone only
defines the finance evidence adapter contract.

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

`payloads` are static recorded-provider payloads supplied by the caller or by
tests. The adapter functions must not perform provider discovery, live fetches,
credential reads, runtime imports, fixture file loading, persistence, model
calls, Telegram calls, or brokerage actions.

### Canonical Fixture Output

Adapter output must be JSON-compatible fixture data accepted by the verified
finance contracts:

- `docs/specs/0001-finance-daily-market-brief.md`
- `docs/specs/0002-finance-entry-zone-strategy.md`

The adapter layer must not bypass existing finance validation. Generated
canonical fixtures must be passable to the existing public APIs without changing
those APIs.

When a daily market brief fixture is produced, it must include the top-level
canonical structure required by `0001`:

- top-level `as_of`
- `market_context.indices`
- top-level `tickers`

It may also include:

- `market_context.notes`
- `invalid_inputs`
- `tickers.<SYMBOL>.company_name`
- `tickers.<SYMBOL>.quote`
- `tickers.<SYMBOL>.range_20d`
- `tickers.<SYMBOL>.support_level`
- `tickers.<SYMBOL>.news`

When an entry-zone strategy fixture is produced, it must include the top-level
canonical structure required by `0002`:

- top-level `as_of`
- top-level `tickers`

It may also include:

- `invalid_inputs`
- `tickers.<SYMBOL>.company_name`
- `tickers.<SYMBOL>.quote`
- `tickers.<SYMBOL>.strategy.moving_averages`
- `tickers.<SYMBOL>.strategy.momentum`
- `tickers.<SYMBOL>.strategy.range_52w`
- `tickers.<SYMBOL>.strategy.support_resistance`
- `tickers.<SYMBOL>.strategy.volatility`
- `tickers.<SYMBOL>.strategy.volume`

Missing optional provider fields may map to absent canonical fields only where
`0001` and `0002` already define visible degradation. Missing required
canonical fields must produce explicit adapter diagnostics instead of invented
values.

If required top-level canonical structure cannot be produced, the adapter must
return `fixture: None` plus diagnostics. It must not return a malformed fixture.

### Adapter Result Shape

Adapter calls must return a deterministic result that separates canonical
fixture data from diagnostics. The exact implementation type may be chosen
during the later dev loop, but the result must carry:

- `fixture`: the canonical JSON-compatible fixture payload when mapping
  produces one.
- `status`: a deterministic status string with allowed values `complete`,
  `partial`, or `failed`.
- `diagnostics`: ordered diagnostic entries for provider errors, missing fields,
  stale data, invalid symbols, unsupported symbols, malformed payloads, symbol
  mismatches, or skipped evidence groups.
- `provider`: the provider name or recorded-provider label supplied by the
  caller.
- `as_of`: the caller-supplied `as_of`, matching the canonical fixture `as_of`
  when a fixture is produced.

Diagnostics must include a deterministic type, message, and affected symbol or
field when applicable. Provider error payloads must map to diagnostics rather
than leaking provider stack traces or opaque exception text into reports.
Diagnostics may be empty only for `complete` mappings.

This milestone does not require the existing finance report functions to
consume adapter diagnostics. Diagnostics must remain present on the adapter
result after fixture mapping so callers and later runtime specs can inspect
them before report generation.

### Diagnostics And Degradation

Adapter behavior must be deterministic for each failure class:

- Malformed payloads, provider error payloads, missing provider provenance,
  symbol mismatches, and invalid provider symbols produce diagnostics and no
  invented canonical evidence for the affected symbol or payload.
- Stale or future-dated but parseable timestamps may be preserved in canonical
  fixtures only when the verified finance function already degrades visibly for
  that timestamp condition. The adapter must also emit diagnostics.
- Missing optional evidence may be omitted from canonical fixtures only where
  `0001` or `0002` already defines visible degradation. The adapter must also
  emit diagnostics.
- Missing required top-level fixture structure produces no fixture.
- Unsupported or ambiguous symbols must be represented through diagnostics and,
  when compatible with the target verified spec, canonical `invalid_inputs`.
- Provider diagnostics must not be rendered as finance report text by this
  milestone.

### Provenance And Freshness

Mapped evidence must preserve source and timestamp information needed by the
verified finance freshness rules.

- Ticker normalization remains limited to trimming leading/trailing whitespace
  and uppercasing.
- `as_of` is explicit and must exactly match the canonical fixture `as_of`.
- Provider timestamps mapped into canonical evidence must remain ISO-8601
  datetimes with timezone offsets.
- Future-dated, stale, or missing timestamps must not be treated as fresh.
- Canonical `source` fields must identify recorded provider provenance. They
  must not claim live data when tests use static or recorded payloads.
- Provider symbols that do not match the requested normalized ticker must
  produce diagnostics instead of silent substitution.

### Finance Boundaries

Adapters must preserve the verified finance boundaries from `0001` and `0002`.

They must not mutate caller-supplied provider payloads, weaken research-only
financial-advice wording boundaries, introduce factual claims outside supplied
provider evidence, perform network access, call models, read credentials, or
touch Telegram, persistence, scheduling, deployment, or brokerage systems.

## Failure Modes

- Malformed recorded provider payload.
- Provider error payload.
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
- Adapter introduces live network access, provider SDKs, credential reads,
  model calls, persistence, Telegram behavior, runtime endpoint changes,
  deployment behavior, or brokerage behavior.

## Acceptance Criteria

- The milestone remains Draft until the `0002` runtime service boundary reaches
  Verified and this file is explicitly moved to Accepted by a later
  `$hermes-requirements` pass, unless that later pass revises the sequencing
  dependency.
- Adapter tests map recorded quote, range, market context, and news payloads
  into a canonical `0001` fixture accepted by the daily market brief function.
- Adapter tests map recorded quote and technical indicator payloads into a
  canonical `0002` fixture accepted by the entry-zone strategy function.
- The adapter API is importable from `hermes_finance.evidence_adapters` with
  separate daily market brief and entry-zone strategy mapping functions.
- Generated canonical fixtures can be passed to
  `generate_daily_market_brief(...)` and `generate_entry_zone_strategy(...)`
  without changing those public APIs.
- Adapter results keep canonical fixture data, deterministic status, and
  diagnostics separate.
- Partial payloads, stale data, invalid symbols, unsupported symbols, provider
  error payloads, malformed payloads, and provider symbol mismatches produce
  deterministic diagnostics according to the diagnostics and degradation
  contract.
- Tests assert diagnostics remain present on adapter results after successful
  fixture mapping when any diagnostic condition occurred.
- Source and timestamp metadata required by verified freshness rules are
  preserved in mapped canonical fixtures.
- Existing `0001` and `0002` finance regression tests pass unchanged.
- The implementation performs no live network access, provider SDK calls,
  credential reads, model calls, Telegram calls, persistence, scheduling, auth,
  runtime endpoint changes, deployment behavior, brokerage behavior, trade
  execution, or position sizing.

## Verification

- Add static recorded-provider fixtures under `tests/`.
- Add adapter unit tests for successful `0001` fixture mapping.
- Add adapter unit tests for successful `0002` fixture mapping.
- Add adapter tests for partial payloads, stale timestamps, future timestamps,
  invalid symbols, unsupported symbols, provider error payloads, malformed
  payloads, symbol mismatches, and missing provenance.
- Add integration-style tests that pass adapter-produced fixtures into
  `generate_daily_market_brief(...)` and
  `generate_entry_zone_strategy(...)`.
- Keep the verified `0001` and `0002` finance tests in the regression baseline.
- Run `uv run pytest`.
- Run `uv run ruff check .`.

## Open Questions

Blocking for acceptance:

- `0002` is Accepted but not implemented in the current repo state. `0003`
  should not be Accepted until that dependency is Verified, unless a later
  `$hermes-requirements` pass explicitly revises this sequencing dependency.
- User decision on 2026-06-29: keep this dependency blocked; do not waive the
  `0002` Verified prerequisite for now.

Deferred to later specs:

- Which live finance provider should be the first target after this contract is
  accepted and verified?
- What optional live smoke-test policy is acceptable once `0004` chooses a live
  provider?
- Whether runtime endpoints should accept adapter-produced evidence directly or
  continue accepting only canonical fixture payloads.

## Handoff

- Producer skill: `$hermes-requirements`
- Intended consumer skill: `$hermes-requirements` for blocker resolution and
  acceptance; later `$hermes-spec` only after this milestone is Accepted.
- Artifact path: `docs/milestones/0003-finance-evidence-provider-contract.md`
- Status: Draft.
- Settled decisions: live provider payloads must pass through provider-neutral
  evidence adapters before report generation; adapter output must be canonical
  fixture data plus explicit diagnostics; deterministic finance functions
  remain the report source of truth; `0003` must not modify or depend on the
  `0002` runtime service boundary.
- Unresolved blockers: `0002` is Accepted but not implemented in the current
  repo state, so `0003` is not ready for implementation. The normal next gate
  is `0002` reaching Verified, unless a later `$hermes-requirements` pass
  explicitly revises the sequencing dependency. User decision on 2026-06-29:
  keep this blocker in place.
- Required next reads: `AGENTS.md`, `README.md`, `docs/PRODUCT.md`,
  `docs/CONTEXT.md`, `docs/WORKFLOWS.md`,
  `docs/milestones/0002-runtime-service-boundary.md`, this milestone, and
  verified finance specs `0001` and `0002`.
- Key contracts and acceptance criteria: map recorded provider-shaped payloads
  into canonical `0001` and `0002` fixtures; preserve provenance, source,
  timestamp, freshness, deterministic adapter status, and diagnostics; expose
  separate daily market brief and entry-zone strategy adapter functions from
  `hermes_finance.evidence_adapters`; keep finance public APIs unchanged;
  prohibit live providers, network access, credentials, models, Telegram,
  persistence, runtime endpoint changes, deployment, and brokerage behavior.
- Verification expectations: static recorded-provider fixtures, adapter unit
  tests, integration-style tests through both finance public APIs, the existing
  finance regression baseline, `uv run pytest`, and `uv run ruff check .`.
- Remaining open questions: first live provider and live smoke-test policy are
  deferred to `0004`; runtime consumption of adapter-produced evidence remains
  a later milestone decision.
- Agent routing log: inherited from the earlier formalization pass; a fresh
  `$hermes-requirements` acceptance run must record current gates before this
  milestone can become Accepted.

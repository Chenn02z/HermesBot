# Spec: AlphaVantage Live Finance Provider Integration

## Status

Accepted

## Goal

Define the AlphaVantage live finance provider integration for the verified
daily market brief and entry-zone strategy workflows.

Live provider code fetches AlphaVantage payloads, groups them into the
verified provider-neutral adapter payload groups, maps them through
`hermes_finance.evidence_adapters`, and then calls the existing deterministic
finance report generators. Deterministic finance functions remain the only
report source of truth.

## Scenario

A developer calls
`hermes_finance.alpha_vantage.generate_live_daily_market_brief(...)` or
`hermes_finance.alpha_vantage.generate_live_entry_zone_strategy(...)` with a
watchlist and explicit `as_of`.

The live function reads `ALPHAVANTAGE_API_KEY` at execution time, fetches the
minimum AlphaVantage endpoint set, groups raw response bodies under the
verified adapter payload groups, calls the matching adapter mapper, and
renders a report only when the adapter returns `complete` or
validator-accepted `partial` evidence.

Provider failures, missing credentials, quota responses, malformed payloads,
stale timestamps, invalid symbols, symbol mismatches, and insufficient
derived history return deterministic failures or visible degradation without
invented evidence.

## In Scope

- AlphaVantage as the only live finance provider for this spec.
- Finance-layer importable live functions for both verified workflows.
- Environment-based credential lookup using `ALPHAVANTAGE_API_KEY`.
- `GLOBAL_QUOTE`, `TIME_SERIES_DAILY`, `NEWS_SENTIMENT`, `SMA`, `RSI`, and
  `ATR` as the only AlphaVantage endpoint functions in scope.
- Raw AlphaVantage response grouping into the verified adapter payload groups.
- Deterministic derivation of 20-day range, 52-week range, support/resistance,
  and 20-day average volume from `TIME_SERIES_DAILY`.
- Fixture-backed tests using recorded or mocked AlphaVantage-shaped payloads.
- Optional local-only live smoke tests gated behind credentials and explicit
  opt-in.

## Out Of Scope

- Additional live providers.
- Direct use of raw AlphaVantage payloads by report renderers.
- Changes to the verified deterministic public APIs:
  `hermes_finance.generate_daily_market_brief`,
  `hermes_finance.daily_market_brief.generate_daily_market_brief`,
  `hermes_finance.generate_entry_zone_strategy`, and
  `hermes_finance.entry_zone_strategy.generate_entry_zone_strategy`.
- Changes to `hermes_runtime` routes, schemas, readiness checks, or runtime
  configuration.
- Telegram delivery, persistence, scheduling, auth, deployment, or multi-user
  behavior.
- Model calls, OpenRouter gateway integration, or model-written synthesis.
- Brokerage integration, alerts, trade execution, order routing, position
  sizing, or personalized financial advice.

## Contracts

### Verified Prerequisites

This spec depends on the already-verified contracts in:

- `docs/specs/0001-finance-daily-market-brief.md`
- `docs/specs/0002-finance-entry-zone-strategy.md`
- `docs/specs/0003-runtime-service-boundary.md`
- `docs/specs/0004-finance-evidence-provider-contract.md`

The live provider implementation must consume the verified adapter API and
result contracts from `hermes_finance.evidence_adapters`. It must not redefine
adapter behavior locally, and it must not change the runtime boundary from
`0003`.

### Public Live API

The implementation must expose these finance-layer functions:

```python
hermes_finance.alpha_vantage.generate_live_daily_market_brief(
    watchlist: list[str],
    as_of: str,
) -> str

hermes_finance.alpha_vantage.generate_live_entry_zone_strategy(
    watchlist: list[str],
    as_of: str,
) -> str
```

These live functions must not change the verified deterministic public APIs,
and they must not add or change any `hermes_runtime` behavior.

These live functions return markdown only when a finance report is actually
rendered. Missing credentials, deterministic fetch failures, adapter
`failed` results, and adapter `partial` results that do not produce a
validator-accepted fixture must raise `ValueError` with deterministic messages
that do not expose secrets, stack traces, raw exception text, or provider
credentials.

### Adapter Boundary

Daily market brief live payloads must use only these adapter groups:

- `market_context`
- `quotes`
- `ranges`
- `support_levels`
- `news`

Entry-zone strategy live payloads must use only these adapter groups:

- `quotes`
- `moving_averages`
- `momentum`
- `range_52w`
- `support_resistance`
- `volatility`
- `volume`

The live provider layer may reshape AlphaVantage responses into these group
boundaries, but raw AlphaVantage evidence must not bypass
`map_daily_market_brief_evidence(...)` or
`map_entry_zone_strategy_evidence(...)`.

### AlphaVantage Endpoint Set

The implementation must use only this minimum endpoint set:

- `GLOBAL_QUOTE` for latest price and latest volume for each requested ticker
  and for required market proxies.
- `TIME_SERIES_DAILY` for daily OHLCV bars and deterministic derivations of
  20-day range, 52-week range, support/resistance, and 20-day average volume.
- `NEWS_SENTIMENT` for ticker news inputs and optional market-context notes.
- Daily `SMA` with `time_period=50`, `series_type=close`.
- Daily `SMA` with `time_period=200`, `series_type=close`.
- Daily `RSI` with `time_period=14`, `series_type=close`.
- Daily `ATR` with `time_period=14`.

`REALTIME_BULK_QUOTES`, intraday endpoints, fundamentals, earnings,
alternative providers, or any additional AlphaVantage endpoints are out of
scope for this spec.

### Workflow Mapping

For daily market brief:

- `market_context.indices` must be backed by AlphaVantage data for `SPY` and
  `QQQ`, because `0001` requires S&P 500 and Nasdaq proxy coverage for a
  complete market-context section.
- `quotes` must provide the requested ticker latest price evidence.
- `ranges` must provide the canonical 20-day range inputs.
- `support_levels` may reuse the deterministic support derivation defined
  below.
- `news` must provide ticker-filtered AlphaVantage news items when available.

For entry-zone strategy:

- `quotes` must provide the requested ticker latest price evidence.
- `moving_averages` must carry 50-day and 200-day SMA evidence.
- `momentum` must carry 14-period RSI evidence.
- `range_52w` must carry deterministic 52-week low/high derivations.
- `support_resistance` must carry deterministic support/resistance
  derivations.
- `volatility` must carry 14-period ATR evidence.
- `volume` must carry latest volume plus 20-day average volume.

### Deterministic Derivations

When AlphaVantage does not provide a required canonical finance field through a
dedicated endpoint in the accepted endpoint set, the implementation must use
these deterministic derivations from `TIME_SERIES_DAILY` bars up to and
including the selected provider trading date:

- `range_20d.recent_low_20d = min("3. low")` over the latest 20 trading bars.
- `range_20d.recent_high_20d = max("2. high")` over the latest 20 trading
  bars.
- `support_resistance.support_1 = min("3. low")` over the latest 20 trading
  bars.
- `support_resistance.resistance_1 = max("2. high")` over the latest 20
  trading bars.
- `support_level.price` for daily market brief reuses
  `support_resistance.support_1`.
- `range_52w.low = min("3. low")` over the latest 252 trading bars.
- `range_52w.high = max("2. high")` over the latest 252 trading bars.
- `volume.avg_volume_20d = arithmetic mean("5. volume")` over the latest 20
  trading bars.

`volume.latest_volume` comes from the `GLOBAL_QUOTE` latest volume field,
falling back to the latest daily-bar volume only if quote volume is missing
and a deterministic diagnostic is emitted.

If fewer than 20 daily bars are available, 20-day range, support/resistance,
and 20-day average-volume derivations for that ticker must fail or degrade
deterministically.

If fewer than 252 daily bars are available, the entry-zone strategy mapping
for that ticker must remain `partial` or `failed`; the implementation must not
relabel a shorter window as a 52-week range.

### Timestamp Mapping

The selected provider trading date is the latest completed US/Eastern trading
session whose canonical market-close timestamp is less than or equal to the
invocation `as_of`. Intraday, weekend, and holiday invocations must resolve to
the most recent completed trading session rather than the wall-clock date of
`as_of`.

AlphaVantage date-only trading-day values from `TIME_SERIES_DAILY`, `SMA`,
`RSI`, and `ATR` must be mapped to market-close timestamps at
`16:00:00-04:00` or `16:00:00-05:00` according to US/Eastern for that date.

`GLOBAL_QUOTE` trading-day values must be mapped to the selected provider
trading date market-close timestamp only when the quote trading date matches
that selected provider trading date. If the quote trading date is missing or
does not match, the implementation must emit a deterministic diagnostic and
must not merge mismatched quote freshness silently into the canonical fixture.

`NEWS_SENTIMENT.time_published` values must be parsed as provider timestamps
and emitted with a timezone offset before adapter mapping.

Provider timestamps later than invocation `as_of` are future-dated diagnostics.
Date-only values must never be mapped to invocation time.

All mapped timestamps must satisfy the verified finance freshness rules from
`0001` and `0002`. Missing, malformed, timezone-less, stale, or future-dated
provider timestamps must become deterministic diagnostics rather than invented
fresh evidence.

For `strategy.volume.timestamp`, the canonical timestamp is the selected
provider trading date market-close timestamp. `latest_volume` may use the
`GLOBAL_QUOTE` volume field only when its trading date matches the selected
provider trading date. Otherwise, the implementation must either fall back to
the matching `TIME_SERIES_DAILY` bar volume with a diagnostic or leave the
volume group partial.

### Credentials And Test Policy

Live execution reads `ALPHAVANTAGE_API_KEY` from the environment. The key must
never be committed, logged, echoed in errors, included in fixtures, or
embedded in generated reports.

Module import and normal automated tests must not require live credentials or
network access. Fixture-backed tests are the required baseline.

Optional local live smoke tests may run only when `ALPHAVANTAGE_API_KEY` is
set and an explicit opt-in flag such as
`HERMES_RUN_LIVE_ALPHA_VANTAGE_SMOKE=1` is supplied by the developer.

### Runtime Boundary

This spec does not add, remove, or change any `hermes_runtime` route, request
schema, response schema, readiness behavior, or runtime configuration
contract. A later milestone may decide whether live-provider behavior should
be exposed through HTTP endpoints.

### Failure Handling

Missing `ALPHAVANTAGE_API_KEY`, auth failures, provider quota or rate-limit
responses, AlphaVantage `Information`, `Note`, or `Error Message` payloads,
timeouts, non-2xx HTTP responses, malformed JSON, empty endpoint payloads,
missing expected response keys, stale timestamps, invalid symbols, symbol
mismatches, and partial payloads must produce deterministic fetch or adapter
failures.

Adapter `complete` results and adapter `partial` results with
validator-accepted fixtures proceed to the existing deterministic report
generators. Adapter `failed` results do not render finance reports.

Adapter `partial` results that do not produce validator-accepted fixtures must
raise deterministic `ValueError` failures rather than returning markdown error
text.

The implementation must not invent prices, market context, news, indicators,
timestamps, sources, symbol mappings, or 52-week history. It must not retry
implicitly unless a later accepted revision defines bounded deterministic retry
behavior.

## Failure Modes

- Missing `ALPHAVANTAGE_API_KEY`.
- Secret value appears in logs, diagnostics, fixtures, or reports.
- AlphaVantage `Information`, `Note`, or `Error Message` payloads.
- Non-2xx response, timeout, malformed JSON, empty endpoint payload, or
  missing expected response key.
- Quote symbol mismatch with the requested normalized ticker.
- Missing `SPY` or `QQQ` evidence leaves market context incomplete.
- Date-only provider data cannot be mapped to an offset-aware US/Eastern close
  timestamp.
- `NEWS_SENTIMENT` provider timestamps cannot be parsed into offset-aware
  canonical timestamps.
- Fewer than 20 daily bars for 20-day range, support/resistance, or
  average-volume derivations.
- Fewer than 252 daily bars for 52-week range derivation.
- Support/resistance derivation produces `support_1 >= resistance_1`.
- Provider payloads bypass adapter diagnostics.
- Adapter returns `failed`.
- Runtime HTTP routes, schemas, readiness behavior, or runtime configuration
  are changed.
- Tests require credentials or network access by default.

## Acceptance Criteria

- AlphaVantage is the only live provider target for this spec.
- `hermes_finance.alpha_vantage` exposes
  `generate_live_daily_market_brief(...)` and
  `generate_live_entry_zone_strategy(...)`.
- Live functions read `ALPHAVANTAGE_API_KEY` only at execution time.
- Normal imports and normal `uv run pytest` require no credentials and no
  network access.
- Daily market brief payloads use only `market_context`, `quotes`, `ranges`,
  `support_levels`, and `news`.
- Entry-zone strategy payloads use only `quotes`, `moving_averages`,
  `momentum`, `range_52w`, `support_resistance`, `volatility`, and `volume`.
- All provider payloads pass through the verified adapter functions before
  deterministic report generation.
- `GLOBAL_QUOTE`, `TIME_SERIES_DAILY`, `NEWS_SENTIMENT`, `SMA`, `RSI`, and
  `ATR` are the only AlphaVantage endpoint functions used by the implementation.
- 20-day range, 52-week range, support/resistance, and 20-day average-volume
  derivations are deterministic and covered by fixture-backed tests.
- Partial payloads and adapter `partial` results are first-class outcomes with
  explicit deterministic diagnostics and fixture-backed acceptance tests.
- Live-function deterministic failure cases raise `ValueError` rather than
  returning markdown failure text.
- The selected provider trading date rule is applied consistently across quote,
  daily-bar, indicator, and volume evidence.
- `SPY` and `QQQ` are the required market proxies for daily market brief
  completeness.
- No `hermes_runtime` route, schema, readiness behavior, or runtime
  configuration contract changes.
- Missing credentials, provider errors, quota or rate-limit responses, stale
  data, invalid symbols, malformed payloads, symbol mismatches, and
  insufficient history degrade deterministically.
- Research-only wording remains enforced by the existing deterministic finance
  report generators.

## Verification

- Add fixture-backed tests for AlphaVantage payload grouping for both
  workflows.
- Add tests for `GLOBAL_QUOTE`, `TIME_SERIES_DAILY`, `NEWS_SENTIMENT`, `SMA`,
  `RSI`, and `ATR` extraction behavior using recorded or mocked provider
  payloads.
- Add tests for 20-day range, 52-week range, support/resistance, and 20-day
  average-volume derivations.
- Add tests proving normal imports and normal test collection do not require
  `ALPHAVANTAGE_API_KEY`.
- Add failure tests for missing key, auth failures, provider `Information`,
  `Note`, and `Error Message` payloads, quota or rate-limit payloads, non-2xx
  responses, timeouts, malformed JSON, symbol mismatch, stale or future
  timestamps, and insufficient daily history.
- Add explicit tests for partial payloads, adapter `partial` results, and
  non-renderable partial outcomes that must raise deterministic `ValueError`
  failures.
- Add tests for intraday, weekend, and holiday `as_of` values to verify the
  selected provider trading date rule and canonical volume timestamp behavior.
- Keep verified finance, adapter, and runtime regression tests in the
  verification baseline.
- Run `uv run pytest`.
- Run `uv run ruff check .`.
- Optional live smoke tests may run only with `ALPHAVANTAGE_API_KEY` and
  `HERMES_RUN_LIVE_ALPHA_VANTAGE_SMOKE=1`.

## Open Questions

None blocking for implementation.

Deferred to later specs:

- Whether bounded deterministic retry behavior is worthwhile.
- Whether a later runtime milestone should expose live-provider behavior
  through HTTP endpoints.
- Whether future provider specs should add endpoint-specific richer
  support/resistance data instead of the deterministic 20-day OHLCV
  derivation.

## Handoff

- Producer skill: `$hermes-spec`
- Intended consumer skill: `$hermes-dev-loop`
- Source milestone path:
  `docs/milestones/0004-live-finance-provider-integration.md`
- Artifact path:
  `docs/specs/0005-alpha-vantage-live-finance-provider-integration.md`
- Status: Accepted.
- Settled decisions: AlphaVantage is the only live provider; live finance work
  remains finance-layer only; existing deterministic report APIs stay
  unchanged; the verified adapter boundary is mandatory; `SPY` and `QQQ` are
  the required market proxies for daily market brief completeness; runtime
  boundary remains unchanged; `ALPHAVANTAGE_API_KEY` is the live credential
  name; fixture-backed tests are the baseline; live smoke tests remain
  credential-gated and opt-in; support/resistance, ranges, and average volume
  use deterministic `TIME_SERIES_DAILY` derivations.
- Unresolved blockers: none.
- Required next reads: `docs/specs/0001-finance-daily-market-brief.md`,
  `docs/specs/0002-finance-entry-zone-strategy.md`,
  `docs/specs/0003-runtime-service-boundary.md`,
  `docs/specs/0004-finance-evidence-provider-contract.md`,
  this spec, and the current finance package and test layout.
- Verification expectations: credential-free pytest baseline, `ruff check`,
  fixture-backed provider tests, deterministic derivation tests, provider
  failure tests, and optional gated live smoke tests.
- Trace path:
  `.agent-trace/20260701-hermes-spec-0005-alpha-vantage-live-finance-provider-integration/`
- Agent routing log: `spec-planner` used; `spec-griller` used.

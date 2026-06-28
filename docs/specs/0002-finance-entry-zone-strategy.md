# Spec: Finance Entry-Zone Strategy

## Status

Verified

## Goal

Add a deterministic, fixture-backed entry-zone strategy report for long-term
investing research candidates.

The strategy layer builds on the `0001` finance boundaries for caller-supplied
watchlists, explicit `as_of` datetimes, fixture-backed evidence, source
metadata, freshness labels, deterministic calculations, research-only wording,
and verification without network access.

For this first accepted version, the strategy report is deterministic
template-rendered only. Model-written synthesis, valuation analysis, and
fundamental analysis are deferred to later specs.

## Scenario

A developer asks Hermes to compare a caller-supplied watchlist such as
`["META", "MSFT", "NVDA"]` as of `2026-06-26T16:30:00-04:00` using static
fixtures. Hermes returns one markdown strategy report with a deterministic
technical setup score, research-candidate label, comparison table, visible
degradation for missing or stale inputs, and a research-only observation zone
for each eligible supported ticker.

If a ticker has conflicting technical signals, Hermes shows the conflict rather
than hiding uncertainty behind the score. If a ticker lacks fresh required
strategy evidence, Hermes renders the ticker section but does not produce a
score, rank, label, or observation zone for that ticker.

## In Scope

- A new standalone public function for entry-zone strategy reports.
- Long-term investing research as the strategy horizon.
- Static fixture-backed technical-analysis inputs.
- Deterministic scoring, labels, comparison ranking, conflict notes, and
  observation-zone calculation.
- Deterministic template-rendered narrative that explains supplied evidence and
  calculated signals without model calls.
- Visible degradation for missing, stale, invalid, future-dated, ambiguous, or
  unsupported inputs.
- Fixture-backed tests for valid, missing, stale, conflicting, and malformed
  strategy inputs.

## Out Of Scope

- Live market-data, fundamentals, filings, news, valuation, or provider
  integration.
- Telegram delivery.
- Automated scheduling.
- Persistent watchlist storage.
- Brokerage integration, alerts, trade execution, order routing, or position
  sizing.
- Personalized financial advice.
- Runtime finance sub-agent architecture.
- Production deployment.
- Model-written synthesis or LLM/model calls.
- Changes to the `0001` daily market brief public API or report output, except
  where shared utility constants need to preserve the financial-advice boundary.

## Contracts

### Dependency On `0001`

`0002` must preserve the `0001` contracts for:

- caller-supplied watchlists
- explicit `as_of` datetime
- fixture-backed evidence
- source metadata and timestamps
- freshness labels
- deterministic calculations
- research-only wording
- no network access during verification

`0002` must not weaken any `0001` failure mode or financial-advice boundary.
Because `0001` is currently `Implemented`, not `Verified`, the `0002` dev loop
must run the existing `0001` regression tests together with the new `0002`
tests before marking this spec `Verified`.

### Public API

The implementation must expose an importable Python function:

```python
generate_entry_zone_strategy(watchlist: list[str], as_of: str, fixture: dict) -> str
```

The function must be importable from both:

- `hermes_finance`
- `hermes_finance.entry_zone_strategy`

The function returns one standalone markdown report. It must not call
`generate_daily_market_brief`, mutate the supplied fixture, perform network
access, call an LLM/model, add Telegram delivery, persist watchlists, or touch
brokerage systems.

Ticker normalization must match `0001`: trim leading/trailing whitespace and
uppercase only.

### Fixture Format

`0002` requires static JSON-compatible fixtures with this top-level shape:

```json
{
  "as_of": "2026-06-26T16:30:00-04:00",
  "invalid_inputs": {
    "BRK.B": "Ambiguous class/share formatting in fixture"
  },
  "tickers": {
    "META": {
      "company_name": "Meta Platforms, Inc.",
      "quote": {
        "current_price": 682.35,
        "timestamp": "2026-06-26T16:00:00-04:00",
        "source": "fixture"
      },
      "strategy": {
        "moving_averages": {
          "sma_50": 660.0,
          "sma_200": 575.0,
          "timestamp": "2026-06-26T16:00:00-04:00",
          "source": "fixture"
        },
        "momentum": {
          "rsi_14": 54.2,
          "timestamp": "2026-06-26T16:00:00-04:00",
          "source": "fixture"
        },
        "range_52w": {
          "low": 442.65,
          "high": 740.91,
          "timestamp": "2026-06-26T16:00:00-04:00",
          "source": "fixture"
        },
        "support_resistance": {
          "support_1": 650.0,
          "resistance_1": 720.0,
          "timestamp": "2026-06-26T16:00:00-04:00",
          "source": "fixture"
        },
        "volatility": {
          "atr_14": 18.25,
          "timestamp": "2026-06-26T16:00:00-04:00",
          "source": "fixture"
        },
        "volume": {
          "latest_volume": 14500000,
          "avg_volume_20d": 13200000,
          "timestamp": "2026-06-26T16:00:00-04:00",
          "source": "fixture"
        }
      }
    }
  }
}
```

Required top-level fields:

- `as_of`
- `tickers`

Optional top-level field:

- `invalid_inputs`

Required ticker fields for scoring, ranking, labels, and observation zones:

- `quote.current_price`
- `quote.timestamp`
- `quote.source`
- `strategy.moving_averages.sma_50`
- `strategy.moving_averages.sma_200`
- `strategy.moving_averages.timestamp`
- `strategy.moving_averages.source`
- `strategy.momentum.rsi_14`
- `strategy.momentum.timestamp`
- `strategy.momentum.source`
- `strategy.range_52w.low`
- `strategy.range_52w.high`
- `strategy.range_52w.timestamp`
- `strategy.range_52w.source`
- `strategy.support_resistance.support_1`
- `strategy.support_resistance.resistance_1`
- `strategy.support_resistance.timestamp`
- `strategy.support_resistance.source`
- `strategy.volatility.atr_14`
- `strategy.volatility.timestamp`
- `strategy.volatility.source`
- `strategy.volume.latest_volume`
- `strategy.volume.avg_volume_20d`
- `strategy.volume.timestamp`
- `strategy.volume.source`

Optional ticker field:

- `company_name`

All numeric fields must be non-boolean numbers. `current_price`, moving
averages, 52-week range values, support, resistance, ATR, and volume values must
be greater than zero. `rsi_14` must be between `0` and `100`, inclusive.
`range_52w.low` must be less than or equal to `range_52w.high`.
`support_1` must be less than `resistance_1`.

Ambiguous inputs are represented only by `fixture["invalid_inputs"]`; the
implementation must not infer ambiguity from external data.

### Freshness

Freshness is evaluated relative to the invocation `as_of`.

- The invocation `as_of` must equal fixture top-level `as_of`; mismatch is a
  validation error.
- `as_of` and all timestamps used by the report must be valid ISO-8601
  datetimes with timezone offsets.
- Timestamps later than `as_of` are invalid and must not be treated as fresh.
- Quote evidence is fresh when its timestamp is no more than 36 hours older
  than `as_of`.
- Strategy indicator groups are fresh when their timestamp dates are no more
  than 7 calendar days older than the `as_of` date.
- Missing timestamps are treated as stale.
- Missing, stale, invalid, or future-dated required ticker evidence prevents
  score, rank, label, and observation-zone evaluation for that ticker.

### Deterministic Score

The strategy report must produce a `technical_setup_score` from `0` to `100`
only when every required scoring input is present, valid, and fresh.

The score is the integer sum of these components:

Trend quality, maximum 25 points:

- `10` points when `current_price > sma_200`, else `0`.
- `10` points when `sma_50 > sma_200`, else `0`.
- `5` points when `current_price >= sma_50`.
- `3` points when `current_price < sma_50` and
  `(sma_50 - current_price) / sma_50 <= 0.05`.
- `0` points otherwise.

Pullback and location quality, maximum 25 points:

- Support distance uses `(current_price - support_1) / support_1`.
- `12` points when support distance is at least `0` and less than or equal to
  `0.05`.
- `8` points when support distance is greater than `0.05` and less than or
  equal to `0.10`.
- `4` points when support distance is greater than `0.10` and less than or
  equal to `0.15`.
- `0` points otherwise.
- High distance uses `(range_52w.high - current_price) / range_52w.high`.
- `8` points when high distance is at least `0.05` and less than or equal to
  `0.25`.
- `4` points when high distance is at least `0` and less than `0.05`.
- `0` points otherwise.
- Resistance buffer uses `(resistance_1 - current_price) / current_price`.
- `5` points when resistance buffer is at least `0.08`.
- `3` points when resistance buffer is at least `0.03` and less than `0.08`.
- `0` points otherwise.

Momentum quality, maximum 20 points:

- `20` points when `rsi_14` is between `40` and `60`, inclusive.
- `12` points when `rsi_14` is between `30` and less than `40`, or greater
  than `60` and less than or equal to `70`.
- `4` points otherwise.

Volume quality, maximum 15 points:

- Volume ratio uses `latest_volume / avg_volume_20d`.
- `8` points when volume ratio is between `0.8` and `1.5`, inclusive.
- `5` points when volume ratio is between `0.5` and less than `0.8`, or greater
  than `1.5` and less than or equal to `2.5`.
- `0` points otherwise.
- `7` points when `avg_volume_20d >= 1_000_000`.
- `4` points when `avg_volume_20d >= 250_000` and less than `1_000_000`.
- `0` points otherwise.

Volatility quality, maximum 15 points:

- ATR ratio uses `atr_14 / current_price`.
- `15` points when ATR ratio is between `0.01` and `0.04`, inclusive.
- `10` points when ATR ratio is less than `0.01`.
- `8` points when ATR ratio is greater than `0.04` and less than or equal to
  `0.06`.
- `3` points otherwise.

### Labels And Ranking

Labels are deterministic:

- `75` through `100`: `High-scoring research candidate`
- `60` through `74`: `Constructive research candidate`
- `45` through `59`: `Mixed research candidate`
- `0` through `44`: `Weak research candidate`
- Missing, stale, invalid, or future-dated required input:
  `Insufficient fresh evidence`

The comparison table must sort scored tickers by score descending. Ties preserve
the caller-supplied watchlist order after normalization and duplicate removal.
Unscored supported tickers appear after scored tickers in caller watchlist
order. Unsupported and ambiguous inputs are shown in visible sections, not in
the ranked scored set.

### Research-Only Observation Zone

The observation zone is deterministic and may be evaluated only when the ticker
has fresh, valid `quote`, `support_resistance`, and `volatility` evidence.

- `zone_lower = support_1`
- `zone_upper = min(support_1 * 1.05, support_1 + 1.5 * atr_14)`
- Bounds are rounded to two decimals.

The observation zone must not be evaluated when:

- `support_1 >= current_price`
- `zone_upper >= current_price`
- `support_1 >= resistance_1`
- quote, support/resistance, or volatility evidence is missing, stale, invalid,
  or future-dated

When `zone_upper >= current_price`, the report must state that current price is
inside or below the observation zone, without presenting that condition as an
instruction.

### Conflict Notes

The report must show concrete conflict notes when any of these conditions are
present:

- `sma_50 <= sma_200`
- `current_price < sma_200`
- `current_price < sma_50`
- `current_price < range_52w.low` or `current_price > range_52w.high`
- `support_1 >= resistance_1`
- `support_1 >= current_price`
- `resistance_1 <= current_price`
- `rsi_14 < 30` or `rsi_14 > 70`
- `latest_volume / avg_volume_20d < 0.5` or greater than `2.5`
- `atr_14 / current_price > 0.06`

Conflict notes must not suppress the score when all required inputs are fresh
and valid unless the condition is also an invalid fixture condition.

### Report Output

The report must include:

- Title with `as_of`.
- Method summary with deterministic scoring weights and label thresholds.
- Watchlist coverage summary with supported, duplicate, unsupported,
  ambiguous, scored, and insufficient-evidence counts.
- Comparison table sorted by the ranking contract.
- One section per unique supported normalized ticker in caller watchlist order.
- Visible sections for unsupported or ambiguous inputs.
- Explicit `Evidence`, `Deterministic Calculation`, and `Deterministic
  Narrative` labels where applicable.
- Per supported ticker:
  - strategy evidence with timestamp, source, and freshness
  - deterministic score component breakdown, or reasons the ticker was not
    scored
  - research-candidate label
  - observation zone, or reason it was not evaluated
  - conflict notes, or a visible `none` marker
- Limitations/disclaimer section.

The limitations section must include this sentence:

```text
Research only. Not personalized financial advice, not a recommendation to buy
or sell, and not a trade instruction.
```

Entry-zone strategy wording must remain research-only. It must not include:

- personalized financial advice
- position sizing
- guarantees
- trade instructions
- brokerage-action language such as "buy now", "place an order", or "execute"
- "buy zone", "target price", "upside", or "should buy"
- "entry recommendation", "recommended entry", or "accumulate now"

The terms `entry-zone strategy` and `observation zone` are allowed only as
research framing, not as instructions.

## Failure Modes

- Empty watchlist: return a visible validation failure instead of an empty
  report.
- Duplicate tickers: render one supported ticker section at the first
  normalized occurrence and note duplicate inputs in the watchlist summary.
- Unsupported or ambiguous ticker: flag the input and do not substitute another
  symbol. Ambiguity must come from `fixture["invalid_inputs"]`, not external
  lookup or inference.
- Invocation `as_of` mismatch with fixture top-level `as_of`: fail with a
  validation error.
- Missing required top-level fixture field: fail with a validation error that
  identifies the missing field.
- Malformed ticker, quote, or strategy group: fail with a validation error that
  identifies the missing or invalid field.
- Invalid numeric values: fail with a validation error for non-number booleans,
  nonpositive prices or volumes, `rsi_14` outside `0` through `100`,
  `range_52w.low > range_52w.high`, or `support_1 >= resistance_1`.
- Invalid, missing, future, or stale timestamps: mark invalid or stale and skip
  score, rank, label, and observation-zone calculations that depend on the
  evidence.
- Missing or stale required strategy input: render the ticker as insufficient
  fresh evidence and omit score, rank, label, and observation zone.
- Conflicting signals: render conflict notes and avoid unsupported confidence.
- No scored tickers: render the report with coverage, visible reasons, and no
  ranked scored candidates.
- Prohibited finance-advice wording in generated output: fail verification.

## Acceptance Criteria

- The implementation exposes
  `generate_entry_zone_strategy(watchlist: list[str], as_of: str, fixture: dict) -> str`
  from `hermes_finance` and `hermes_finance.entry_zone_strategy`.
- Valid `META`-style fixtures produce one dated markdown strategy report with
  method summary, watchlist coverage summary, comparison table, supported
  ticker sections, source metadata, freshness labels, score breakdowns,
  labels, observation zones, conflict notes, and limitations.
- Every score, label, rank, conflict note, and observation zone is reproducible
  from deterministic fixture inputs.
- Missing, stale, invalid, future-dated, ambiguous, or unsupported inputs
  degrade visibly instead of being guessed or invented.
- If any required scoring group is missing, stale, invalid, or future-dated, no
  score, rank, research-candidate label, or observation zone is produced for
  that ticker.
- The comparison table sorts scored tickers by score descending and preserves
  caller watchlist order for ties and unscored supported tickers.
- The output distinguishes supplied evidence, deterministic calculations, and
  deterministic narrative.
- The output preserves research-only wording and excludes personalized advice,
  position sizing, guarantees, trade instructions, and brokerage-action
  language.
- The implementation performs no LLM/model calls, network access, live provider
  calls, Telegram delivery, persistence, scheduling, or brokerage integration.
- Verification can run entirely against static fixtures without network access.
- Existing `0001` daily market brief behavior remains covered by regression
  tests.

## Verification

- Add fixture-backed tests for a valid `META` strategy report with deterministic
  score, component breakdown, label, rank, observation zone, and no conflict
  notes.
- Add fixture-backed tests for comparison ranking, score ties, and unscored
  supported ticker ordering.
- Add fixture-backed tests for empty watchlist, duplicate ticker inputs,
  unsupported inputs, and ambiguous inputs.
- Add fixture-backed tests for stale quote and stale strategy groups.
- Add fixture-backed tests for malformed timestamps, missing timezone offsets,
  future timestamps, and `as_of` mismatch.
- Add fixture-backed tests for invalid indicator values, including nonpositive
  prices or volumes, invalid RSI, invalid 52-week range, and
  `support_1 >= resistance_1`.
- Add fixture-backed tests for each missing required strategy group.
- Add fixture-backed tests for conflict notes.
- Add fixture-backed tests for observation-zone skip conditions, including
  stale support/resistance, stale volatility, `support_1 >= current_price`, and
  `zone_upper >= current_price`.
- Add fixture-backed tests for no scored tickers.
- Add fixture-backed tests for deterministic output and prohibited
  finance-advice wording.
- Run `uv run pytest` once implementation exists.
- Run `uv run ruff check .` once implementation exists.

If the commands or project files do not exist at implementation time, report the
missing command or file as a repo maturity gap instead of inventing a parallel
toolchain.

## Open Questions

None blocking for `0002`.

Deferred to later specs:

- Whether model-written synthesis should explain deterministic strategy outputs.
- Whether valuation or fundamental signals should be added.
- Whether live provider adapters should map provider payloads into this fixture
  shape.
- Whether strategy outputs should integrate into Telegram delivery, alerts, or
  persistent watchlists.

## Handoff

- Producer skill: `$hermes-dev-loop`
- Intended consumer skill: `$hermes-context`
- Artifact path: `docs/specs/0002-finance-entry-zone-strategy.md`
- Status: Verified; implementation and targeted verification complete.
- Settled decisions: long-term investing research horizon; deterministic
  fixture-backed technical setup score; standalone
  `generate_entry_zone_strategy` public API; required strategy groups and
  freshness windows; valuation/fundamentals and model synthesis deferred;
  missing strategy timestamps degrade visibly as stale.
- Unresolved blockers: none.
- Verification: full `uv run pytest` passed with `60 passed`; full
  `uv run ruff check .` passed.
- Trace path: `.agent-trace/20260628-142132-finance-entry-zone-dev-loop/`.
- Duplicated-work findings: one follow-up implementer created a noncanonical
  `.agent-trace/2026-06-28-entry-zone-strategy-followup/` trace despite the
  main agent owning canonical trace writes; no conflicting code edits resulted.
- Required next reads: `AGENTS.md`, `docs/PRODUCT.md`, `docs/CONTEXT.md`,
  `docs/WORKFLOWS.md`, `docs/specs/0001-finance-daily-market-brief.md`,
  `docs/specs/0002-finance-entry-zone-strategy.md`,
  `docs/milestones/0001-finance-agent-foundation.md`, and current finance
  package/tests.
- Agent routing log:
  - `spec-planner`: used.
  - `spec-griller`: used.
  - `explorer`: used for current implementation shape.
  - `$grill-with-docs`: used as focused status and docs alignment review.
  - dev-loop `explorer`: used.
  - dev-loop `implementer`: used for initial implementation and focused
    reviewer-fix follow-up.
  - dev-loop `test-runner`: used before and after reviewer fixes.
  - dev-loop `reviewer`: used before and after reviewer fixes.

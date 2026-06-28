# Spec: Finance Daily Market Brief

## Status

Accepted

## Goal

Generate an on-demand, fixture-backed daily-style finance brief for a
caller-supplied US equity watchlist and explicit `as_of` datetime.

The first slice must be useful for research while keeping supplied market data,
deterministic calculations, and deterministic report narrative distinguishable.
For `0001`, report text is deterministic template-rendered only. Model-written
synthesis is deferred to a follow-up spec.

It must not depend on Telegram, scheduling, live data providers, persistent
watchlists, runtime finance subagents, brokerage integrations, model-provider
integrations, or network access.

## Scenario

A developer requests a market brief for `["NVDA", "AAPL", "MSFT"]` as of
`2026-06-26T16:30:00-04:00` using static fixtures. Hermes produces one dated
markdown report with general US market context, one section per unique
supported normalized ticker, visible sections for unsupported or ambiguous
inputs, source metadata, freshness labels, and a constrained `Research-Only
Pullback Zone` section for each ticker with sufficient fresh evidence.

If a ticker has valid quote evidence but missing news, the ticker section still
renders and marks news incomplete. If quote data is stale, the report labels it
stale and does not evaluate the pullback zone. If a ticker input is ambiguous or
unsupported, the workflow flags it instead of guessing.

## In Scope

- On-demand report generation for a caller-supplied list of US-listed equity
  ticker symbols.
- An explicit caller-supplied `as_of` datetime.
- Static fixture-backed market, quote, range, and news evidence.
- General US market context.
- One report section per unique supported normalized ticker and visible
  sections for unsupported or ambiguous inputs.
- Source metadata, timestamps, and freshness labels for factual claims.
- A constrained research-only pullback-zone calculation per eligible ticker.
- Visible separation between supplied evidence, deterministic calculations, and
  deterministic report narrative.
- Fixture-backed verification without network access.

## Out Of Scope

- Telegram delivery.
- Automated scheduling.
- Persistent watchlist storage.
- Live market-data, fundamentals, filings, or news provider integration.
- Brokerage integration, alerts, trade execution, order routing, or position
  sizing.
- Personalized financial advice.
- Full technical analysis, scoring, ranking, or strategy logic.
- Runtime finance sub-agent architecture.
- Production deployment.

## Contracts

### Invocation

The workflow accepts:

- `watchlist`: ordered list of ticker strings supplied by the caller.
- `as_of`: explicit ISO-8601 datetime supplied by the caller.
- `fixture`: JSON-compatible evidence object loaded locally.

The implementation must expose an importable Python function:

```python
generate_daily_market_brief(watchlist: list[str], as_of: str, fixture: dict) -> str
```

The function returns one markdown report. The first implementation may create
the minimal package and test structure needed for this callable, but must not
add Telegram, scheduling, persistence, live providers, model-provider
integration, or network access.

The report must preserve the caller-supplied watchlist order for supported
tickers after normalization. Duplicate normalized tickers render one ticker
section at the first occurrence and note later duplicate inputs in the watchlist
summary. Unsupported or ambiguous inputs must get visible report sections.

For `0001`, report text is deterministic template-rendered only. No LLM or
model call is required or allowed. Narrative text may summarize and explain
supplied evidence, but it must be deterministically rendered from fixture data
and must not create factual market, price, or news claims that are absent from
the fixture.

### Fixture Format

`0001` requires static JSON-compatible fixtures with this top-level shape:

```json
{
  "as_of": "2026-06-26T16:30:00-04:00",
  "market_context": {
    "indices": [
      {
        "symbol": "SPY",
        "name": "S&P 500 proxy",
        "price": 650.0,
        "change_percent": 0.4,
        "timestamp": "2026-06-26T16:00:00-04:00",
        "source": "fixture"
      },
      {
        "symbol": "QQQ",
        "name": "Nasdaq proxy",
        "price": 580.0,
        "change_percent": 0.7,
        "timestamp": "2026-06-26T16:00:00-04:00",
        "source": "fixture"
      }
    ],
    "notes": [
      {
        "headline": "Market breadth improved into the close",
        "timestamp": "2026-06-26T15:45:00-04:00",
        "source": "fixture"
      }
    ]
  },
  "invalid_inputs": {
    "BRK.B": "Ambiguous class/share formatting in fixture"
  },
  "tickers": {
    "NVDA": {
      "company_name": "NVIDIA Corporation",
      "quote": {
        "current_price": 171.82,
        "timestamp": "2026-06-26T16:00:00-04:00",
        "source": "fixture"
      },
      "range_20d": {
        "recent_low_20d": 165.0,
        "recent_high_20d": 184.5,
        "timestamp": "2026-06-26T16:00:00-04:00",
        "source": "fixture"
      },
      "support_level": {
        "price": 166.0,
        "timestamp": "2026-06-26T16:00:00-04:00",
        "source": "fixture"
      },
      "news": [
        {
          "headline": "Example headline",
          "summary": "Short fixture-backed summary.",
          "timestamp": "2026-06-26T10:00:00-04:00",
          "source": "fixture"
        }
      ]
    }
  }
}
```

Complete market context requires:

- S&P 500 evidence, represented by `SPY`, `^GSPC`, or an explicit fixture label
  that names S&P 500.
- Nasdaq evidence, represented by `QQQ`, `^IXIC`, or an explicit fixture label
  that names Nasdaq.

If either required market proxy is missing, the report may still render ticker
sections when ticker evidence is otherwise valid, but must mark general market
context incomplete.

Optional market context may include Dow, Russell 2000, VIX, sector proxies,
macro notes, or market news, but the report must mark optional missing evidence
as unavailable rather than inventing it.

Required ticker fields for a pullback-zone evaluation:

- `quote.current_price`
- `quote.timestamp`
- `range_20d.recent_low_20d`
- `range_20d.recent_high_20d`
- `range_20d.timestamp`

Optional ticker fields:

- `support_level.price`
- `support_level.timestamp`
- `news[]`
- `company_name`

Optional top-level invalid input field:

- `invalid_inputs`: object whose keys are normalized input symbols after
  trimming whitespace and uppercasing and whose values are fixture-provided
  reasons for unsupported or ambiguous inputs.

Ticker normalization is limited to trimming leading/trailing whitespace and
uppercasing. A ticker is supported only when the normalized symbol exists in
`fixture["tickers"]`. Ambiguous inputs are represented only by
`fixture["invalid_inputs"]`; the implementation must not infer ambiguity from
external data.

### Freshness

Freshness is evaluated relative to the invocation `as_of`.

- The invocation `as_of` must equal fixture top-level `as_of`; mismatch is a
  validation error.
- `as_of` and all timestamps used by the report must be valid ISO-8601
  datetimes with timezone offsets.
- Timestamps later than `as_of` are invalid and must not be treated as fresh.
- Quote and range evidence is fresh when its timestamp is no more than 36 hours
  older than `as_of`.
- News evidence is fresh when its timestamp is no more than 7 calendar days
  older than `as_of`.
- Missing timestamps are treated as stale.
- Stale quote or range evidence prevents pullback-zone evaluation.
- Stale news does not prevent the ticker section from rendering, but the news
  section must label the evidence stale or unavailable.

### Pullback-Zone Calculation

The pullback-zone calculation is deterministic and uses only supplied fixture
fields.

- `reference_price` is `support_level.price` when present and fresh.
- Otherwise, `reference_price` is `range_20d.recent_low_20d`.
- `candidate_zone_lower` is `reference_price`.
- `candidate_zone_upper` is `reference_price * 1.03`.
- Lower and upper bounds are rounded to two decimals.
- If any required pullback field is missing or stale, the pullback zone is not
  evaluated.
- If `candidate_zone_upper >= quote.current_price`, the pullback zone is not
  evaluated because the current price is already inside or below the candidate
  zone.

### Report Output

The report must include:

- Title with `as_of`.
- General market context section.
- Watchlist summary section.
- One section per unique supported normalized ticker and visible sections for
  unsupported or ambiguous inputs.
- Explicit `Evidence`, `Deterministic Calculation`, and `Deterministic
  Narrative` labels where applicable so price, market, news, and pullback-zone
  claims can be traced to the fixture or deterministic calculation.
- Pullback-zone section for each ticker, either with the calculated candidate
  zone or a visible reason it was not evaluated.
- Limitations/disclaimer section.

The limitations section must include this sentence:

```text
Research only. Not personalized financial advice, not a recommendation to buy
or sell, and not a trade instruction.
```

Entry-related wording must use research-only language. It must not include:

- personalized financial advice
- position sizing
- guarantees
- trade instructions
- brokerage-action language such as "buy now", "place an order", or "execute"
- "buy zone", "target price", "upside", or "should buy"

The section title `Research-Only Pullback Zone` is allowed, but the report must
avoid broader entry, recommendation, or brokerage-action wording outside that
title and the deterministic explanation of the candidate zone.

## Failure Modes

- Empty watchlist: return a visible validation failure instead of an empty
  report.
- Duplicate tickers: render one ticker section at the first normalized
  occurrence and note duplicate inputs in the watchlist summary.
- Unsupported or ambiguous ticker: flag the input and do not substitute another
  symbol. Ambiguity must come from `fixture["invalid_inputs"]`, not external
  lookup or inference.
- Missing mandatory market proxies: render the report only if ticker evidence is
  otherwise valid, but mark general market context incomplete.
- Missing ticker quote: render the ticker as incomplete and skip calculations.
- Invalid, missing, future, or stale timestamps: mark invalid or stale and skip
  calculations that depend on the invalid or stale evidence.
- Invocation `as_of` mismatch with fixture top-level `as_of`: fail with a
  validation error.
- Missing news: render the ticker and mark news unavailable.
- Malformed fixture: fail with a validation error that identifies the missing or
  invalid field.
- Pullback-zone upper bound greater than or equal to current price: skip the
  pullback-zone evaluation and state the deterministic reason.

## Acceptance Criteria

- Valid fixtures produce one dated markdown report with general market context,
  one section per unique supported normalized ticker, and visible sections for
  unsupported or ambiguous inputs.
- The report preserves caller-supplied watchlist order for supported tickers.
- Every factual price, market, and news claim traces to supplied fixture
  evidence with timestamp or source metadata.
- The report visibly distinguishes quote/range evidence, deterministic
  pullback-zone calculation, and deterministic report narrative.
- The pullback-zone section uses only the specified deterministic heuristic.
- Missing, stale, ambiguous, or unsupported inputs degrade visibly instead of
  being silently guessed or invented.
- If required pullback fields are missing or stale, the pullback zone is not
  evaluated.
- If the candidate zone upper bound is greater than or equal to
  `current_price`, the pullback zone is not evaluated.
- Entry-related wording remains research-only and excludes personalized advice,
  position sizing, guarantees, trade instructions, and brokerage-action
  language.
- The implementation exposes
  `generate_daily_market_brief(watchlist: list[str], as_of: str, fixture: dict) -> str`.
- The implementation performs no LLM/model calls, network access, live provider
  calls, Telegram delivery, persistence, scheduling, or brokerage integration.
- Verification can run entirely against static fixtures without network access.

## Verification

- Add fixture-backed tests for a fully valid watchlist report.
- Add fixture-backed tests for empty watchlist and duplicate ticker inputs.
- Add fixture-backed tests for missing news with otherwise valid quote evidence.
- Add fixture-backed tests for stale quote or range evidence.
- Add fixture-backed tests for stale news.
- Add fixture-backed tests for missing mandatory market proxies.
- Add fixture-backed tests for missing ticker quote.
- Add fixture-backed tests for unsupported or ambiguous ticker input.
- Add fixture-backed tests for malformed fixture validation errors.
- Add fixture-backed tests for invalid timestamp parse errors, missing timezone
  offsets, `as_of` mismatch, and future timestamps.
- Add fixture-backed tests for pullback-zone calculation and skip conditions.
- Add fixture-backed tests for prohibited finance-advice wording.
- Run `uv run pytest` once implementation exists.
- Run `uv run ruff check .` once implementation exists.

If the commands or project files do not exist at implementation time, report the
missing command or file as a repo maturity gap instead of inventing a parallel
toolchain.

## Open Questions

None blocking for `0001`.

Deferred to later specs:

- Whether model-written synthesis should be added after deterministic
  fixture-backed reporting is verified.
- Whether a live-provider adapter should preserve this exact JSON shape or map
  provider-specific payloads into this shape at the boundary.

## Handoff

- Producer skill: `$hermes-spec`
- Intended consumer skill: `$hermes-dev-loop`.
- Status: Accepted; ready for implementation.
- Required next reads: `AGENTS.md`, `docs/PRODUCT.md`, `docs/CONTEXT.md`,
  `docs/milestones/0001-finance-agent-foundation.md`, and this spec.

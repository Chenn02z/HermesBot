# Milestone Handoff: Finance Agent Foundation

## Status

Verified

## Goal

Capture the verified first finance-domain slice of Hermes: a fixture-backed
market brief followed by a richer, separately scoped entry-zone strategy layer.

This milestone exists to record the completed fixture-backed finance foundation
without turning `0001` into the entire Finance Agent MVP.

## Producer And Consumer

- Producer skill: `$hermes-requirements`
- Intended consumer skill: `$hermes-spec`
- Next action: consume the future milestone files under `docs/milestones/`
  when planning runtime, provider, Telegram, persistence, or deployment work.

## Developer Workflow

Requirements gathering -> milestone handoff -> spec authoring -> accepted spec
implementation -> fixture-backed verification -> context maintenance.

## Specs

- `docs/specs/0001-finance-daily-market-brief.md` - Verified
- `docs/specs/0002-finance-entry-zone-strategy.md` - Verified

## Milestone Scope

- Research-only finance boundaries and terminology.
- Fixture-backed verification before live provider integration.
- Handoff artifacts between requirements, spec, dev-loop, and context workflows.

## Out Of Scope

- Telegram delivery.
- Automated scheduling.
- Persistent watchlist storage.
- Live market-data or news provider integration.
- Brokerage integration, alerts, trade execution, or position sizing.
- Full runtime finance subagent architecture.
- Production deployment.

## Requirements Packet: `0001`

Resolved workflow: formal spec for the first finance-domain implementation
slice.

Proposed spec path: `docs/specs/0001-finance-daily-market-brief.md`

Scope boundary:

- Generate an on-demand daily-style finance brief for a caller-supplied list of
  US-listed equity ticker symbols.
- Accept an explicit `as_of` datetime.
- Use fixture-backed market, quote, range, and news evidence.
- Include general US market context, one section per unique supported
  normalized ticker, and visible sections for unsupported or ambiguous inputs.
- Include source metadata, timestamps, and freshness labels.
- Include a constrained `Research-Only Pullback Zone` section per ticker.
- Keep supplied data, deterministic calculations, and deterministic report
  narrative distinguishable.
- Defer live provider integrations, Telegram delivery, scheduling, persistent
  watchlists, trade execution, full technical analysis, scoring, ranking,
  strategy logic, and runtime finance sub-agent architecture.

Scenarios:

- The developer requests a market brief for `["NVDA", "AAPL", "MSFT"]` as of a
  specific datetime and receives a dated markdown report.
- A ticker has valid price evidence but missing news; the report still renders
  and marks the news section incomplete.
- A ticker has stale quote data; the report labels the data stale and does not
  evaluate the pullback zone.
- A ticker input is ambiguous or unsupported; the workflow flags it instead of
  guessing.

Acceptance criteria candidates:

- Valid fixtures produce one dated markdown report with general market context,
  one section per unique supported normalized ticker, and visible sections for
  unsupported or ambiguous inputs.
- Every factual price, market, and news claim traces to supplied fixture
  evidence with timestamp or source metadata.
- The report distinguishes quote/range data, pullback-zone calculation, and
  deterministic report narrative.
- The pullback-zone section uses only a simple fixture-backed heuristic:
  required fields are `current_price`, `recent_low_20d`, `recent_high_20d`, and
  quote `timestamp`; optional `support_level` overrides `recent_low_20d` as the
  reference price; candidate zone is `reference_price` through
  `reference_price * 1.03`, rounded to two decimals.
- If required fields are missing or stale, or the candidate zone upper bound is
  greater than or equal to `current_price`, the pullback zone is not evaluated.
- Entry-related wording is research-only and avoids personalized advice,
  position sizing, guarantees, trade instructions, and brokerage-action
  language.
- Verification can run entirely against static fixtures without network access.

Resolved questions from `$hermes-spec` Draft:

- `0001` requires static JSON-compatible fixtures.
- `0001` requires S&P 500 and Nasdaq evidence. Dow, Russell 2000, VIX, sector
  proxies, macro notes, and market news are optional.
- `0001` uses deterministic template-rendered report text only; model-written
  synthesis is deferred to a later spec.

## Requirements Packet: `0002`

Resolved workflow: follow-up formal spec for richer entry-zone strategy after
`0001`.

Proposed spec path: `docs/specs/0002-finance-entry-zone-strategy.md`

Scope boundary:

- Build on the `0001` evidence and report boundaries.
- Define long-term investing research as the strategy horizon.
- Define exact fixture-backed technical-analysis inputs for moving averages,
  support and resistance, volatility, volume, momentum, and 52-week range.
- Define deterministic research-only entry-zone strategy logic.
- Define deterministic scoring, labels, and ranking across watched tickers.
- Separate supplied evidence, deterministic signal calculation, and
  deterministic template-rendered narrative.
- Preserve the `0001` financial-advice boundary.
- Defer model-written synthesis, valuation, fundamentals, live providers,
  Telegram, persistent watchlists, alerts, brokerage integration, and runtime
  finance sub-agents to later specs.

Scenarios:

- The developer asks Hermes to compare a watchlist and identify stronger
  research candidates from fixture-backed signals.
- A ticker has missing or stale strategy inputs; the strategy output degrades
  visibly instead of inventing a score.
- Technical signals conflict; the output explains the conflict without hiding
  uncertainty.

Acceptance criteria candidates:

- The accepted spec defines exact supported strategy inputs before
  implementation.
- Every score, rank, label, conflict note, or observation zone is reproducible
  from deterministic fixture inputs.
- The output distinguishes supplied evidence, calculated signals, and
  deterministic template-rendered narrative.
- The output preserves research-only wording and excludes trade instructions,
  position sizing, guarantees, and brokerage-action language.
- Missing or stale signal inputs are visible in the output.

Resolved questions from `$hermes-spec`:

- `0002` optimizes for long-term investing research.
- `0002` uses a deterministic 100-point technical setup score plus tiered
  research-candidate labels.
- Required technical groups are moving averages, RSI, 52-week range,
  support/resistance, ATR volatility, and volume.
- Valuation and fundamental signals are deferred to later specs.
- Model-written synthesis is deferred to later specs.

## Milestone Acceptance Criteria

- `$hermes-spec` wrote formal specs for `0001` and `0002` from this handoff.
- `0001` is verified after implementation and targeted finance checks.
- `0002` is verified after implementation and targeted finance checks.
- Durable docs identify finance as the first domain expansion while preserving
  Telegram, scheduling, live provider integration, and trade execution as later
  specs.
- Handoff artifacts are present so the next skill can continue without relying
  on conversational memory.

## Verification

- `docs/specs/0001-finance-daily-market-brief.md` is Verified.
- `docs/specs/0002-finance-entry-zone-strategy.md` is Verified.
- Full `uv run pytest` passed with `60 passed`.
- Full `uv run ruff check .` passed.
- No acceptance criterion requires network access, brokerage access, or
  Telegram delivery.

## Open Questions

- Which live data providers should be specified after fixture-backed behavior is
  verified?

## Handoff

- Producer skills: `$hermes-requirements`, `$hermes-spec`, then
  `$hermes-dev-loop`
- Intended consumer skill: `$hermes-spec` for future milestone contracts;
  `$hermes-context` when durable context needs alignment
- Artifact path: `docs/milestones/0001-finance-agent-foundation.md`.
- Status: Verified.
- Settled decisions: `0001` and `0002` are the verified fixture-backed finance
  foundation; live data providers, Telegram, persistence, runtime
  orchestration, and deployment remain later milestone/spec work.
- Unresolved blockers: none for this milestone; live data providers remain a
  later-spec question.
- Required next reads: `AGENTS.md`, `docs/PRODUCT.md`, `docs/CONTEXT.md`,
  `docs/specs/0001-finance-daily-market-brief.md`,
  `docs/specs/0002-finance-entry-zone-strategy.md`, and this milestone handoff.
- Formal specs now live under `docs/specs/`; `0001` and `0002` are Verified.
- Future work should consume the individual milestone files under
  `docs/milestones/` instead of a consolidated roadmap handoff.
- Agent routing log: `$hermes-requirements` and `$hermes-spec` gates predate
  this cleanup; this update aligns the touched handoff with the shared
  interface.

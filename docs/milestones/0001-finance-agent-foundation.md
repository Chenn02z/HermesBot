# Milestone Handoff: Finance Agent Foundation

## Status

Draft

## Goal

Capture the settled requirements for the first finance-domain slice of Hermes:
a fixture-backed market brief followed by a richer, separately scoped
entry-zone strategy layer.

This milestone exists to keep the immediate finance work useful without turning
`0001` into the entire Finance Agent MVP.

## Producer And Consumer

- Producer skill: `$hermes-requirements`
- Intended consumer skill: `$hermes-spec`
- Next action: keep `0002` Draft until its strategy questions are resolved;
  use `$hermes-context` only when implemented finance work settles durable
  terminology or workflow boundaries.

## Developer Workflow

Requirements gathering -> milestone handoff -> spec authoring -> accepted spec
implementation -> fixture-backed verification -> context maintenance.

## Specs

- `docs/specs/0001-finance-daily-market-brief.md` - Implemented
- `docs/specs/0002-finance-entry-zone-strategy.md` - Draft

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
- Define richer technical-analysis inputs such as moving averages, support and
  resistance levels, volatility, volume, trend, and recent price ranges.
- Define staged research-only entry-zone strategy logic.
- Define optional scoring or ranking across watched tickers.
- Separate deterministic signal calculation from model-written explanation.
- Preserve the `0001` financial-advice boundary.
- Defer implementation until `0001` is stable and the open strategy questions
  are resolved.

Scenarios:

- The developer asks Hermes to compare a watchlist and identify stronger
  research candidates from fixture-backed signals.
- A ticker has missing or stale strategy inputs; the strategy output degrades
  visibly instead of inventing a score.
- Technical signals conflict; the output explains the conflict without hiding
  uncertainty.

Acceptance criteria candidates:

- The formal spec defines exact supported strategy inputs before
  implementation.
- Every score, rank, or entry-zone candidate is reproducible from deterministic
  fixture inputs.
- The output distinguishes calculated signals from model-written explanation.
- The output preserves research-only wording and excludes trade instructions,
  position sizing, guarantees, and brokerage-action language.
- Missing or stale signal inputs are visible in the output.

Blocking questions for `$hermes-spec`:

- What investment horizon should `0002` optimize for: intraday, swing trade,
  multi-week accumulation, or long-term investing?
- Should scoring be numeric, tiered, or avoided in favor of qualitative setup
  labels?
- Which technical indicators are required for the first accepted strategy
  version?
- Should valuation or fundamental signals be included in `0002` or deferred?

## Milestone Acceptance Candidates

- `$hermes-spec` writes formal specs for `0001` and `0002` from this handoff.
- `0001` is reviewed and accepted before implementation starts.
- `0002` remains Draft until its strategy questions are resolved.
- Durable docs identify finance as the first domain expansion while preserving
  Telegram, scheduling, live provider integration, and trade execution as later
  specs.
- Handoff artifacts are present so the next skill can continue without relying
  on conversational memory.

## Verification

- Review `README.md`, `docs/PRODUCT.md`, `docs/CONTEXT.md`, and this milestone
  for consistent scope language.
- Run fixture-backed tests once implementation exists.
- Confirm no acceptance criterion requires network access, brokerage access, or
  Telegram delivery.

## Open Questions

- Should `0002` include valuation/fundamental signals or stay purely technical
  for its first accepted version?
- Which live data providers should be specified after fixture-backed behavior is
  verified?

## Handoff

- Producer skills: `$hermes-requirements`, then `$hermes-spec`
- Intended consumer skill: `$hermes-dev-loop` for accepted `0001`;
  `$hermes-spec` for unresolved `0002`
- Artifact path: `docs/milestones/0001-finance-agent-foundation.md`.
- Status: Draft.
- Settled decisions: `0001` is Implemented and remains the fixture-backed
  finance brief slice; `0002` remains Draft until strategy questions are
  resolved.
- Unresolved blockers: `0002` strategy horizon, scoring style, technical
  indicators, and valuation/fundamental scope remain open.
- Required next reads: `AGENTS.md`, `docs/PRODUCT.md`, `docs/CONTEXT.md`,
  `docs/specs/0001-finance-daily-market-brief.md`,
  `docs/specs/0002-finance-entry-zone-strategy.md`, and this milestone handoff.
- Formal specs now live under `docs/specs/`; `0001` is Implemented and `0002`
  remains Draft.
- `$hermes-context` should consume the implemented `0001` handoff when durable
  docs or workflow contracts need alignment; `$hermes-spec` should consume
  unresolved `0002` when its strategy questions are ready.
- Agent routing log: `$hermes-requirements` and `$hermes-spec` gates predate
  this cleanup; this update aligns the touched handoff with the shared
  interface.

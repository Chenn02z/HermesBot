# Spec: Finance Entry-Zone Strategy

## Status

Draft

## Goal

Define the follow-up finance strategy layer that builds on
`docs/specs/0001-finance-daily-market-brief.md` after `0001` is stable.

This spec will eventually add richer technical-analysis inputs, staged
research-only entry-zone strategy logic, and optional watchlist comparison while
preserving deterministic calculations, fixture-backed verification, and the
financial-advice boundary from `0001`.

## Scenario

A developer asks Hermes to compare a caller-supplied watchlist and identify
stronger research candidates using fixture-backed technical signals. Hermes
calculates supported signals deterministically, degrades visibly when inputs are
missing or stale, and explains signal conflicts without inventing a score or
recommendation.

## In Scope

- Strategy logic that builds on the `0001` evidence and report boundaries.
- Static fixture-backed technical-analysis inputs.
- Deterministic signal calculation separated from model-written explanation.
- Research-only entry-zone strategy wording.
- Visible degradation for missing or stale signal inputs.
- Optional comparison across watched tickers once scoring or labeling is
  settled.

## Out Of Scope

- Implementation before `0001` is accepted, implemented, and verified.
- Live market-data, fundamentals, filings, or news provider integration.
- Telegram delivery.
- Automated scheduling.
- Persistent watchlist storage.
- Brokerage integration, alerts, trade execution, order routing, or position
  sizing.
- Personalized financial advice.
- Runtime finance sub-agent architecture.
- Production deployment.

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

### Candidate Strategy Inputs

The first accepted version must define exact required and optional inputs before
implementation. Candidate inputs include:

- moving averages
- support and resistance levels
- volatility
- volume
- trend
- recent price ranges
- gap or drawdown measures

No score, rank, setup label, or entry-zone candidate may be produced unless its
required fixture inputs are present and fresh.

### Strategy Output

The future strategy output should distinguish:

- supplied evidence
- deterministic signal calculations
- deterministic score, rank, or setup label if adopted
- model-written explanation
- limitations and research-only disclaimer

If technical signals conflict, the output must show the conflict instead of
hiding uncertainty behind a single confident conclusion.

### Financial-Advice Boundary

Entry-zone strategy wording must remain research-only. It must not include:

- personalized financial advice
- position sizing
- guarantees
- trade instructions
- brokerage-action language such as "buy now", "place an order", or "execute"

## Failure Modes

- Missing strategy input: omit the dependent signal, score, rank, or label and
  show the missing input.
- Stale strategy input: mark stale and omit dependent calculations.
- Conflicting signals: show the conflict and avoid unsupported confidence.
- Unsupported ticker: preserve the `0001` unsupported-input behavior.
- Ambiguous strategy horizon: do not implement scoring or ranking until the
  horizon is settled.
- Undefined scoring method: do not invent ad hoc weights or thresholds.
- Valuation or fundamental data requested before scope is settled: defer to a
  later spec or explicit update to this spec.

## Acceptance Criteria

- Before implementation, the accepted spec defines exact supported strategy
  inputs, freshness rules, and required fixture fields.
- Every score, rank, setup label, or entry-zone candidate is reproducible from
  deterministic fixture inputs.
- The output distinguishes calculated signals from model-written explanation.
- The output preserves research-only wording and excludes personalized advice,
  position sizing, guarantees, trade instructions, and brokerage-action
  language.
- Missing or stale signal inputs are visible in the output.
- Conflicting signals are visible in the output.
- Verification can run entirely against static fixtures without network access.

## Verification

- Do not implement this spec until `0001` is stable and this spec's open
  questions are resolved.
- Add fixture-backed tests for supported strategy inputs and deterministic
  calculations after the accepted input set is defined.
- Add fixture-backed tests for missing, stale, and conflicting strategy inputs.
- Add fixture-backed tests for any adopted scoring, ranking, or setup-label
  behavior.
- Run `uv run pytest` once implementation exists.
- Run `uv run ruff check .` once implementation exists.

If the commands or project files do not exist at implementation time, report the
missing command or file as a repo maturity gap instead of inventing a parallel
toolchain.

## Open Questions

- What investment horizon should `0002` optimize for: intraday, swing trade,
  multi-week accumulation, or long-term investing?
- Should scoring be numeric, tiered, or avoided in favor of qualitative setup
  labels?
- Which technical indicators are required for the first accepted strategy
  version?
- Should valuation or fundamental signals be included in `0002` or deferred?
- Which freshness windows should apply to each strategy input?

## Handoff

- Producer skill: `$hermes-spec`
- Intended consumer skill: `$hermes-spec`
- Status: Draft; not ready for implementation.
- Required next reads: `AGENTS.md`, `docs/PRODUCT.md`, `docs/CONTEXT.md`,
  `docs/specs/0001-finance-daily-market-brief.md`,
  `docs/milestones/0001-finance-agent-foundation.md`, and this spec.

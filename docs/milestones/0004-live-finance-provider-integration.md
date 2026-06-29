# Milestone: Live Finance Provider Integration

## Status

Draft

## Source

Split from the consolidated roadmap requirements handoff, which has been
decomposed and removed. This file preserves future milestone direction only; it
does not authorize implementation.

Yahoo Finance was reviewed as a candidate on 2026-06-29 and is not accepted as
the first live provider target for this milestone. Yahoo's current terms
prohibit automated means of accessing or collecting data without prior written
permission, which makes it a poor default provider contract for this project.

## Goal

Integrate the first live finance provider after provider-neutral contracts are
accepted and verified.

## Scope Boundary

- Fetch live quote, market, news, and strategy inputs only through accepted
  adapters.
- Reuse deterministic finance report generation after evidence validation.
- Keep live behavior optional and explicitly configured.
- Exclude brokerage, trade execution, personalized advice, Telegram delivery,
  scheduling, persistence, model calls, and deployment.

## Scenarios

- The developer requests a report for a supported watchlist and the system
  fetches live evidence, maps it into canonical evidence, and renders a
  research-only report.
- Provider outage, rate limit, stale data, invalid symbol, or partial data
  produces visible degradation.

## Acceptance Criteria Candidates

- Provider choice and required credentials are explicit.
- Live behavior has fixture-backed tests plus optional local-only live smoke
  tests gated behind explicit credentials.
- Rate limits and provider errors are handled deterministically.
- No provider payload bypasses validation.
- Research-only wording remains enforced.

## Verification

- Add fixture-backed tests for live-provider adapter behavior.
- Add optional live smoke tests gated behind explicit credentials.
- Run `uv run pytest` without requiring live credentials.
- Run `uv run ruff check .`.

## Open Questions

Blocking for acceptance:

- Which licensed or permission-compatible provider should be first?

Settled:

- Yahoo Finance is not accepted as the first provider target unless a later
  requirements pass documents a permission-compatible access path.
- Live smoke tests, when introduced, must be optional local-only tests gated
  behind explicit credentials and excluded from the normal `uv run pytest`
  baseline.

## Handoff

- Producer skill: `$hermes-requirements`
- Intended consumer skill: `$hermes-requirements` for blocker resolution and
  acceptance; later `$hermes-spec` only after this milestone is Accepted.
- Artifact path: `docs/milestones/0004-live-finance-provider-integration.md`
- Status: Draft.
- Settled decisions: live provider work follows adapter contracts and preserves
  deterministic finance truth; Yahoo Finance is not accepted as the first
  provider target under current terms; live smoke tests must be optional,
  local-only, credential-gated, and excluded from normal tests.
- Unresolved blockers: first provider choice.
- Required next reads: `docs/milestones/0003-finance-evidence-provider-contract.md`
  and verified finance specs.
- Agent routing log: inherited from the roadmap split requirements pass; a
  fresh `$hermes-requirements` acceptance run must record current gates before
  this milestone can become Accepted.

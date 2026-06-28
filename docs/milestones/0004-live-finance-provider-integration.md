# Milestone: Live Finance Provider Integration

## Status

Draft

## Source

Split from the consolidated roadmap requirements handoff, which has been
decomposed and removed. This file preserves future milestone direction only; it
does not authorize implementation.

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
- Live behavior has fixture-backed tests plus optional live smoke tests.
- Rate limits and provider errors are handled deterministically.
- No provider payload bypasses validation.
- Research-only wording remains enforced.

## Verification

- Add fixture-backed tests for live-provider adapter behavior.
- Add optional live smoke tests gated behind explicit credentials.
- Run `uv run pytest` without requiring live credentials.
- Run `uv run ruff check .`.

## Open Questions

- Which provider should be first?
- What live smoke-test policy is acceptable for a personal project without
  making CI depend on paid or rate-limited APIs?

## Handoff

- Producer skill: `$hermes-requirements`
- Intended consumer skill: `$hermes-spec`
- Artifact path: `docs/milestones/0004-live-finance-provider-integration.md`
- Status: Draft.
- Settled decisions: live provider work follows adapter contracts and preserves
  deterministic finance truth.
- Unresolved blockers: provider choice and smoke-test policy.
- Required next reads: `docs/milestones/0003-finance-evidence-provider-contract.md`
  and verified finance specs.
- Agent routing log: inherited from the roadmap split requirements pass.

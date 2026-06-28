# Milestone: Finance Evidence Provider Contract

## Status

Draft

## Source

Split from the consolidated roadmap requirements handoff, which has been
decomposed and removed. This file preserves future milestone direction only; it
does not authorize implementation.

## Goal

Define provider-neutral adapter contracts that map finance provider payloads
into validated evidence objects before deterministic finance functions run.

## Scope Boundary

- Define adapter contracts for quote, market context, news, and strategy
  evidence.
- Map provider-shaped payloads into the existing validated evidence objects.
- Keep verification fixture-backed using recorded or static provider payloads.
- Keep provider credentials out of git.
- Exclude live network calls by default, Telegram delivery, persistence,
  model calls, brokerage, and deployment.

## Scenarios

- A recorded provider quote payload maps into the `0001` quote/range evidence
  shape.
- A recorded provider technical payload maps into the `0002` strategy evidence
  shape.
- Missing provider fields degrade visibly instead of reaching report generation
  as invented facts.

## Acceptance Criteria Candidates

- Adapter interfaces preserve source, timestamp, and freshness metadata.
- Provider failures, partial payloads, stale data, and invalid symbols are
  represented explicitly.
- Secrets are read from environment or config only when live behavior is later
  enabled.
- Deterministic finance functions remain the report source of truth.

## Verification

- Add fixture-backed adapter tests using recorded provider-shaped payloads.
- Add tests for partial payloads, stale data, invalid symbols, and provider
  error mapping.
- Run `uv run pytest`.
- Run `uv run ruff check .`.

## Open Questions

- Which live finance provider should be the first target after this contract is
  accepted and verified?

## Handoff

- Producer skill: `$hermes-requirements`
- Intended consumer skill: `$hermes-spec`
- Artifact path: `docs/milestones/0003-finance-evidence-provider-contract.md`
- Status: Draft.
- Settled decisions: live provider payloads must pass through validated
  evidence adapters before report generation.
- Unresolved blockers: first provider remains unsettled.
- Required next reads: verified finance specs and this milestone.
- Agent routing log: inherited from the roadmap split requirements pass.

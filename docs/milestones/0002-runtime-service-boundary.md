# Milestone: Runtime Service Boundary

## Status

Draft

## Source

Split from the consolidated roadmap requirements handoff, which has been
decomposed and removed. This file preserves future milestone direction only; it
does not authorize implementation.

## Goal

Define a local runtime boundary around the verified deterministic finance
functions before adding live providers, Telegram delivery, persistence, or
deployment.

## Scope Boundary

- Include a stable command or service interface for daily brief and entry-zone
  strategy generation.
- Include deterministic request and response schemas.
- Include health and readiness behavior.
- Preserve the current single-user personal product assumption.
- Exclude Telegram, Hermes Agent runtime integration, live providers,
  persistence, model calls, and deployment.

## Scenarios

- The developer invokes a local endpoint or command with a watchlist, `as_of`,
  and fixture payload and receives a deterministic markdown or structured
  report.
- Invalid requests return deterministic validation errors.
- Health checks do not require secrets, live providers, model calls, or network
  access.

## Acceptance Criteria Candidates

- Public runtime interface exposes both verified finance workflows.
- Request and response schemas are explicit and fixture-backed in tests.
- Health checks do not require secrets or network access.
- No model calls, provider calls, Telegram calls, persistence, or deployment
  behavior is introduced.

## Verification

- Add fixture-backed tests for valid runtime requests.
- Add tests for invalid request validation.
- Run `uv run pytest`.
- Run `uv run ruff check .`.

## Open Questions

- Should the first interface be a CLI, FastAPI endpoint, or both?

## Handoff

- Producer skill: `$hermes-requirements`
- Intended consumer skill: `$hermes-spec`
- Artifact path: `docs/milestones/0002-runtime-service-boundary.md`
- Status: Draft.
- Settled decisions: runtime boundary comes before live providers, Telegram,
  persistence, and deployment.
- Unresolved blockers: interface shape must be settled before acceptance.
- Required next reads: `docs/milestones/0001-finance-agent-foundation.md`,
  `docs/specs/0001-finance-daily-market-brief.md`,
  `docs/specs/0002-finance-entry-zone-strategy.md`, and this milestone.
- Agent routing log: inherited from the roadmap split requirements pass.

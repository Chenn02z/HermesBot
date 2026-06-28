# Milestone: Hermes Agent Runtime Integration

## Status

Draft

## Source

Split from the consolidated roadmap requirements handoff, which has been
decomposed and removed. This file preserves future milestone direction only; it
does not authorize implementation.

## Goal

Define how this repo integrates with the Nous Hermes Agent substrate while
preserving deterministic finance tools as the source of factual truth.

## Scope Boundary

- Expose deterministic finance functions as tools, actions, or agent-callable
  capabilities.
- Define planner, tool, and synthesis boundaries.
- Consume the OpenRouter model routing boundary when model-backed behavior is
  accepted by spec.
- Keep provider and model choices in config or explicit specs.
- Preserve the single-user personal product assumption.
- Exclude Telegram delivery, persistence, scheduling, AWS deployment, and
  brokerage integrations.

## Scenarios

- Hermes Agent plans a finance research workflow, calls deterministic finance
  tools, and returns an evidence-grounded answer.
- If model-written synthesis is enabled, it explains only supplied evidence and
  deterministic outputs.
- Routing trace records planner, tool, synthesis, and model-gateway steps.

## Acceptance Criteria Candidates

- "Hermes Agent integration" is defined as an explicit runtime/tool boundary.
- Deterministic tools remain the source of factual finance truth.
- OpenRouter usage is config-driven and never hardcodes model keys.
- Model-written synthesis, if included, has a separate financial-advice
  boundary and test coverage.
- Agent routing traces are visible and auditable.

## Verification

- Add tests or fixtures for tool invocation boundaries.
- Add tests for model-synthesis guardrails if synthesis is accepted.
- Run `uv run pytest`.
- Run `uv run ruff check .`.

## Open Questions

- Which Hermes Agent capabilities are required first: tool orchestration,
  model synthesis, memory, or all three?
- Which model-backed behavior, if any, belongs in the first Hermes Agent
  runtime integration pass?

## Handoff

- Producer skill: `$hermes-requirements`
- Intended consumer skill: `$hermes-spec`
- Artifact path: `docs/milestones/0006-hermes-agent-runtime-integration.md`
- Status: Draft.
- Settled decisions: Hermes Agent runtime integration consumes deterministic
  finance tools and, when model-backed behavior is accepted, the OpenRouter
  model routing boundary.
- Unresolved blockers: exact Hermes Agent runtime boundary.
- Required next reads: verified finance specs,
  `docs/milestones/0005-openrouter-model-routing-boundary.md`,
  `docs/CONTEXT.md`, and this milestone.
- Agent routing log: inherited from the roadmap split requirements pass.

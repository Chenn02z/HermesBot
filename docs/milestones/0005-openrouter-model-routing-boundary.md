# Milestone: OpenRouter Model Routing Boundary

## Status

Accepted

## Source

Split from the consolidated roadmap requirements handoff and the settled
product direction that OpenRouter is the planned gateway for varied runtime
model usage. The consolidated handoff has been decomposed and removed.

This milestone is accepted as input for `$hermes-spec` spec authoring. It does
not authorize implementation without an Accepted child spec under `docs/specs/`.

## Goal

Define how future model-backed runtime features route through OpenRouter without
allowing model output to become the source of factual finance truth.

## Scope Boundary

- Define configurable OpenRouter model identifiers for accepted model-backed
  runtime roles such as planning, synthesis, and low-risk utility work.
- Use these default model identifiers unless a child spec explicitly revises
  them:
  - planning: `~anthropic/claude-sonnet-latest`
  - synthesis: `~openai/gpt-latest`
  - low-risk utility: `openrouter/auto`
- Define secret/config handling for OpenRouter credentials.
- Define model-output boundaries for research-only finance synthesis.
- Preserve provider-agnostic implementation boundaries where a later spec
  explicitly chooses a different gateway.
- Exclude model calls from verified fixture-backed finance specs unless a later
  accepted spec introduces them.
- Exclude Telegram delivery, live finance providers, persistence, and
  deployment.

## Scenarios

- A later accepted runtime workflow chooses a configured OpenRouter model for
  planning and records that routing decision.
- Missing OpenRouter credentials fail startup or model-backed workflow
  execution safely, without affecting deterministic finance tool tests.
- Model-written synthesis explains supplied evidence and deterministic outputs
  without inventing price, market, news, score, or strategy claims.

The first model-backed runtime behavior should be planning only. Synthesis is
defined as a boundary and default for later specs, but it must not be the first
runtime behavior unless a child spec explicitly accepts the extra guardrails.

## Acceptance Criteria

- Model calls, when in scope, route through OpenRouter by configurable model
  identifiers and keep secrets outside git.
- Default model identifiers are documented as planning
  `~anthropic/claude-sonnet-latest`, synthesis `~openai/gpt-latest`, and
  low-risk utility `openrouter/auto`.
- The first model-backed runtime behavior is planning only.
- OpenRouter/model output may synthesize or explain supplied evidence, but must
  not become the source of factual finance truth.
- Deterministic finance tools and validated evidence objects remain the source
  of price, market, news, score, and strategy claims.
- Verified fixture-backed finance specs continue to perform no model calls.
- Provider-agnostic principles are preserved by keeping OpenRouter behind a
  model-gateway boundary.

## Verification

- Add config validation tests for missing or malformed OpenRouter settings when
  model-backed runtime behavior is enabled.
- Add tests proving default model identifiers are configurable and secrets stay
  outside git.
- Add planning-only routing tests for the first model-backed runtime behavior.
- Add tests for synthesis guardrails only if a later child spec accepts
  model-written synthesis.
- Run `uv run pytest`.
- Run `uv run ruff check .`.

## Open Questions

Blocking for acceptance:

- None.

Deferred to child specs:

- Exact runtime configuration shape.
- Whether synthesis should be enabled after planning-only routing is verified.
- Whether `openrouter/auto` is acceptable for production low-risk utility work
  or should be replaced by a fixed low-cost model.

## Handoff

- Producer skill: `$hermes-requirements`
- Intended consumer skill: `$hermes-spec`.
- Artifact path: `docs/milestones/0005-openrouter-model-routing-boundary.md`
- Status: Accepted.
- Settled decisions: OpenRouter is the planned gateway for varied model usage
  in later accepted specs; no current verified finance spec uses model calls;
  defaults are planning `~anthropic/claude-sonnet-latest`, synthesis
  `~openai/gpt-latest`, and low-risk utility `openrouter/auto`; the first
  model-backed runtime behavior is planning only.
- Unresolved blockers: none.
- Required next reads: verified finance specs, `docs/PRODUCT.md`,
  `docs/CONTEXT.md`, and this milestone.
- Agent routing log: `$hermes-requirements` continuation used current user
  decisions and external source checks; `spec-planner` and `spec-griller` were
  not re-run for this narrow blocker-resolution pass.

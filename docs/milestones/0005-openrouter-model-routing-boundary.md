# Milestone: OpenRouter Model Routing Boundary

## Status

Draft

## Source

Split from the consolidated roadmap requirements handoff and the settled
product direction that OpenRouter is the planned gateway for varied runtime
model usage. The consolidated handoff has been decomposed and removed. This
file preserves future milestone direction only; it does not authorize
implementation.

## Goal

Define how future model-backed runtime features route through OpenRouter without
allowing model output to become the source of factual finance truth.

## Scope Boundary

- Define configurable OpenRouter model identifiers for accepted model-backed
  runtime roles such as planning, synthesis, and low-risk utility work.
- Define secret/config handling for OpenRouter credentials.
- Define model-output boundaries for research-only finance synthesis.
- Preserve provider-agnostic implementation boundaries where a later spec
  explicitly chooses a different gateway.
- Exclude model calls from verified fixture-backed finance specs unless a later
  accepted spec introduces them.
- Exclude Telegram delivery, live finance providers, persistence, and
  deployment.

## Scenarios

- A later accepted Hermes runtime workflow chooses a configured OpenRouter model
  for synthesis and records that routing decision.
- Missing OpenRouter credentials fail startup or model-backed workflow
  execution safely, without affecting deterministic finance tool tests.
- Model-written synthesis explains supplied evidence and deterministic outputs
  without inventing price, market, news, score, or strategy claims.

## Acceptance Criteria Candidates

- Model calls, when in scope, route through OpenRouter by configurable model
  identifiers and keep secrets outside git.
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
- Add tests for synthesis guardrails if model-written synthesis is accepted.
- Run `uv run pytest`.
- Run `uv run ruff check .`.

## Open Questions

- Which OpenRouter models should be configured as defaults for planning,
  synthesis, and low-risk utility work?
- Should the first model-backed behavior be planning only, synthesis only, or
  both?

## Handoff

- Producer skill: `$hermes-requirements`
- Intended consumer skill: `$hermes-spec`
- Artifact path: `docs/milestones/0005-openrouter-model-routing-boundary.md`
- Status: Draft.
- Settled decisions: OpenRouter is the planned gateway for varied model usage
  in later accepted specs; no current verified finance spec uses model calls.
- Unresolved blockers: default model choices and first model-backed behavior.
- Required next reads: verified finance specs, `docs/PRODUCT.md`,
  `docs/CONTEXT.md`, and this milestone.
- Agent routing log: inherited from the roadmap split requirements pass.

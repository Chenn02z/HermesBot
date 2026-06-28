# Milestone: Telegram Delivery Foundation

## Status

Draft

## Source

Split from the consolidated roadmap requirements handoff, which has been
decomposed and removed. This file preserves future milestone direction only; it
does not authorize implementation.

## Goal

Add Telegram Bot API delivery for authorized, on-demand finance information
after the runtime and finance evidence boundaries are ready.

## Scope Boundary

- Define command parsing, response formatting, authorization, and error
  handling.
- Start with on-demand commands only unless `$hermes-spec` explicitly accepts
  scheduling in this milestone.
- Treat Telegram as a delivery channel, not the source of truth.
- Preserve the single-user personal product assumption by default.
- Exclude persistence, scheduled delivery, AWS deployment, brokerage, trade
  execution, and unauthorized multi-user behavior.

## Scenarios

- The authorized Telegram user sends `/brief NVDA MSFT` and receives a concise
  research-only report.
- The authorized Telegram user sends `/strategy META` and receives an
  entry-zone strategy report.
- An unauthorized chat receives no finance data.
- A request for personalized advice or execution instructions is refused or
  reframed within the research-only boundary.

## Acceptance Criteria Candidates

- Allowed chat IDs or users are explicit and default to the developer's
  personal use.
- Authorization is explicit and single-user first, such as one configured chat
  ID or user ID.
- Bot token and webhook secrets are never committed.
- Unsupported commands degrade clearly.
- Long reports are chunked, summarized, or linked according to a documented
  rule.
- Telegram errors, retries, and rate limits are handled.
- Advice and trading-language guardrails are tested.

## Verification

- Add fixture-backed command parsing and authorization tests.
- Add tests for unauthorized chats and advice-boundary refusals.
- Run `uv run pytest`.
- Run `uv run ruff check .`.

## Open Questions

- Should the Telegram MVP include only on-demand commands, or include scheduled
  delivery later through persistence and scheduling?

## Handoff

- Producer skill: `$hermes-requirements`
- Intended consumer skill: `$hermes-spec`
- Artifact path: `docs/milestones/0007-telegram-delivery-foundation.md`
- Status: Draft.
- Settled decisions: Telegram delivery is authorized and single-user by
  default, and it does not become the finance source of truth.
- Unresolved blockers: command set and scheduling boundary.
- Required next reads: runtime/service milestone, verified finance specs, and
  this milestone.
- Agent routing log: inherited from the roadmap split requirements pass.

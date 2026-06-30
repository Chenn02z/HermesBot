# Milestone: Telegram Delivery Foundation

## Status

Draft

## Source

Split from the consolidated roadmap requirements handoff, which has been
decomposed and removed. This file preserves future milestone direction only; it
does not authorize implementation.

## Goal

Add Telegram Bot API as the primary user interface for HermesBot, delivering
both on-demand finance information and push updates (morning brief, event-driven
price alerts, and "good buy" research summaries) after the runtime and finance
evidence boundaries are ready.

## Scope Boundary

- Define command parsing, response formatting, push delivery scheduling,
  authorization, and error handling.
- On-demand commands: `/brief`, `/research`, `/watch` (add/remove/list), plus
  any commands surfaced by accepted finance specs.
- Push delivery: one aggregated morning brief message per day, plus per-ticker
  event-driven alerts (price threshold triggers and "good buy" composite scoring
  triggers). Bundled per-ticker scheduled messages are out of scope.
- Treat Telegram as a delivery channel, not the source of truth.
- Scheduling follows US market clock; no waking-hours filter.
- Preserve the single-user personal product assumption.
- Exclude persistence and watchlist storage (deferred to milestone 0008), AWS
  deployment, trade execution, trade tracking, and unauthorized multi-user
  behavior.

## Scenarios

- The authorized Telegram user receives a single aggregated morning brief
  covering macro conditions, overnight moves, and a one-line status per
  watchlist ticker.
- The authorized Telegram user receives an event-driven price alert when a
  watchlist ticker crosses a configured threshold.
- The authorized Telegram user receives a "good buy" alert when a watchlist
  ticker triggers the composite scoring threshold (technical + fundamental +
  news).
- The authorized Telegram user sends `/brief NVDA MSFT` and receives an on-demand
  research-only report.
- The authorized Telegram user sends `/watch add NVDA` / `/watch remove TSLA`
  and the command is queued for persistence when milestone 0008 is ready.
- An unauthorized chat receives no finance data.

## Acceptance Criteria Candidates

- Allowed chat IDs or users are explicit and default to the developer's
  personal use.
- Authorization is explicit and single-user first, such as one configured chat
  ID or user ID.
- Bot token and webhook secrets are never committed.
- Morning brief is delivered as a single aggregated Telegram message.
- Per-ticker alerts are event-driven only (price threshold and "good buy"
  signals), not bundled scheduled dumps.
- Alert triggers follow US market clock; no waking-hours gating.
- Unsupported commands degrade clearly.
- Long reports are chunked, summarized, or linked according to a documented
  rule.
- Telegram errors, retries, and rate limits are handled.
- Advice and trading-language guardrails are tested.

## Verification

- Add fixture-backed command parsing, push-delivery scheduling, and
  authorization tests.
- Add tests for morning brief formatting and alert-trigger routing.
- Add tests for unauthorized chats and advice-boundary refusals.
- Run `uv run pytest`.
- Run `uv run ruff check .`.

## Open Questions

- None. Push delivery (morning brief + event-driven alerts) and on-demand
  commands are both in scope. Persistence and watchlist state are deferred to
  milestone 0008.

## Handoff

- Producer skill: `$hermes-requirements`
- Intended consumer skill: `$hermes-spec`
- Artifact path: `docs/milestones/0007-telegram-delivery-foundation.md`
- Status: Draft.
- Settled decisions: Telegram is the primary user interface. Push delivery
  includes one aggregated morning brief plus per-ticker event-driven price and
  "good buy" alerts. Scheduling uses US market clock. On-demand commands
  include watchlist management (`/watch`). Trade tracking is out of scope.
- Unresolved blockers: none; acceptance blocked only on milestone 0008 for
  watchlist persistence.
- Required next reads: runtime/service milestone, verified finance specs, and
  this milestone.
- Agent routing log: inherited from the roadmap split requirements pass.

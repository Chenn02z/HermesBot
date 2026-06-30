# Milestone: Persistence, Watchlists, And Scheduling

## Status

Draft

## Source

Split from the consolidated roadmap requirements handoff, which has been
decomposed and removed. This file preserves future milestone direction only; it
does not authorize implementation.

## Goal

Add PostgreSQL-backed personal watchlist state, preferences, scheduled delivery,
event-driven alert triggers, and audit records for the single-user product.

## Scope Boundary

- Define developer-owned watchlist state and preferences (5–10 tickers,
  user-managed via Telegram).
- Define Telegram identity mapping for the authorized user.
- Define timezone-aware schedules following US market clock.
- Define event-driven alert triggers: price thresholds and "good buy" composite
  scoring thresholds (transparent technical + fundamental + news scoring).
- Define audit records for generated and delivered research outputs.
- Exclude pgvector, semantic search, and vector embeddings (no concrete use
  case yet).
- Exclude brokerage, portfolio management, order routing, trade execution,
  trade tracking, multi-tenant behavior, and broad user-management features.

## Scenarios

- The authorized user saves a watchlist through Telegram `/watch add/remove/list`.
- The authorized user receives a scheduled daily morning brief.
- The authorized user receives an event-driven alert when a watchlist ticker
  crosses a configured price or scoring threshold.
- Duplicate scheduled deliveries are prevented.
- Failed scheduled deliveries are logged and recoverable.

## Acceptance Criteria Candidates

- User identity mapping is explicit and testable.
- Watchlist CRUD is scoped to authorized personal use.
- Persistence stores personal watchlists, schedules, preferences, alert
  thresholds, and audit records for the single authorized user; multi-user
  isolation is out of scope.
- Schedules are timezone-aware (US market clock).
- Data retention and deletion behavior are documented.
- Fixture-backed scheduler tests precede live jobs.
- Migrations are deterministic and reversible where possible.

## Verification

- Add persistence tests for watchlist CRUD and identity mapping.
- Add scheduler tests for timezone behavior and duplicate prevention.
- Add alert-trigger persistence tests (price and scoring thresholds).
- Run migrations in test setup when applicable.
- Run `uv run pytest`.
- Run `uv run ruff check .`.

## Open Questions

- What retention policy is appropriate for a personal audit trail?

## Handoff

- Producer skill: `$hermes-requirements`
- Intended consumer skill: `$hermes-spec`
- Artifact path: `docs/milestones/0008-persistence-watchlists-and-scheduling.md`
- Status: Draft.
- Settled decisions: persistence starts as single-user personal state. Watchlist
  is 5–10 tickers, user-managed via Telegram. Alerts are event-driven with
  transparent composite scoring. pgvector and semantic search deferred. US
  market clock is the scheduling timezone.
- Unresolved blockers: retention policy.
- Required next reads: Telegram milestone, runtime milestone, verified finance
  specs, and this milestone.
- Agent routing log: inherited from the roadmap split requirements pass.

# Milestone: Persistence, Watchlists, And Scheduling

## Status

Draft

## Source

Split from the consolidated roadmap requirements handoff, which has been
decomposed and removed. This file preserves future milestone direction only; it
does not authorize implementation.

## Goal

Add PostgreSQL-backed personal watchlist state, preferences, scheduled delivery,
and audit records for the single-user product.

## Scope Boundary

- Define developer-owned watchlist state and preferences.
- Define Telegram identity mapping for the authorized user.
- Define timezone-aware schedules.
- Define audit records for generated and delivered research outputs.
- Exclude brokerage, portfolio management, order routing, trade execution,
  multi-tenant behavior, and broad user-management features.

## Scenarios

- The authorized user saves a watchlist through Telegram.
- The authorized user receives a scheduled daily research brief.
- Duplicate scheduled deliveries are prevented.
- Failed scheduled deliveries are logged and recoverable.

## Acceptance Criteria Candidates

- User identity mapping is explicit and testable.
- Watchlist CRUD is scoped to authorized personal use.
- Persistence stores personal watchlists, schedules, preferences, and audit
  records for the single authorized user; multi-user isolation is out of scope.
- Schedules are timezone-aware.
- Data retention and deletion behavior are documented.
- Fixture-backed scheduler tests precede live jobs.
- Migrations are deterministic and reversible where possible.

## Verification

- Add persistence tests for watchlist CRUD and identity mapping.
- Add scheduler tests for timezone behavior and duplicate prevention.
- Run migrations in test setup when applicable.
- Run `uv run pytest`.
- Run `uv run ruff check .`.

## Open Questions

- Which timezone should be the default for scheduled briefs?
- What retention policy is appropriate for a personal audit trail?

## Handoff

- Producer skill: `$hermes-requirements`
- Intended consumer skill: `$hermes-spec`
- Artifact path: `docs/milestones/0008-persistence-watchlists-and-scheduling.md`
- Status: Draft.
- Settled decisions: persistence starts as single-user personal state, not a
  multi-tenant product surface.
- Unresolved blockers: timezone and retention policy.
- Required next reads: Telegram milestone, runtime milestone, verified finance
  specs, and this milestone.
- Agent routing log: inherited from the roadmap split requirements pass.

# Milestone: Containerization And Runtime Config

## Status

Draft

## Source

Split from the consolidated roadmap requirements handoff, which has been
decomposed and removed. This file preserves future milestone direction only; it
does not authorize implementation.

## Goal

Package the runtime service, worker, and database dependencies for
production-shaped local operation before cloud deployment.

## Scope Boundary

- Define Docker or equivalent runtime packaging.
- Define `.env.example`, required environment variables, startup validation,
  health checks, and local compose behavior.
- Include OpenRouter, provider, Telegram, and database configuration boundaries
  only as required by accepted earlier milestones.
- Exclude cloud deployment.

## Scenarios

- The developer starts the runtime locally with production-shaped
  configuration.
- Missing required config fails startup safely.
- Health checks report service readiness without requiring live provider calls
  or model calls.

## Acceptance Criteria Candidates

- `.env.example` documents required variables without secrets.
- Containers expose health/readiness checks.
- Startup validates required config.
- Tests do not require live credentials.
- Logs avoid leaking secrets, tokens, provider keys, OpenRouter keys, or
  Telegram content beyond accepted retention rules.

## Verification

- Add config validation tests.
- Add local container or compose smoke checks when tooling exists.
- Run `uv run pytest`.
- Run `uv run ruff check .`.

## Open Questions

- Should local production-shaped operation include PostgreSQL from the start or
  defer it until persistence is accepted?

## Handoff

- Producer skill: `$hermes-requirements`
- Intended consumer skill: `$hermes-spec`
- Artifact path: `docs/milestones/0009-containerization-and-runtime-config.md`
- Status: Draft.
- Settled decisions: config must validate secrets and gateway/provider
  boundaries without committing credentials.
- Unresolved blockers: exact local dependency set.
- Required next reads: accepted runtime, Telegram, persistence, provider, and
  OpenRouter-related specs as applicable.
- Agent routing log: inherited from the roadmap split requirements pass.

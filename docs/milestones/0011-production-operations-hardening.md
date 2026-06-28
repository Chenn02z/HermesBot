# Milestone: Production Operations Hardening

## Status

Draft

## Source

Split from the consolidated roadmap requirements handoff, which has been
decomposed and removed. This file preserves future milestone direction only; it
does not authorize implementation.

## Goal

Add operational readiness after EC2 deployment without expanding product scope.

## Scope Boundary

- Cover logs, monitoring, backups, restore drills, secret rotation, provider
  outage playbooks, Telegram delivery failure handling, and rate limits.
- Include OpenRouter outage, quota, and model-routing failure behavior when
  model-backed features have been accepted.
- Preserve the single-user personal product operating model unless a later spec
  explicitly broadens it.
- Exclude major product expansion.

## Scenarios

- The developer can inspect failures without exposing secrets.
- The developer can rotate Telegram, provider, OpenRouter, and AWS
  credentials.
- The developer can back up and restore persistent data.
- Provider, OpenRouter, or Telegram outages produce visible operator signals.

## Acceptance Criteria Candidates

- Structured logs exist and redact sensitive values.
- Backup and restore procedure is documented and tested.
- Secret rotation steps are documented.
- Provider, OpenRouter, and Telegram outage playbooks exist.
- No silent failed scheduled deliveries.

## Verification

- Add tests or runbooks for redaction and backup/restore behavior.
- Validate secret rotation documentation.
- Validate outage playbooks against accepted runtime behavior.

## Open Questions

- What monitoring surface is sufficient for a single-user deployment?
- Which backup cadence is appropriate for personal watchlists and audit logs?

## Handoff

- Producer skill: `$hermes-requirements`
- Intended consumer skill: `$hermes-spec`
- Artifact path: `docs/milestones/0011-production-operations-hardening.md`
- Status: Draft.
- Settled decisions: operations hardening follows deployment and includes
  OpenRouter only when model-backed features exist.
- Unresolved blockers: monitoring and backup policy.
- Required next reads: deployment, persistence, Telegram, provider, and
  OpenRouter-related specs as applicable.
- Agent routing log: inherited from the roadmap split requirements pass.

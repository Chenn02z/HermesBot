# Milestone: AWS EC2 Deployment Foundation

## Status

Draft

## Source

Split from the consolidated roadmap requirements handoff, which has been
decomposed and removed. This file preserves future milestone direction only; it
does not authorize implementation.

## Goal

Deploy the containerized Hermes runtime to AWS EC2 for the personal product
after service, config, health check, and rollback boundaries exist.

## Scope Boundary

- Define EC2 provisioning assumptions, networking, TLS/webhook URL strategy,
  runtime environment injection, restart behavior, and rollback.
- Keep deployment sized for a single-user personal product by default.
- Exclude multi-region high availability, managed Kubernetes, trade execution,
  and unbounded production operations work.

## Scenarios

- The developer provisions EC2, configures runtime environment variables,
  starts the service, and verifies health.
- Telegram webhook delivery reaches the deployed service.
- A bad deploy can be rolled back.

## Acceptance Criteria Candidates

- Deployment runbook exists.
- Secrets stay outside git.
- TLS/webhook strategy is specified.
- Restart and rollback paths exist.
- Least-privilege AWS assumptions are documented.
- Deployment verification does not expose unauthorized finance data.

## Verification

- Add or document a deployment smoke-check procedure.
- Verify health checks after deployment.
- Verify rollback steps with a non-destructive dry run where feasible.

## Open Questions

- Is single-instance Docker on EC2 acceptable for MVP?
- Should managed database, managed TLS, backups, and monitoring be required
  before first deployment?

## Handoff

- Producer skill: `$hermes-requirements`
- Intended consumer skill: `$hermes-spec`
- Artifact path: `docs/milestones/0010-aws-ec2-deployment-foundation.md`
- Status: Draft.
- Settled decisions: AWS deployment waits for service, container, config,
  secrets, and health-check boundaries.
- Unresolved blockers: deployment architecture choices.
- Required next reads: containerization/config milestone and this milestone.
- Agent routing log: inherited from the roadmap split requirements pass.

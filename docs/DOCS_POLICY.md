# Documentation Policy

This document defines where durable project information belongs.

## Canonical Destinations

- `README.md`: public overview.
- `docs/PRODUCT.md`: product intent, audience, scope, principles, and roadmap.
- `docs/CONTEXT.md`: canonical terminology and workflow boundaries.
- `docs/WORKFLOWS.md`: detailed skill workflow rules and handoff expectations.
- `docs/AGENT_ROLES.md`: subagent roles, edit permissions, and routing
  principles.
- `docs/DOCS_POLICY.md`: documentation destinations and status rules.
- `docs/specs/`: implementation-ready contracts.
- `docs/milestones/`: larger deliverable slices.
- `.agents/skills/`: reusable Codex workflows.
- `.codex/agents/`: project-scoped role/model/permission presets.

## Spec And Milestone Docs

Use `docs/specs/` for executable contracts with goal, scope, contracts, failure
modes, acceptance criteria, verification, and open questions.

Use `docs/milestones/` for larger deliverable slices that may produce or group
multiple specs.

Use `docs/adr/NNNN-slug.md` only for durable, hard-to-reverse decisions with
real trade-offs. Do not create an ADR for ordinary cleanup, obvious routing, or
small reversible documentation changes.

## Context Maintenance

Use `$hermes-context` to update docs when a term, boundary, workflow, product
decision, role definition, or agent/skill usage becomes settled.

Keep implementation details out of `docs/CONTEXT.md`. Put executable behavior
in specs, product direction in `docs/PRODUCT.md`, and operating workflow detail
in `docs/WORKFLOWS.md`.

## Documentation Changes

- Keep changes surgical and tied to the current spec or explicit task.
- Prefer repo docs over general assumptions.
- Do not batch unrelated terminology changes.
- Preserve handoff artifacts when one skill expects another skill to continue.
- Report missing commands or missing tooling as repo maturity gaps.

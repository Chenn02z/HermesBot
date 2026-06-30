---
name: hermes-context
description: Keeps repo context aligned across AGENTS.md, README, durable docs, specs, skills, and agents. Use whenever terminology, workflow boundaries, project direction, or agent/skill setup changes.
---

# Context Workflow

Use when settled work changes terminology, workflow boundaries, product
direction, role definitions, or agent/skill usage.

## Prerequisites

1. `AGENTS.md` (one-time orientation)
2. The handoff artifact that triggered the context update

## Canonical Files

- `README.md`, `AGENTS.md`: overview and operating contract
- `docs/PRODUCT.md`, `docs/CONTEXT.md`: product and terminology
- `docs/WORKFLOWS.md`: handoff interface, spec status
- `docs/AGENT_ROLES.md`, `docs/DOCS_POLICY.md`: roles and doc rules
- `docs/specs/`, `docs/milestones/`: contracts and deliverables
- `.agents/skills/`, `.codex/agents/`: workflows and presets

## Workflow

1. Use `explorer` to inspect current docs and skills.
2. Use `doc-curator` for surgical updates to context docs and skill/agent rules.
3. Use `spec-griller` when changes affect scope, terminology, or workflow.
4. Use `$grill-with-docs` as adversarial pass.
5. Keep implementation details out of `docs/CONTEXT.md`.

## Output

Return handoff artifact. Include: changed docs, settled terms/decisions,
removed contradictions, follow-up updates needed.

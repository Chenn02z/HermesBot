---
name: hermes-context
description: Keeps Hermes Agent repo context aligned across AGENTS.md, README, product docs, context docs, specs, and skills. Use whenever terminology, workflow boundaries, project direction, or agent/skill setup changes.
---

# Hermes Context

Use this skill when project meaning or developer workflow changes, especially
after requirements or spec decisions settle. It consumes handoff artifacts from
`$hermes-requirements`, `$hermes-spec`, or `$hermes-dev-loop` when those
workflows settle terminology, scope, product direction, or skill behavior.

This skill is the required follow-up whenever settled work changes canonical
context: terminology, workflow boundaries, product direction, role definitions,
agent/skill usage, or cross-document meaning.

The named project agents in this workflow are authorized subagents for this
skill's scoped task. The main agent still owns judgment, user interaction,
reconciliation, and final reporting.

## Canonical Files

- `README.md`: public project overview.
- `AGENTS.md`: Codex operating rules for this repo.
- `docs/PRODUCT.md`: product intent and roadmap.
- `docs/CONTEXT.md`: terminology and boundaries.
- `docs/specs/`: executable component/workflow contracts.
- `.agents/skills/`: reusable development workflows.
- `.codex/agents/`: role/model/permission presets.

## Workflow

1. Use `explorer` to inspect current docs and skills.
2. Identify contradictions, stale inherited language, or duplicated concepts.
3. Use `doc-curator` for surgical updates to durable context docs and skill or
   agent rules.
4. Use `spec-griller` when changes affect scope, terminology, or workflow
   contracts. Independent read-only passes may run in parallel.
5. Use `$grill-with-docs` as the adversarial pass when the context change could
   conflict with README, product docs, specs, milestones, or current repo state.
6. Keep implementation details out of `docs/CONTEXT.md`.

## Output

Return changed docs, settled terms, removed contradictions, and any follow-up
skill/spec updates still needed. If another workflow must continue, return a
handoff artifact naming the intended consumer skill, relevant docs/specs, settled
context decisions, and remaining blockers.

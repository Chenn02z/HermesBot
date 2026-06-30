---
name: grill-with-docs
description: "Pressure-test workspace plans, specs, milestones, and terminology against README, AGENTS.md, product docs, context docs, and current repo state."
---

# Grill With Docs

Use this skill when a plan, spec, milestone, or terminology decision needs
pressure-testing against the repo's documented intent and current files.

Prefer `$hermes-spec` for writing specs and `$hermes-requirements` for shaping
vague ideas. Use this skill as a focused adversarial review pass.

This is a support skill, not the owner of a workflow. `$hermes-requirements`,
`$hermes-spec`, and `$hermes-context` may use it to challenge proposed
requirements packets, formal specs, milestone changes, and context updates
against the repo's documented boundaries.

## Read First

1. `AGENTS.md`
2. `README.md`
3. `docs/PRODUCT.md`
4. `docs/CONTEXT.md`
5. Relevant reference docs such as `docs/WORKFLOWS.md`,
   `docs/AGENT_ROLES.md`, or `docs/DOCS_POLICY.md`
6. Relevant files under `docs/specs/` or `docs/milestones/`
7. Touched code or skill files, if any

## Workflow

1. Resolve the user's actual goal in workspace terms.
2. Read the repo before asking anything the repo can answer.
3. Challenge fuzzy, overloaded, or conflicting terms immediately.
4. Use concrete developer workflows to force boundary decisions.
5. Separate settled decisions from open questions.
6. Recommend the smallest doc/spec update that removes ambiguity.
7. Create an ADR only when the decision is hard to reverse, surprising, and a
   real trade-off.

## Review Targets

- `docs/CONTEXT.md` for canonical terminology and workflow boundaries.
- `docs/PRODUCT.md` for product intent, scope, and roadmap.
- `docs/WORKFLOWS.md` for skill workflow rules and handoff expectations.
- `docs/AGENT_ROLES.md` for subagent roles, edit permissions, and routing.
- `docs/DOCS_POLICY.md` for documentation destinations and status rules.
- `docs/specs/` for executable contracts.
- `docs/milestones/` for larger deliverable slices.
- `docs/adr/NNNN-slug.md` for durable architecture decisions.

## Workspace Terminology

Prefer the repo's language over generic alternatives:

- `HermesBot` for this repository's personal finance research product.
- `workspace` for this repo and its docs, skills, specs, and agents.
- `main agent` for the active Codex thread that owns final judgment.
- `subagent` for delegated role/model workers.
- `skill` for reusable workflows under `.agents/skills/`.
- `spec` for executable contracts under `docs/specs/`.
- `milestone` for larger deliverable slices.
- `spec grilling` for adversarial spec review.
- `dev loop` for accepted-spec implementation and verification.

## Output Discipline

- Lead with contradictions, missing decisions, and scope risks.
- Keep findings grounded in file references where possible.
- Do not write implementation details into `docs/CONTEXT.md`.
- Do not batch unrelated terminology changes.

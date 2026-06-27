---
name: hermes-requirements
description: Produces pre-spec requirements packets for Hermes Agent work. Use when gathering requirements, clarifying product direction, deciding scope, or turning an idea into inputs for hermes-spec; do not use it to write full specs.
---

# Hermes Requirements

Use this skill before writing implementation specs when the request is still
ambiguous. This skill produces a pre-spec requirements packet handoff, not a
`docs/specs/...` file.

The named project agents in this workflow are authorized subagents for this
skill's scoped task. The main agent still owns judgment, user interaction,
reconciliation, and final reporting.

## Workflow

1. Read `README.md`, `AGENTS.md`, `docs/PRODUCT.md`, and `docs/CONTEXT.md`.
2. Resolve the request into one developer workflow:
   - milestone update
   - requirements packet for a new spec
   - context/terminology decision
   - implementation request that needs a spec first
3. Ask at most one blocking question if the repo cannot answer it.
4. Use `spec-planner` for the proposed workflow, scope boundary, scenarios, and
   acceptance criteria candidates.
5. Use `spec-griller` or `$grill-with-docs` to challenge ambiguity, failure
   modes, context drift, and scope creep. Independent read-only passes may run
   in parallel.
6. Have the main agent settle decisions with the user.
7. If a term, boundary, workflow, product direction, or skill usage changes,
   hand off to `$hermes-context` after the decision is settled.
8. Hand the requirements packet to `$hermes-spec` when a formal spec or
   milestone contract is needed.

## Output

Return a handoff artifact for `$hermes-spec`:

- the resolved workflow
- producer skill and intended consumer skill
- proposed spec name/path
- proposed milestone name/path, when the workflow is milestone work
- scope boundary
- scenarios
- acceptance criteria candidates
- settled user decisions
- blocking questions
- docs/specs/milestones that `$hermes-spec` should read next

Do not create or update a full `docs/specs/...` file from this skill. Do not
start implementation from this skill unless the user explicitly waives the spec
step. This skill may write or update requirements handoff artifacts and
proposed milestone handoffs only. If the resolved workflow is a milestone
update, this skill proposes the milestone handoff; `$hermes-spec` writes or
updates the milestone contract.

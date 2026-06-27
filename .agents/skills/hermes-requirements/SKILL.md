---
name: hermes-requirements
description: Produces pre-spec requirements packets for Hermes Agent work. Use when gathering requirements, clarifying product direction, deciding scope, or turning an idea into inputs for hermes-spec; do not use it to write full specs.
---

# Hermes Requirements

Use this skill before writing implementation specs when the request is still
ambiguous. This skill produces a pre-spec requirements packet, not a
`docs/specs/...` file.

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
   modes, context drift, and scope creep.
6. Have the main agent settle decisions with the user.
7. If a term, boundary, workflow, product direction, or skill usage changes,
   hand off to `$hermes-context` after the decision is settled.
8. Hand the requirements packet to `$hermes-spec` when a formal spec is needed.

## Output

Return:

- the resolved workflow
- proposed spec name/path
- scope boundary
- scenarios
- acceptance criteria candidates
- blocking questions

Do not create or update a full `docs/specs/...` file from this skill. Do not
start implementation from this skill unless the user explicitly waives the spec
step.

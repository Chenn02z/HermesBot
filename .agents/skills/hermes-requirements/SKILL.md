---
name: hermes-requirements
description: Produces requirements packets and Accepted milestone contracts for Hermes Agent work. Use when gathering requirements, clarifying product direction, deciding scope, or accepting milestone direction before hermes-spec creates specs; do not use it to write full specs.
---

# Hermes Requirements

Use this skill before writing implementation specs when the request is still
ambiguous or when milestone direction must be accepted before spec work starts.
This skill produces requirements handoffs and milestone contracts, not
`docs/specs/...` files.

The named project agents in this workflow are authorized subagents for this
skill's scoped task. The main agent still owns judgment, user interaction,
reconciliation, and final reporting.

## Workflow

1. Read `README.md`, `AGENTS.md`, `docs/PRODUCT.md`, and `docs/CONTEXT.md`.
2. Resolve the request into one developer workflow:
   - milestone contract or milestone acceptance
   - requirements packet for a new spec
   - context/terminology decision
   - implementation request that needs a spec first
3. Identify every blocking question the repo cannot answer. Ask the user before
   closing the run, and do not emit an Accepted milestone with unresolved
   blockers.
4. Use `$grill-with-docs` to keep asking questions and align on needs and
   requirements of the user.
5. Use `spec-planner` for the proposed workflow, scope boundary, scenarios, and
   acceptance criteria candidates.
6. Use `spec-griller` to challenge ambiguity, failure modes, context drift,
   and scope creep. Independent read-only passes may run in parallel.
7. Have the main agent settle decisions with the user.
8. When the resolved workflow is milestone work, use `doc-curator` to write or
   update the milestone contract under `docs/milestones/`.
9. Mark a milestone `Accepted` only after all acceptance-blocking questions are
   answered or explicitly deferred as non-blocking.
10. If a term, boundary, workflow, product direction, or skill usage changes,
   hand off to `$hermes-context` after the decision is settled.
11. Hand Accepted milestone contracts to `$hermes-spec` when implementation
    specs under `docs/specs/` are needed.

## Output

Return a handoff artifact using the shared interface in `docs/WORKFLOWS.md`.
When the next step is spec creation, the intended consumer is `$hermes-spec`
and the artifact must be an Accepted milestone contract.

Include these requirements-specific fields:

- resolved workflow
- proposed spec name/path
- milestone path, when the workflow is milestone work
- milestone status, when the workflow is milestone work
- scope boundary
- scenarios
- acceptance criteria candidates
- settled user decisions
- blocking questions

Do not create or update a full `docs/specs/...` file from this skill. Do not
start implementation from this skill unless the user explicitly waives the spec
step. This skill may write or update requirements handoff artifacts and
milestone contracts under `docs/milestones/`.

If the resolved workflow is a milestone acceptance run, all blocking questions
must be answered by the repo or the user before the milestone is marked
`Accepted`. If the user does not answer a blocking question, return a blocked or
Draft handoff instead of closing as Accepted.

Blocking questions are questions whose answer is required before milestone
acceptance. Deferred questions may remain only when explicitly listed as
non-blocking and assigned to child specs or later milestones.

`$hermes-spec` consumes Accepted milestones from this skill and creates
implementation specs under `docs/specs/`; it does not own milestone updates.

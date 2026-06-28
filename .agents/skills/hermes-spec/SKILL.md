---
name: hermes-spec
description: Converts settled Hermes Agent requirements packets into formal specs or milestone contracts. Use when writing docs/specs files, milestone specs, workflow contracts, acceptance criteria, or moving a spec through Draft, Accepted, Implemented, and Verified states.
---

# Hermes Spec

Use this skill when the work needs an executable spec or milestone contract. It
consumes handoff artifacts from `$hermes-requirements` when the request began
ambiguous: resolved workflow, producer/consumer, proposed spec or milestone
path, scope boundary, scenarios, acceptance criteria candidates, settled user
decisions, blocking questions, and docs to read next.

The named project agents in this workflow are authorized subagents for this
skill's scoped task. The main agent still owns judgment, user interaction,
reconciliation, and final reporting.

## Read First

1. `AGENTS.md`
2. `docs/PRODUCT.md`
3. `docs/CONTEXT.md`
4. Relevant files under `docs/milestones/` or `docs/specs/`
5. Touched code, if any exists

## Spec Template

```md
# Spec: Title

## Status
Draft

## Goal

## Scenario

## In Scope

## Out Of Scope

## Contracts

## Failure Modes

## Acceptance Criteria

## Verification

## Open Questions
```

## Workflow

1. Use `explorer` if current repo state is unclear.
2. If the request is still vague, return to `$hermes-requirements` before
   writing the formal spec.
3. Use `spec-planner` to draft or revise the spec from the requirements packet.
4. Use `spec-griller` before marking a spec Accepted. Independent read-only
   passes may run in parallel.
5. Use `$grill-with-docs` when the spec changes terminology, workflow
   boundaries, milestone direction, or other repo context.
6. Keep specs implementation-ready but not implementation-heavy.
7. If code reveals the spec is wrong, update the spec before continuing.
8. If the spec settles a context change, hand off to `$hermes-context`.
9. When the spec or milestone is ready for implementation, leave an explicit
   handoff artifact for `$hermes-dev-loop`.


## Required Agent Gates

  For every `$hermes-spec` run that creates or materially revises a spec:

  1. `spec-planner` must be used to draft or revise the spec from the requirements
     packet.
  2. `spec-griller` must be used before any spec is marked Accepted.
  3. If either agent cannot be invoked, stop and report the blocker or explicitly
     continue only if the user approves a manual fallback.

  The main agent may reconcile and edit the final spec, but must not silently skip
  these gates.

## Status Rules

- `Draft`: requirements are still being shaped.
- `Accepted`: implementation can start.
- `Implemented`: code/docs have been changed but final verification may remain.
- `Verified`: acceptance criteria have passed or documented exceptions exist.

## Output

Return a handoff artifact:

- producer skill and intended consumer skill
- spec or milestone path
- status
- key contracts and acceptance criteria
- settled decisions carried forward from requirements
- remaining open questions or blockers
- verification expectations
- docs/specs/milestones that the next skill should read

Do not hide new scope inside implementation notes.
This skill writes or updates formal contracts under `docs/specs/` and
`docs/milestones/`.

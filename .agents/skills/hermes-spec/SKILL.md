---
name: hermes-spec
description: Converts Accepted milestone contracts into implementation specs under docs/specs. Reject Draft or non-Accepted milestones; do not update milestone contracts.
---

# Spec Workflow

Use this skill when an Accepted milestone needs one or more executable
implementation specs under `docs/specs/`. It consumes Accepted milestone
contracts produced by `$hermes-requirements`, including scope boundary,
scenarios, acceptance criteria candidates, settled user decisions, answered
blockers, and docs to read next.

Reject the run if the supplied milestone is missing, not marked `Accepted`, has
unresolved blocking questions, or asks this skill to update a milestone
contract. Send milestone drafting, milestone acceptance, or blocker resolution
back to `$hermes-requirements`.

The named project agents in this workflow are authorized subagents for this
skill's scoped task. The main agent still owns judgment, user interaction,
reconciliation, and final reporting.

## Read First

1. `AGENTS.md`
2. `docs/PRODUCT.md`
3. `docs/CONTEXT.md`
4. The Accepted milestone under `docs/milestones/`
5. Relevant files under `docs/specs/`
6. Touched code, if any exists

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
2. Confirm the input milestone is marked `Accepted` and has no unresolved
   blocking questions.
3. If the milestone is Draft, missing, blocked, vague, or needs milestone
   edits, reject the run and return to `$hermes-requirements`.
4. Use `spec-planner` to draft or revise implementation specs from the Accepted
   milestone contract.
5. If the milestone can produce multiple specs, first name the child spec paths
   and whether each child spec should remain Draft or be marked Accepted after
   grilling. Milestone acceptance does not automatically accept child specs.
6. Use `spec-griller` before marking a spec Accepted. Independent read-only
   passes may run in parallel.
7. Use `$grill-with-docs` when the spec changes terminology, workflow
   boundaries, milestone direction, or other repo context.
8. Keep specs implementation-ready but not implementation-heavy.
9. If code reveals the milestone is wrong or incomplete, stop spec work and
   hand the issue back to `$hermes-requirements`.
10. If the spec settles a context change, hand off to `$hermes-context`.
11. When the spec is ready for implementation, leave an explicit
   handoff artifact for `$hermes-dev-loop`.


## Required Agent Gates

  For every `$hermes-spec` run that creates or materially revises a spec:

  1. `spec-planner` must be used to draft or revise the spec from the Accepted
     milestone contract.
  2. `spec-griller` must be used before any spec is marked Accepted.
  3. If either agent cannot be invoked, stop and report the blocker or explicitly
     continue only if the user approves a manual fallback.

  The main agent may reconcile and edit the final spec, but must not silently skip
  these gates.

## Output

Use the spec status contract in `docs/WORKFLOWS.md` as the canonical source for
status language.

Return a handoff artifact using the shared interface in `docs/WORKFLOWS.md`.

Include these spec-specific fields:

- source milestone path
- created or revised spec path
- key contracts and acceptance criteria
- settled decisions carried forward from the Accepted milestone
- remaining open questions
- verification expectations

Do not hide new scope inside implementation notes.
This skill writes or updates formal contracts under `docs/specs/` only. It does
not create, accept, revise, or status-update milestone contracts under
`docs/milestones/`.

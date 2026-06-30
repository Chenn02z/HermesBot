---
name: hermes-spec
description: Converts Accepted milestone contracts into implementation specs under docs/specs. Reject Draft or non-Accepted milestones; do not update milestone contracts.
---

# Spec Workflow

Use when an Accepted milestone needs one or more executable implementation specs
under `docs/specs/`. Consumes Accepted milestone contracts from
`$hermes-requirements`. Reject Draft, blocked, or non-Accepted milestones.

## Prerequisites

1. `AGENTS.md` (one-time orientation)
2. `docs/WORKFLOWS.md` (handoff interface and spec status contract)
3. The Accepted milestone under `docs/milestones/`

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

1. Start `$codex-agent-tracer` to create a `.agent-trace/<workflow-id>/`
   trace folder immediately, before any reads.
2. Use `explorer` if repo state is unclear. Confirm milestone is `Accepted`.
3. Use `spec-planner` to draft/revise specs from the Accepted milestone.
4. For multi-spec milestones: name child spec paths and Draft/Accepted targets.
5. Use `spec-griller` before marking any spec Accepted.
6. Use `$grill-with-docs` when spec changes terminology, boundaries, or milestone direction.
7. If code reveals milestone is wrong, hand back to `$hermes-requirements`.
8. If spec settles context changes, hand off to `$hermes-context`.
9. Leave explicit handoff artifact for `$hermes-dev-loop` when ready.

## Required Agent Gates

1. `spec-planner` must draft/revise the spec.
2. `spec-griller` must review before Accepted.

## Output

Return handoff artifact. Include: source milestone path, created/revised spec
path, key contracts and acceptance criteria, settled decisions, open questions,
trace path, verification expectations.

---
name: hermes-spec
description: Converts settled Hermes Agent requirements packets into formal specs or milestone contracts. Use when writing docs/specs files, milestone specs, workflow contracts, acceptance criteria, or moving a spec through Draft, Accepted, Implemented, and Verified states.
---

# Hermes Spec

Use this skill when the work needs an executable spec or milestone contract. It
consumes output from `$hermes-requirements` when the request began ambiguous:
resolved workflow, proposed spec name/path, scope boundary, scenarios,
acceptance criteria candidates, and blocking questions.

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
4. Use `spec-griller` before marking a spec Accepted.
5. Use `$grill-with-docs` when the spec changes terminology, workflow
   boundaries, milestone direction, or other repo context.
6. Keep specs implementation-ready but not implementation-heavy.
7. If code reveals the spec is wrong, update the spec before continuing.
8. If the spec settles a context change, hand off to `$hermes-context`.

## Status Rules

- `Draft`: requirements are still being shaped.
- `Accepted`: implementation can start.
- `Implemented`: code/docs have been changed but final verification may remain.
- `Verified`: acceptance criteria have passed or documented exceptions exist.

## Output

Return the spec path, status, key acceptance criteria, and remaining open
questions. Do not hide new scope inside implementation notes.

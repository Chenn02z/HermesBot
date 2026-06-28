# Hermes Workflows

This document holds the detailed workflow rules that do not need to live in the
root `AGENTS.md` orientation file.

## Core Model

Specs define truth. Skills define process. Agents execute roles. Model choices
are capacity decisions.

Workflow skills should leave explicit handoff artifacts for the next skill
instead of relying on conversational memory. A handoff should name:

- producer skill
- intended consumer skill
- artifact path or packet contents
- settled decisions
- unresolved blockers
- docs, specs, or milestones the next skill must read

Use skill names literally in status and handoff language. If spec-like drafting
was done manually while `$hermes-requirements` was active, describe it as manual
spec-like work, not as a literal invocation of `$hermes-spec`.

## Non-Trivial Work

Use the full workflow for non-trivial product, code, workflow, or context
changes:

1. Gather requirements.
2. Draft or update a spec.
3. Grill the spec for ambiguity and missing failure modes.
4. Mark the spec Accepted before implementation.
5. Implement only what the spec requires.
6. Verify and review against the spec.
7. Update docs/spec status when decisions settle, using `$hermes-context` for
   any settled context change.

Small documentation or cleanup tasks may skip a formal spec when the user makes
that explicit or when the change is obviously local and reversible.

## `$hermes-requirements`

Use `$hermes-requirements` for requirement gathering, product shaping,
milestone direction, and deciding whether a spec is needed.

It produces a pre-spec requirements packet containing:

- resolved workflow
- proposed spec name/path
- proposed milestone name/path, when relevant
- scope boundary
- scenarios
- acceptance criteria candidates
- settled decisions
- blocking questions

It should not write full specs or milestone contracts. It should hand formal
spec or milestone work to `$hermes-spec`.

## `$hermes-spec`

Use `$hermes-spec` to turn a requirements packet into formal specs, milestone
contracts, acceptance criteria, and spec status.

It consumes `$hermes-requirements` handoffs and writes or updates contracts
under `docs/specs/` and `docs/milestones/`.

Spec status values:

- `Draft`: requirements are still being shaped.
- `Accepted`: implementation can start.
- `Implemented`: code/docs have been changed but final verification may remain.
- `Verified`: acceptance criteria have passed or documented exceptions exist.

When a spec or milestone is ready for implementation, `$hermes-spec` should
leave an explicit handoff for `$hermes-dev-loop`.

## `$hermes-dev-loop`

Use `$hermes-dev-loop` for implementation from an Accepted spec through
verification and review.

The dev loop should:

- read the accepted spec and canonical docs
- inspect current repo patterns before editing
- confirm spec gaps before implementation
- use targeted verification
- compare the diff against the spec
- leave follow-up handoffs for `$hermes-context` or `$hermes-spec` when the work
  settles terminology, changes scope, or exposes a spec gap

Do not expand scope without updating the spec first.

## `$hermes-context`

Use `$hermes-context` whenever settled work changes terminology, workflow
boundaries, product direction, role definitions, agent/skill usage, or
cross-document meaning.

It keeps `AGENTS.md`, product docs, context docs, specs, skills, and agent rules
aligned. Keep implementation details out of `docs/CONTEXT.md`.

## `$grill-with-docs`

Use `$grill-with-docs` as a focused adversarial pass inside requirements, spec,
milestone, or context workflows.

It checks proposed changes against `README.md`, `AGENTS.md`,
`docs/PRODUCT.md`, `docs/CONTEXT.md`, relevant specs, relevant milestones, and
current repo state.

Lead with contradictions, missing decisions, and scope risks. Recommend the
smallest doc/spec update that removes ambiguity. Create an ADR only when the
decision is hard to reverse, surprising, and a real trade-off.

## Agent Routing Log

Any non-trivial workflow using a Hermes skill must include an agent routing log
in its final handoff.

A required subagent named by the selected skill is a gate, not a suggestion. If
the agent is skipped, the final handoff must say whether the workflow remains
Draft, blocked, or approved for manual fallback.
# Hermes Workflows

This document holds the detailed workflow rules that do not need to live in the
root `AGENTS.md` orientation file.

## Core Model

Specs define truth. Skills define process. Agents execute roles. Model choices
are capacity decisions.

Workflow skills should leave explicit handoff artifacts for the next skill
instead of relying on conversational memory.

## Handoff Artifact Interface

Every non-trivial Hermes workflow handoff must include these shared fields:

- producer skill
- intended consumer skill
- artifact path or packet contents
- status
- settled decisions
- unresolved blockers
- docs, specs, or milestones the next skill must read
- agent routing log

The agent routing log should record the subagents or equivalent manual fallback
used by the workflow. For each required agent gate, say one of:

- used
- unavailable; manual fallback approved
- not applicable for this scoped pass

For workflows that use `$codex-agent-tracer`, the `.agent-trace` file is the
detailed evidence log. The handoff artifact remains the canonical summary and
must include the trace path plus any missing-event risks.

Use skill names literally in status and handoff language. If spec-like drafting
was done manually while `$hermes-requirements` was active, describe it as manual
spec-like work, not as a literal invocation of `$hermes-spec`.

## Non-Trivial Work

Use the full workflow for non-trivial product, code, workflow, or context
changes:

1. Gather requirements.
2. Draft or update an Accepted milestone when the work is milestone-sized.
3. Create or update specs from Accepted milestones.
4. Grill the spec for ambiguity and missing failure modes.
5. Mark the spec Accepted before implementation.
6. Implement only what the spec requires.
7. Verify and review against the spec.
8. Update docs/spec status when decisions settle, using `$hermes-context` for
   any settled context change.

Small documentation or cleanup tasks may skip a formal spec when the user makes
that explicit or when the change is obviously local and reversible.

## `$hermes-requirements`

Use `$hermes-requirements` for requirement gathering, product shaping,
milestone direction, accepting milestone contracts, and deciding whether a spec
is needed.

It produces requirements packets and Accepted milestone contracts containing:

- resolved workflow
- proposed spec name/path
- milestone path, when relevant
- milestone status, when relevant
- scope boundary
- scenarios
- acceptance criteria candidates
- settled decisions
- blocking questions

It should not write full specs under `docs/specs/`. For milestone work, it owns
writing or updating `docs/milestones/` contracts through `doc-curator` and may
mark them `Accepted` only after acceptance-blocking questions have been answered
by repo context or by the user.

It must not close a milestone acceptance run with unresolved blocking questions.
If blockers remain unanswered, the output status is Draft or blocked, not
Accepted.

Blocking questions are questions whose answer is required before milestone
acceptance. Deferred questions may remain only when they are explicitly listed
as non-blocking and assigned to child specs or later milestones.

## `$hermes-spec`

Use `$hermes-spec` to turn Accepted milestones into formal implementation specs
under `docs/specs/`.

It consumes `$hermes-requirements` handoffs only when the artifact is an
Accepted milestone contract with no unresolved blocking questions. It rejects
Draft, blocked, missing, or non-Accepted milestones and sends milestone
drafting, acceptance, or blocker resolution back to `$hermes-requirements`.

It writes or updates contracts under `docs/specs/` only. It does not create,
accept, revise, or status-update `docs/milestones/` contracts.

Existing Draft milestones under `docs/milestones/` must be reopened through
`$hermes-requirements` for blocker resolution and promotion to Accepted before
`$hermes-spec` consumes them. `$hermes-spec` must not promote Draft milestones.

When an Accepted milestone can produce multiple specs, `$hermes-spec` must first
name the child spec paths and whether each child spec is expected to remain
Draft or become Accepted after grilling. Milestone acceptance does not
automatically accept child specs.

## Spec Status Contract

`docs/WORKFLOWS.md` is the canonical source for spec and milestone status
language.

Status values:

- `Draft`: requirements are still being shaped.
- `Accepted`: for specs, implementation can start; for milestones, spec
  authoring can start but implementation is not authorized.
- `Implemented`: code/docs have been changed but final verification may remain.
- `Verified`: acceptance criteria have passed or documented exceptions exist.

Header status, downstream handoff status, and skill output status must agree.
Do not leave a spec header at `Implemented` while a handoff still says
`Accepted`, or vice versa.

When a spec is ready for implementation, `$hermes-spec` should leave an
explicit handoff for `$hermes-dev-loop` using the shared handoff artifact
interface.

## `$hermes-dev-loop`

Use `$hermes-dev-loop` for implementation from an Accepted spec through
verification and review.

The dev loop should:

- read the accepted spec and canonical docs
- use `$codex-agent-tracer` to maintain a `.agent-trace` log for delegation,
  edits, commands, verification, review, handoff, and duplicated-work findings
- inspect current repo patterns before editing
- confirm spec gaps before implementation
- use targeted verification
- compare the diff against the spec
- update the spec status so it matches the current implementation state
- leave follow-up handoffs for `$hermes-context` or `$hermes-spec` when the work
  settles terminology, changes scope, or exposes a spec gap
- leave follow-up handoffs for `$hermes-requirements` when milestone roll-up
  status needs to change after child specs are verified

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

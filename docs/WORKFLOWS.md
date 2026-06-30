# Project Workflows

Shared contracts and status language. Per-skill workflow details live in the
individual SKILL.md files under `.agents/skills/`.

## Core Model

Specs define truth. Skills define process. Agents execute roles. Model choices
are capacity decisions.

Workflow skills leave explicit handoff artifacts for the next skill.

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
8. Update docs/spec status when decisions settle.

Small documentation or cleanup tasks may skip a formal spec when the user
makes that explicit or when the change is obviously local and reversible.

## Handoff Artifact Interface

Every non-trivial project workflow handoff must include these shared fields:

- producer skill
- intended consumer skill
- artifact path or packet contents
- status
- settled decisions
- unresolved blockers
- docs, specs, or milestones the next skill must read
- agent routing log

For each required agent gate, the routing log says one of:

- used
- unavailable; manual fallback approved
- not applicable for this scoped pass

For workflows that use `$codex-agent-tracer`, the `.agent-trace` file is the
detailed evidence log. The handoff artifact is the canonical summary and must
include the trace path plus any missing-event risks.

## Agent Routing Log

Any non-trivial workflow using a project workflow skill must include an agent
routing log in its final handoff.

A required subagent named by the selected skill is a gate, not a suggestion.
If the agent is skipped, the final handoff must say whether the workflow remains
Draft, blocked, or approved for manual fallback.

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

---
name: hermes-dev-loop
description: Runs the specs-driven implementation loop for product work. Use when an accepted spec should be implemented, verified, reviewed, and summarized with model-routed subagents.
---

# Dev Loop

Use this skill after a spec is Accepted, or when the user explicitly marks a
small task as a spec exception.

## Prerequisites

Read these before delegating any work:

1. The accepted spec under `docs/specs/`.
2. `docs/WORKFLOWS.md` (handoff interface and spec status contract only).

Do not pre-read `AGENTS.md`, `docs/PRODUCT.md`, or `docs/CONTEXT.md` — those
are one-time orientation, not per-invocation reads.

## Workflow

1. Start `$codex-agent-tracer` to create a `.agent-trace/<workflow-id>/`
   trace folder immediately, before any reads.
2. Read only the accepted spec and the Prerequisites above.
3. Delegate exploration to `explorer`. Do not read source files yourself.
4. Confirm any spec gap with the user before implementation.
5. Delegate implementation to `implementer`. Do not edit files yourself.
   Batch all reviewer findings into a single implementer pass — do not
   fix-verify-fix-verify ping-pong.
6. Delegate verification to `test-runner`. Do not run commands yourself.
   Submit once per implementer pass. If failures, send back to implementer
   as one batch.
7. Delegate review to `reviewer`. Collect findings, deduplicate, then send
   as one batch to implementer.
8. If reviewer findings trigger an implementer pass, re-verify with
   `test-runner` before marking the spec Verified. Do not skip this gate.
9. Update the spec status after the final review and verification pass.
10. Leave a follow-up handoff for `$hermes-context` or `$hermes-spec` when the
    implementation settles terminology, changes scope, or exposes a spec gap.

## Guardrails

- Do not let parallel agents edit the same files.
- Write-capable agents must have disjoint file ownership.
- Do not expand scope without updating the spec first.
- Prefer targeted tests and checks over broad commands early.
- Delegate, don't DIY: explorer reads, implementer edits, test-runner verifies,
  reviewer reviews. Main agent only reconciles and reports.

## Output

Return a handoff artifact using the shared interface in `docs/WORKFLOWS.md`.

Include:

- spec path
- files changed
- verification commands and results
- reviewer findings
- trace path and duplicated-work findings
- remaining risks or follow-up specs

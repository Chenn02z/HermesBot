---
name: hermes-dev-loop
description: Runs the specs-driven implementation loop for product work. Use when an accepted spec should be implemented, verified, reviewed, and summarized with model-routed subagents.
---

# Dev Loop

Use this skill after a spec is Accepted, or when the user explicitly marks a
small task as a spec exception. It consumes the handoff artifact from
`$hermes-spec`, especially the accepted spec path, key contracts, acceptance
criteria, verification expectations, and remaining blockers.

The named project agents in this workflow are authorized subagents for this
skill's scoped task. The main agent still owns judgment, user interaction,
reconciliation, and final reporting.

## Workflow

1. Read the accepted spec, `AGENTS.md`, `docs/PRODUCT.md`, and
   `docs/CONTEXT.md`.
2. Use `$codex-agent-tracer` to start a `.agent-trace/<workflow-id>/`
   trace folder before exploration. Keep it current through delegation, edits,
   commands, verification, review, duplicated-work findings, and handoff.
3. Use `explorer` to inspect relevant files and current patterns.
4. Ask the main agent to confirm any spec gap before implementation.
5. Use one `implementer` at a time for write-heavy work unless the Accepted
   spec explicitly decomposes disjoint write scopes.
6. Use `test-runner` for targeted verification.
7. Use `reviewer` to compare the diff against the spec. Independent read-only
   passes may run in parallel.
8. Have the main agent apply any final doc/spec status updates.
9. Leave a follow-up handoff for `$hermes-context` or `$hermes-spec` when the
   implementation settles terminology, changes scope, or exposes a spec gap.

## Guardrails

- Do not let parallel agents edit the same files.
- Write-capable agents must have disjoint file ownership.
- Do not expand scope without updating the spec first.
- Prefer targeted tests and checks over broad commands early in the repo.
- Report missing tooling as a repo maturity gap, not a silent success.

## Output

Return a handoff artifact using the shared interface in `docs/WORKFLOWS.md`.

Include these dev-loop-specific fields:

- spec path
- files changed
- verification commands and results
- reviewer findings
- trace path and duplicated-work findings
- remaining risks or follow-up specs

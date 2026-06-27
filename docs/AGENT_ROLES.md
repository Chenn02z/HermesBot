# Project Agent Roles

Project-scoped Codex agents live under `.codex/agents/`.

The main agent owns judgment, reconciliation across subagent outputs, user
interaction, and final reporting. Skills are the workflow layer;
`.codex/agents/*.toml` are the concrete subagent presets those workflows invoke.

If a selected skill instructs the main agent to use a named project agent role,
that skill instruction authorizes using that role as a scoped subagent for the
task, subject to system/tool constraints, sandbox limits, and file ownership
rules.

## Read-Only Agents

- `spec-planner`: strong planner for requirements, milestones, specs, and
  acceptance criteria.
- `spec-griller`: strong reviewer for ambiguity, failure modes, scope creep,
  and weak contracts.
- `explorer`: cheap read-only repo explorer for current state and patterns.
- `reviewer`: strong read-only diff/spec reviewer.

Read-only subagents may run in parallel when their questions are independent.

## Write-Capable Agents

- `implementer`: write-capable worker for accepted specs.
- `test-runner`: targeted verification worker.
- `doc-curator`: write-capable documentation maintainer.

Only `implementer`, `test-runner`, and `doc-curator` should edit files, and
only when the main workflow calls for it.

Write-capable subagents must have disjoint file ownership. Use one
`implementer` at a time unless an Accepted spec explicitly decomposes disjoint
write scopes. `doc-curator` may edit docs and skill or agent rules when
`$hermes-context` calls for surgical updates.

## Routing Principles

- Use stronger planning and review agents for ambiguity, scope, and failure
  modes.
- Use cheaper read-only exploration for narrow repo-state questions.
- Keep model/provider choices in agent config or explicit specs, not scattered
  across scripts.
- Do not use shell scripts as the orchestration brain.
- Preserve user-owned worktree changes. Do not revert unrelated edits.

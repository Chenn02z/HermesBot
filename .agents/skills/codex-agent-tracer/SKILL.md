---
name: codex-agent-tracer
description: Records and audits structured execution traces for Codex agent workflows. Use when evaluating multi-agent efficiency, tracing hermes-dev-loop runs, or producing .agent-trace logs, Mermaid graphs, and audit reports.
---

# Codex Agent Tracer

Use this skill when a workflow needs durable traceability across delegation,
skill usage, reads, edits, commands, review, and handoff.

All project workflow skills (`$hermes-requirements`, `$hermes-spec`,
`$hermes-dev-loop`, `$hermes-context`, `$hermes-with-docs`) must
produce a trace under `.agent-trace/<workflow-id>/`. The trace is the
canonical evidence log for the handoff artifact's agent routing log.

## Trace Scope

Start a run-specific folder under `.agent-trace/`. Minimum artifacts:
`trace.jsonl`, `graph.mmd`, `audit.md`. The main agent owns trace writes.

## Required Event Kinds

- `agent_delegation` / `delegate_result`: subagent delegation and return
- `skill_usage`, `context_read`, `file_edit`
- `verification` / `command`: checks run with outcome
- `handoff`: artifact left for another workflow
- `duplicated_work`, `missing_event`

Per-skill events:

- `\-dev-loop`: `trace_start`, `accepted_spec_read`, delegation
  events per required agent gate, `file_edit` per changed path,
  `verification` per check, `review_result`, `handoff`, `trace_end`.
- `\-requirements`: `trace_start`, `milestone_read` (if applicable),
  `grill_pass`, `spec_planner_delegation`, `spec_griller_delegation`,
  `doc_curator_delegation`, `user_settlement`, `handoff`, `trace_end`.
- `\-spec`: `trace_start`, `milestone_read`, `spec_planner_delegation`,
  `spec_griller_delegation`, `grill_with_docs_pass`, `handoff`, `trace_end`.
- `\-context`: `trace_start`, `explorer_delegation`,
  `doc_curator_delegation`, `pruning_audit` (with before/after sizes),
  `spec_griller_delegation`, `grill_with_docs_pass`, `handoff`, `trace_end`.
- `\-with-docs`: `trace_start`, `context_read` per doc,
  `contradiction_found`, `recommendation`, `handoff`, `trace_end`.

## Audit Pass

Audit for: missing event kinds, unexplained jumps, repeated scope work,
avoidable coordination overhead. Do not flag intentional independent review as
duplicated work. Summarize in `audit.md`.

## Output

Report: trace path, completeness, duplicated-work findings, audit recommendations.

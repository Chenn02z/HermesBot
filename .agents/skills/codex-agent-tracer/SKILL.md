---
name: codex-agent-tracer
description: Records and audits structured execution traces for Codex agent workflows. Use when evaluating multi-agent efficiency, tracing future `$hermes-dev-loop` runs, or producing `.agent-trace` logs, Mermaid graphs, and audit reports.
---

# Codex Agent Tracer

Use this skill when a workflow needs durable traceability across delegation,
skill usage, reads, edits, commands, review, and handoff.

## Trace Scope

Start a run-specific folder under `.agent-trace/`. Minimum artifacts:
`trace.jsonl`, `graph.mmd`, `audit.md`. The main agent owns trace writes.

## Required Event Kinds

- `agent_delegation` / `delegate_result`: subagent delegation and return
- `skill_usage`, `context_read`, `file_edit`
- `verification` / `command`: checks run with outcome
- `handoff`: artifact left for another workflow
- `duplicated_work`, `missing_event`

For `$hermes-dev-loop`, include: `trace_start`, `accepted_spec_read`,
delegation events per required agent gate, `file_edit` per changed path,
`verification` per check, `review_result`, `handoff`, `trace_end`.

## Audit Pass

Audit for: missing event kinds, unexplained jumps, repeated scope work,
avoidable coordination overhead. Do not flag intentional independent review as
duplicated work. Summarize in `audit.md`.

## Output

Report: trace path, completeness, duplicated-work findings, audit recommendations.

---
name: codex-agent-tracer
description: Records and audits structured execution traces for Codex agent workflows. Use when evaluating multi-agent efficiency, tracing future `$hermes-dev-loop` runs, or producing `.agent-trace` logs, Mermaid graphs, and audit reports.
---

# Codex Agent Tracer

Use this skill when a workflow needs durable traceability across delegation,
skill usage, reads, edits, commands, review, and handoff. Future
`$hermes-dev-loop` runs should treat this skill as the trace layer for the
implementation pass.

## Trace Scope

Start a run-specific folder under `.agent-trace/` and keep all tracer outputs
for that workflow there.

Minimum artifacts:

- `trace.jsonl`: append-only structured event log
- `graph.mmd`: Mermaid graph of agent and skill flow
- `audit.md`: concise audit of efficiency, duplicated work, and trace gaps

The main agent owns trace writes. Subagents return trace-relevant summaries;
they do not write trace logs unless their sandbox and workflow explicitly allow
it. The trace is detailed evidence, while the workflow handoff remains the
canonical summary.

## Event Contract

Record one JSON event per line. Each event should include:

- `ts`: ISO 8601 timestamp
- `run_id`: stable workflow identifier
- `event_id`: unique event identifier
- `kind`: event type
- `actor`: main agent, subagent, or skill producing the event
- `summary`: short human-readable description
- `inputs`: key files, prompts, commands, or artifacts consumed
- `outputs`: key files, artifacts, findings, or status produced
- `related_event_ids`: dependencies, follow-ups, or suspected duplication

## Required Event Types

Capture these kinds whenever they occur:

- `agent_delegation`: main-agent delegation decision
- `subagent_call`: subagent invocation and return
- `skill_usage`: skill selection or handoff consumption
- `context_read`: canonical docs, specs, or repo files read for context
- `file_edit`: created, modified, or reviewed file targets
- `command`: verification or repo commands with outcome
- `handoff`: artifact left for another workflow
- `duplicated_work`: repeated reads, edits, or agent effort that should be
  reduced
- `missing_event`: known trace gap, interruption, malformed event, or redaction

For `$hermes-dev-loop`, include at least `trace_start`,
`accepted_spec_read`, `canonical_docs_read`, `delegate_start` and
`delegate_result` for each required agent gate or fallback, `file_edit` for
each changed path, `command` or `verification` for each check run or skipped,
`review_result`, `handoff`, and `trace_end`.

## Audit Pass

At the end of the run, audit the trace for:

- missing required event kinds
- unexplained handoffs or delegation jumps
- repeated exploration or implementation on the same scope
- parallel work that created avoidable coordination overhead
- commands or edits that were not reflected in the final handoff

Do not flag intentional independent review as duplicated work. Flag duplication
only when repeated reads, edits, or commands caused avoidable delay, conflicting
ownership, or inconsistent outputs without adding review value.

Summarize the findings in `audit.md` with concrete recommendations for the next
run.

## Mermaid Graph

Generate `graph.mmd` from the trace. Show:

- main agent
- each subagent used
- each skill used
- major reads, edits, commands, and handoffs
- duplicated-work edges or notes when present

Prefer a simple `flowchart` over decorative styling.

## Output

When this skill is part of another workflow, report:

- trace path
- whether the trace is complete enough to audit
- duplicated-work findings
- audit recommendations for the next run

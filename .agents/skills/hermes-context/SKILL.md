---
name: hermes-context
description: Keeps repo context aligned across AGENTS.md, README, durable docs, specs, skills, and agents. Use whenever terminology, workflow boundaries, project direction, or agent/skill setup changes.
---

# Context Workflow

Use when settled work changes terminology, workflow boundaries, product
direction, role definitions, or agent/skill usage.

## Prerequisites

1. `AGENTS.md` (one-time orientation)
2. The handoff artifact that triggered the context update

## Canonical Files

- `README.md`, `AGENTS.md`: overview and operating contract
- `docs/PRODUCT.md`, `docs/CONTEXT.md`: product and terminology
- `docs/WORKFLOWS.md`: handoff interface, spec status
- `docs/AGENT_ROLES.md`, `docs/DOCS_POLICY.md`: roles and doc rules
- `docs/specs/`, `docs/milestones/`: contracts and deliverables
- `.agents/skills/`, `.codex/agents/`: workflows and presets

## Workflow

1. Start `$codex-agent-tracer` to create a `.agent-trace/<workflow-id>/`
   trace folder immediately, before any reads.
2. Use `explorer` to inspect current docs and skills.
3. Use `doc-curator` for surgical updates to context docs and skill/agent rules.
4. **Pruning audit** — apply token-efficiency pruning across skills and agents:
   - **Skills**: check each SKILL.md for duplicated terminology (should reference
     `docs/CONTEXT.md` not restate it), prose that restates companion files
     (move to reference, reference by path), and overall size (>4KB is suspect).
   - **Agents**: check each `.codex/agents/*.toml` developer_instructions for
     full-doc-stack pre-reads (subagents should read only what their task needs).
   - **Traces**: check `.agent-trace/` for stale folders; clean past traces
     unless explicitly kept.
   - **Cross-references**: verify handoff references, vocab pointers, and file
     paths are live and not stale.
   - **Output**: report before/after sizes for every file changed by the pruning.
5. Use `spec-griller` when changes affect scope, terminology, or workflow.
6. Use `$grill-with-docs` as adversarial pass.
7. Keep implementation details out of `docs/CONTEXT.md`.

## Output

Return a handoff artifact using the shared interface in `docs/WORKFLOWS.md`.
Include: changed docs, settled terms/decisions, removed contradictions,
trace path, before/after size summary, follow-up updates needed.

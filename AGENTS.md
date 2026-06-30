# AGENTS.md

Operating instructions for Codex in this repo.

Read first:

1. `README.md`
2. `docs/PRODUCT.md`
3. `docs/CONTEXT.md`
4. Relevant files under `docs/specs/` or `docs/milestones/`

Use detailed reference docs when needed:

- `docs/WORKFLOWS.md` for skill workflows and handoffs.
- `docs/AGENT_ROLES.md` for project subagent roles and ownership rules.
- `docs/DOCS_POLICY.md` for documentation destinations and status rules.

## Project

This is a specs-driven finance research agent workspace for building a durable
developer workflow around:

- requirements gathering
- specs and milestone planning
- model-routed subagents
- domain-specific skills
- implementation loops that trace back to accepted specs

Future domains such as finance, Telegram, market research, or personal-ops
agents must be introduced through specs, not assumed globally.

## Core Rule

Specs define truth. Skills define process. Agents execute roles. Model choices
are capacity decisions.

Any non-trivial work must have a routing trace. This includes:

1. Gather requirements.
2. Draft or update an Accepted milestone when the work is milestone-sized.
3. Create or update a spec from an Accepted milestone.
4. Review the spec for ambiguity and failure modes.
5. Mark the spec Accepted before implementation.
6. Implement only what the spec requires.
7. Verify against the spec.
8. Update docs/context when decisions settle.

Small local documentation or cleanup tasks may skip a formal spec only when the
user explicitly allows it or the change is obviously reversible.

## Main Skills

 When the user invokes a project workflow skill, that invocation explicitly authorizes the
 main agent to use the project subagents named by that skill's workflow.
 
 If a selected skill says to use a subagent, the main agent must either:

  1. invoke that subagent,
  2. report that the subagent tool is unavailable, or
  3. explicitly explain why the subagent is not applicable before proceeding.
  
 Silent manual substitution for a required subagent is a workflow violation.

- `$hermes-requirements`: gather requirements and produce Accepted milestones.
- `$hermes-spec`: turn Accepted milestones into formal specs.
- `$hermes-dev-loop`: implement from an Accepted spec through verification.
- `$hermes-context`: keep AGENTS, docs, specs, skills, and agents aligned.
- `$grill-with-docs`: adversarial review for ambiguity, scope creep, and weak
  contracts.

If a skill emits a handoff, preserve it for the next workflow. Do not rely on
conversational memory.

## Project Agents

Project agents live in `.codex/agents/`.

Read-only agents:

- `spec-planner`
- `spec-griller`
- `explorer`
- `reviewer`

Write-capable agents:

- `implementer`
- `test-runner`
- `doc-curator`

Only `implementer`, `test-runner`, and `doc-curator` should edit files, and
only when the active workflow calls for it.

The main agent owns judgment, reconciliation, user interaction, and final
reporting.

## Repository Rules

- Keep changes surgical and tied to the current spec or explicit task.
- Prefer repo docs over general assumptions.
- Do not expand scope during implementation without updating the spec first.
- Keep model/provider choices in agent config or explicit specs.
- Do not make bash the orchestration brain.
- Never hardcode secrets, tokens, or keys.
- Preserve user-owned worktree changes.
- Do not revert unrelated edits.

## Commands

Use these once the relevant files exist:

```bash
uv sync
cp .env.example .env
uv run pytest
uv run ruff check .
uv run ruff format .
```

If a command does not exist yet, report it as a repo maturity gap. Do not invent
a parallel toolchain without a spec.

## Definition Of Done

A task is done when:

1. The change satisfies the relevant spec or explicit task.
2. The diff is scoped to the requested behavior.
3. Verification was run, or the missing command/reason is reported.
4. Docs/spec status are updated when a decision settles.
5. Remaining risks or follow-up specs are named plainly.

# AGENTS.md

Operating instructions for Codex working in this repo. Read this first, then
read `README.md`, `docs/PRODUCT.md`, and `docs/CONTEXT.md`. If a relevant spec
exists under `docs/specs/` or `docs/milestones/`, read it before changing files.

## Project: Hermes Agent Workspace

Hermes refers to Nous Research's Hermes Agent project:
`https://hermes-agent.nousresearch.com/`.

This repo is a specs-driven Hermes Agent workspace for orchestrated development.
The immediate goal is to build a durable developer workflow around:

- requirements gathering
- specs and milestone planning
- model-routed subagents
- domain-specific skills
- implementation loops that trace back to accepted specs

Future domain work may include finance workflows, Telegram interfaces, market
research agents, or other personal-ops agents, but those domains should be
introduced through specs rather than assumed globally.

## Development Model

Specs define truth. Skills define process. Agents execute roles. Model choices
are capacity decisions.

For non-trivial work:

1. Gather requirements.
2. Draft or update a spec.
3. Grill the spec for ambiguity and missing failure modes.
4. Mark the spec Accepted before implementation.
5. Implement only what the spec requires.
6. Verify and review against the spec.
7. Update docs/spec status when decisions settle, using `$hermes-context` for
   any settled context change.

Small documentation or cleanup tasks may skip a formal spec when the user makes
that explicit or when the change is obviously local and reversible.

## Project Structure

- `README.md`: public overview.
- `docs/PRODUCT.md`: product intent and roadmap.
- `docs/CONTEXT.md`: canonical terminology and boundaries.
- `docs/specs/`: executable component and workflow contracts.
- `docs/milestones/`: larger milestone plans.
- `.agents/skills/`: reusable Codex workflows.
- `.codex/agents/`: project-scoped role/model/permission presets.

## High-Level Skills

Use these repo skills as the main developer workflows:

- `$hermes-requirements` for requirement gathering, product shaping, milestone
  direction, and deciding whether a spec is needed. It produces a pre-spec
  requirements packet: resolved workflow, proposed spec name/path, scope
  boundary, scenarios, acceptance criteria candidates, and blocking questions.
  It should not write full specs.
- `$hermes-spec` for turning a requirements packet into formal specs,
  milestone contracts, acceptance criteria, and spec status.
- `$hermes-dev-loop` for implementation from an accepted spec through
  verification and review.
- `$hermes-context` for keeping `AGENTS.md`, product docs, context docs, specs,
  and skills aligned. Use it whenever terminology, workflow boundaries,
  project direction, or agent/skill usage changes.

Use `$grill-with-docs` as a focused adversarial pass inside those workflows
when requirements, specs, milestones, or context updates need to be checked
against README, product docs, context docs, specs, and current repo state.

Inherited or experimental skills may exist under `.agents/skills/`; prefer the
Hermes-specific skills above for this repo.

## Project Agents

Project-scoped Codex agents live under `.codex/agents/`.

- `spec-planner`: strong planner for requirements, milestones, specs, and
  acceptance criteria. Read-only.
- `spec-griller`: strong reviewer for ambiguity, failure modes, scope creep,
  and weak contracts. Read-only.
- `explorer`: cheap read-only repo explorer for current state and patterns.
- `implementer`: write-capable worker for accepted specs.
- `test-runner`: targeted verification worker.
- `reviewer`: strong read-only diff/spec reviewer.
- `doc-curator`: write-capable documentation maintainer.

Default rule: only `implementer`, `test-runner`, and `doc-curator` should edit
files, and only when the main workflow calls for it.

## Commands

This repo is still early. Use these commands once the corresponding project
files exist:

```bash
uv sync
cp .env.example .env
uv run pytest
uv run ruff check .
uv run ruff format .
```

If a command does not exist yet, report that as a repo maturity gap. Do not
invent a parallel toolchain without a spec.

## Repository Rules

- Keep changes surgical and tied to the current spec or explicit task.
- Prefer repo docs over general assumptions.
- Do not expand scope during implementation without updating the spec first.
- Keep model/provider choices in agent config or explicit specs, not scattered
  across scripts.
- Use shell scripts only as thin repeatable entrypoints for non-interactive
  checks; do not make bash the orchestration brain.
- Secrets come from environment/config only. Never hardcode tokens or keys.
- Tests should track acceptance criteria once code exists.
- Preserve user-owned worktree changes. Do not revert unrelated edits.

## Documentation Rules

- Use `docs/PRODUCT.md` for product intent, audience, scope, and roadmap.
- Use `docs/CONTEXT.md` for canonical terminology and boundaries.
- Use `docs/specs/` for implementation-ready contracts.
- Use `docs/milestones/` for larger deliverable slices.
- Use `docs/adr/NNNN-slug.md` only for durable, hard-to-reverse decisions with
  real trade-offs.
- Use `$hermes-context` to update docs when a term, boundary, workflow, product
  decision, or agent/skill usage becomes settled.

## Definition Of Done

1. The change satisfies the relevant spec or explicit small-task request.
2. The diff is scoped to the requested behavior.
3. Verification was run for the touched area, or the missing command/reason is
   reported.
4. Docs/spec status are updated when the work settles a decision.
5. Remaining risks or follow-up specs are named plainly.

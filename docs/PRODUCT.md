# Hermes Agent Workspace Product Backbone

## Product Intent

This repo is a specs-driven development workspace for Hermes Agent, referring to
Nous Research's Hermes Agent project at
`https://hermes-agent.nousresearch.com/`.

The purpose of this workspace is to make agentic development reliable by
combining:

- explicit requirements gathering
- executable specs and milestones
- role-specific subagents
- model routing by task risk and ambiguity
- reusable skills for repeatable developer workflows
- review and verification against specs

Hermes Agent is the substrate. This repo defines how the developer uses that
substrate for disciplined, domain-specific work.

## Primary User

The primary user is the developer operating this repository. The developer wants
to build with AI agents while preserving clarity, reviewability, and durable
project context.

The workspace should help the developer move from vague ideas to accepted specs,
then from accepted specs to verified implementation.

## Current Scope

The current scope is the development system plus the first finance-domain
specification slice:

- repo operating instructions
- specs and milestone structure
- Hermes-specific workflow skills
- Codex project agents for planning, grilling, exploration, implementation,
  verification, review, and documentation
- context docs that prevent terminology drift
- first finance milestone handoff for a fixture-backed market brief and
  follow-up entry-zone strategy layer

Application domains such as Telegram or broader personal operations remain
future domain specs, not global assumptions. Finance is the first domain
expansion, currently captured as a requirements handoff for later specs.

## Non-Goals For Now

- Deployment workflow.
- Evals infrastructure.
- Production application architecture.
- Full finance agent implementation outside accepted specs.
- Live brokerage, trade execution, or personalized financial advice.
- General-purpose agent marketplace.
- Complex bash-based orchestration.

## Product Principles

- Specs define truth: implementation must trace to accepted requirements.
- Skills define process: repeatable workflows live in `.agents/skills/`.
- Agents execute roles: model, reasoning, and permission defaults live in
  `.codex/agents/`.
- Main thread owns judgment: subagents gather, challenge, implement, or review;
  the main agent reconciles.
- Model routing follows risk: ambiguous or high-impact work gets stronger
  models; read-heavy exploration can use cheaper models.
- Keep orchestration visible: avoid hiding important decisions inside shell
  scripts.

## Success Criteria

This workspace is succeeding when:

- a vague request can be turned into a clear spec or milestone update
- specs are grilled before implementation starts
- development work follows a consistent explorer -> implementer -> verifier ->
  reviewer loop
- docs, specs, skills, and agent presets remain aligned
- future domain work can be added without rewriting the development workflow

## Roadmap Backbone

1. Context foundation: align `AGENTS.md`, `docs/PRODUCT.md`, and
   `docs/CONTEXT.md`.
2. Workflow foundation: add requirements, spec, dev-loop, and context skills.
3. Agent foundation: add role/model/permission presets under `.codex/agents/`.
4. Spec foundation: add spec template and first milestone specs.
5. Domain expansion: introduce finance first through
   `docs/milestones/0001-finance-agent-foundation.md`, which proposes
   `docs/specs/0001-finance-daily-market-brief.md` and
   `docs/specs/0002-finance-entry-zone-strategy.md` for `$hermes-spec`;
   introduce Telegram or other personal-ops domains through later accepted
   specs.
6. Later: add evals and deployment workflows when implementation maturity
   justifies them.

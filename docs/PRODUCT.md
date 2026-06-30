# Product Backbone

## Product Intent

This repo is a specs-driven workspace for building a personal finance research
agent product. The runtime is owned by this application rather than an external
agent framework.

The product direction is inspired by multi-agent trading research systems, but
tailored for a single operator and a research-only boundary. Runtime finance
agents should gather, compare, debate, and synthesize market evidence into
actionable research artifacts, including suggested research entry prices or
entry zones when supported by accepted specs.

The development workspace makes that product reliable by combining:

- explicit requirements gathering
- executable specs and milestones
- role-specific subagents
- model routing by task risk and ambiguity
- reusable skills for repeatable developer workflows
- review and verification against specs

Codex project agents and workflow skills are development machinery used to
build and verify the product; they are not the product's runtime analyst agents.

## Primary User

The primary user is the developer operating this repository. The developer wants
to build with AI agents while preserving clarity, reviewability, and durable
project context.

The workspace should help the developer move from vague ideas to accepted specs,
then from accepted specs to verified implementation.

The runtime product target is a single-operator personal finance research
system. Multi-user SaaS, public bot access, shared workspaces, team accounts,
billing, role administration, and general marketplace behavior are out of scope
unless a later accepted spec introduces them.

## Current Scope

The current scope is the development system plus the verified first
finance-domain specification slice:

- repo operating instructions
- specs and milestone structure
- project workflow skills
- Codex project agents for planning, grilling, exploration, implementation,
  verification, review, and documentation
- context docs that prevent terminology drift
- verified finance milestone for a fixture-backed market brief and follow-up
  entry-zone strategy layer

Runtime product agents such as news, price, technical, fundamentals, valuation,
risk, bull/bear researcher, chief analyst, or portfolio-manager-style roles
remain future runtime specs, not current implementation. Telegram and broader
personal operations also remain future domain specs, not global assumptions.
Finance is the first domain expansion, currently verified through
`docs/milestones/0001-finance-agent-foundation.md` and child specs `0001` and
`0002`.

When a later accepted spec introduces model-written runtime synthesis, model
calls should route through OpenRouter by default unless that spec explicitly
accepts another gateway. Verified fixture-backed finance specs perform no model
calls.

## Non-Goals For Now

- Deployment workflow.
- Evals infrastructure.
- Production application architecture.
- Full finance agent implementation outside accepted specs.
- Live brokerage, trade execution, position sizing, guarantees, or personalized
  financial advice.
- General-purpose agent marketplace.
- Complex bash-based orchestration.

## Product Principles

- Specs define truth: implementation must trace to accepted requirements.
- Skills define process: repeatable workflows live in `.agents/skills/`.
- Development agents execute workflow roles: model, reasoning, and permission
  defaults live in `.codex/agents/`.
- Main thread owns judgment: subagents gather, challenge, implement, or review;
  the main agent reconciles.
- Runtime product agents are separate from Codex development subagents. Product
  agent roles belong in accepted runtime specs before implementation.
- Model routing follows risk: ambiguous or high-impact work gets stronger
  models; read-heavy exploration can use cheaper models.
- Runtime model calls, when in scope, route through OpenRouter by configurable
  model identifiers and keep secrets outside git.
- OpenRouter/model output may synthesize or explain supplied evidence, but must
  not become the source of factual finance truth.
- Suggested research entry prices or zones must be evidence-grounded,
  auditable, and clearly labeled as research artifacts rather than trading
  instructions.
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
5. Domain expansion: finance is verified through
   `docs/milestones/0001-finance-agent-foundation.md`,
   `docs/specs/0001-finance-daily-market-brief.md`, and
   `docs/specs/0002-finance-entry-zone-strategy.md`.
6. Future runtime expansion: represent each later roadmap slice as an
   individual milestone file under `docs/milestones/`, starting with runtime
   boundary, provider contracts, live providers, OpenRouter model routing,
   Telegram delivery, persistence, containerization, AWS EC2 deployment, and
   operations hardening.
7. Later: add evals when implementation maturity justifies them.

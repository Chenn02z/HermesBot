# Product Backbone

## Product Intent

A personal finance research agent product built through specs-driven development.
The runtime is owned by this application, not an external agent framework.

Runtime finance agents gather, compare, debate, and synthesize market evidence
into actionable research artifacts, including suggested research entry prices
or entry zones when supported by accepted specs.

The development workspace (this repo) makes that product reliable through
explicit requirements, executable specs, role-specific subagents, model
routing by task risk, and reusable workflow skills.

## Current Scope

- Repo operating instructions and workflow skills
- Specs/milestone structure
- Codex project agents for planning, grilling, exploration, implementation,
  verification, review, and documentation
- Context docs that prevent terminology drift
- Verified finance milestone with fixture-backed market brief and entry-zone
  strategy layer (`docs/milestones/0001-finance-agent-foundation.md`,
  child specs `0001`, `0002`)

## Non-Goals For Now

- Deployment workflow, evals infrastructure, production app architecture
- Full finance agent implementation outside accepted specs
- Live brokerage, trade execution, position sizing, guarantees, or
  personalized financial advice
- General-purpose agent marketplace
- Multi-user SaaS, public bot access, shared workspaces, team accounts

## Product Principles

- **Specs define truth**: implementation traces to accepted requirements.
- **Skills define process**: repeatable workflows in `.agents/skills/`.
- **Agents execute roles**: model/reasoning/permission presets in `.codex/agents/`.
- **Main agent owns judgment**: subagents gather, challenge, implement, review;
  the main agent reconciles and reports.
- **Runtime product agents are separate** from Codex development subagents.
- **Model routing follows risk**: ambiguous/high-impact work gets stronger
  models; exploration uses cheaper models.
- **Runtime model calls route through OpenRouter** by configurable identifiers
  and keep secrets outside git.
- **OpenRouter/model output may synthesize but not become factual truth**.
- **Suggested research prices/zones are evidence-grounded and labeled as
  research artifacts**, not trading instructions.
- **Bash is not the orchestration brain**.

## Success Criteria

- Vague requests become clear specs or milestone updates
- Specs are grilled before implementation
- Work follows a consistent explorer → implementer → verifier → reviewer loop
- Docs, specs, skills, and agent presets remain aligned
- Future domains can be added without rewriting the development workflow

## Roadmap Backbone

1. Context foundation: `AGENTS.md`, `docs/PRODUCT.md`, `docs/CONTEXT.md`.
2. Workflow foundation: requirements, spec, dev-loop, context skills.
3. Agent foundation: role/model/permission presets under `.codex/agents/`.
4. Spec foundation: spec template, first milestone specs.
5. Domain expansion: finance verified through milestone 0001 and child specs
   0001/0002.
6. Future: runtime boundary, provider contracts, live providers, OpenRouter
   model routing, Telegram delivery, persistence, containerization, AWS EC2,
   operations hardening — each as individual milestone files.

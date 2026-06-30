# Workspace Context

This document defines project terminology and boundaries. Keep it about meaning
and workflow context, not implementation details.

## Canonical Terms

- `HermesBot`: this repository's personal finance research agent product.
- `workspace`: this repository and its docs, skills, specs, and agent presets.
- `developer`: the human using this repo to drive specs-driven agentic work.
- `single-user product boundary`: the current runtime product assumption: one
  developer/operator and one authorized personal Telegram identity unless a
  later accepted spec explicitly introduces broader user scope.
- `runtime product agent`: a production/runtime finance research role such as
  news analyst, price analyst, technical analyst, fundamentals analyst,
  valuation analyst, risk analyst, bull/bear researcher, chief analyst, or
  portfolio-manager-style synthesizer. These are distinct from Codex development
  subagents and require accepted runtime specs before implementation.
- `OpenRouter gateway`: the planned model access boundary for varied model
  usage in later accepted runtime specs. This is a product-direction decision,
  not permission to add model calls outside accepted spec scope.
- `main agent`: the active Codex thread that owns judgment, user interaction,
  final decisions, and final reporting.
- `subagent`: a delegated Codex development agent with a narrow role, model,
  reasoning, and permission profile. In this repo, unqualified `subagent`
  means a development-time Codex worker, not a runtime product finance analyst.
- `skill`: a reusable workflow under `.agents/skills/` that tells the main agent
  how to do a class of work.
- `agent preset`: a concrete subagent role under `.codex/agents/` that defines
  model, reasoning, and permission defaults for a delegated task.
- `requirements packet`: the pre-spec output of `hermes-requirements`,
  containing the resolved workflow, proposed spec name/path, scope boundary,
  scenarios, acceptance criteria candidates, and blocking questions.
- `Accepted milestone`: a milestone contract under `docs/milestones/` that
  `hermes-requirements` has moved to `Accepted` after resolving all blocking
  questions. It is eligible input for `hermes-spec`; it does not authorize
  implementation without an Accepted child spec.
- `handoff artifact`: the explicit output one workflow skill leaves for the
  next skill to consume. It names the producer skill, intended consumer skill,
  artifact path or packet contents, status, settled decisions, unresolved
  blockers, docs or specs that must be read next, and the agent routing log
  defined in `docs/WORKFLOWS.md`.
- `spec`: an executable contract under `docs/specs/` that defines goal, scope,
  contracts, failure modes, acceptance criteria, and verification.
- `milestone`: a larger deliverable slice under `docs/milestones/`.
- `finance brief`: a finance-domain report generated from supplied evidence for
  a caller-provided watchlist and as-of datetime. The first version is verified
  through `docs/specs/0001-finance-daily-market-brief.md`.
- `watchlist`: the caller-supplied list of ticker symbols for one finance
  workflow invocation. Persistent watchlist storage requires a later spec.
- `research-only pullback zone`: a constrained entry-related output that uses a
  deterministic fixture-backed heuristic and must not provide personalized
  advice, position sizing, guarantees, or trade instructions.
- `suggested research entry price`: a research-only price artifact derived from
  accepted evidence and deterministic or model-governed logic. It may guide the
  operator's research, but it must not be framed as personalized advice, a buy
  order, position sizing, guaranteed outcome, or brokerage action.
- `entry-zone strategy`: the richer finance layer for technical analysis,
  scoring, ranking, and strategy logic. It is verified through
  `docs/specs/0002-finance-entry-zone-strategy.md`.
- `finance agent foundation`: the first finance-domain milestone, defined by
  and verified in `docs/milestones/0001-finance-agent-foundation.md`.
- `requirement gathering`: the workflow that turns vague intent into a
  requirements packet or Accepted milestone for spec, milestone, or context
  work.
- `spec grilling`: adversarial review of a spec before implementation.
- `dev loop`: the implementation workflow from accepted spec to verified,
  reviewed diff.
- `context maintenance`: keeping docs, specs, skills, and agent presets aligned
  after decisions settle.

## Reference Documents

- `AGENTS.md`: fast Codex orientation and minimum operating contract.
- `docs/PRODUCT.md`: product intent, current scope, principles, and roadmap.
- `docs/WORKFLOWS.md`: detailed skill workflow rules and handoff expectations.
- `docs/AGENT_ROLES.md`: subagent roles, edit permissions, and routing
  principles.
- `docs/DOCS_POLICY.md`: documentation destinations and status rules.

## Agent Roles

- `spec-planner`: drafts requirements, specs, milestones, and acceptance
  criteria.
- `spec-griller`: challenges vague terms, missing failure modes, weak contracts,
  and scope creep.
- `explorer`: reads the repo and summarizes current state without editing.
- `implementer`: edits files to satisfy accepted specs.
- `test-runner`: runs targeted verification and summarizes results.
- `reviewer`: checks diffs against specs and looks for bugs, regressions, and
  missing tests.
- `doc-curator`: updates durable docs after decisions settle.

If a selected skill names one of these roles in its workflow, that skill-level
instruction authorizes the main agent to spawn or use that role for the scoped
task, subject to system/tool constraints and file ownership rules.

## Workflow Boundaries

- Requirements work can identify product/context changes, write or update
  milestone contracts, and accept milestone direction after blockers are
  resolved. It should not implement code, write a full spec under `docs/specs/`,
  or directly own context maintenance. It produces requirements packets or
  Accepted milestone handoffs for spec work and hands settled context changes to
  `hermes-context`.
- Spec work can define executable implementation contracts and acceptance
  criteria under `docs/specs/`, but should not hide implementation details as
  settled architecture. It consumes only Accepted milestone contracts with no
  unresolved blocking questions. It does not create, accept, revise, or
  status-update `docs/milestones/` contracts. It leaves spec handoff artifacts
  for `hermes-dev-loop` or `hermes-context`.
- Existing Draft milestones must be reopened through `hermes-requirements` for
  blocker resolution and promotion before `hermes-spec` consumes them.
- Development work starts from an Accepted spec unless the user explicitly marks
  the task as a small exception. It consumes an Accepted spec handoff and
  reports changed files, verification results, review findings, and any follow-up
  spec or context handoff.
- Review work compares the diff to the spec; it should not become open-ended
  redesign unless the spec is wrong.
- Context maintenance runs whenever settled work changes terminology, workflow
  boundaries, product direction, role definitions, or agent/skill usage.
  `hermes-context` and `doc-curator` own surgical updates to durable context
  docs and skill or agent rules when those decisions settle.
- `grill-with-docs` is a support skill for pressure-testing requirements,
  specs, milestones, and context updates; it does not replace the main
  requirements, spec, dev-loop, or context workflows.
- The main agent owns judgment, reconciliation, user interaction, and final
  reporting. Read-only subagents may run in parallel when their questions are
  independent. Write-capable subagents must have disjoint file ownership; use
  one `implementer` at a time unless an Accepted spec explicitly decomposes
  disjoint write scopes.
- Manual spec-like drafting performed while `hermes-requirements` is active is
  not a literal invocation of `hermes-spec`; describe that clearly and correct
  the workflow boundary in the next update.
- Bash scripts may invoke repeatable checks or `codex exec`, but they should not
  own agent routing decisions.
- Finance is the first domain expansion for this workspace. Its fixture-backed
  foundation is verified in `docs/milestones/0001-finance-agent-foundation.md`
  and child specs `0001` and `0002`, not by broad assumptions from the README
  architecture sketch.
- The product focus is runtime finance research agents, not development-time
  Codex subagents. Codex agents under `.codex/agents/` are the way the repo is
  built and reviewed; runtime product agents must be introduced through
  accepted product specs.
- Future roadmap slices should be captured as individual milestone files under
  `docs/milestones/`, not maintained as one consolidated roadmap handoff after
  milestone boundaries settle.
- Model calls remain out of scope for verified fixture-backed finance specs.
  When a later accepted runtime spec introduces model-backed behavior,
  OpenRouter is the planned model gateway by default, and deterministic finance
  tools plus validated evidence remain the factual source of truth.
- The runtime product target is single-user by default. Multi-user auth, public
  bot access, team accounts, billing, role administration, and multi-tenant
  persistence require later accepted specs.
- The research-only boundary allows suggested research entry prices or entry
  zones when accepted specs define their evidence, calculation, wording, and
  verification contracts. It still excludes trade execution, brokerage actions,
  position sizing, guarantees, and personalized financial advice.

## Open Questions

- When should Telegram delivery become its own accepted spec?
- Should inherited skills be retired, renamed, or kept as references?

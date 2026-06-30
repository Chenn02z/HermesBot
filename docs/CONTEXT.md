# Workspace Context

Canonical terminology and workflow boundaries. Keep implementation details out.

## Canonical Terms

- `HermesBot`: this repository's personal finance research agent product.
- `workspace`: this repo and its docs, skills, specs, and agent presets.
- `developer`: the human using this repo for specs-driven agentic work.
- `single-user product boundary`: one developer/operator, one authorized
  personal Telegram identity, unless a later accepted spec broadens scope.
- `runtime product agent`: a production finance research role (news analyst,
  price analyst, technical analyst, fundamentals analyst, valuation analyst,
  risk analyst, bull/bear researcher, chief analyst, portfolio-manager-style
  synthesizer). Distinct from Codex development subagents.
- `OpenRouter gateway`: planned model access boundary for varied model usage
  in future accepted runtime specs. Not permission for unspec'd model calls.
- `main agent`: the Codex thread owning judgment, delegation, reconciliation,
  user interaction, and final reporting.
- `subagent`: a delegated Codex development agent with narrow role/model/
  reasoning/permission profile. Unqualified = development-time, not runtime.
- `skill`: a reusable workflow under `.agents/skills/`.
- `agent preset`: a `.codex/agents/*.toml` role/model/permission default.
- `requirements packet`: pre-spec output of `hermes-requirements` with resolved
  workflow, proposed spec path, scope, scenarios, criteria, blockers.
- `Accepted milestone`: a `docs/milestones/` contract with all blocking
  questions resolved. Eligible for `hermes-spec`; does not authorize
  implementation without an Accepted child spec.
- `handoff artifact`: explicit producer→consumer artifact naming the producing
  skill, intended consumer, path, status, decisions, blockers, and agent
  routing log.
- `spec`: executable contract under `docs/specs/` (goal, scope, contracts,
  failure modes, acceptance criteria, verification).
- `milestone`: larger deliverable slice under `docs/milestones/`.
- `finance brief`: report from supplied evidence for a caller-provided
  watchlist and as-of datetime. Verified via spec 0001.
- `watchlist`: caller-supplied ticker symbol list. Persistent storage is later spec.
- `research-only pullback zone`: constrained entry-related output using
  fixture-backed heuristics. Not advice, not trading instructions.
- `suggested research entry price`: research-only artifact from accepted
  evidence and logic. Not advice, not a buy order, not a guarantee.
- `entry-zone strategy`: technical analysis, scoring, ranking layer. Verified
  via spec 0002.
- `finance agent foundation`: first finance milestone (milestone 0001).
- `requirement gathering`: vague intent → requirements packet or Accepted
  milestone.
- `spec grilling`: adversarial review before implementation.
- `dev loop`: Accepted spec → verified, reviewed diff.
- `context maintenance`: keeping docs/specs/skills/agents aligned post-decisions.

## Reference Documents

- `AGENTS.md`: Codex orientation and operating contract.
- `docs/PRODUCT.md`: product intent, scope, principles, roadmap.
- `docs/WORKFLOWS.md`: handoff interface, spec status contract.
- `docs/AGENT_ROLES.md`: subagent roles, permissions, routing principles.
- `docs/DOCS_POLICY.md`: documentation destinations and status rules.

## Workflow Boundaries

- Requirements: produces milestone contracts and requirements packets. Does
  not write specs or implement code.
- Specs: produces executable contracts under `docs/specs/` from Accepted
  milestones only. Does not modify milestones.
- Draft milestones must be reopened through `hermes-requirements`.
- Dev loop: implements from Accepted spec only. Reports changed files,
  verification, review findings, follow-up handoffs.
- Review: compares diff to spec; not open-ended redesign.
- Context maintenance: runs when settled work changes terminology, boundaries,
  product direction, roles, or agent/skill usage.
- `grill-with-docs`: pressure-tests against docs; does not replace main
  workflows.
- Read-only subagents may run in parallel if independent. Write-capable
  subagents need disjoint file ownership.
- Bash scripts may run repeatable checks, not own agent routing.
- Finance is the first domain expansion. Verified through milestone 0001 and
  child specs 0001/0002.
- Runtime product agents require accepted runtime specs.
- Model calls stay out of scope for fixture-backed finance specs.

## Open Questions

- When does Telegram delivery become its own accepted spec?
- Should inherited skills be retired, renamed, or kept as references?

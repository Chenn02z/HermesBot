# Hermes Agent Workspace Context

This document defines project terminology and boundaries. Keep it about meaning
and workflow context, not implementation details.

## Canonical Terms

- `Hermes`: Nous Research's Hermes Agent project, used here as the agentic
  substrate and product reference.
- `workspace`: this repository and its docs, skills, specs, and agent presets.
- `developer`: the human using this repo to drive specs-driven agentic work.
- `main agent`: the active Codex thread that owns judgment, user interaction,
  final decisions, and final reporting.
- `subagent`: a delegated Codex agent with a narrow role, model, reasoning, and
  permission profile.
- `skill`: a reusable workflow under `.agents/skills/` that tells the main agent
  how to do a class of work.
- `agent preset`: a concrete subagent role under `.codex/agents/` that defines
  model, reasoning, and permission defaults for a delegated task.
- `requirements packet`: the pre-spec output of `hermes-requirements`,
  containing the resolved workflow, proposed spec name/path, scope boundary,
  scenarios, acceptance criteria candidates, and blocking questions.
- `handoff artifact`: the explicit output one workflow skill leaves for the
  next skill to consume. It names the producer skill, intended consumer skill,
  artifact path or packet contents, status, settled decisions, unresolved
  blockers, docs or specs that must be read next, and the agent routing log
  defined in `docs/WORKFLOWS.md`.
- `spec`: an executable contract under `docs/specs/` that defines goal, scope,
  contracts, failure modes, acceptance criteria, and verification.
- `milestone`: a larger deliverable slice under `docs/milestones/`.
- `finance brief`: a finance-domain report generated from supplied evidence for
  a caller-provided watchlist and as-of datetime. The first version is proposed
  in `docs/milestones/0001-finance-agent-foundation.md` for later `$hermes-spec`
  authoring.
- `watchlist`: the caller-supplied list of ticker symbols for one finance
  workflow invocation. Persistent watchlist storage requires a later spec.
- `research-only pullback zone`: a constrained entry-related output that uses a
  deterministic fixture-backed heuristic and must not provide personalized
  advice, position sizing, guarantees, or trade instructions.
- `entry-zone strategy`: the richer finance layer for technical analysis,
  scoring, ranking, and strategy logic. It is proposed as follow-up spec work in
  `docs/milestones/0001-finance-agent-foundation.md`.
- `finance agent foundation`: the first finance-domain milestone, defined by
  `docs/milestones/0001-finance-agent-foundation.md`.
- `requirement gathering`: the workflow that turns vague intent into a
  requirements packet for spec, milestone, or context work.
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

- Requirements work can identify product/context changes, but should not
  implement code, write a full spec, or directly own context maintenance. It
  may write or update requirements handoff artifacts and proposed milestone
  handoffs only. It should produce a requirements packet as a handoff artifact
  for spec work and hand settled context changes to `hermes-context`.
- Spec work can define contracts and acceptance criteria, but should not hide
  implementation details as settled architecture. It consumes requirements
  packets or milestone direction and writes or updates `docs/specs/` and
  `docs/milestones/` contracts. It leaves specs or milestone contracts as
  handoff artifacts for `hermes-dev-loop` or `hermes-context`.
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
- Finance is the first domain expansion for this workspace. Its initial
  requirements are captured by
  `docs/milestones/0001-finance-agent-foundation.md`, not by broad assumptions
  from the README architecture sketch. `$hermes-spec` owns writing the proposed
  `docs/specs/0001-finance-daily-market-brief.md` and
  `docs/specs/0002-finance-entry-zone-strategy.md` contracts.

## Open Questions

- When should Telegram delivery become its own accepted spec?
- Should inherited skills be retired, renamed, or kept as references?
- Which Hermes Agent features should be treated as required substrate versus
  optional integrations?

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
- `requirements packet`: the pre-spec output of `hermes-requirements`,
  containing the resolved workflow, proposed spec name/path, scope boundary,
  scenarios, acceptance criteria candidates, and blocking questions.
- `spec`: an executable contract under `docs/specs/` that defines goal, scope,
  contracts, failure modes, acceptance criteria, and verification.
- `milestone`: a larger deliverable slice under `docs/milestones/`.
- `requirement gathering`: the workflow that turns vague intent into a
  requirements packet for spec, milestone, or context work.
- `spec grilling`: adversarial review of a spec before implementation.
- `dev loop`: the implementation workflow from accepted spec to verified,
  reviewed diff.
- `context maintenance`: keeping docs, specs, skills, and agent presets aligned
  after decisions settle.

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

## Workflow Boundaries

- Requirements work can identify product/context changes, but should not
  implement code, write a full spec, or directly own context maintenance. It
  should produce a requirements packet for spec work and hand settled context
  changes to `hermes-context`.
- Spec work can define contracts and acceptance criteria, but should not hide
  implementation details as settled architecture.
- Development work starts from an Accepted spec unless the user explicitly marks
  the task as a small exception.
- Review work compares the diff to the spec; it should not become open-ended
  redesign unless the spec is wrong.
- Context maintenance runs whenever settled work changes terminology, workflow
  boundaries, product direction, role definitions, or agent/skill usage.
- `grill-with-docs` is a support skill for pressure-testing requirements,
  specs, milestones, and context updates; it does not replace the main
  requirements, spec, dev-loop, or context workflows.
- Bash scripts may invoke repeatable checks or `codex exec`, but they should not
  own agent routing decisions.

## Open Questions

- What should the first real milestone be for this workspace?
- Which future domain should be specified first: finance, Telegram interface, or
  core Hermes Agent extension workflow?
- Should inherited skills be retired, renamed, or kept as references?
- Which Hermes Agent features should be treated as required substrate versus
  optional integrations?

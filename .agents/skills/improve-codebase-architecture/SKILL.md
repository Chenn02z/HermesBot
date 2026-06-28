---
name: improve-codebase-architecture
description: Find Hermes Agent workspace architecture-deepening opportunities that reduce AI-spaghetti risk, present them as a visual HTML report, then route the chosen candidate through grill-with-docs. Use when reviewing workspace code structure, workflow seams, module boundaries, testability, long-term maintainability, or before implementing a spec or milestone that may spread behavior across docs, skills, agents, finance code, and tests.
---

# Improve Codebase Architecture

Surface architectural friction in the Hermes Agent workspace and propose
deepening opportunities: refactors that move scattered behavior behind a small,
useful interface. The aim is to prevent AI-generated spaghetti by improving
locality, leverage, and testability before implementation work expands.

This skill is for architecture review, not immediate implementation. It should
produce review artifacts the developer can inspect and then pressure-test with
`$grill-with-docs` before any spec or code work expands.

The named project agents in this workflow are authorized subagents for this
skill's scoped task. The main agent still owns judgment, user interaction,
reconciliation, and final reporting.

## Vocabulary

Use these architecture terms consistently: `module`, `interface`,
`implementation`, `deep`, `shallow`, `seam`, `adapter`, `locality`, and
`leverage`.

Definitions: a deep module has a small interface and substantial useful
implementation; a shallow module exposes nearly as much complexity as it hides;
a seam is a real split where dependencies or tests can substitute behavior; an
adapter translates across a seam; locality keeps related behavior together;
leverage means one interface improves many call sites or tests.

Use Hermes workspace language from `docs/CONTEXT.md` and the current specs:
workspace, developer, main agent, subagent, skill, agent preset, requirements
packet, handoff artifact, spec, milestone, finance brief, watchlist,
research-only pullback zone, entry-zone strategy, and finance agent
foundation.

## Process

### 1. Read context

Read first: `README.md`, `AGENTS.md`, `docs/PRODUCT.md`, `docs/CONTEXT.md`,
`docs/WORKFLOWS.md`, `docs/AGENT_ROLES.md`, `docs/DOCS_POLICY.md`, relevant
files under `docs/specs/`, relevant files under `docs/milestones/`, and
existing `docs/techdebt/` tickets if present. Read existing `docs/adr/`
entries if present.

Then inspect the repo area that matches the architecture review target. Current
Hermes workspace areas include:

- workflow docs and handoff contracts under `docs/`
- reusable workflow skills under `.agents/skills/`
- project agent presets under `.codex/agents/`
- finance implementation code under `src/hermes_finance/`
- fixture-backed verification under `tests/finance/` and `tests/fixtures/`

Use `explorer` for the read-only pass when delegated exploration is helpful.

### 2. Explore code

Inspect docs, skills, code, and tests directly. Favor the current Accepted,
Implemented, or Draft specs and milestones over assumptions from the README
architecture sketch.

Look for friction:

- One Hermes workflow concept requires bouncing across many files.
- A module is shallow: callers know too much about its implementation.
- A spec or milestone behavior spreads across docs, skills, code, and tests
  with no stable interface.
- Tests reach through internals instead of exercising a meaningful interface.
- Handoff artifact rules, spec status transitions, workflow boundaries, or
  finance evidence contracts are duplicated or bypassable.
- A seam exists for only one adapter and creates indirection without leverage.

Apply the deletion test to suspected shallow modules: if deleting the module
concentrates behavior and simplifies tests, it is probably shallow.

Hermes-specific examples that fit this review:

- Spec status logic leaks across multiple skills instead of one shared workflow
  module or contract.
- Finance brief rendering mixes fixture validation, deterministic calculation,
  and markdown narration in a way that makes focused tests awkward.
- A skill duplicates terminology that should live in `docs/CONTEXT.md` or
  `docs/WORKFLOWS.md`.
- A seam between docs and implementation exists only as prose, with no focused
  spec or test anchor.
- The proposed `0002` entry-zone strategy would force callers to know too much
  about `0001` report internals instead of building on a narrower interface.

### 3. Present candidates

Write a self-contained HTML file to the OS temp directory so bulky generated
reports do not land in the repo. Durable follow-up tickets live in
`docs/techdebt/` and must be self-contained because temp links may expire.
Resolve the temp dir from `$TMPDIR`, falling back to `/tmp` or `%TEMP%`, and write to
`<tmpdir>/hermes-agent-architecture-review-<timestamp>.html`. Open it for the
user if allowed by the current environment and report the absolute path.

Use Tailwind via CDN and Mermaid via CDN. Mix Mermaid with hand-built CSS/SVG.
Every candidate must have a before/after visualization.

Each candidate card includes:

- Files and modules involved
- Problem and solution, without implementing yet
- Benefits in locality, leverage, and tests
- Before/after diagram
- Recommendation strength: `Strong`, `Worth exploring`, or `Speculative`
- Relevant spec, milestone, or doc anchor, when one applies

End with a top recommendation and why it should be handled first.

See [HTML-REPORT.md](HTML-REPORT.md) for the scaffold, diagram patterns, and
styling guidance.

Use `doc-curator` to create or update markdown handoff tickets in the repo
under `docs/techdebt/`, one file per candidate, or record an approved manual
fallback in the agent routing log. Use [TECHDEBT-TICKET.md](TECHDEBT-TICKET.md)
as the template and name files `YYYY-MM-DD-<candidate-slug>.md`. For example, a
report with four architecture suggestions should produce four separate markdown
files, not one combined document. Each ticket should include enough copied
context to stand alone, record the temp report path when available, capture the
current code snapshot, include before/after Mermaid diagrams, and state
acceptance criteria for implementation. Default new tickets to `proposed`
unless the review or follow-up workflow has already settled a different status
under `docs/DOCS_POLICY.md`.

Ticket examples that fit the current workspace:

- `2026-06-28-deepen-finance-brief-pipeline.md`
- `2026-06-28-centralize-spec-status-rules.md`
- `2026-06-28-define-architecture-candidate-destination.md`
- `2026-06-28-shrink-skill-handoff-surface.md`

Do not implement or finalize a new interface during the report. After the file
is written, ask: "Which candidate do you want to grill first?"

### 4. Grilling loop

Once the user picks a candidate, use `grill-with-docs` to pressure-test it
against product intent, milestone docs, code, and terminology.

During the grilling loop:

- Ask one question at a time and include a recommended answer.
- Update durable docs only when the candidate settles a real context change.
- Use `doc-curator` for surgical doc updates when the grilling loop settles
  terminology, workflow boundaries, or documentation ownership.
- Create an ADR only for hard-to-reverse, surprising trade-offs.
- If the candidate changes product requirements or executable behavior, route to
  `$hermes-requirements` or `$hermes-spec` before implementation.
- If the candidate can proceed from an Accepted spec, route implementation to
  `$hermes-dev-loop` after the design is settled.

The final output of the grilling loop should be either a scoped implementation
plan, a spec update handoff, or a documented reason to reject the refactor.

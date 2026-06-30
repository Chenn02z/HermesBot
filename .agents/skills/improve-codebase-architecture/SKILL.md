---
name: improve-codebase-architecture
description: Find workspace architecture-deepening opportunities that reduce AI-spaghetti risk, present them as a visual HTML report, then route the chosen candidate through grill-with-docs. Use when reviewing workspace code structure, workflow seams, module boundaries, testability, long-term maintainability, or before implementing a spec or milestone that may spread behavior across docs, skills, agents, finance code, and tests.
---

# Improve Codebase Architecture

Surface architectural friction in the workspace and propose
deepening opportunities: refactors that move scattered behavior behind a small,
useful interface. The aim is to prevent AI-generated spaghetti by improving
locality, leverage, and testability before implementation work expands.

This skill is for architecture review, not immediate implementation. It should
produce review artifacts the developer can inspect and then pressure-test with
`\-with-docs` before any spec or code work expands.

The named project agents in this workflow are authorized subagents for this
skill's scoped task. The main agent still owns judgment, user interaction,
reconciliation, and final reporting.

## Vocabulary

Use architecture terms in [HTML-REPORT.md](HTML-REPORT.md) (module, interface,
implementation, deep, shallow, seam, adapter, locality, leverage) and workspace
language from `docs/CONTEXT.md`. See those files for definitions.

## Process

### 1. Read context

Read `docs/CONTEXT.md` for terminology. Read only the docs, specs, and
milestones relevant to the architecture review target. Use `explorer` for
the read-only pass when delegated exploration is helpful.

### 2. Explore code

Inspect docs, skills, code, and tests directly. Favor the current Accepted,
Implemented, or Draft specs and milestones over assumptions from the README
architecture sketch.

Look for friction:

- One workflow concept requires bouncing across many files.
- A module is shallow: callers know too much about its implementation.
- A spec or milestone behavior spreads across docs, skills, code, and tests
  with no stable interface.
- Tests reach through internals instead of exercising a meaningful interface.
- Handoff artifact rules, spec status transitions, workflow boundaries, or
  finance evidence contracts are duplicated or bypassable.
- A seam exists for only one adapter and creates indirection without leverage.

Apply the deletion test to suspected shallow modules: if deleting the module
concentrates behavior and simplifies tests, it is probably shallow.

### 3. Present candidates

Write a self-contained HTML report: see [HTML-REPORT.md](HTML-REPORT.md) for
scaffold, patterns, and style. Write to `<tmpdir>/architecture-review-<timestamp>.html`.
Create durable follow-up tickets under `docs/techdebt/`: see
[TECHDEBT-TICKET.md](TECHDEBT-TICKET.md) for the template and naming convention.
One ticket per candidate, each self-contained. Default new tickets to `proposed`.

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
  `\-requirements` or `\-spec` before implementation.
- If the candidate can proceed from an Accepted spec, route implementation to
  `\-dev-loop` after the design is settled.

The final output of the grilling loop should be either a scoped implementation
plan, a spec update handoff, or a documented reason to reject the refactor.

---
name: hermes-dev-loop
description: Runs the specs-driven implementation loop for Hermes Agent work. Use when an accepted spec should be implemented, verified, reviewed, and summarized with model-routed subagents.
---

# Hermes Dev Loop

Use this skill after a spec is Accepted, or when the user explicitly marks a
small task as a spec exception.

## Workflow

1. Read the accepted spec, `AGENTS.md`, `docs/PRODUCT.md`, and
   `docs/CONTEXT.md`.
2. Use `explorer` to inspect relevant files and current patterns.
3. Ask the main agent to confirm any spec gap before implementation.
4. Use one `implementer` at a time for write-heavy work.
5. Use `test-runner` for targeted verification.
6. Use `reviewer` to compare the diff against the spec.
7. Have the main agent apply any final doc/spec status updates.

## Guardrails

- Do not let parallel agents edit the same files.
- Do not expand scope without updating the spec first.
- Prefer targeted tests and checks over broad commands early in the repo.
- Report missing tooling as a repo maturity gap, not a silent success.

## Output

Return:

- spec path and status
- files changed
- verification commands and results
- reviewer findings
- remaining risks or follow-up specs

# Guidelines for AI Agents

This repository is the Tier A IDD experiment for the `daymark` offline
task-planning CLI. The goal is to measure whether a middle-tier cloud
model can author, implement, verify, and repeat an issue-driven loop
without frontier-only guidance.

## Tooling priority and compatibility

`AGENTS.md`, `CLAUDE.md`, and `GEMINI.md` are lightweight compatibility
entry points for Codex, Claude Code, and Gemini CLI. Keep this file as
the canonical project guide unless benchmark results justify a neutral
layout.

## IDD workflow

Use [docs/idd-workflow.md](../docs/idd-workflow.md) as the cross-agent
entry path. Before changing state, read
`.github/instructions/idd-overview-core.instructions.md` and the routed
phase file. The repository policy is recorded in
[`.github/idd/config.json`](idd/config.json): `mid-llm-test` markers,
`instructions-only` helpers, `no-advisory` review, and fully autonomous
merge gates for this controlled experiment.

Record loop observations in
[`docs/tier-a-experiment.md`](../docs/tier-a-experiment.md).

## Branch strategy

All changes reach `main` through pull requests using merge commits.
Feature branches are rebased onto `main` before their first
publication. Direct pushes to `main` are not part of the experiment.

## Validation

Run `python -m unittest discover -s tests -v` before pushing application
changes. Keep comments and source documentation in English.

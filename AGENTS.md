# Guidelines for AI Agents

This repository is a Tier A IDD experiment. It hosts `daymark`, a small
offline task-planning CLI, and records how a middle-tier cloud model
handles issue authoring and repeated IDD loops.

## Immediate rules

- Match the conversational language to the user's language.
- Write comments and documentation in English unless there is a clear
  project-specific reason otherwise.
- If uncertainty, hidden risk, or missing context blocks a safe change,
  stop and ask a concise question before proceeding.
- Keep changes small and reviewable. If you create commits, follow the
  project's Conventional Commits rules and keep each commit atomic.
- Do not modify community documents (`CODE_OF_CONDUCT*`,
  `CONTRIBUTING*`) without explicit approval.

## Project standards

- **Indentation**: 2 spaces
- **Line endings**: LF only
- **Trailing whitespace**: trimmed except in Markdown
- **File naming**: lowercase with hyphens unless a platform convention
  requires otherwise

## Commit rules

This project follows
[Conventional Commits](https://www.conventionalcommits.org/).
Write user-facing, lowercase subjects under 72 characters and keep each
commit atomic.

## Branch strategy

This project follows GitHub Flow. All changes reach `main` through pull
requests using merge commits; feature branches are rebased onto `main`
before their first publication. See the full rules in
[.github/copilot-instructions.md](.github/copilot-instructions.md#branch-strategy).

## IDD workflow

This repository uses Issue-Driven Development (IDD). Start with
[docs/idd-workflow.md](docs/idd-workflow.md), then open
`.github/instructions/idd-overview-core.instructions.md` and the routed
phase file before acting.

The local policy uses `mid-llm-test` markers, `instructions-only` helper
fallbacks, a `no-advisory` PR profile, and fully autonomous merge gates
for this controlled experiment. Keep the issue-authoring hold separate
from execution release, and record every loop in
`docs/tier-a-experiment.md`.

## Validation

Run `python -m unittest discover -s tests -v` for the application once
the first implementation issue has landed.

## Experiment boundary

Do not add checked-in `.agents/skills/` or `.opencode/skills/` mirrors.
The issue-authoring companion is used through the canonical
`idd-skill/skills/issue-authoring/` checkout for this experiment.

## Canonical reference

The full, Copilot-first guidance lives in
[.github/copilot-instructions.md](.github/copilot-instructions.md).

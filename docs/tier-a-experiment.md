# Tier A IDD Experiment

## Purpose

This repository measures whether a middle-tier cloud model can carry a
small but stateful application through repeated Issue-Driven Development
loops. The application is `daymark`, an offline task-planning CLI built
with the Python standard library.

The experiment evaluates the workflow, not a model benchmark score. Each
observation must distinguish a repository or instruction defect from an
ordinary implementation mistake.

## Recorded policy

- **IDD source**: `kurone-kito/idd-skill`, imported from the local clone.
- **Marker prefix**: `mid-llm-test`.
- **Helper runtime**: `instructions-only`; no package manager existed at
  onboarding time.
- **PR review**: `no-advisory`; the repository has no IDD-managed advisory
  reviewer. CI, branch protection, unresolved conversations, and claim
  gates remain authoritative.
- **Merge policy**: `fully_autonomous_merge`, selected for this controlled
  user-authorized experiment; the repository currently has no protected
  branch or required check.
- **Required-check read trust**: `ciGate.trustEmptyProtectionReads: true`
  is enabled because the authenticated GitHub token has admin permission,
  classic protection returned 404, and the ruleset list was empty. This
  explicitly records the verified empty-protection decision required by
  the fail-closed IDD default.
- **Thread resolution**: `fast-agent-resolve`.
- **Issue-author approval**: enabled by default; `kurone-kito` is an admin
  and can self-authorize the issues created for this run.
- **Critique loop**: standard self-critique when no native reviewer is
  available.
- **Issue-authoring companion**: not copied into a second runtime root;
  the canonical bundle under the local `idd-skill` checkout is read
  explicitly to avoid duplicate skill discovery.

## Operating rules

1. Author and publish each candidate under `status:authoring`.
2. Run the mechanical authoring audit with the resolved target prefix.
3. Keep the hold until the roadmap task list, placeholders, and all issue
   bodies are stable; release only after that checklist passes.
4. For each released child, run Discover, Claim, Work, PR Submit, CI,
   review triage, and merge according to the imported instructions.
5. Append an entry below after every meaningful loop transition, including
   a stopped or held run.
6. Create an upstream feedback issue only for a reproducible problem in
   IDD's instructions, tooling, or distributed template. Do not file
   speculative improvements.

## Loop log

| Run | Issue/PR | Result | Observation | Upstream feedback |
| --- | --- | --- | --- | --- |
| 0 | bootstrap / PR #1 | held on CI | The imported docs produced 119 cspell findings across 23 repeated words in the target's generic dictionary. A CodeRabbit status also remained pending, while no branch protection or required check was configured. | candidate: imported-doc dictionary contract |
| 1 | #3 / B1-B3 | implemented locally; CI pending | B1 first created a worktree one directory too high; the empty branch was safely removed and recreated at the required sibling path. The local shell has `python3` but no `python` alias, so validation was made explicit and portable with `python3`. Core tests now cover validation, versioned persistence, duplicate IDs, and preservation after serialization or replace failure. A body-only issue update also reintroduced the `roadmap` label on this child, so the full label set was restored before continuing. | candidate: imported-doc dictionary and generic-linter contract |
| 2 | #3 / E1-F2 | policy fix committed; CI pending | Copilot and Codex review threads identified actionable input-boundary and indentation defects; the fixes were verified locally and all threads were replied to and resolved. CodeRabbit returned only a rate-limit notice. F2 then stopped on the imported fail-closed 404 protection-read rule, so the verified empty-protection policy was recorded explicitly in target config before merge. | candidate: onboarding should surface the verified empty-protection trust decision |
| 3 | #4 / B1-B3 | implemented locally; CI pending | A pre-claim worktree was removed after A5(e) correctly identified it as an unowned issue-number branch collision; B1 then recreated the sibling worktree after claim and acquired the local lock. A refined-plan comment initially hit shell quoting because an apostrophe closed a hand-written single-quoted body; no comment was posted, and the retry used encoded JSON. The CLI keeps `--data` explicit, uses deterministic list rendering, and covers subprocess error boundaries. | candidate: instructions-only mutation/comment helpers should reduce hand-written quoting and path hazards |

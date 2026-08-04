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
| 0 | bootstrap | in progress | Template import and policy wiring are being verified. | pending |

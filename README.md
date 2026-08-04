# Daymark

Daymark is a small offline task-planning CLI used to evaluate the Tier A
IDD workflow in `kurone-kito/idd-skill-mid-llm-test`.

The application keeps a local task ledger with generated IDs, due-date
metadata, completion transitions, and safe JSON persistence. It uses only
the Python standard library so the experiment can isolate
workflow and model behavior from dependency installation.

## CLI flow

The data path is explicit and required; Daymark never selects a repository
or home-directory ledger automatically.

```sh
DATA_PATH="$(mktemp -d)/tasks.json"
python3 -m daymark --data "$DATA_PATH" add "Write tests" \
  --due-date 2026-08-05 --tag work
python3 -m daymark --data "$DATA_PATH" list --status pending
python3 -m daymark --data "$DATA_PATH" done TASK_ID
python3 -m daymark --data "$DATA_PATH" restore TASK_ID
```

`list` emits deterministic tab-separated rows, with `tags` represented as a
JSON array. Replace `TASK_ID` with the ID printed by `add`; query and
recurring-task options are planned for the next roadmap issue.

Ledger writes use a same-directory temporary file, flush and fsync it, then
atomically replace the requested data path. Temporary files are cleaned up
after both successful and failed writes.

## Development

Read [docs/idd-workflow.md](docs/idd-workflow.md) before starting an IDD
phase. The experiment policy and loop log live in
[docs/tier-a-experiment.md](docs/tier-a-experiment.md).

Run the test suite with:

```sh
python3 -m unittest discover -s tests -v
```

## Status

The repository is intentionally developed through GitHub Issues. The
initial roadmap and its child issues define the first runnable slice;
later observations may produce follow-up issues in the upstream
`idd-skill` repository.

## License

[MIT](./LICENSE)

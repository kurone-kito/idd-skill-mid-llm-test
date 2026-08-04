# Daymark

Daymark is a small offline task-planning CLI used to evaluate the Tier A
IDD workflow in `kurone-kito/idd-skill-mid-llm-test`.

The application will keep a local task ledger with deterministic IDs,
due-date queries, completion transitions, and safe JSON persistence. It
uses only the Python standard library so the experiment can isolate
workflow and model behavior from dependency installation.

## Development

Read [docs/idd-workflow.md](docs/idd-workflow.md) before starting an IDD
phase. The experiment policy and loop log live in
[docs/tier-a-experiment.md](docs/tier-a-experiment.md).

Run the test suite with:

```sh
python -m unittest discover -s tests -v
```

## Status

The repository is intentionally developed through GitHub Issues. The
initial roadmap and its child issues define the first runnable slice;
later observations may produce follow-up issues in the upstream
`idd-skill` repository.

## License

[MIT](./LICENSE)

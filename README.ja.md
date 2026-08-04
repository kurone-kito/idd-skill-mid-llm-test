# Daymark

Daymark は、`kurone-kito/idd-skill-mid-llm-test` で Tier A の IDD
ワークフローを評価するための、小規模なオフライン・タスク計画 CLI
です。

アプリケーションは、生成された ID、期限情報、完了状態の遷移、
安全な JSON 永続化を備えたローカルのタスク台帳を扱います。依存関係
の導入とモデルの挙動を分離できるよう、Python 標準ライブラリだけを
使用します。

## CLI の流れ

データパスは必須かつ明示的に指定します。Daymark はリポジトリや
ホームディレクトリの台帳を自動選択しません。

```sh
DATA_PATH="$(mktemp -d)/tasks.json"
python3 -m daymark --data "$DATA_PATH" add "Write tests" \
  --due-date 2026-08-05 --tag work --repeat daily
python3 -m daymark --data "$DATA_PATH" list --status pending
python3 -m daymark --data "$DATA_PATH" list \
  --reference-date 2026-08-05 --due-by 2026-08-05 --tag work
python3 -m daymark --data "$DATA_PATH" done TASK_ID
python3 -m daymark --data "$DATA_PATH" restore TASK_ID
```

`list` は決定的なタブ区切りの行を出力し、`tags` 列は JSON 配列で
表現し、`repeat` 列は `-`、`daily`、`weekly` のいずれかになります。
`TASK_ID` は `add` が出力する ID に置き換えてください。

検索フィルターを複数指定した場合は AND 条件で結合され、ID 順の決定性
を保ちます。`--due-on` は指定日のタスク、`--due-by` は指定日以前の
タスク、`--overdue` は `--reference-date` より前に期限がある pending
タスクを選びます。複数の `--tag` は `--tag-mode all|any` で全一致または
いずれか一致を選べます。`--repeat` は検証済みの metadata を絞り込む
だけで、将来の occurrence を展開したり期限日を変更したりしません。
`--reference-date` を省略した場合の CLI はローカルの現在日を使いますが、
テストとライブラリ利用者は明示的な基準日を渡してください。

台帳の書き込みでは同じディレクトリに一時ファイルを作成し、flush と
fsync を行ってから指定されたデータパスをアトミックに置き換えます。
成功時と失敗時のいずれも一時ファイルは後片付けされます。

## 開発

IDD の各フェーズを開始する前に
[docs/idd-workflow.md](docs/idd-workflow.md) を読みます。実験方針と
ループの記録は [docs/tier-a-experiment.md](docs/tier-a-experiment.md)
にあります。

テストは次のコマンドで実行します。

```sh
python3 -m unittest discover -s tests -v
```

## 状態

このリポジトリは GitHub Issue を通じて意図的に開発します。最初の
実行可能なスライスは初期 roadmap と子 issue が定義し、その後の観測
から upstream の `idd-skill` への follow-up issue を作成します。

## ライセンス

[MIT](./LICENSE)

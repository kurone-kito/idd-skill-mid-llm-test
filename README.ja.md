# Daymark

Daymark は、`kurone-kito/idd-skill-mid-llm-test` で Tier A の IDD
ワークフローを評価するための、小規模なオフライン・タスク計画 CLI
です。

アプリケーションは、決定的な ID、期限による検索、完了状態の遷移、
安全な JSON 永続化を備えたローカルのタスク台帳を扱います。依存関係
の導入とモデルの挙動を分離できるよう、Python 標準ライブラリだけを
使用します。

## 開発

IDD の各フェーズを開始する前に
[docs/idd-workflow.md](docs/idd-workflow.md) を読みます。実験方針と
ループの記録は [docs/tier-a-experiment.md](docs/tier-a-experiment.md)
にあります。

テストは次のコマンドで実行します。

```sh
python -m unittest discover -s tests -v
```

## 状態

このリポジトリは GitHub Issue を通じて意図的に開発します。最初の
実行可能なスライスは初期 roadmap と子 issue が定義し、その後の観測
から upstream の `idd-skill` への follow-up issue を作成します。

## ライセンス

[MIT](./LICENSE)

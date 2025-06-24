# retry.py - 評価失敗データの修復ツール

## 背景

LLM評価フレームワークShaberiにおいて、`judge_answers.py`による評価処理は大量のデータを扱うため、以下のような問題が発生することがあります：

### 発生する問題
- **API制限・ネットワークエラー**: 長時間の評価処理中にAPI制限やネットワーク障害で一部の評価が失敗
- **部分的な処理失敗**: 大量データの処理中に一部のエントリで`score: null`が残る
- **処理の中断**: システム障害や手動停止により評価が途中で終了

### 従来の対応の問題点
- **全体再実行の非効率性**: `judge_answers.py`を再実行すると、正常に取得済みのスコアも再計算
- **コスト増大**: 不要なAPI呼び出しによる使用量とコストの無駄
- **時間の浪費**: 長時間の処理を最初からやり直す必要

## 解決策

`retry.py`は失敗した評価データのみを選択的に修復するツールです。

### 主な機能
1. **選択的処理**: `score`が`null`のエントリのみを特定・再評価
2. **設定の自動復元**: ファイルパスから元の評価設定を自動抽出
3. **柔軟なパラメータ調整**: 温度やトークン数を調整して再試行
4. **詳細なログ出力**: 問題の特定と進行状況の確認

## 実装の詳細

### ファイルパス解析
```python
# data/judgements/judge_gpt-4-turbo/lightblue__tengu_bench/model.json
# ↓
# judge_model: gpt-4-turbo
# dataset_name: lightblue/tengu_bench
```

パス構造から以下を自動抽出：
- **Judge Model**: `judge_*`ディレクトリ名から評価モデルを特定
- **Dataset Name**: ディレクトリ名の`__`を`/`に復元してデータセット名を取得

### 評価関数の選択
```python
evaluator_function = EVAL_MODEL_CONFIGS[dataset_name]["evaluator_function"]
```

データセット名に基づいて`evaluation_datasets_config.py`から適切な評価関数を自動選択します。

### 温度調整機能
失敗した評価に対して温度パラメータを調整することで、より安定した評価結果の取得を試みます：

- **開始温度**: `--start-temperature`で指定（0-100の整数）
- **自動調整**: `llm_functions.py`の温度調整リトライ機能と連携

## 使用方法

### 基本的な使用
```bash
# 失敗データの確認と修復
uv run retry.py data/judgements/judge_gpt-4-turbo/lightblue__tengu_bench/model.json
```

### オプション指定
```bash
# 最大トークン数と開始温度を指定
uv run retry.py -t 2048 -st 30 data/judgements/judge_*/dataset/model.json
```

### パラメータ
- `filename`: 修復対象のJSONLファイルパス
- `-t, --max-tokens`: 評価時の最大トークン数（デフォルト: 1024）
- `-st, --start-temperature`: 評価時の開始温度（0-100、デフォルト: 0）

## 実行例

```bash
$ uv run retry.py data/judgements/judge_gpt-4-turbo/lightblue__tengu_bench/shisa-ai__shisa-v1-llama3-8b.json

ファイルを解析中: data/judgements/judge_gpt-4-turbo/lightblue__tengu_bench/shisa-ai__shisa-v1-llama3-8b.json
最大トークン数: 1024
開始温度: 0.00
Judge model: gpt-4-turbo
Dataset: lightblue/tengu_bench
scoreがnullの行数: 5行
該当行番号: [12, 35, 78, 156, 203]
Evaluator: evaluate_tengu_bench

各行を再評価中...

行 12 を評価中...
行 12: スコア = 7

行 35 を評価中...
行 35: スコア = 4
...
```

## 運用での活用

### 定期的な確認
```bash
# null scoreの有無を確認
find data/judgements -name "*.json" -exec grep -l '"score": null' {} \;
```

### 自動修復スクリプトとの組み合わせ
```bash
#!/bin/bash
# 全ての失敗ファイルを修復
for file in $(find data/judgements -name "*.json" -exec grep -l '"score": null' {} \;); do
    echo "修復中: $file"
    uv run retry.py "$file"
done
```

## 注意事項

- 元のJSONLファイルは直接更新されません（現在は表示のみ）
- 大量の失敗データがある場合は、API制限に注意
- 評価モデルのAPI keyが適切に設定されている必要があります

## 今後の改善案

1. **ファイル更新機能**: 修復結果を元ファイルに自動反映
2. **バッチ処理**: 複数ファイルの一括修復
3. **進行状況表示**: 大量データ処理時のプログレスバー
4. **統計情報**: 修復前後の成功率比較
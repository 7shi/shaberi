# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## プロジェクト概要

Shaberi（しゃべり）は日本語LLMの評価フレームワークです。複数の日本語ベンチマークを使ってモデルの回答を生成し、LLM-as-a-Judge手法で自動評価を行います。

## 主要コマンド

### 環境構築
```bash
uv sync
```

### 評価の実行
```bash
# 1. vLLMでモデルサーバーを起動（別ターミナル）
python -m vllm.entrypoints.openai.api_server --model shisa-ai/shisa-v1-llama3-70b -tp 8

# または llama.cpp でサーバーを起動
./server -ngl 99 -c 8192 -m model.gguf --chat-template llama3 --host 0.0.0.0 --port 8000

# 2. モデルの回答を生成
uv run generate_answers.py --model_name 'shisa-ai/shisa-v1-llama3-8b' -fp 0.5

# 3. 回答を評価（要OPENAI_API_KEY環境変数）
uv run judge_answers.py -m shisa-ai/shisa-v1-llama3-8b

# 4. 結果の可視化
uv run results_vizualization.py
cat output.csv
```

### 一般的なオプション
- `--model_name` / `-m`: 評価対象のモデル名
- `--eval_dataset_name`: ベンチマーク名（"all", "shaberi3", または個別指定）
- `--frequency_penalty` / `-fp`: 生成時の頻度ペナルティ（推奨: 0.5）
- `--num_proc`: 並列処理数
- `--evaluation_model`: 評価用モデル（デフォルト: gpt-4-turbo-preview）

## アーキテクチャ

### 3段階の評価パイプライン
1. **generate_answers.py**: ベンチマーク質問に対するモデル回答の生成
2. **judge_answers.py**: LLM審査員による回答の評価・採点
3. **results_vizualization.py**: 結果の集計・分析・可視化

### データフロー
- 入力: HuggingFaceの日本語評価データセット
- 中間: JSONファイル（`data/model_answers/`, `data/judgements/`）
- 出力: CSV、グラフ、レポート

### 対応ベンチマーク
- `lightblue/tengu_bench`: 総合的な日本語能力
- `elyza/ELYZA-tasks-100`: タスク特化型評価（2倍の重み付け）
- `shisa-ai/ja-mt-bench-1shot`: マルチターン会話
- `kunishou/do-not-answer-120-ja`: 安全性評価
- `umiyuki/do-not-answer-ja-creative-150`: 創作系安全性

## 重要なファイル

### 設定・設計
- `evaluation_datasets_config.py`: 各ベンチマークの評価関数とプロンプト定義
- `llm_functions.py`: LLM API統合レイヤー（OpenAI、Gemini、vLLM対応）
- `requirements.txt`: Python依存関係

### ドキュメント
- `CLAUDE.md`: このファイル。Claude Codeへのプロジェクト概要説明

### ユーティリティ
- `chat_templates/`: 各モデル用のJinja2チャットテンプレート
- `results_to_csv.py`, `totals_to_csv.py`: 結果変換スクリプト
- `run_eval.sh`: 評価実行の自動化スクリプト

### 実行ヘルパー
- `01-answer.sh`, `02-judge.sh`: 段階別実行スクリプト
- `sampler-*.sh`: サンプリングパラメータ調整用

## 開発上の注意

### エラー対応
- meta-llama/Llama-2-7b-chat-hfでtengu_benchを実行時は`--num_proc=1`を使用
- APIエラー時は自動リトライが実装済み
- ログは実行ログファイルに出力される

### モデル対応
- OpenAI互換API（vLLM、llama.cpp等）をサポート
- Anthropic、Google Geminiも評価用モデルとして利用可能
- 新しいモデルを追加する場合は`chat_templates/`にテンプレートを追加

### 結果の重み付け
- ELYZA-tasks-100は他のベンチマークの2倍の重みで最終スコア計算に使用
- この重み付けは`results_vizualization.py`で定義されている

### データ構造
モデル回答は`data/model_answers/{dataset_name}/{model_name}.json`、評価結果は`data/judgements/judge_{judge_model}/{dataset_name}/{model_name}.json`に保存される。

## 独自修正内容

### llm_functions.py の変更点
1. **デバッグログの現代化**
   - 廃止予定の`litellm.set_verbose=True`を`litellm._logging._turn_on_debug()`に変更
   - より安定したデバッグログ出力

2. **トークン数制限の拡張（2025年6月17日更新）**
   - `generation_max_tokens`と`evaluation_max_tokens`を131072にグローバル変数として統一
   - 思考モデルの思考プロセスで大量のトークンを消費するため制限を大幅拡張
   - 各関数から重複するローカルなトークン制限パラメータを削除し保守性を向上

3. **Gemini APIの実装**
   - `get_response_from_litellm_gemini`: 基本的なGemini API呼び出し
   - セーフティ設定でコンテンツフィルタリングを無効化
   - モデル名を動的に設定: `model=f"gemini/{model_name}"`

4. **評価システムの温度調整リトライ機能（2025年6月17日追加）**
   - `get_model_response`関数に`parser_func`パラメータを追加
   - 評価結果のパース失敗時に温度を段階的に上げて再試行
   - 詳細は[EVAL.md](EVAL.md)を参照

### 新規追加ファイル
- [HOWTO.md](HOWTO.md): よくある質問と詳細な使い方ガイド（キャッシュ問題の解決方法を含む）
- [EVAL.md](EVAL.md): 評価システムのリファクタリング詳細（温度調整リトライ機能の実装について）

## Gemini対応について
このプロジェクトはGemini API対応のためにフォークされ、`for-gemini`ブランチで作業を進めています。主な変更点は上記の「独自修正内容」に記載されています。

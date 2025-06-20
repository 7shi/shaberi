# Experimental - Shaberi評価システム構造化出力移行ツール

## 概要

このディレクトリには、Shaberi評価フレームワークをFew-shot形式から構造化出力（JSONスキーマ）形式に移行するための実験的ツール群が含まれています。

## ファイル構成

実際にはexperimental/直下に多数のファイルが存在しますが、ここでは主要なサブディレクトリ構造のみ示します：

```
experimental/
└── 1tengu/                  # 生成されるファイル群
    ├── 001.md ～ 120.md     # 評価プロンプト
    ├── 001.json ～ 120.json # JSONスキーマ
    └── {評価者}/{回答者}/   # 評価結果
        └── 001.json ～ 120.json
```

## ツール一覧

**データ準備**
- **analyze_evaluations.py** - shaberi3-evaluations.jsonのデータ構造分析・調査ツール
- **dump_questions.py** - shaberi3-evaluations.jsonから3つのベンチマークデータを分類・抽出

**Tengu Benchmark 関連**
- **conv_tengu.py** - JSONデータを個別Markdownファイルに変換
- **check_criteria.py** - 評価項目形式を検証（単層/階層構造の判定）
- **md_to_schema.py** - MarkdownファイルからJSONスキーマを自動生成
- **tengu-000.py** - 構造化出力の概念実証（単一タスクテスト）
- **tengu.py** - 本格的な評価システム（スキーマ検証統合済み）

**ELYZA-tasks-100 関連**
- （今後実装予定）

**ja-mt-bench-1shot 関連**
- （今後実装予定）

**集計・分析**
- **score_tool.py** - 評価結果からスコア統計を集計しTOML形式で出力
- **totals_to_csv.py** - 複数の評価結果を集計してCSVファイルに出力（改修版）
- **merge_csv.py** - 異なる列順序を持つCSVファイルをマージ（列名ベース統合）

**過去データ調整**
- **validate_schema.py** - 評価結果がJSONスキーマに適合しているか検証
- **add_scores.py** - 過去の評価結果にscoreフィールドを追加

## 使用順序

以下の順序で実行することで、段階的に構造化出力システムを構築できます：

### 1. データ準備

#### `analyze_evaluations.py` - データ構造分析（任意）
```bash
uv run analyze_evaluations.py
```
- `shaberi3-evaluations.json`のデータ構造を調査分析
- `len(line_data) != 4`のケース等の詳細分析
- データ前処理の品質確認に使用（必須ではない）

#### `dump_questions.py` - 質問内容分類・抽出
```bash
uv run dump_questions.py
```
- `shaberi3-evaluations.json`から3つのベンチマークを分類
- tengu_bench (120件)、ELYZA-tasks-100 (100件)、ja-mt-bench-1shot (60件)
- 出力: `1tengu.json`, `2elyza.json`, `3mt.json`

### 2. Tengu Benchmark 関連

#### `conv_tengu.py` - JSON→Markdown変換
```bash
uv run conv_tengu.py
```
- `1tengu.json`から個別Markdownファイルに変換
- 出力: `1tengu/001.md` ～ `1tengu/120.md`

#### `check_criteria.py` - 評価項目形式検証
```bash
uv run check_criteria.py
```
- 120件の評価項目形式を自動検証
- 単層構造（97件）と階層構造（23件）を適切に処理
- 全件正常確認後、次の段階に進む

#### `md_to_schema.py` - Markdown→JSONスキーマ変換
```bash
uv run md_to_schema.py
```
- MarkdownファイルからJSONスキーマを自動生成
- 出力: `1tengu/001.json` ～ `1tengu/120.json`
- 構造化出力用スキーマファイルを120件作成

#### `tengu-000.py` - 単一タスク実証テスト
```bash
uv run tengu-000.py
```
- 「急がば回れ」の説明タスクで構造化出力をテスト
- llm7shiライブラリを使用してGemini 2.5 Flash APIにアクセス
- 概念実証として最初に実行

#### `tengu.py` - 本格的な評価システム
```bash
# 単一タスク評価
uv run tengu.py <model_answer_file> -n <task_number> [-m <evaluator_model>]

# 全タスク評価
uv run tengu.py <model_answer_file> --all [-m <evaluator_model>]

# 具体例
uv run tengu.py ../data/model_answers/lightblue__tengu_bench/gemini-2.5-pro.json -n 1
uv run tengu.py ../data/model_answers/lightblue__tengu_bench/gemini-2.5-pro.json --all
```
- リアルタイムスキーマ検証機能統合済み

#### 開発過程の補助ツール

##### `validate_schema.py` - 評価結果スキーマ検証
```bash
# 評価結果ディレクトリの検証
uv run validate_schema.py <評価結果ディレクトリ>

# 具体例
uv run validate_schema.py 1tengu/gemini-2.5-flash/gemini-2.5-pro
```
- Tengu Benchmark評価結果がJSONスキーマに適合しているかチェック
- 評価項目の完全性、ポイント値の妥当性、必須フィールドを検証
- `tengu.py`でリアルタイム検証機能として統合済み

##### `add_scores.py` - 過去データのスコア追加
```bash
# 特定ディレクトリの処理
uv run add_scores.py 1tengu/gemini-2.5-flash/gemini-2.5-pro

# ドライランモード
uv run add_scores.py 1tengu/gemini-2.5-flash/gemini-2.5-pro --dry-run

# 再帰的処理
uv run add_scores.py 1tengu --recursive
```
- 過去の評価結果に`score`フィールドを追加
- 新旧データの形式統一

### 3. ELYZA-tasks-100 関連

*（今後実装予定）*

### 4. ja-mt-bench-1shot 関連

*（今後実装予定）*

### 5. 集計・分析

#### `score_tool.py` - スコア集計・統合ツール
```bash
# 単一組み合わせの集計
uv run score_tool.py 1tengu/gemini-2.5-flash/gemini-2.5-pro

# カスタム出力ファイル
uv run score_tool.py 1tengu/gemini-2.5-flash/gemini-2.5-pro -o my_scores.toml

# 複数組み合わせの段階的集計
uv run score_tool.py 1tengu/gemini-2.5-flash/gemini-2.5-pro
uv run score_tool.py 1tengu/gemini-2.5-flash/claude-3-5-sonnet
# → scores.tomlに自動統合
```
- 評価結果ディレクトリからスコア統計を集計
- TOML形式での統合データ出力
- 増分更新による段階的データ蓄積
- モデル性能比較・分析の基盤データ提供

#### `totals_to_csv.py` - 評価結果CSV集計ツール（改修版）
```bash
# デフォルト設定で実行（totals.csvに出力）
uv run totals_to_csv.py

# カスタムディレクトリを指定（ディレクトリ名.csvに自動出力）
uv run totals_to_csv.py ./data/judgements/judge_gemini-2.5-flash
# → judge_gemini-2.5-flash.csvに出力

# 出力ファイルも指定
uv run totals_to_csv.py ./data/judgements -o ./output/summary.csv

# CP932エンコーディングで出力（Windows Excel用）
uv run totals_to_csv.py --encoding cp932 -o totals_cp932.csv
```
- 任意のディレクトリ構造から評価結果を再帰的に検索・集計
- モデル・データセットごとの重み付け平均スコアを計算
- 出力ファイル名の自動生成（入力パスから.csv拡張子で生成）
- CSV形式での出力（デフォルト：入力パス名.csv）
- 詳細は[totals_to_csv.md](totals_to_csv.md)を参照

#### `merge_csv.py` - CSVファイルマージツール
```bash
# 2つのCSVファイルをマージ
python merge_csv.py file1.csv file2.csv -o merged.csv

# 複数ファイルを一度にマージ
python merge_csv.py *.csv -o all_results.csv

# 標準出力に結果を表示
python merge_csv.py file1.csv file2.csv
```
- 異なる列順序を持つCSVファイルを列名ベースで統合
- 重複行の自動除去（同じモデル名の場合、最初の出現を保持）
- 列順序の統一（アルファベット順）
- 標準ライブラリのみ使用（pandas不要）
- 詳細は[merge_csv.md](merge_csv.md)を参照

### 6. 過去データ調整

*（tengu.pyの開発過程で使用した補助ツール。現在は`tengu.py`に機能統合済み）*

### 5. ELYZA-tasks-100 構造化出力システム

*（今後実装予定）*

### 6. ja-mt-bench-1shot 構造化出力システム

*（今後実装予定）*

## 技術的な改善点

### 従来のFew-shot形式の問題点
1. **計算ミス**: LLMが評価項目の合計点を誤計算
2. **形式不統一**: 出力フォーマットが一貫しない
3. **パース困難**: 自由形式テキストからの情報抽出が複雑
4. **効率低下**: Few-shot例で不要なトークンを消費

### 構造化出力による解決
1. **計算精度**: 後処理で確実に合計点を計算
2. **形式保証**: JSONスキーマによる厳密な構造制御
3. **効率処理**: 構造化データの直接利用
4. **トークン節約**: Few-shot例が不要
5. **品質保証**: リアルタイムスキーマ検証による自動品質管理

## 依存関係

```bash
# TOML読み込み（Python 3.10以前のみ）
pip install tomli

# 内部モジュール
# - llm7shi: Gemini API統合機能
# - utils.py: 共通ユーティリティ関数
```

## 出力形式

### 構造化出力例
```json
{
  "evaluation": {
    "答えが867万円である": {
      "points": "3",
      "reasoning": "正確な計算結果を示している"
    },
    "説明が具体的でわかりやすい": {
      "points": "2", 
      "reasoning": "計算過程が明確に記述されている"
    }
  },
  "summary": "全体的に優秀な回答",
  "score": 10
}
```

## 実行結果

### 処理統計
- **対象タスク**: 120件（Tengu Benchmark）
- **成功率**: 100%
- **形式分類**: 単層構造（97件）+ 階層構造（23件）
- **スキーマ生成**: 全120件対応

### パフォーマンス
- **高速処理**: 120件を数秒で完了
- **メモリ効率**: ファイル単位での逐次処理
- **エラー耐性**: 1件の失敗が全体に影響しない

## 今後の展開

1. **他ベンチマーク対応**: ELYZA、ja-mt-benchへの適用
2. **API統合拡張**: OpenAI、Anthropic対応
3. **評価精度向上**: 温度調整、プロンプト改良
4. **統計分析**: タスク別難易度分析

## 関連ドキュメント

- [CLAUDE.md](../CLAUDE.md): プロジェクト全体概要
- [docs/README.md](docs/README.md): 技術ドキュメント概要
- 各ツールの詳細: `{tool_name}.md`ファイル参照

## まとめ

このツール群により、Shaberi評価フレームワークは従来のFew-shot形式から構造化出力形式への移行を実現し、より精確で効率的な日本語LLM評価システムを構築できます。段階的な実行により、安全かつ確実にシステムを移行できます。

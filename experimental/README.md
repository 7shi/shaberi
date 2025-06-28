# Experimental - Shaberi評価システム構造化出力移行ツール

## 概要

このディレクトリには、Shaberi評価フレームワークをFew-shot形式から構造化出力（JSONスキーマ）形式に移行するための実験的ツール群が含まれています。

**注**: このREADMEでは各ツールの代表的なコマンド例のみを掲載しています。詳細な使用方法やオプションについては、各ツールのドキュメント（`{tool_name}.md`）を参照してください。

## ファイル構成

実際にはexperimental/直下に多数のファイルが存在しますが、ここでは主要なサブディレクトリ構造のみ示します：

```
experimental/
├── 1tengu/                  # Tengu Benchmark関連ファイル
│   ├── data/
│   │   ├── 001.md ～ 120.md     # 評価プロンプト
│   │   └── 001.json ～ 120.json # JSONスキーマ
│   └── judge/
│       └── {評価者}/{回答者}/   # 評価結果
│           └── 001.json ～ 120.json
├── 2elyza/                  # ELYZA-tasks-100関連ファイル
│   ├── data/
│   │   └── 001.md ～ 100.md     # 評価プロンプト
│   ├── elyza-schema.json        # ベーススキーマ
│   ├── rubrics.py               # 問題固有採点ルール
│   └── judge/
│       └── {評価者}/{回答者}/   # 評価結果
│           └── 001.json ～ 100.json
└── 3mt/                     # ja-mt-bench-1shot関連ファイル
    ├── data/
    │   └── 001.md ～ 060.md     # 評価プロンプト
    ├── mt-schema.json           # ベーススキーマ
    └── judge/
        └── {評価者}/{回答者}/   # 評価結果
            └── 001.json ～ 060.json
```

## ツール一覧

**データ準備**
- **analyze_evaluations.py** - shaberi3-evaluations.jsonのデータ構造分析・調査ツール（標準的でないデータ構造の特定と品質確認）
- **dump_questions.py** - shaberi3-evaluations.jsonから3つのベンチマークデータを分類・抽出（Few-shot形式からの質問抽出とベンチマーク識別）

**Tengu Benchmark 関連**
- [1tengu/](1tengu/) - Tengu Benchmark構造化出力評価システム（詳細はREADME参照）

**ELYZA-tasks-100 関連**
- [2elyza/](2elyza/) - ELYZA-tasks-100構造化出力評価システム（詳細はREADME参照）

**ja-mt-bench-1shot 関連**
- [3mt/](3mt/) - ja-mt-bench-1shot構造化出力評価システム（詳細はREADME参照）

**集計・分析**
- **score_tool.py** - 評価結果からスコア統計を集計しYAML形式で出力（分散データの統合管理、list/add/remove サブコマンド対応）
- **analyze_variance.py** - 評価者間分散の詳細分析による構造化出力の効果検証ツール（評価者間分散の定量化）
- **totals_to_csv.py** - 複数の評価結果を集計してCSVファイルに出力（重み付け平均スコア計算）
- **merge_csv.py** - 異なる列順序を持つCSVファイルをマージ（列名ベース統合、標準ライブラリのみ実装）

**補助ツール**
- **get_answer.py** - JSONLファイルから特定行のModelAnswerフィールドを抽出（評価結果の個別確認用）

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
- **主要機能**: 配列長分布分析、異常データの詳細調査、統計的アプローチによる効率化

#### `dump_questions.py` - 質問内容分類・抽出
```bash
uv run dump_questions.py
```
- `shaberi3-evaluations.json`から3つのベンチマークを分類
- tengu_bench (120件)、ELYZA-tasks-100 (100件)、ja-mt-bench-1shot (60件)
- 出力: `1tengu.json`, `2elyza.json`, `3mt.json`
- **主要機能**: 統合データのベンチマーク別分離、Few-shot形式からの質問抽出、コンテンツプレフィックスによる識別

### 2. Tengu Benchmark 関連

詳細は[1tengu/README.md](1tengu/README.md)を参照してください。

### 3. ELYZA-tasks-100 関連

詳細は[2elyza/README.md](2elyza/README.md)を参照してください。

### 4. ja-mt-bench-1shot 関連

詳細は[3mt/README.md](3mt/README.md)を参照してください。

### 5. 集計・分析

#### `score_tool.py` - スコア集計・統合ツール
```bash
# 既存の集計結果を表示
uv run score_tool.py list
uv run score_tool.py list "gemini"         # パターンマッチングで表示

# エントリの削除
uv run score_tool.py remove "gemini-2.0-flash"  # 部分一致で削除

# 全デフォルトパスから自動収集して集計
uv run score_tool.py add

# 特定のディレクトリのみから収集
uv run score_tool.py add --tengu 1tengu    # Tengu Benchのみ
```
- サブコマンド形式（`list`/`add`/`remove`）による直感的な操作
- パターンマッチングによる柔軟な表示・削除機能
- 評価結果からスコア統計を集計してYAML形式で出力
- **主要機能**: 分散評価結果の統合管理、階層的ディレクトリ解析、JSONスコア集計、増分更新機能
- **詳細な使用方法は[score_tool.md](score_tool.md)を参照**

#### `analyze_variance.py` - 評価者間分散分析ツール
```bash
# Tengu Benchmarkの分散分析
uv run analyze_variance.py -b lightblue/tengu_bench
```
- 構造化出力による評価者間分散の減少効果を定量的に分析
- **主要機能**: 評価対象モデル別分析、形式自動判別、統計的指標の包括計算、分散減少率の算出
- **実証結果**: 平均56.4%の分散削減効果（最大87.5%改善）
- **詳細な使用方法は[analyze_variance.md](analyze_variance.md)を参照**

#### `totals_to_csv.py` - 評価結果CSV集計ツール
```bash
# デフォルト設定で実行
uv run totals_to_csv.py

# カスタムディレクトリを指定
uv run totals_to_csv.py ./data/judgements/judge_gemini-2.5-flash
```
- 評価結果を再帰的に検索し、重み付け平均スコアをCSV出力
- **主要機能**: 重み付け平均スコア計算（ELYZA-tasks-100を2倍重み）、階層構造の自動解析
- **詳細な使用方法は[totals_to_csv.md](totals_to_csv.md)を参照**

#### `merge_csv.py` - CSVファイルマージツール
```bash
# 2つのCSVファイルをマージ
uv run merge_csv.py file1.csv file2.csv -o merged.csv

# 複数ファイルを一度にマージ
uv run merge_csv.py *.csv -o all_results.csv
```
- 異なる列順序を持つCSVファイルを列名ベースで統合
- **主要機能**: 列名ベースのマージ、重複除去、列順序の統一、標準ライブラリのみ実装
- **詳細な使用方法は[merge_csv.md](merge_csv.md)を参照**

#### `get_answer.py` - ModelAnswer抽出ツール
```bash
# JSONLファイルの5行目からModelAnswerを抽出
uv run get_answer.py input.jsonl -l 5 -o answer.txt
```
- JSONLファイルから特定行のModelAnswerフィールドを抽出
- **主要機能**: 行番号指定による抽出、ModelAnswerフィールド専用、ファイル出力
- **詳細な使用方法は[get_answer.md](get_answer.md)を参照**


### 5. ja-mt-bench-1shot 構造化出力システム

詳細は[3mt/README.md](3mt/README.md)を参照してください。

## 技術的な改善点

### 従来のFew-shot形式の問題点
1. **計算ミス**: LLMが評価項目の合計点を誤計算
2. **形式不統一**: 出力フォーマットが一貫しない
3. **パース困難**: 自由形式テキストからの情報抽出が複雑
4. **効率低下**: Few-shot例で不要なトークンを消費
5. **評価者間分散**: 同一回答に対する評価者間のスコアばらつき

### 構造化出力による解決
1. **計算精度**: 後処理で確実に合計点を計算
2. **形式保証**: JSONスキーマによる厳密な構造制御
3. **効率処理**: 構造化データの直接利用
4. **トークン節約**: Few-shot例が不要
5. **品質保証**: リアルタイムスキーマ検証による自動品質管理
6. **評価者間一貫性**: 平均56.4%の分散削減を実現（最大87.5%改善）
7. **詳細データ活用**: 項目別評価点と理由付けの構造化による分析精度向上

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
- **対象タスク**: 280件（Tengu Benchmark 120件 + ELYZA-tasks-100 100件 + ja-mt-bench-1shot 60件）
- **成功率**: 100%
- **形式分類**: 
  - Tengu: 単層構造（97件）+ 階層構造（23件）
  - ELYZA: 動的スキーマ生成（judge関数統合）
  - ja-mt-bench: 統一スキーマ（60件）
- **スキーマ生成**: 全280件対応

### パフォーマンス
- **高速処理**: 全ベンチマーク280件を効率的に処理
- **メモリ効率**: ファイル単位での逐次処理
- **エラー耐性**: 1件の失敗が全体に影響しない
- **進捗管理**: tqdmによるリアルタイム進捗表示

## 今後の展開

1. **ベンチマーク対応**: 3つのベンチマーク全て完了済み（Tengu、ELYZA、ja-mt-bench）
2. **API統合拡張**: OpenAI、Anthropic対応
3. **評価精度向上**: 温度調整、プロンプト改良
4. **統計分析拡張**: タスク別難易度分析、項目別パフォーマンス分析
5. **分散分析の高度化**: 効果量計算、信頼区間推定、統計的検定
6. **可視化機能**: ヒストグラム、箱ひげ図、散布図による分散の視覚的比較
7. **自動レポート生成**: Markdown/HTML形式の詳細レポート出力

## 関連ドキュメント

- [CLAUDE.md](../CLAUDE.md): プロジェクト全体概要
- [docs/README.md](docs/README.md): 技術ドキュメント概要
- 各ツールの詳細: `{tool_name}.md`ファイル参照

## まとめ

このツール群により、Shaberi評価フレームワークは従来のFew-shot形式から構造化出力形式への移行を実現し、より精確で効率的な日本語LLM評価システムを構築できます。段階的な実行により、安全かつ確実にシステムを移行できます。

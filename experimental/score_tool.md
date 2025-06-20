# score_tool.py - Shaberi評価結果スコア集計ツール

## 概要

`score_tool.py`は、Shaberi評価フレームワークの構造化出力評価結果から、evaluator/model組み合わせごとのスコア統計を集計し、TOML形式で出力するツールです。tengu.pyで生成された評価結果ディレクトリから個別のスコアデータを読み込み、統合されたスコア集計ファイルを生成します。

## 背景

### 評価結果の分散管理の課題

Shaberi評価フレームワークでは、評価結果が以下のような階層的ディレクトリ構造で管理されています：

```
1tengu/
├── gemini-2.5-flash/           # 評価者モデル
│   ├── gemini-2.5-pro/         # 被評価モデル
│   │   ├── 001.json            # タスク1の評価結果
│   │   ├── 002.json            # タスク2の評価結果
│   │   └── ...                 # 120タスク分
│   └── claude-3-5-sonnet/
│       └── ...
└── gemini-2.5-pro/
    └── ...
```

この構造では、各組み合わせのスコア統計を把握するために：
- 120個のJSONファイルを個別に開く必要がある
- 手動でスコアを合計計算する必要がある
- 複数の組み合わせを比較するのが困難

### 構造化出力による詳細データの活用

tengu.pyの構造化出力により、各評価結果JSONファイルには以下の情報が含まれています：

```json
{
  "answer": "被評価モデルの回答",
  "evaluation": {
    "評価項目1": {
      "points": "3",
      "reasoning": "評価理由"
    },
    ...
  },
  "summary": "評価総括",
  "score": 10
}
```

このうち`score`フィールドは、各タスクの合計点数を示しており、これらを集計することで：
- **total**: 全タスクの合計スコア
- **scores**: 個別タスクのスコア配列

を効率的に算出できます。

## 主要機能

### 1. 階層的ディレクトリ解析

**目的**: evaluator/model の2階層構造からデータを抽出

```python
# basename(dirname)/basename の形式でdir名を作成
parent_path = base_path.parent
dir_name = f"{parent_path.name}/{base_path.name}"
```

**動作例**:
- 入力: `1tengu/gemini-2.5-flash/gemini-2.5-pro`
- 出力: `gemini-2.5-flash/gemini-2.5-pro`

### 2. JSONスコア集計

**処理フロー**:
```python
scores = []
for json_file in sorted(base_path.glob("*.json")):
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    score = data.get('score', 0)
    scores.append(score)
```

**特徴**:
- ファイル名順（001.json → 120.json）での読み込み
- `score`フィールドからの直接取得
- エラー耐性（欠損時は0として扱う）

### 3. TOML形式での統合出力

**出力形式**:
```toml
["evaluator/model"]
total = 合計スコア
scores = [タスク1スコア, タスク2スコア, ...]
```

**具体例**:
```toml
["gemini-2.5-flash/gemini-2.5-pro"]
total = 1061
scores = [10, 10, 10, 10, 10, 10, 7, 10, 10, 10, ...]
```

### 4. 増分更新機能

**目的**: 既存の集計結果に新しいデータを追加・更新

**処理フロー**:
1. 既存の`scores.toml`ファイルを読み込み（存在する場合）
2. 新しいevaluator/model組み合わせのデータを集計
3. 既存データに統合（上書き・追加）
4. 更新されたTOMLファイルを保存

**利点**:
- 段階的なデータ蓄積が可能
- 既存の評価結果を保護
- 新しい組み合わせの追加が効率的

### 5. スコア降順ソート機能

**目的**: モデル性能の比較を容易にする

**実装**:
```python
# スコア（total）の降順でソート
sorted_items = sorted(toml_data.items(), key=lambda x: x[1]['total'], reverse=True)
```

**効果**:
- 最も性能の良いモデル組み合わせが最初に表示
- ファイル出力とコンソール表示の両方で適用
- 性能ランキングが一目で把握可能

### 6. 表示専用機能

**目的**: 既存の集計結果の確認

**実装**:
```python
def display_scores(output_file='scores.toml'):
    # TOMLファイルを読み込み、統計情報を表示
    # 平均スコア（avg）も計算
```

**表示内容**:
- 総組み合わせ数
- 各組み合わせの詳細統計（1行形式: `{total}/{tasks}={avg:.2f} {dir_name}`）
- スコア降順での一覧表示

### 7. 従来評価結果ファイル対応

**目的**: 既存のJSONL形式評価結果ファイルとの統合

**対応ファイル形式**:
```
../data/judgements/judge_evaluator/dataset/model.json
```

**パス解析**:
- `judge_gemini-2.5-flash-preview-05-20/gemini-2.5-pro.json`の形式でdir名生成
- JSONL形式（1行1JSON）からスコア抽出

### 8. 複数パス一括処理

**目的**: 効率的な大量データ処理

**機能**:
- 引数での複数パス指定（`paths1 path2 path3 ...`）
- ファイル/ディレクトリの自動判定
- エラー耐性（1つのパスでエラーが発生しても他を継続処理）
- 統合結果の一括保存

## 使用方法

### 基本的な実行

```bash
# 既存集計結果の表示のみ（引数なし）
uv run score_tool.py

# カスタム出力ファイルの表示
uv run score_tool.py -o my_scores.toml

# 単一の組み合わせを集計
uv run score_tool.py 1tengu/gemini-2.5-flash/gemini-2.5-pro

# 従来の評価結果ファイル（JSONL）を集計
uv run score_tool.py ../data/judgements/judge_gemini-2.5-flash/lightblue__tengu_bench/gemini-2.5-pro.json

# 複数パスの一括集計
uv run score_tool.py 1tengu/gemini-2.5-flash/gemini-2.5-pro 1tengu/gemini-2.5-flash/claude-3-5-sonnet

# 新旧ファイル形式の混在処理
uv run score_tool.py ../data/judgements/judge_*/lightblue__tengu_bench/gemini-2.5-pro.json 1tengu/gemini-2.5-flash/gemini-2.5-pro
```

### 複数ファイル形式対応

```bash
# 構造化出力結果ディレクトリ（1tengu/evaluator/model/）
uv run score_tool.py 1tengu/gemini-2.5-flash/gemini-2.5-pro

# 従来の評価結果ファイル（../data/judgements/judge_evaluator/dataset/model.json）
uv run score_tool.py ../data/judgements/judge_gemini-2.5-flash/lightblue__tengu_bench/gemini-2.5-pro.json

# 複数パスの一括処理
uv run score_tool.py path1 path2 path3 ...

# 段階的集計（既存ファイルに追加）
uv run score_tool.py 1tengu/gemini-2.5-flash/gemini-2.5-pro
uv run score_tool.py ../data/judgements/judge_gemini-2.5-flash/lightblue__tengu_bench/claude-3-5-sonnet.json
# → scores.tomlに両方の結果が蓄積される
```

### 出力例

**表示専用実行**:
```bash
uv run score_tool.py
```
```
スコア統計表示: scores.toml
総組み合わせ数: 10
--------------------------------------------------------------------------------
1097/120=9.14 judge_gemini-2.5-flash-preview-05-20/gemini-2.5-pro-preview-03-25.json
1094/120=9.12 judge_gemini-2.5-flash-preview-05-20/gemini-2.5-pro-preview-06-05.json
1088/120=9.07 gemini-2.5-flash-preview-05-20/gemini-2.5-pro-preview-03-25
1083/120=9.03 gemini-2.5-flash-preview-05-20/gemini-2.5-pro-preview-06-05
1082/120=9.02 judge_gemini-2.5-flash-preview-05-20/gemini-2.5-pro.json
1082/120=9.02 judge_gemini-2.5-flash-preview-05-20/gemini-2.5-pro-preview-05-06.json
1076/120=8.97 gemini-2.5-flash/gemini-2.5-pro-preview-06-05
1074/120=8.95 gemini-2.5-flash/gemini-2.5-pro-preview-03-25
```

**集計実行時のコンソール出力**:
```bash
# 単一ファイル処理
uv run score_tool.py ../data/judgements/judge_gemini-2.5-flash/lightblue__tengu_bench/gemini-2.5-pro.json
```
```
評価結果ファイルを集計中: ../data/judgements/judge_gemini-2.5-flash/lightblue__tengu_bench/gemini-2.5-pro.json
スコア集計結果を scores.toml に保存しました
更新された組み合わせ: 1
ファイル内の総組み合わせ数: 10
--------------------------------------------------------------------------------
1097/120=9.14 judge_gemini-2.5-flash-preview-05-20/gemini-2.5-pro-preview-03-25.json
1094/120=9.12 judge_gemini-2.5-flash-preview-05-20/gemini-2.5-pro-preview-06-05.json
1082/120=9.02 judge_gemini-2.5-flash/gemini-2.5-pro.json
...（降順で全組み合わせ表示）
```

**複数パス処理**:
```bash
uv run score_tool.py 1tengu/gemini-2.5-flash/gemini-2.5-pro ../data/judgements/judge_gemini-2.5-flash/lightblue__tengu_bench/claude-3-5-sonnet.json
```
```
評価結果ディレクトリを集計中: 1tengu/gemini-2.5-flash/gemini-2.5-pro
評価結果ファイルを集計中: ../data/judgements/judge_gemini-2.5-flash/lightblue__tengu_bench/claude-3-5-sonnet.json
合計 2 組み合わせを処理しました
スコア集計結果を scores.toml に保存しました
更新された組み合わせ: 2
ファイル内の総組み合わせ数: 12
...（統合結果表示）
```

**scores.tomlファイル（スコア降順ソート）**:
```toml
["judge_gemini-2.5-flash-preview-05-20/gemini-2.5-pro-preview-03-25.json"]
total = 1097
scores = [10, 10, 10, 10, 10, 10, 7, 2, 10, 4, ...]

["gemini-2.5-flash-preview-05-20/gemini-2.5-pro-preview-03-25"]
total = 1088
scores = [10, 10, 10, 10, 10, 10, 7, 3, 10, 5, ...]

["judge_gemini-2.5-flash/gemini-2.5-pro.json"]
total = 1082
scores = [10, 10, 10, 10, 10, 10, 7, 10, 10, 10, ...]

...（スコア降順で全組み合わせ）
```

## 技術仕様

### 依存関係

**必須ライブラリ**:
```bash
# TOML読み込み（Python 3.10以前のみ）
pip install tomli  # Python 3.11+では組み込みtomllib使用
```

**内部モジュール**:
- `pathlib`: ファイルパス操作
- `json`: JSONファイル読み込み
- `argparse`: コマンドライン引数解析

### ファイル形式

**入力（評価結果JSON）**:
```json
{
  "answer": "モデル回答",
  "evaluation": { "評価項目": {"points": "点数", "reasoning": "理由"} },
  "summary": "評価サマリー",
  "score": 10
}
```

**出力（TOML形式）**:
```toml
["evaluator/model"]
total = 合計点数
scores = [個別スコア配列]
```

### エラーハンドリング

**ファイル関連エラー**:
- ディレクトリ不存在: 空の結果を返す
- JSONファイル不存在: 警告表示、スコア0として扱う
- JSON解析エラー: 警告表示、スコア0として扱う

**TOML関連エラー**:
- 既存ファイル読み込み失敗: 警告表示、新規作成
- ファイル書き込み失敗: エラー表示、処理中断

## 活用シナリオ

### 1. モデル性能比較分析

```bash
# 複数モデルの評価結果を集計
uv run score_tool.py 1tengu/gemini-2.5-flash/gemini-2.5-pro
uv run score_tool.py 1tengu/gemini-2.5-flash/claude-3-5-sonnet
uv run score_tool.py 1tengu/gemini-2.5-flash/gpt-4o

# scores.tomlから平均スコア、標準偏差を分析
```

### 2. 評価者一貫性の検証

```bash
# 同一モデルを異なる評価者で評価
uv run score_tool.py 1tengu/gemini-2.5-flash/target-model
uv run score_tool.py 1tengu/gemini-2.5-pro/target-model
uv run score_tool.py 1tengu/claude-3-5-sonnet/target-model

# 評価者間のスコア分布を比較
```

### 3. タスク別難易度分析

TOMLファイルから`scores`配列を分析することで：
- **易しいタスク**: 多くのモデルが高スコア
- **難しいタスク**: 多くのモデルが低スコア
- **識別力の高いタスク**: モデル間でスコア差が大きい

### 4. 継続的評価監視

```bash
# 新しい評価結果の追加
uv run score_tool.py 1tengu/new-evaluator/new-model

# 既存のscores.tomlに自動統合
# 履歴的な性能追跡が可能
```

## 関連ファイル

### 前段階スクリプト
- **tengu.py**: 構造化出力評価の実行（scoreフィールド生成）
- **validate_schema.py**: 評価結果の品質保証

### 設定ファイル
- **scores.toml**: 出力される統合スコアファイル
- **pyproject.toml**: tomli-w等の依存関係定義

### ドキュメント
- **tengu.md**: 構造化出力評価システムの詳細
- **README.md**: experimental ツール群の全体概要

## 今後の展開

### 統計分析機能の追加

1. **自動統計計算**: 平均、標準偏差、四分位数
2. **可視化出力**: ヒストグラム、箱ひげ図の生成
3. **比較レポート**: モデル間、評価者間の詳細比較

### 他ベンチマークへの対応

1. **ELYZA-tasks-100**: 5段階評価システム対応
2. **ja-mt-bench-1shot**: マルチターン会話評価
3. **汎用拡張**: 任意のベンチマーク形式に対応

### データ分析統合

1. **pandas連携**: DataFrameでの高度な分析
2. **Jupyter Notebook**: 対話的な分析環境
3. **ダッシュボード**: リアルタイム評価監視

## まとめ

`score_tool.py`は、Shaberi評価フレームワークの構造化出力評価結果を効率的に集計・統合するための重要なツールです。

**主要価値**:
- **効率化**: 120個のJSONファイルの手動集計を自動化
- **標準化**: TOML形式による統一的なデータ表現
- **拡張性**: 増分更新による段階的データ蓄積
- **分析支援**: 統計分析・可視化の基盤データ提供

**適用効果**:
- 評価結果の迅速な把握
- モデル性能の定量的比較
- 評価システムの品質管理
- 研究・開発の意思決定支援

この実装により、Shaberi評価フレームワークはより実用的で分析しやすい評価システムへと進化し、日本語LLM研究の効率化に貢献します。

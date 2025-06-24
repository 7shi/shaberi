# score_tool.py - Shaberi評価結果スコア集計ツール

## 概要

`score_tool.py`は、Shaberi評価フレームワークの評価結果から、ベンチマーク別・evaluator/model組み合わせごとのスコア統計を集計し、YAML形式で出力するツールです。新形式の構造化出力（`1tengu/`, `2elyza/`, `3mt/`）と従来のJSONL形式の両方に対応し、ベンチマーク分類による統合されたスコア集計ファイルを生成します。

## 背景

### 評価結果の分散管理の課題

Shaberi評価フレームワークでは、評価結果が以下のような階層的ディレクトリ構造で管理されています：

**新形式**（ベンチマーク別）:
```
1tengu/                             # Tengu Bench
├── gemini-2.5-flash/               # 評価者モデル
│   ├── gemini-2.5-pro/             # 被評価モデル
│   │   ├── 001.json                # タスク1の評価結果
│   │   ├── 002.json                # タスク2の評価結果
│   │   └── ...                     # 120タスク分
│   └── claude-3-5-sonnet/
│       └── ...
└── gemini-2.5-pro/
    └── ...

2elyza/                             # ELYZA-tasks-100
├── gemini-2.5-flash/
│   └── ...

3mt/                                # MT-Bench
├── gemini-2.5-flash/
│   └── ...
```

**従来形式**:
```
../data/judgements/
├── judge_gemini-2.5-flash/
│   ├── lightblue__tengu_bench/
│   │   └── model.json              # JSONL形式
│   └── elyza__ELYZA-tasks-100/
│       └── model.json
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
- 入力: `1tengu/judge/gemini-2.5-flash/gemini-2.5-pro`
- 出力: `gemini-2.5-flash/gemini-2.5-pro`

### 2. JSONスコア集計

**処理フロー**:
```python
scores = []
for json_file in sorted(base_path.glob("*.json")):
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    score = data.get('score', 0)
    scores.append(int(score))  # 整数として処理
```

**特徴**:
- ファイル名順（001.json → 120.json）での読み込み
- `score`フィールドからの直接取得（整数変換）
- エラー耐性（欠損時は0として扱う）

### 3. YAML形式でのベンチマーク分類出力

**出力形式**:
```yaml
benchmark_name:
  evaluator/model:
    total: 合計スコア
    scores: [タスク1スコア, タスク2スコア, ...]  # インライン配列形式で簡潔表示
```

**具体例**:
```yaml
lightblue/tengu_bench:
  gemini-2.5-flash/gemini-2.5-pro:
    total: 1061
    scores: [10, 10, 10, 10, 10, 10, 7, 10, 10, 10, 8, 9, 10, 5, 10, 10, 10, 10, 7, 10, ...]
  gemini-2.5-flash/claude-3-5-sonnet:
    total: 1055
    scores: [9, 10, 8, 10, 10, 10, 6, 9, 10, 10, 7, 8, 10, 4, 10, 10, 9, 10, 6, 9, ...]

elyza/ELYZA-tasks-100:
  gemini-2.5-flash/gemini-2.5-pro:
    total: 485
    scores: [5, 4, 5, 4, 5, 5, 3, 4, 5, 5, 4, 5, 4, 3, 5, 5, 4, 5, 3, 4, ...]
```

### 4. 増分更新機能

**目的**: 既存の集計結果に新しいデータを追加・更新

**処理フロー**:
1. 既存の`scores.yaml`ファイルを読み込み（存在する場合）
2. 新しいベンチマーク/evaluator/model組み合わせのデータを集計
3. 既存データに統合（ベンチマーク別に上書き・追加）
4. 更新されたYAMLファイルを保存

**利点**:
- 段階的なデータ蓄積が可能
- 既存の評価結果を保護
- 新しい組み合わせの追加が効率的

### 5. ベンチマーク別スコア降順ソート機能

**目的**: ベンチマーク別のモデル性能比較を容易にする

**実装**:
```python
# 各ベンチマーク内でスコア（total）の降順でソート
for benchmark_name in sorted(yaml_data.keys()):
    benchmark_data = yaml_data[benchmark_name]
    sorted_items = sorted(benchmark_data.items(), 
                        key=lambda x: x[1]['total'], reverse=True)
    sorted_yaml_data[benchmark_name] = dict(sorted_items)
```

**効果**:
- 最も性能の良いモデル組み合わせが最初に表示
- ファイル出力とコンソール表示の両方で適用
- 性能ランキングが一目で把握可能

### 6. ベンチマーク別表示機能

**目的**: 既存の集計結果の確認とフィルタリング表示

**実装**:
```python
def display_scores(output_file='scores.yaml', patterns=None, benchmark=None, exclude_patterns=None):
    # YAMLファイルを読み込み、ベンチマーク別統計情報を表示
    # パターンマッチングによるフィルタリング対応（包含・除外の両方）
    # 平均スコア（avg）も計算
```

**表示内容**:
- 総組み合わせ数
- ベンチマーク別グループ表示
- 各組み合わせの詳細統計（1行形式: `{total}/{tasks}={avg:.2f} {benchmark}/{evaluator/model}`）
- 各ベンチマーク内でスコア降順一覧
- スコアは整数として表示（例：`1035/120=8.62`）

**フィルタリング機能**:
- パターン指定による部分一致検索（複数パターンのAND条件）
- 除外パターン指定による逆マッチング（grep -v相当、複数指定可能）
- ベンチマーク指定による範囲限定
- `find_matching_entries`共通関数を使用してremoveコマンドと同じ検索ロジックを共有

### 7. 従来評価結果ファイル対応

**目的**: 既存のJSONL形式評価結果ファイルとの統合

**対応ファイル形式**:
```
../data/judgements/judge_evaluator/dataset/model.json
```

**パス解析**:
- `judge_gemini-2.5-flash-preview-05-20/gemini-2.5-pro.json`の形式でdir名生成
- JSONL形式（1行1JSON）からスコア抽出

### 8. サブコマンド体系による直感的な操作

**目的**: より直感的で柔軟な評価結果の収集・表示

**サブコマンド体系**:
- `list`: 既存の集計結果を表示
- `remove`: 部分一致パターンでエントリを削除
- `add`: 評価結果を収集して集計

**引数構造の変更（2025年6月24日更新）**:
- 出力ファイル名は第1引数として指定（オプション、デフォルト: scores.yaml）
- 従来の各サブコマンドの`-o`オプションを廃止し、メインコマンドレベルに統一

**listコマンドの表示オプション**:
- `pattern`: 表示対象パターン（項目名の部分一致、複数指定でAND条件）（任意）
- `-b, --benchmark BENCHMARK`: 指定したベンチマーク内でpatternの部分一致検索を実行
- `-v, --exclude PATTERN`: 除外パターン（grep -v相当、複数指定可能）

**removeコマンドの削除オプション**:
- `pattern`: 削除対象パターン（項目名の部分一致、複数指定でAND条件）（任意）
- `-b, --benchmark BENCHMARK`: 指定したベンチマーク内でpatternの部分一致検索を実行
- `-v, --exclude PATTERN`: 除外パターン（grep -v相当、複数指定可能）
- `-f, --force`: 確認なしで削除を実行

**addコマンドのディレクトリ指定オプション**:
- `-j DIR`, `--judgements-dir DIR`: 従来形式の評価結果ディレクトリを指定
- `--tengu DIR`: Tengu Benchの評価結果ディレクトリを指定
- `--elyza DIR`: ELYZA-tasks-100の評価結果ディレクトリを指定
- `--mt DIR`: MT-Benchの評価結果ディレクトリを指定

**デフォルト動作**:
- `add`コマンドでオプション未指定時は全デフォルトパスを自動試行
  - `../data/judgements` (従来形式)
  - `1tengu/judge` (Tengu Bench)
  - `2elyza/judge` (ELYZA-tasks-100)
  - `3mt/judge` (MT-Bench)

**重要な仕様変更**:
- サブコマンド未指定時はヘルプメッセージを表示してエラー終了
- 明示的な`list`または`add`サブコマンドの指定が必須

## 使用方法

### 基本的な実行

```bash
# サブコマンド未指定時はヘルプを表示
uv run score_tool.py
# → ヘルプメッセージが表示され、エラー終了

# 既存集計結果の表示（デフォルト: scores.yaml）
uv run score_tool.py list                                         # 全エントリを表示
uv run score_tool.py list "gemini"                                # geminiを含むエントリのみ表示
uv run score_tool.py list "judge_gpt" "gemini"                    # judge_gptとgeminiの両方を含むエントリのみ表示
uv run score_tool.py list -b "lightblue/tengu_bench" "gemini"     # 指定ベンチマーク内でgeminiを含むエントリのみ表示
uv run score_tool.py list "gemini-2.5-pro" -v "preview"           # gemini-2.5-proを含み、previewを含まないエントリ
uv run score_tool.py list "gemini" -v "preview" -v "lite"         # geminiを含み、previewとliteを含まないエントリ

# カスタム出力ファイルの表示
uv run score_tool.py my_scores.yaml list

# 部分一致パターンでエントリを削除
uv run score_tool.py remove "gemini-2.0-flash"                    # 全ベンチマークから項目名の部分一致
uv run score_tool.py remove "judge_gpt" "gemini"                  # AND条件：judge_gptとgeminiの両方を含む項目
uv run score_tool.py remove -b "lightblue/tengu_bench" "gemini"   # 指定ベンチマーク内での部分一致
uv run score_tool.py remove "gemini" -v "preview" -v "lite"       # geminiを含み、previewとliteを含まないエントリを削除
uv run score_tool.py my_scores.yaml remove "pattern"              # カスタムファイルでエントリ削除

# 全デフォルトパスから自動収集して集計
uv run score_tool.py add
uv run score_tool.py my_scores.yaml add                           # カスタムファイルに集計

# 特定のディレクトリのみから収集
uv run score_tool.py add -j ../data/judgements                    # 従来形式のみ
uv run score_tool.py add --tengu 1tengu/judge                     # Tengu Benchのみ
uv run score_tool.py add --elyza 2elyza/judge                     # ELYZA-tasks-100のみ
uv run score_tool.py add --mt 3mt/judge                           # MT-Benchのみ

# カスタムディレクトリから収集
uv run score_tool.py add --tengu /custom/tengu
uv run score_tool.py my_scores.yaml add -j /custom/judgements --elyza /custom/elyza

# 複数ディレクトリを同時指定
uv run score_tool.py add -j ../data/judgements --tengu 1tengu/judge --elyza 2elyza/judge
```

### ベンチマーク別収集の詳細

```bash
# Tengu Benchのみ収集（新形式）
uv run score_tool.py add --tengu 1tengu/judge
# → 1tengu/judge/ ディレクトリから evaluator/model を自動検索

# ELYZA-tasks-100のみ収集（新形式）
uv run score_tool.py add --elyza 2elyza/judge
# → 2elyza/judge/ ディレクトリから evaluator/model を自動検索

# MT-Benchのみ収集（新形式）
uv run score_tool.py add --mt 3mt/judge
# → 3mt/judge/ ディレクトリから evaluator/model を自動検索

# 従来形式のみ収集
uv run score_tool.py add -j ../data/judgements
# → ../data/judgements/judge_*/dataset/model.json を自動検索

# 段階的集計（既存ファイルに追加）
uv run score_tool.py add --tengu 1tengu/judge     # Tengu Benchを追加
uv run score_tool.py add --elyza 2elyza/judge     # ELYZA-tasks-100を追加
# → scores.yamlに両方の結果がベンチマーク別に蓄積される

# カスタムファイルでの集計
uv run score_tool.py tengu-only.yaml add --tengu 1tengu/judge      # Tengu Benchのみ
uv run score_tool.py elyza-only.yaml add --elyza 2elyza/judge      # ELYZA-tasks-100のみ

# 特定のエントリを削除
uv run score_tool.py remove "gemini-2.0-flash"                     # 全ベンチマークから項目名の部分一致
uv run score_tool.py remove "judge_gpt" "gemini"                   # AND条件：judge_gptとgeminiの両方を含む項目
uv run score_tool.py remove -b "lightblue/tengu_bench"             # 指定ベンチマーク全体を削除
uv run score_tool.py remove -b "lightblue/tengu_bench" "gemini" --force  # 指定ベンチマーク内での部分一致
uv run score_tool.py my_scores.yaml remove "pattern"               # カスタムファイルでの削除
```

### 出力例

**表示専用実行（デフォルトファイル）**:
```bash
# 全エントリを表示
uv run score_tool.py list
```
```
[lightblue/tengu_bench]
1097/120=9.14 judge_gemini-2.5-flash/gemini-2.5-pro.json
1094/120=9.12 judge_gemini-2.5-flash/claude-3-5-sonnet.json
1088/120=9.07 judge_gemini-2.5-pro/gemini-2.5-pro.json

[elyza/ELYZA-tasks-100]
 485/100=4.85 judge_gemini-2.5-flash/gemini-2.5-pro.json
 480/100=4.80 judge_gemini-2.5-flash/claude-3-5-sonnet.json

[shisa-ai/ja-mt-bench-1shot]
 585/60=9.75 judge_gemini-2.5-flash/gemini-2.5-pro.json
 580/60=9.67 judge_gemini-2.5-flash/claude-3-5-sonnet.json

総組み合わせ数: 15
```

**フィルタリング表示**:
```bash
# geminiを含むエントリのみ表示
uv run score_tool.py list "gemini"
```
```
[lightblue/tengu_bench]
1097/120=9.14 judge_gemini-2.5-flash/gemini-2.5-pro.json
1088/120=9.07 judge_gemini-2.5-pro/gemini-2.5-pro.json

[elyza/ELYZA-tasks-100]
 485/100=4.85 judge_gemini-2.5-flash/gemini-2.5-pro.json

[shisa-ai/ja-mt-bench-1shot]
 585/60=9.75 judge_gemini-2.5-flash/gemini-2.5-pro.json

総組み合わせ数: 4
```

**除外パターンによるフィルタリング**:
```bash
# gemini-2.5-proを含み、previewを除外
uv run score_tool.py list -b "lightblue/tengu_bench" "gemini-2.5-pro" -v "preview"
```
```
[lightblue/tengu_bench]
1111/120=9.26 judge_gpt-4.1-mini/gemini-2.5-pro.json
1091/120=9.09 judge_gemini-2.0-flash/gemini-2.5-pro.json
1087/120=9.06 judge_gemini-2.5-pro/gemini-2.5-pro.json
1082/120=9.02 judge_gemini-2.5-flash/gemini-2.5-pro.json

総組み合わせ数: 4
```

**集計実行時のコンソール出力**:
```bash
# Tengu Benchのみ収集
uv run score_tool.py add --tengu 1tengu/judge
```
```
1tengu/judge から 8 個のTengu Bench評価結果ディレクトリを発見
評価結果ディレクトリを集計中: 1tengu/gemini-2.5-flash/gemini-2.5-pro
評価結果ディレクトリを集計中: 1tengu/gemini-2.5-flash/claude-3-5-sonnet
...
合計 8 組み合わせを処理しました
スコア集計結果を scores.yaml に保存しました
更新された組み合わせ: 8
ファイル内の総組み合わせ数: 8
```

**全ベンチマーク処理**:
```bash
uv run score_tool.py add
```
```
../data/judgements から 15 個の従来形式評価結果ファイルを発見
1tengu/judge から 8 個のTengu Bench評価結果ディレクトリを発見
2elyza/judge から 6 個のELYZA-tasks-100評価結果ディレクトリを発見
3mt/judge から 4 個のMT-Bench評価結果ディレクトリを発見
合計 33 組み合わせを処理しました
スコア集計結果を scores.yaml に保存しました
更新された組み合わせ: 33
ファイル内の総組み合わせ数: 33
```

**scores.yamlファイル（ベンチマーク別・スコア降順ソート）**:
```yaml
lightblue/tengu_bench:
  gemini-2.5-flash/gemini-2.5-pro:
    total: 1097
    scores: [10, 10, 10, 10, 10, 10, 7, 2, 10, 4, 8, 9, 10, 5, 10, 10, 10, 10, 7, 10, 8, 9, 10, 5, 10, 10, ...]
  gemini-2.5-flash/claude-3-5-sonnet:
    total: 1094
    scores: [10, 10, 10, 10, 10, 10, 7, 3, 10, 5, 7, 8, 10, 4, 10, 10, 9, 10, 6, 9, 7, 8, 10, 4, 10, 10, ...]

elyza/ELYZA-tasks-100:
  gemini-2.5-flash/gemini-2.5-pro:
    total: 485
    scores: [5, 4, 5, 4, 5, 5, 3, 4, 5, 5, 4, 5, 4, 3, 5, 5, 4, 5, 3, 4, 5, 4, 5, 4, 5, 5, ...]
  gemini-2.5-flash/claude-3-5-sonnet:
    total: 480
    scores: [5, 4, 4, 4, 5, 5, 3, 4, 5, 4, 3, 4, 4, 3, 5, 5, 3, 5, 2, 4, 5, 4, 4, 4, 5, 5, ...]

shisa-ai/ja-mt-bench-1shot:
  gemini-2.5-flash/gemini-2.5-pro:
    total: 585
    scores: [10, 10, 9, 10, 10, 10, 8, 9, 10, 10, 9, 8, 10, 7, 10, 10, 9, 10, 8, 9, 10, 10, 9, 8, 10, 7, ...]
```

## 技術仕様

### 依存関係

**必須ライブラリ**:
```bash
# YAML読み書き
uv add pyyaml
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

**出力（YAML形式）**:
```yaml
benchmark_name:
  evaluator/model:
    total: 合計点数
    scores: [個別スコア配列]  # インライン配列形式で大幅に圧縮
```

### エラーハンドリング

**ファイル関連エラー**:
- ディレクトリ不存在: 空の結果を返す
- JSONファイル不存在: 警告表示、スコア0として扱う
- JSON解析エラー: 警告表示、スコア0として扱う

**データ型処理**:
- スコア値は整数に変換（`int(score)`）して処理
- 浮動小数点数での保存を防止し、表示時の一貫性を確保

**YAML関連エラー**:
- 既存ファイル読み込み失敗: 警告表示、新規作成
- ファイル書き込み失敗: エラー表示、処理中断

## 活用シナリオ

### 1. モデル性能比較分析

```bash
# 複数モデルの評価結果を集計
uv run score_tool.py add --tengu 1tengu/judge     # Tengu Benchのみ
uv run score_tool.py add --elyza 2elyza/judge     # ELYZA-tasks-100のみ
uv run score_tool.py add --mt 3mt/judge           # MT-Benchのみ

# scores.yamlからベンチマーク別の平均スコア、標準偏差を分析
```

### 2. 評価者一貫性の検証

```bash
# 全ベンチマークから同一モデルの評価結果を収集
uv run score_tool.py add

# scores.yamlから同一モデルの評価者間・ベンチマーク間のスコア分布を比較
```

### 3. タスク別難易度分析

YAMLファイルの各ベンチマークから`scores`配列を分析することで：
- **易しいタスク**: 多くのモデルが高スコア
- **難しいタスク**: 多くのモデルが低スコア
- **識別力の高いタスク**: モデル間でスコア差が大きい
- **ベンチマーク間の難易度比較**: 同一モデルのベンチマーク間スコア差

### 4. 継続的評価監視

```bash
# 新しい評価結果の追加
uv run score_tool.py add  # 全ベンチマークを再収集

# 既存のscores.yamlに自動統合
# ベンチマーク別の履歴的性能追跡が可能
```

## 関連ファイル

### 前段階スクリプト
- **tengu.py**: 構造化出力評価の実行（scoreフィールド生成）
- **validate_schema.py**: 評価結果の品質保証

### 設定ファイル
- **scores.yaml**: 出力される統合スコアファイル
- **pyproject.toml**: PyYAML等の依存関係定義
- **evaluation_datasets_config.py**: ベンチマーク定義とマッピング

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
- **効率化**: 複数ベンチマークの大量JSONファイル手動集計を自動化
- **標準化**: YAML形式によるベンチマーク分類データ表現
- **拡張性**: ベンチマーク別増分更新による段階的データ蓄積
- **分析支援**: ベンチマーク横断的な統計分析・可視化の基盤データ提供
- **新形式対応**: 1tengu/, 2elyza/, 3mt/の新ディレクトリ構造に完全対応
- **直感的フィルタリング**: grep風の除外パターン指定による柔軟なデータ抽出

**適用効果**:
- 評価結果の迅速な把握
- モデル性能の定量的比較
- 評価システムの品質管理
- 研究・開発の意思決定支援

この実装により、Shaberi評価フレームワークはより実用的で分析しやすい評価システムへと進化し、日本語LLM研究の効率化に貢献します。

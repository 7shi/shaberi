# add_scores.py - 評価結果へのスコアフィールド追加ツール

## 概要

`add_scores.py`は、既存のTengu Benchmark評価結果JSONファイルに`score`フィールドを追加するためのユーティリティスクリプトです。`tengu.py`の機能拡張により新たに追加された`score`フィールドを、過去に生成された評価結果にも遡及的に適用できます。

## 背景

### 問題の発生

`tengu.py`の開発過程において、以下の進化がありました：

1. **初期実装**: 評価結果にはモデルの回答（`answer`）と評価内容（`evaluation`、`summary`）のみを保存
2. **機能拡張**: 合計得点の即座の確認ニーズから`score`フィールドを追加

この結果、異なる時期に生成された評価結果ファイルに以下の不整合が発生：

```json
// 旧形式（scoreなし）
{
  "answer": "モデルの回答内容",
  "evaluation": { ... },
  "summary": "評価サマリー"
}

// 新形式（scoreあり）
{
  "answer": "モデルの回答内容",
  "evaluation": { ... },
  "summary": "評価サマリー",
  "score": 10
}
```

### 解決の必要性

1. **データ整合性**: 全評価結果の形式統一
2. **分析効率化**: スコアの即時取得による集計処理の高速化
3. **互換性維持**: 新旧両形式を扱うツールとの連携

## 機能詳細

### 基本動作

1. 指定ディレクトリ内のJSONファイルを検索
2. 各ファイルの`score`フィールド有無を確認
3. 不足している場合は`evaluation`から合計点を計算して追加
4. ファイルを更新（または更新内容を表示）

### スコア計算ロジック

```python
def calculate_score(result_json):
    total = 0
    evaluation = result_json.get("evaluation", {})
    
    for criterion, data in evaluation.items():
        points = int(data.get("points", "0"))
        total += points
    
    return total
```

`tengu.py`と同一の計算ロジックを使用し、一貫性を保証。

## 使用方法

### 基本的な使用

```bash
# 特定の評価結果ディレクトリを処理
uv run add_scores.py judge/gemini-2.5-flash/gemini-2.5-pro

# 処理結果の例
対象ファイル数: 120
処理中: 100%|████████████████████████████████| 120/120 [00:02<00:00, 50.00it/s]

処理完了:
  - 変更済み: 85件
  - score既存: 35件
```

### ドライランモード

実際の変更なしに処理内容を確認：

```bash
uv run add_scores.py judge/gemini-2.5-flash/gemini-2.5-pro --dry-run

# 出力例
対象ファイル数: 120
ドライランモード: ファイルは変更されません

追加予定: judge/gemini-2.5-flash/gemini-2.5-pro/001.json (score=10)
追加予定: judge/gemini-2.5-flash/gemini-2.5-pro/002.json (score=8)
...

処理完了:
  - 変更予定: 85件
  - score既存: 35件

実際にファイルを変更するには、--dry-runオプションを外して再実行してください
```

### 再帰的処理

サブディレクトリも含めて処理：

```bash
# judge以下の全評価結果を一括処理
uv run add_scores.py judge --recursive

# 処理対象の例
judge/
├── gemini-2.5-flash/
│   ├── claude-3-5-sonnet/
│   │   ├── 001.json
│   │   └── ...
│   └── gemini-2.5-pro/
│       ├── 001.json
│       └── ...
└── gemini-2.5-pro/
    └── ...
```

## 技術仕様

### コマンドライン引数

- `directory`: 処理対象のディレクトリパス（必須）
- `--dry-run`: 実際の変更を行わず、処理内容を表示
- `--recursive`, `-r`: サブディレクトリも再帰的に処理

### エラーハンドリング

1. **ファイル読み込みエラー**: エラーメッセージを表示して継続
2. **JSON解析エラー**: 該当ファイルをスキップ
3. **ディレクトリ検証**: 存在確認とディレクトリ判定

### パフォーマンス考慮

- tqdmによる進捗表示で長時間処理の可視化
- ファイルパスのソートにより予測可能な処理順序
- 必要なファイルのみを更新（score既存は読み込みのみ）

## 実行例

### ケース1: 部分的な移行

```bash
# 特定モデルの評価結果のみ更新
uv run add_scores.py judge/gemini-2.5-flash/claude-3-5-sonnet

処理完了:
  - 変更済み: 120件
  - score既存: 0件
```

### ケース2: 混在環境での実行

```bash
# 新旧混在ディレクトリの処理
uv run add_scores.py judge/gemini-2.5-flash/mixed-results

処理完了:
  - 変更済み: 45件
  - score既存: 75件
```

### ケース3: エラー処理

```bash
# 破損ファイルを含むディレクトリ
uv run add_scores.py judge/corrupted-data

Error processing judge/corrupted-data/broken.json: Expecting value: line 1 column 1 (char 0)

処理完了:
  - 変更済み: 98件
  - score既存: 20件
  - エラー: 2件
```

## 注意事項

### データ整合性

- 元のファイルは上書きされるため、必要に応じてバックアップを推奨
- JSONの整形（indent=2）により、ファイルサイズがわずかに増加する可能性

### 実行タイミング

- `tengu.py`の新バージョン移行後、既存データの更新時に実行
- 定期的な実行は不要（一度の実行で完了）

### 互換性

- Python 3.6以上
- 必要なライブラリ: `tqdm`（進捗表示用）

## 関連ファイル

- `tengu.py`: 評価実行スクリプト（score計算ロジックの参照元）
- `tengu.md`: Tengu Benchmark評価システムのドキュメント
- `judge/`: 評価結果の保存ディレクトリ

## まとめ

`add_scores.py`は、評価システムの進化に伴うデータ形式の不整合を解消するための移行ツールです。安全性（ドライラン）と効率性（再帰処理、進捗表示）を両立し、大量の評価結果ファイルを確実に更新できます。

このツールにより、新旧すべての評価結果が統一された形式となり、後続の分析処理やレポート生成がより効率的に実行できるようになります。

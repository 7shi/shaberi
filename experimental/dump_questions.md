# dump_questions.py - 質問内容分類・抽出スクリプト

## 概要

このスクリプトは、Shaberi評価フレームワークの`shaberi3-evaluations.json`ファイルから、3つの異なるベンチマークの質問内容を分類・抽出して個別のJSONLファイルに出力するツールです。

## 背景

Shaberi（しゃべり）は日本語LLMの評価フレームワークで、複数のベンチマークを統合した評価セット「shaberi3」を提供しています。この評価セットには以下の3つのベンチマークが含まれています：

1. **lightblue/tengu_bench** (120件) - Few-shot形式の総合的な日本語能力評価
2. **elyza/ELYZA-tasks-100** (100件) - タスク特化型評価（5段階評価）
3. **shisa-ai/ja-mt-bench-1shot** (60件) - マルチターン会話能力（品質評価）

`shaberi3-evaluations.json`は、これら3つのベンチマークの評価タスクが混在した形で280件（120+100+60）のデータを含んでいます。

## データ構造の理解

### 入力データ形式

元のJSONLファイルは1行1JSONの形式で、各行は`line_data`というリスト形式になっています。リストの長さによって2つのタイプに分類されます：

- **長さ4**: tengu_bench (Few-shot形式)
- **長さ2**: ELYZA-tasks-100 + ja-mt-bench-1shot (シンプル形式)

### データ構造の詳細

#### tengu_bench (Few-shot形式)
```json
[
  {"role": "system", "content": "システムプロンプト"},
  {"role": "user", "content": "Few-shot例の評価指示"},
  {"role": "assistant", "content": "Few-shot例の模範回答"},
  {"role": "user", "content": "実際の評価タスク"}  ← これを抽出
]
```

#### ELYZA-tasks-100 / ja-mt-bench-1shot (シンプル形式)
```json
[
  {"role": "system", "content": "システムプロンプト"},
  {"role": "user", "content": "評価指示"}  ← これを抽出
]
```

## 分類ロジック

スクリプトは以下の条件で3つのベンチマークを自動分類します：

1. **構造による一次分類**：
   - `len(line_data) == 4` → tengu_bench
   - `len(line_data) == 2` → ELYZA または ja-mt-bench

2. **内容による二次分類**（長さ2の場合）：
   - 内容が `"あなたは採点者です。"` で始まる → ELYZA-tasks-100
   - 内容が `"[指示]\n公平な判断者として行動し"` で始まる → ja-mt-bench-1shot

## 出力ファイル

スクリプトは以下の3つのJSONLファイルを生成します：

- **1tengu.json**: 120件のtengu_bench質問
- **2elyza.json**: 100件のELYZA-tasks-100質問  
- **3mt.json**: 60件のja-mt-bench-1shot質問

### 出力形式

各ファイルはJSONL（JSON Lines）形式で、1行に1つの質問文字列が記録されます：

```
"質問内容1"
"質問内容2"
"質問内容3"
...
```

## 使用方法

```bash
uv run dump_questions.py
```

### 前提条件

- `shaberi3-evaluations.json`が同じディレクトリに存在すること
- Python 3.6以上

### 実行結果例

```
Dumped 120 questions to 1tengu.json
Dumped 100 questions to 2elyza.json
Dumped 60 questions to 3mt.json

Summary:
  tengu: 120 questions
  elyza: 100 questions
  mt: 60 questions
  Total: 280 questions
```

## 活用場面

このスクリプトで分類された質問データは、以下のような用途に活用できます：

1. **個別ベンチマークの分析**: 各ベンチマークの質問傾向や特徴の把握
2. **カスタム評価セットの構築**: 特定のベンチマークのみを使用した評価
3. **質問内容の検証**: 各ベンチマークの質問品質や重複の確認
4. **構造化出力への移行**: Few-shot形式からJSONスキーマベースの評価への変換準備

## 技術的詳細

- **言語**: Python 3
- **依存関係**: 標準ライブラリのみ（json, os, pathlib）
- **エラーハンドリング**: JSONパースエラーやキー不足エラーを適切に処理
- **出力エンコーディング**: UTF-8、日本語文字の適切な処理

## 関連ドキュメント

- [20250619-evaluations.md](docs/20250619-evaluations.md): shaberi3-evaluations.jsonの詳細分析
- [20250619-schema.md](docs/20250619-schema.md): 構造化出力への移行手順
- [CLAUDE.md](../CLAUDE.md): Shaberiプロジェクト全体の概要

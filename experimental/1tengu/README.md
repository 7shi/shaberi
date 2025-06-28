# 1tengu - Tengu Benchmark構造化出力評価システム

## 概要

このディレクトリには、Tengu Benchmarkの評価をFew-shot形式から構造化出力（JSONスキーマ）形式に移行するためのツール群が含まれています。120件の日本語タスクに対して、LLM-as-a-Judge手法による自動評価を構造化出力で実行します。

**注**: このREADMEでは各ツールの代表的なコマンド例のみを掲載しています。詳細な使用方法やオプションについては、各ツールのドキュメント（`{tool_name}.md`）を参照してください。

## ファイル構成

```
1tengu/
├── data/
│   ├── 001.md ～ 120.md     # 評価プロンプト
│   └── 001.json ～ 120.json # JSONスキーマ
├── judge/
│   └── {評価者モデル}/
│       └── {回答者モデル}/
│           └── 001.json ～ 120.json  # 評価結果
├── tengu.py                 # メイン評価システム
├── tengu-000.py             # 単一タスクテストスクリプト
├── conv_tengu.py            # データ抽出・変換
├── check_criteria.py        # 評価項目形式検証
├── md_to_schema.py          # JSONスキーマ生成
├── validate_schema.py       # スキーマ準拠性検証
├── add_scores.py            # スコアフィールド追加
├── llm7shi/compat/          # LLM API統合レイヤー
└── *.md                     # 各ツールのドキュメント
```

## ツール一覧

### コア機能

- **llm7shi.compat** - LLM API統合レイヤー（OpenAI/Gemini統一インターフェース）
- **tengu.py** - メイン評価システム（構造化出力による自動評価実行）
- **tengu-000.py** - 単一タスクテストスクリプト

### データ準備

- **conv_tengu.py** - shaberi3-evaluations.jsonからTengu Benchmarkデータを抽出・変換
- **check_criteria.py** - 120件の評価項目形式を自動検証
- **md_to_schema.py** - 評価プロンプトからJSONスキーマを自動生成

### 検証・補助

- **validate_schema.py** - 生成された評価結果のスキーマ準拠性を検証
- **add_scores.py** - 過去の評価結果に合計スコアを後付け計算

**注**: これらのツールは仕様変更に伴う調整用のもので、通常の評価フローでは使用しません。

## 使用手順

### 1. 環境設定
```bash
export GOOGLE_API_KEY="your-gemini-api-key"  # Gemini使用時
export OPENAI_API_KEY="your-openai-api-key"  # OpenAI使用時
```

### 2. データ準備（初回のみ）
```bash
# 評価データの抽出
uv run conv_tengu.py

# JSONスキーマの生成
uv run md_to_schema.py
```

### 3. 評価実行

#### `tengu.py` - 構造化出力評価の実行
```bash
# 1件のみテスト実行
uv run tengu.py ../../data/model_answers/lightblue__tengu_bench/shisa-v1-llama3-8b.json -n 1

# 全120件を評価
uv run tengu.py ../../data/model_answers/lightblue__tengu_bench/shisa-v1-llama3-8b.json --all

# 特定の評価モデルを使用
uv run tengu.py ../../data/model_answers/lightblue__tengu_bench/gpt-4o.json --all -m gpt-4.1-mini

# 温度調整リトライを無効化（o4-miniでの使用例）
uv run tengu.py ../../data/model_answers/lightblue__tengu_bench/gpt-4o.json --all -m o4-mini -st -1
```

### 4. 結果検証

#### `validate_schema.py` - 評価結果の検証
```bash
uv run validate_schema.py judge/gpt-4o-mini/shisa-v1-llama3-8b
```

## 技術設計

### 構造化出力による課題解決

**従来のFew-shot形式の問題点**:
- LLMの計算ミス、出力形式不安定、パース処理複雑、トークン浪費

**構造化出力による解決**:
- 計算精度向上、形式統一、効率処理、コスト最適化

### データフロー

```
評価対象モデル回答 → タスクファイル読み込み → LLM評価 → 構造化JSON出力
                   (プロンプト + スキーマ)    (自動スコア計算)
```

### 評価結果形式

```json
{
  "answer": "評価対象の回答",
  "evaluation": {
    "評価項目名": {
      "points": "3",
      "reasoning": "評価理由"
    }
  },
  "summary": "総合評価コメント",
  "score": 10
}
```

詳細な使用方法は各ツールのドキュメント（`{tool_name}.md`）を参照してください。

## 主要な改善効果

1. **計算精度**: 後処理で確実に合計点を計算（LLMの計算ミスを排除）
2. **形式保証**: JSONスキーマによる厳密な構造制御
3. **効率処理**: 構造化データの直接利用
4. **トークン節約**: Few-shot例が不要
5. **品質保証**: リアルタイムスキーマ検証

## 関連ドキュメント

各ツールの詳細な使用方法：
- [llm7shi.compat](https://pypi.org/project/llm7shi/) - LLM API統合レイヤーの詳細
- [tengu.md](tengu.md) - メイン評価システムの詳細
- [tengu-000.md](tengu-000.md) - 単一タスクテストの詳細
- [conv_tengu.md](conv_tengu.md) - データ抽出・変換の詳細
- [md_to_schema.md](md_to_schema.md) - スキーマ生成の詳細
- [validate_schema.md](validate_schema.md) - スキーマ検証の詳細

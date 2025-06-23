# 1tengu - Tengu Benchmark構造化出力評価システム

## 概要

このディレクトリには、Tengu Benchmarkの評価をFew-shot形式から構造化出力（JSONスキーマ）形式に移行するためのツール群が含まれています。120件の日本語タスクに対して、LLM-as-a-Judge手法による自動評価を構造化出力で実行します。

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
├── llm.py                    # LLM API統合レイヤー
├── tengu.py                  # メイン評価システム
├── tengu-000.py             # 単一タスクテストスクリプト
└── その他の補助ツール
```

## 主要コンポーネント

### コア機能

#### `llm.py` - LLM API統合レイヤー
- OpenAI APIとGemini APIの統一インターフェース
- モデル名による自動API判別（`gemini-*` → Gemini、その他 → OpenAI）
- シンプルなcontents配列とシステムプロンプト分離形式
- ストリーミング出力対応（OpenAI）
- 詳細は[llm.md](llm.md)を参照

#### `tengu.py` - メイン評価システム
```bash
# 基本的な使用例
uv run tengu.py ../../data/model_answers/lightblue__tengu_bench/model.json -n 1
```
- リアルタイムスキーマ検証機能統合
- 温度調整リトライ機能内蔵（`generate_with_temperature_retry`）
- 詳細は[tengu.md](tengu.md)を参照

#### `tengu-000.py` - 単一タスクテスト
```bash
uv run tengu-000.py
```
- 「急がば回れ」の説明タスクで構造化出力をテスト
- 詳細は[tengu-000.md](tengu-000.md)を参照

### データ準備ツール

#### `conv_tengu.py` - JSON→Markdown変換
```bash
uv run conv_tengu.py
```
- 詳細は[conv_tengu.md](conv_tengu.md)を参照

#### `check_criteria.py` - 評価項目形式検証
```bash
uv run check_criteria.py
```
- 120件の評価項目形式を自動検証

#### `md_to_schema.py` - Markdown→JSONスキーマ変換
```bash
uv run md_to_schema.py
```
- 詳細は[md_to_schema.md](md_to_schema.md)を参照

### 検証・補助ツール

#### `validate_schema.py` - 評価結果スキーマ検証
```bash
uv run validate_schema.py judge/gemini-2.5-flash/gemini-2.5-pro
```
- 詳細は[validate_schema.md](validate_schema.md)を参照

#### `add_scores.py` - 過去データのスコア追加
```bash
uv run add_scores.py judge/gemini-2.5-flash/gemini-2.5-pro
```
- 過去の評価結果に`score`フィールドを追加

## 使用手順

### 1. 環境設定
```bash
# 必要な環境変数
export GOOGLE_API_KEY="your-gemini-api-key"  # Gemini使用時
export OPENAI_API_KEY="your-openai-api-key"  # OpenAI使用時
```

### 2. データ準備（初回のみ）
```bash
# 評価プロンプトとスキーマの生成
uv run conv_tengu.py
uv run check_criteria.py
uv run md_to_schema.py
```

### 3. 評価実行
```bash
# 基本的な評価実行
uv run tengu.py ../../data/model_answers/lightblue__tengu_bench/model.json -n 1
```
詳細なコマンドオプションは各ツールのドキュメントを参照してください。

## 技術的特徴

### 構造化出力の利点
1. **計算精度**: 後処理で確実に合計点を計算（LLMの計算ミスを排除）
2. **形式保証**: JSONスキーマによる厳密な構造制御
3. **効率処理**: 構造化データの直接利用
4. **トークン節約**: Few-shot例が不要
5. **品質保証**: リアルタイムスキーマ検証

### 出力形式
```json
{
  "evaluation": {
    "評価項目名": {
      "points": "3",
      "reasoning": "評価理由の説明"
    }
  },
  "summary": "評価の総括",
  "score": 10
}
```

### マルチLLM対応
- **Gemini API**: `gemini-2.5-flash`、`gemini-2.5-pro`など
- **OpenAI API**: `gpt-4.1-mini`、`gpt-4o`など
- モデル名で自動判別、統一インターフェース

## 実績

- **対象タスク**: 120件（Tengu Benchmark）
- **成功率**: 100%
- **形式分類**: 単層構造（97件）+ 階層構造（23件）
- **対応API**: OpenAI、Gemini（llm.py経由）

## 関連ドキュメント

- [llm.md](llm.md): LLM API統合レイヤーの設計詳細
- [tengu.md](tengu.md): メイン評価システムの詳細仕様
- [tengu-000.md](tengu-000.md): 単一タスクテストの詳細
- [conv_tengu.md](conv_tengu.md): JSON→Markdown変換の説明
- [md_to_schema.md](md_to_schema.md): スキーマ生成の詳細
- [validate_schema.md](validate_schema.md): スキーマ検証の仕様

## 今後の展開

1. **温度調整最適化**: 評価の一貫性向上
2. **バッチ処理効率化**: 並列処理の実装
3. **統計分析機能**: タスク別難易度分析
4. **他ベンチマーク対応**: ELYZA-tasks-100、ja-mt-bench-1shotへの展開
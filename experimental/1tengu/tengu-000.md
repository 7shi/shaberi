# tengu-000.py - 構造化出力評価システム実証スクリプト

## 概要

`tengu-000.py`は、Tengu Benchmark評価タスクにおいて、構造化出力（JSONスキーマ）形式による評価を実証するテストスクリプトです。OpenAI APIとGemini APIの両方に対応し、日本語諺「急がば回れ」の説明に関する評価タスクを実行して、構造化出力の有効性を検証します。

## 関連ファイル一覧

### メインスクリプト
- **tengu-000.py**: 実装版スクリプト（OpenAI/Gemini両対応）
- **tengu-000-base.py**: 基本版スクリプト（学習・テスト用の簡素版）

### 入力ファイル
- **tengu-000-user.md**: 評価指示プロンプト（評価タスクの詳細な指示文）
- **tengu-000-schema.json**: 構造化出力用JSONスキーマ（出力形式の定義）

### ドキュメント
- **tengu-000.md**: このファイル（詳細仕様・使用方法）
- **tengu-000-full.md**: 完全な実行例と模範解答
- **tengu-000-json.md**: 構造化出力の詳細解析とJSONスキーマ設計

### 共通モジュール
- **llm.py**: LLM API統合レイヤー（OpenAI/Gemini共通インターフェース）

## 背景

### 従来評価システムの課題

Shaberi評価フレームワークでは、これまでFew-shot形式でLLM-as-a-Judge評価を実施していました：

**従来の問題点：**
1. **計算ミス**: LLMが評価項目の合計点を誤計算
2. **形式不統一**: 出力フォーマットが一貫しない
3. **パース困難**: 自由形式テキストからの情報抽出が複雑
4. **効率低下**: Few-shot例で不要なトークンを消費

### 構造化出力による解決

JSONスキーマを活用した構造化出力により、これらの問題を根本的に解決：

**改善効果：**
- **計算精度**: 後処理で確実に合計点を計算
- **形式保証**: JSONスキーマによる厳密な構造制御
- **効率処理**: 構造化データの直接利用
- **トークン節約**: Few-shot例が不要

## テストケース

### 評価対象

**質問**: 「急がば回れ」という言葉について説明してください。

**模範解答**: 
```
「急がば回れ」という言葉は、日本の諺の一つであり、直接的な意味は「急ぐときは、早道や危険な方法を選ばずに、むしろ回り道で確実で安全な道を通った方が結局は早く着けるものだ」というものです。この言葉は、物事は慌てずに着実に進めることが結果としてうまくいくという教訓を含んでいます
```

### 評価項目（10点満点）

1. **本来の意味の説明**（3点）: 「急ぐときは、早道や危険な方法を選ばずに...」
2. **一般化した意味の説明**（3点）: 「物事は慌てずに着実に進める...」  
3. **ことわざであることの明示**（2点）
4. **説明の具体性・分かりやすさ**（1点）
5. **自然な日本語**（1点）

### サンプル回答と評価結果

**テスト対象の回答**:
```
「急がば回れ」とは、物事を急いで進めるよりも、慎重に計画を立てて行動する方が結果が良くなるという意味のことわざです。つまり、無駄なミスやトラブルを避けるためには、急いで手を打つのではなく、ゆっくりと計画を練り、周囲をよく考えて行動することが大切だということを教えています。急いで物事を進めようとして失敗してしまうよりも、手間と時間をかけてじっくりと準備をする方が結果的に効率的で成功する可能性が高いという教訓を持つ言葉です。
```

**模範評価**: 7/10点
- 本来の意味（回り道の概念）が欠けているため0点
- 一般化した意味は適切に説明されている

## 技術仕様

### 対応モデル

**デフォルトモデル**: `gemini-2.5-flash`

**Gemini API**:
- gemini-2.5-flash
- gemini-2.5-pro
- その他のGeminiモデル

**OpenAI API**:
- gpt-4.1-mini
- gpt-4o
- その他のOpenAIモデル

### アーキテクチャ

```
tengu-000.py
    ├── llm.py (LLM統合レイヤー)
    │   ├── generate_with_schema()
    │   ├── generate_with_temperature_retry()
    │   ├── _generate_with_gemini()
    │   └── _generate_with_openai()
    ├── tengu-000-user.md (プロンプト)
    └── tengu-000-schema.json (スキーマ)
```

### 主要機能

1. **統一インターフェース**: OpenAI/Gemini両対応の共通API
2. **ストリーミング出力**: OpenAIでリアルタイム表示
3. **温度リトライ機能**: JSONパースエラー時の自動リトライ
4. **自動スコア計算**: 構造化出力から合計点を自動算出

## 使用方法

### 基本的な実行

```bash
# デフォルトモデル（Gemini 2.5 Flash）で実行
uv run tengu-000.py

# OpenAI GPT-4.1-miniで実行
uv run tengu-000.py -m gpt-4.1-mini

# 別のGeminiモデルで実行
uv run tengu-000.py -m gemini-2.5-pro
```

### コマンドラインオプション

- `-m`, `--model`: 使用するモデルを指定（デフォルト: gemini-2.5-flash）

### 前提条件

1. **APIキー設定**: 
   - Gemini: `GOOGLE_API_KEY`環境変数
   - OpenAI: `OPENAI_API_KEY`環境変数
2. **依存関係**: 
   - `llm7shi`ライブラリ（Gemini用）
   - `openai`ライブラリ（OpenAI用）
3. **入力ファイル**: 
   - `tengu-000-user.md`
   - `tengu-000-schema.json`

## 実行結果例

### Geminiの出力例
```
- model: gemini-2.5-flash

> [指示]
> あなたは熟練した生成AIモデルの性能評価者です...

> [評価するモデルの回答]
> 「急がば回れ」とは、物事を急いで進めるよりも...

{
  "evaluation": {
    "本来の意味について説明している": {
      "points": "1",
      "reasoning": "回り道という具体的な表現がなく..."
    },
    ...
  },
  "summary": "..."
}

合計点数: 8/10点
```

### OpenAIの出力例
```
- model: gpt-4.1-mini

> [指示]
> あなたは熟練した生成AIモデルの性能評価者です...

> [評価するモデルの回答]
> 「急がば回れ」とは、物事を急いで進めるよりも...

{"evaluation":{"本来の意味について説明している":{"points":"2","reasoning":"..."},...}}

合計点数: 9/10点
```

## 期待される出力形式

構造化されたJSON形式で以下の情報を含む：

```json
{
  "evaluation": {
    "評価項目名": {
      "points": "点数",
      "reasoning": "評価理由"
    },
    ...
  },
  "summary": "総合的な評価コメント"
}
```

## 実装の詳細

### モデル判定ロジック

```python
def generate_with_schema(model, contents, schema, temperature=0, system_prompt=None):
    if model.startswith("gemini"):
        return _generate_with_gemini(model, contents, schema, temperature, system_prompt)
    else:
        return _generate_with_openai(model, contents, schema, temperature, system_prompt)
```

### スコア計算

```python
def calculate_score(result_json):
    total = 0
    evaluation = result_json.get("evaluation", {})
    
    for criterion, data in evaluation.items():
        points = int(data.get("points", "0"))
        total += points
    
    return total
```

## 今後の展開

### 大規模評価への適用

1. **バッチ処理**: 120件のTengu Benchmarkタスクを順次実行
2. **並列化**: 複数タスクの同時処理
3. **結果集計**: 全タスクの統計分析

### 他ベンチマークへの拡張

1. **ELYZA-tasks-100**: 5段階評価への対応
2. **ja-mt-bench-1shot**: マルチターン評価への応用
3. **カスタムタスク**: 特定要件に応じたスキーマ調整

## 関連プロジェクト

- **tengu.py**: 全120タスクの一括評価スクリプト
- **validate_schema.py**: スキーマ検証ユーティリティ
- **md_to_schema.py**: Markdownからスキーマ自動生成

## まとめ

`tengu-000.py`は、構造化出力による評価システムの実証実験として、従来のFew-shot形式の課題を解決し、より精確で効率的な評価を実現しています。OpenAIとGeminiの両方に対応することで、異なるLLMプロバイダー間での評価の一貫性も確保しています。

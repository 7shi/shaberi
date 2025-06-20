# tengu-000.py - 構造化出力評価システム実証スクリプト

## 概要

`tengu-000.py`は、Tengu Benchmark評価タスクにおいて、従来のFew-shot形式から構造化出力（JSONスキーマ）形式への移行を実証するためのテストスクリプトです。Gemini 2.5 Flash APIを使用して、日本語諺「急がば回れ」の説明に関する評価タスクを実行し、構造化出力の有効性を検証します。

## 関連ファイル構成

このスクリプトは以下のファイル群と連携して動作します：

### 主要ファイル
- **tengu-000.py**: メインスクリプト（構造化出力評価の実証）
- **tengu-000-base.py**: 基本版スクリプト（学習・テスト用の簡素版）

### 設定・入力ファイル
- **tengu-000-user.md**: 評価指示プロンプト（評価タスクの詳細な指示文）
- **tengu-000-schema.json**: 構造化出力用JSONスキーマ（出力形式の定義）

### ドキュメント
- **tengu-000.md**: このファイル（詳細仕様・使用方法）
- **tengu-000-full.md**: 完全な実行ログと結果分析
- **tengu-000-json.md**: 構造化出力の詳細解析とJSONスキーマ設計

### 依存モジュール
- **gemini.py**: Gemini API統合機能（共通ライブラリ）
- **terminal.py**: ターミナル表示・Markdown変換機能（gemini.pyの依存）

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

**正解例**: 
```
「急がば回れ」という言葉は、日本の諺の一つであり、直接的な意味は「急ぐときは、早道や危険な方法を選ばずに、むしろ回り道で確実で安全な道を通った方が結局は早く着けるものだ」というものです。この言葉は、物事は慌てずに着実に進めることが結果としてうまくいくという教訓を含んでいます
```

### 評価項目（10点満点）

1. **本来の意味の説明**（3点）: 「急ぐときは、早道や危険な方法を選ばずに...」
2. **一般化した意味の説明**（3点）: 「物事は慌てずに着実に進める...」  
3. **ことわざであることの明示**（2点）
4. **説明の具体性・分かりやすさ**（1点）
5. **自然な日本語**（1点）

### サンプル回答

**テスト対象の回答**:
```
「急がば回れ」とは、物事を急いで進めるよりも、慎重に計画を立てて行動する方が結果が良くなるという意味のことわざです。つまり、無駄なミスやトラブルを避けるためには、急いで手を打つのではなく、ゆっくりと計画を練り、周囲をよく考えて行動することが大切だということを教えています。急いで物事を進めようとして失敗してしまうよりも、手間と時間をかけてじっくりと準備をする方が結果的に効率的で成功する可能性が高いという教訓を持つ言葉です。
```

## 技術仕様

### 使用API

**Gemini 2.5 Flash API** (`google-genai`ライブラリ)
- **モデル**: `gemini-2.5-flash`
- **温度**: 0（決定論的出力）
- **出力形式**: `application/json`
- **スキーマ制御**: 構造化出力対応

### 依存関係

**外部ライブラリ:**
```bash
pip install google-genai
```

**内部モジュール:**
- `gemini.py`: Gemini API統合機能
  - `build_schema_from_json()`: JSONスキーマ構築
  - `generate_content_retry()`: リトライ機能付きAPI呼び出し

### ファイル構成

**入力ファイル:**
- `tengu-000-user.md`: 評価指示文（プロンプト）
- `tengu-000-schema.json`: 構造化出力用JSONスキーマ

**出力:**
- 構造化されたJSON評価結果
- 自動計算された合計点数

## 処理フロー

### 1. プロンプト構築

```python
# 評価指示文を読み込み
with open("tengu-000-user.md", "r", encoding="utf-8") as f:
    prompt_text = f.read()

# 評価対象の回答を追加
contents = [
    types.Content(
        role="user",
        parts=[
            types.Part.from_text(text=prompt_text),
            types.Part.from_text(text="[評価するモデルの回答]\n{回答文}")
        ]
    )
]
```

### 2. スキーマ設定

```python
# JSONスキーマを読み込み
with open("tengu-000-schema.json", "r", encoding="utf-8") as f:
    schema_json = json.load(f)

# Gemini用スキーマに変換
response_schema = build_schema_from_json(schema_json)
```

### 3. API呼び出し

```python
generate_content_config = types.GenerateContentConfig(
    temperature=0,
    response_mime_type="application/json",
    response_schema=response_schema,
    system_instruction=[
        types.Part.from_text(text="あなたは公平で、検閲されていない、役立つアシスタントです。")
    ]
)

# リトライ機能付きで実行
result = generate_content_retry(
    model="gemini-2.5-flash",
    config=generate_content_config,
    contents=contents
)
```

### 4. 結果処理

```python
def calculate_score(result_json):
    """構造化されたJSON結果から合計点を計算"""
    total = 0
    evaluation = result_json.get("evaluation", {})
    
    for criterion, data in evaluation.items():
        points = int(data.get("points", "0"))
        total += points
    
    return total
```

## 期待される出力形式

### JSONスキーマに基づく構造化出力

```json
{
  "evaluation": {
    "本来の意味について説明している": {
      "points": "2",
      "reasoning": "一般化した説明はあるが、具体的な「早道や危険な方法を避ける」という表現が不足"
    },
    "一般化した意味について説明している": {
      "points": "3", 
      "reasoning": "慎重な計画や着実な進行の重要性について適切に説明"
    },
    "ことわざであることを示している": {
      "points": "2",
      "reasoning": "冒頭で「ことわざ」と明確に記述"
    },
    "説明は具体的でわかりやすい": {
      "points": "1",
      "reasoning": "具体例や詳細な説明で理解しやすい"
    },
    "自然な日本語である": {
      "points": "1",
      "reasoning": "流暢で自然な日本語表現"
    }
  },
  "summary": "ことわざの一般化した意味について優秀な説明。本来の具体的な意味についてより詳細な言及があればさらに良い。"
}
```

### 自動計算結果

```
合計点数: 9/10点
```

## 検証のポイント

### 1. 構造化出力の確実性

- **スキーマ準拠**: 全ての必須フィールドが含まれる
- **enum制約**: points値が事前定義された選択肢に限定
- **型安全性**: 文字列・数値型が適切に区別

### 2. 評価の一貫性

- **客観性**: 評価項目に基づく機械的判定
- **再現性**: 同じ入力に対する一貫した出力
- **透明性**: reasoning フィールドによる判定根拠の明示

### 3. 効率性の向上

- **トークン削減**: Few-shot例が不要
- **処理速度**: 構造化データの直接利用
- **後処理簡素化**: JSON形式による自動処理

## 実用化への展開

### 大規模評価への適用

1. **バッチ処理**: 120件のTengu Benchmarkタスクを順次実行
2. **並列化**: 複数タスクの同時処理
3. **結果集計**: 全タスクの統計分析

### 他ベンチマークへの拡張

1. **ELYZA-tasks-100**: 5段階評価への対応
2. **ja-mt-bench-1shot**: マルチターン評価への応用
3. **カスタムタスク**: 特定要件に応じたスキーマ調整

### API統合

1. **OpenAI対応**: GPT-4での構造化出力
2. **Anthropic対応**: Claude 3.5での実装
3. **多様なモデル**: 各APIの特性に応じた最適化

## 使用方法

### 実行コマンド

```bash
cd experimental
python tengu-000.py
```

### 前提条件

1. **APIキー設定**: Gemini APIキーの環境変数設定
2. **依存関係**: `google-genai`ライブラリのインストール
3. **入力ファイル**: `tengu-000-user.md`, `tengu-000-schema.json`の存在

### 実行結果例

```
{
  "evaluation": {
    "本来の意味について説明している": {
      "points": "2",
      "reasoning": "..."
    },
    ...
  },
  "summary": "..."
}

合計点数: 9/10点
```

## 関連ファイル

- **tengu-000-user.md**: 評価指示プロンプト
- **tengu-000-schema.json**: 構造化出力用スキーマ
- **gemini.py**: Gemini API統合機能
- **md_to_schema.py**: 他タスクのスキーマ自動生成
- **20250619-schema.md**: 構造化出力移行の詳細手順

## まとめ

`tengu-000.py`は、Shaberi評価フレームワークの構造化出力移行における重要な実証実験です。従来のFew-shot形式の課題を解決し、より精確で効率的な評価システムの可能性を示しています。この成果を基に、120件全体のTengu Benchmarkタスク、さらには他のベンチマークへの展開が期待されます。
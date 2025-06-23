# llm.py - LLM API統合レイヤー

## 概要

`llm.py`は、OpenAI APIとGemini APIの両方に対応した統一インターフェースを提供するLLM統合レイヤーです。構造化出力（JSON Schema）を使用した生成において、異なるAPIの実装の違いを吸収し、共通の使用方法を実現します。

## 背景と動機

### 問題の発生

Tengu Benchmarkの評価システムを開発する過程で、以下の課題に直面しました：

1. **API依存の分散**
   - OpenAI専用の`tengu-000-openai.py`
   - Gemini専用の`tengu-000.py`
   - 同じ評価ロジックが複数ファイルに重複

2. **メンテナンスの困難**
   - 評価ロジックの変更時に複数ファイルの更新が必要
   - APIごとに異なる実装方法
   - コードの一貫性の欠如

3. **拡張性の問題**
   - 新しいLLMプロバイダーの追加が困難
   - 各APIの特性に応じた最適化が分散

### 解決アプローチ

これらの問題を解決するため、以下の設計方針で統合レイヤーを実装：

1. **単一インターフェース**: `generate_with_schema()`で全APIに対応
2. **自動判別**: モデル名からAPIを自動選択
3. **共通機能**: 温度リトライなどの汎用機能を一元化
4. **API固有の最適化**: 内部実装で各APIの特性を活かす

## 主要機能

### 1. generate_with_schema()

統一されたインターフェースで構造化出力を生成：

```python
result = generate_with_schema(
    model="gemini-2.5-flash",  # または "gpt-4.1-mini"
    contents=[
        "ユーザープロンプト1",
        "ユーザープロンプト2"
    ],
    schema=json_schema,
    temperature=0,
    system_prompt="システムプロンプト"
)
```

**特徴**:
- モデル名で自動的にAPIを判別
- シンプルな`contents`配列とシステムプロンプト分離
- 構造化出力（JSON Schema）をサポート

### 2. contents_to_openai_messages()

Contents配列とシステムプロンプトをOpenAI形式に変換：

```python
from llm import contents_to_openai_messages

openai_messages = contents_to_openai_messages(
    contents=["プロンプト1", "プロンプト2"],
    system_prompt="システムプロンプト"
)
# 結果: [{"role": "system", "content": "..."}, {"role": "user", "content": "プロンプト1"}, ...]
```

**特徴**:
- シンプルなcontents配列をOpenAI形式のmessages配列に変換
- システムプロンプトを最初に配置
- 各contentをuserロールとして追加

### 3. API固有の実装

#### Gemini API (_generate_with_gemini)

- `llm7shi`ライブラリを使用
- システムインストラクションとユーザーメッセージを分離
- `config_from_schema()`でスキーマから設定を生成
- `show_params=False`でパラメータ表示を抑制

#### OpenAI API (_generate_with_openai)

- 公式`openai`ライブラリを使用
- ストリーミング出力をデフォルトで有効化
- `additionalProperties: false`を自動追加（OpenAI必須）

## 設計の詳細

### モデル判別ロジック

```python
if model.startswith("gemini"):
    return _generate_with_gemini(...)
else:
    return _generate_with_openai(...)
```

シンプルなプレフィックス判定により、拡張性と保守性を確保。

### メッセージ形式の統一

シンプルな配列とシステムプロンプト分離形式を採用：

```python
contents = ["ユーザープロンプト1", "ユーザープロンプト2"]
system_prompt = "システムプロンプト"
```

各APIでは内部で以下のように変換：
- **Gemini API**: `contents`直接使用、`system_prompt` → `system_instruction`
- **OpenAI API**: `contents_to_openai_messages()`でOpenAI形式に変換

### スキーマの自動調整

OpenAI APIは`additionalProperties: false`を必須とするため、自動的に追加：

```python
def _add_additional_properties_false(schema):
    schema["additionalProperties"] = False
    # ネストされたオブジェクトにも再帰的に適用
```

### ストリーミング出力

OpenAI APIでは、ユーザー体験向上のためストリーミングをデフォルト化：

```python
stream = client.chat.completions.create(..., stream=True)
for chunk in stream:
    print(chunk.choices[0].delta.content, end='', flush=True)
```

### エラーハンドリング

温度リトライ機能により、構造化出力の信頼性を向上：

1. 温度0での生成を試行
2. パースエラー時は温度を上げて再試行
3. 全ての試行が失敗した場合のみエラーを発生

## 使用例

### 基本的な使用

```python
from llm import generate_with_schema, DEFAULT_MODEL

# デフォルトモデル（Gemini）での生成
result = generate_with_schema(
    model=DEFAULT_MODEL,
    contents=["質問"],
    schema={"type": "object", "properties": {...}},
    system_prompt="システムプロンプト"
)

# OpenAIモデルでの生成
result = generate_with_schema(
    model="gpt-4.1-mini",
    contents=["質問"],
    schema={"type": "object", "properties": {...}},
    system_prompt="システムプロンプト"
)
```

### OpenAI形式への変換

```python
from llm import contents_to_openai_messages

# Contents配列をOpenAI形式に変換
openai_messages = contents_to_openai_messages(
    contents=["質問1", "質問2"],
    system_prompt="システムプロンプト"
)

# 外部ライブラリで直接使用
import openai
client = openai.OpenAI()
response = client.chat.completions.create(
    model="gpt-4.1-mini",
    messages=openai_messages
)
```

## 環境設定

### 必要な環境変数

- **Gemini**: `GOOGLE_API_KEY`
- **OpenAI**: `OPENAI_API_KEY`

### 依存ライブラリ

```python
# Gemini API用
pip install llm7shi

# OpenAI API用
pip install openai
```

## 今後の拡張

### 新しいプロバイダーの追加

新しいLLMプロバイダーを追加する場合：

1. モデル名の判別ロジックを更新
2. `_generate_with_[provider]`関数を実装
3. 必要に応じてスキーマ変換を追加

### 機能の拡張案

1. **非同期対応**: asyncio対応で並列処理を効率化
2. **キャッシング**: 同一リクエストの結果をキャッシュ
3. **メトリクス**: API使用量やレスポンス時間の記録
4. **フォールバック**: APIエラー時の自動切り替え

## まとめ

`llm.py`は、異なるLLM APIの実装の違いを吸収し、統一されたインターフェースを提供することで、以下を実現しています：

1. **開発効率の向上**: 一つのコードで複数のAPIに対応
2. **保守性の向上**: API固有のロジックを一箇所に集約
3. **信頼性の向上**: 温度リトライなどの共通機能
4. **拡張性の確保**: 新しいプロバイダーの追加が容易

この設計により、Shaberi評価フレームワークの構造化出力への移行がスムーズに進められ、将来的な拡張にも対応できる基盤が整いました。
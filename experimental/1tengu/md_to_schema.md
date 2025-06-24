# md_to_schema.py - Markdown→JSONスキーマ変換スクリプト

## 概要

`md_to_schema.py`は、Tengu Benchmark評価タスクのMarkdownファイル（data/*.md）から、構造化出力用のJSONスキーマファイル（data/*.json）を自動生成するスクリプトです。Few-shot形式からJSONスキーマベースの評価システムへの移行を自動化します。

## 背景

### 従来のFew-shot形式の問題点

Shaberi評価フレームワークでは、これまでFew-shot形式でLLM-as-a-Judge評価を実施していました：

```
[指示]
あなたは熟練した生成AIモデルの性能評価者です。
...
[評価項目]
- 答えが867万円である:3点
- 説明が具体的でわかりやすい:2点
...
# 以下の形式で回答してください。
[該当する評価項目とその簡潔な理由]
[計算式]
[点数]
```

#### 問題点
1. **計算エラー**: LLMが合計点を誤計算する
2. **形式の不安定性**: 出力フォーマットが一貫しない
3. **パース困難**: 自由形式テキストからの情報抽出が複雑
4. **トークン浪費**: Few-shot例で不要なトークンを消費

### 構造化出力による解決

JSONスキーマを使用した構造化出力により、これらの問題を根本的に解決：

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
  "summary": "全体的に優秀な回答"
}
```

#### 解決効果
- **計算精度**: 後処理で確実に合計点を計算
- **形式統一**: JSONスキーマによる厳密な構造保証
- **効率処理**: 構造化データの直接利用
- **トークン節約**: Few-shot例が不要

## 変換アルゴリズム

### 入力データ解析

#### 状態機械による解析

スクリプトは4つの状態で評価項目を段階的に解析：

1. **search**: `[評価項目]`セクションを探索
2. **reading_criteria**: 通常の評価項目を読み取り
3. **checking_indent**: 階層構造の子項目を読み取り
4. **waiting_for_next**: `[評価するモデルの回答]`まで待機

#### 階層構造の処理

**入力（階層あり）:**
```markdown
[評価項目]
- 文章中の以下の情報を含んでいる
  - 取引デジタルフォームの定義:2点
  - その他の関連用語の定義:2点
- 自然な日本語である:1点
```

**処理結果:**
```python
[
  {"description": "文章中の以下の情報を含んでいる：取引デジタルフォームの定義", "points": 2},
  {"description": "文章中の以下の情報を含んでいる：その他の関連用語の定義", "points": 2},
  {"description": "自然な日本語である", "points": 1}
]
```

### JSONスキーマ生成

#### 基本構造

各評価項目は以下の構造に変換：

```json
"評価項目名": {
  "type": "object",
  "properties": {
    "points": {
      "type": "string",
      "enum": ["0", "1", "2", ...],
      "description": "Points assigned (0-N scale based on how well this criterion is met)"
    },
    "reasoning": {
      "type": "string", 
      "description": "Brief explanation in Japanese of why this score was assigned"
    }
  },
  "required": ["points", "reasoning"]
}
```

#### enum値の動的生成

配点に応じて選択肢を自動生成：

- **1点満点** → `["0", "1"]`
- **2点満点** → `["0", "1", "2"]`
- **3点満点** → `["0", "1", "2", "3"]`
- **4点満点** → `["0", "1", "2", "3", "4"]`

#### ダブルクォートの処理

評価項目の見出しにダブルクォート（"）が含まれている場合、JSONのキー名として使用する際の誤動作を防ぐため、自動的にシングルクォート（'）に置換されます。

例：
- 入力: `"良い"回答である`
- 出力: `'良い'回答である`

## 処理結果

### 変換統計

**処理対象**: data/ディレクトリの120件のMarkdownファイル

**成功率**: 100%（120/120件）

**出力形式**: 各MDファイルに対応するJSONスキーマファイル

### 形式別対応状況

#### 単層構造（97件）
```markdown
- 答えが867万円である:3点
- 説明が具体的でわかりやすい:2点
→ 直接的な変換
```

#### 階層構造（23件）
```markdown
- 親項目の説明
  - 子項目の説明:2点
→ "親項目の説明：子項目の説明" として統合
```

### サンプル出力

**001.md → 001.json**の変換例：

**入力（MD）:**
```markdown
[評価項目]
- 答えが867万円である:3点
- 全ての月の売り上げの合計を求めることで年平均売り上げ金額を求めている:2点
- 表の値を正しく読み取れている:2点
- 説明が具体的でわかりやすい:2点
- 自然な日本語である:1点
```

**出力（JSON）:**
```json
{
  "type": "object",
  "properties": {
    "evaluation": {
      "type": "object", 
      "properties": {
        "答えが867万円である": {
          "type": "object",
          "properties": {
            "points": {
              "type": "string",
              "enum": ["0", "1", "2", "3"],
              "description": "Points assigned (0-3 scale based on how well this criterion is met)"
            },
            "reasoning": {
              "type": "string",
              "description": "Brief explanation in Japanese of why this score was assigned"
            }
          },
          "required": ["points", "reasoning"]
        }
        // ... 他の評価項目
      },
      "required": ["答えが867万円である", ...]
    },
    "summary": {
      "type": "string",
      "description": "Overall assessment summary in Japanese of the model's answer"
    }
  },
  "required": ["evaluation", "summary"]
}
```

## 技術仕様

### 依存関係
- **標準ライブラリのみ**: `json`, `re`, `pathlib`
- **外部依存なし**: 追加インストール不要

### パフォーマンス
- **高速処理**: 120件を数秒で完了
- **メモリ効率**: ファイル単位での逐次処理
- **エラー耐性**: 1件の失敗が全体に影響しない

### 文字エンコーディング
- **入力**: UTF-8（Markdownファイル）
- **出力**: UTF-8（JSONファイル、日本語文字保持）
- **JSON形式**: `ensure_ascii=False`で日本語を直接出力

## 使用方法

### 実行コマンド
```bash
cd experimental
uv run md_to_schema.py
```

### 前提条件
- `data/`ディレクトリが存在すること
- ディレクトリ内に`.md`ファイルが存在すること
- Python 3.6以上

### 実行結果例
```
MD → JSONスキーマ変換開始
✓ 001.md → 001.json
✓ 002.md → 002.json
...
✓ 120.md → 120.json

変換完了:
  処理ファイル: 120件
  成功: 120件
  エラー: 0件
```

## エラーハンドリング

### 想定されるエラー

#### 1. 評価項目形式エラー
```
✗ XXX.md: 評価項目の解析に失敗
```
**原因**: 期待する形式（`- 説明:点数点`）に適合しない

#### 2. ファイル読み込みエラー
```
✗ XXX.md: [Errno 2] No such file or directory
```
**原因**: ファイルが存在しない、または権限不足

#### 3. 文字エンコーディングエラー
```
✗ XXX.md: 'utf-8' codec can't decode
```
**原因**: UTF-8以外のエンコーディング

### エラー対策

1. **事前検証**: `check_criteria.py`で形式確認
2. **個別処理**: 1件のエラーで全体が停止しない
3. **詳細ログ**: エラー内容の明確な表示

## 今後の活用

### 構造化評価の実行

生成されたJSONスキーマは以下の用途で活用：

1. **OpenAI APIでの構造化出力**
   ```python
   response = client.chat.completions.create(
       model="gpt-4o",
       response_format={"type": "json_schema", "json_schema": schema}
   )
   ```

2. **Anthropic Claude APIでの構造化出力**
   ```python
   response = client.messages.create(
       model="claude-3-5-sonnet-20241022",
       tools=[{"name": "evaluation", "input_schema": schema}]
   )
   ```

3. **評価結果の後処理**
   ```python
   total_score = sum(int(item["points"]) for item in evaluation.values())
   ```

### 拡張可能性

1. **他ベンチマーク対応**: ELYZA、ja-mt-benchへの適用
2. **カスタム形式**: 特定要件に応じたスキーマ調整
3. **バリデーション強化**: より厳密な入力検証
4. **統計分析**: 評価項目の配点分布や傾向分析

## 関連ファイル

- **conv_tengu.py**: JSON→MD変換（前段階）
- **check_criteria.py**: MD形式検証
- **tengu-000-schema.json**: 参照スキーマ（手動作成例）
- **20250619-schema.md**: 変換手順の詳細説明

## まとめ

`md_to_schema.py`により、Tengu Benchmark 120件すべての評価タスクが構造化出力対応になりました。これにより、より精確で効率的なLLM評価システムの構築が可能になります。従来のFew-shot形式の問題を根本的に解決し、次世代の評価フレームワークへの移行を実現しています。

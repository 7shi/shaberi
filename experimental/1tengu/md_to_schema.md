# md_to_schema.py - Markdown→JSONスキーマ変換スクリプト

## 概要

`md_to_schema.py`は、Tengu Benchmark評価タスクのMarkdownファイル（data/*.md）から、構造化出力用のJSONスキーマファイル（data/*.json）を自動生成するスクリプトです。Few-shot形式からJSONスキーマベースの評価システムへの移行を自動化します。

## 背景

**Problem**: 従来のFew-shot形式では、LLMの計算エラー、出力形式の不安定性、パース困難、トークン浪費などの問題が発生。

**Solution**: JSONスキーマを使用した構造化出力により、計算精度、形式統一、効率処理、トークン節約を実現。

## 変換アルゴリズム

### 処理概要
1. **状態機械解析**: 4状態で評価項目を段階的に解析
2. **階層構造処理**: 親項目と子項目を「親：子」形式で結合
3. **JSONスキーマ生成**: 各項目を`points`と`reasoning`を持つオブジェクトに変換
4. **enum動的生成**: 配点に応じて選択肢を自動生成
5. **ダブルクォート処理**: JSONキー名の誤動作防止

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
- **入力**: 5項目の評価基準（答えが867万円:3点、計算過程:2点等）
- **出力**: 各項目が`points`と`reasoning`を持つJSONスキーマ
- **構造**: `evaluation`オブジェクトと`summary`文字列を持つルート

## 技術仕様

- **依存**: 標準ライブラリのみ（`json`, `re`, `pathlib`）
- **パフォーマンス**: 120件を数秒で処理、エラー耐性あり
- **エンコーディング**: UTF-8、日本語完全対応

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

- **想定エラー**: 評価項目形式不適合、ファイル読み込み失敗、文字エンコーディングエラー
- **対策**: `check_criteria.py`で事前検証、個別処理、詳細ログ出力

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

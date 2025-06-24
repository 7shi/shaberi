# analyze_evaluations.py - Shaberi3データセット構造分析ツール

## 概要

`analyze_evaluations.py`は、`shaberi3-evaluations.json`ファイルのデータ構造を詳細に分析し、データ品質を確認するための調査ツールです。特に、標準的でないデータ構造（`len(line_data) != 4`）のケースを特定し、データ前処理における品質管理を支援します。

## 背景

### Shaberi3データセットの構造

`shaberi3-evaluations.json`は、複数の日本語ベンチマーク評価データを統合したJSONLファイルです：

```
- tengu_bench: 120件の日本語能力評価タスク
- ELYZA-tasks-100: 100件のタスク特化型評価
- ja-mt-bench-1shot: 60件のマルチターン会話評価
```

### データ構造の期待値

標準的な各行のJSONデータは、以下の4要素配列構造を持つことが期待されます：

```json
[
  element_0,  // データセット情報
  element_1,  // コンテンツ情報（content フィールドを含む）
  element_2,  // 評価情報
  element_3   // メタデータ
]
```

### データ品質の課題

実際のデータセットでは、以下の問題が発生する可能性があります：

1. **長さの不一致**: `len(line_data) != 4`のケース
2. **構造の不整合**: 期待されるフィールドの欠損
3. **エンコーディング問題**: 文字化けや不正なJSON
4. **重複データ**: 同一コンテンツの重複

これらの問題により、`dump_questions.py`での分類・抽出処理が失敗したり、不正確な結果を生成する可能性があります。

## 主要機能

### 1. データ長分布の分析

**目的**: 各行の`line_data`配列の長さを集計し、標準的でないデータの存在を把握

```python
length_counter = Counter()
for line_data in jsonl_file:
    if isinstance(line_data, list):
        length = len(line_data)
        length_counter[length] += 1
```

**出力例**:
```
=== Length Distribution of line_data ===
Total different lengths: 2
Length 4: 275 occurrences
Length 3: 5 occurrences
```

### 2. 異常データの詳細分析

**目的**: `len(line_data) != 4`のケースについて、コンテンツの特徴を調査

```python
content_prefix_counter = Counter()
if length != 4 and len(line_data) >= 2:
    if isinstance(line_data[1], dict) and "content" in line_data[1]:
        content = line_data[1]["content"]
        prefix = content[:10]  # 最初の10文字
        content_prefix_counter[prefix] += 1
```

**出力例**:
```
=== Analysis for len(line_data) != 4 ===
Total unique line_data[1]['content'][:10] prefixes: 3

Frequency of each content prefix (first 10 chars):

Count: 3
Prefix: '以下の文章を要約'

Count: 1
Prefix: 'あなたは日本の'

Count: 1
Prefix: '次の文章から重'
```

### 3. エラー耐性処理

**JSON解析エラー**:
```python
try:
    line_data = json.loads(line.strip())
except json.JSONDecodeError as e:
    print(f"Error parsing line {line_num}: {e}")
```

**データ構造エラー**:
```python
except Exception as e:
    print(f"Error processing line {line_num}: {e}")
```

## 使用方法

### 基本実行

```bash
uv run analyze_evaluations.py
```

### 前提条件

1. **入力ファイル**: `shaberi3-evaluations.json`が同一ディレクトリに存在
2. **依存関係**: 標準ライブラリのみ使用（追加インストール不要）

### 実行例

```bash
uv run analyze_evaluations.py
```

**出力例**:
```
=== Length Distribution of line_data ===
Total different lengths: 1
Length 4: 280 occurrences

=== Analysis for len(line_data) != 4 ===
Total unique line_data[1]['content'][:10] prefixes: 0

Frequency of each content prefix (first 10 chars):
（標準的なデータのみの場合、異常データなし）
```

## 分析結果の解釈

### 1. 理想的なケース

```
Total different lengths: 1
Length 4: 280 occurrences
Total unique prefixes: 0
```

- 全データが期待される4要素構造
- 異常データなし
- `dump_questions.py`の安全な実行が可能

### 2. 異常データ存在ケース

```
Total different lengths: 2
Length 4: 275 occurrences
Length 3: 5 occurrences
Total unique prefixes: 3
```

- 5件の異常データ（3要素構造）が存在
- 3種類の異なるコンテンツパターン
- 詳細調査と修正が必要

### 3. 対応方針

**軽微な異常（5件未満）**:
- `dump_questions.py`実行時に警告表示
- 手動での確認・修正

**重大な異常（10件以上）**:
- データソースの再確認
- 前処理スクリプトでの自動修正
- データ提供元への報告

## 活用シナリオ

### 1. データ前処理の品質確認

```bash
# 新しいshaberi3-evaluations.jsonを受け取った場合
uv run analyze_evaluations.py
# → 異常データの有無を確認
# → 問題なければdump_questions.pyに進む
```

### 2. トラブルシューティング

```bash
# dump_questions.pyでエラーが発生した場合
uv run analyze_evaluations.py
# → データ構造の問題を特定
# → 修正方針を決定
```

### 3. データセット更新時の検証

```bash
# shaberi3-evaluations.jsonの更新後
uv run analyze_evaluations.py
# → 新旧データの構造比較
# → 互換性の確認
```

## 技術仕様

### 依存関係

**標準ライブラリのみ**:
- `json`: JSONファイルの解析
- `collections.Counter`: 頻度集計

### 処理性能

- **処理速度**: 280件のデータを数秒で分析
- **メモリ使用量**: 最小限（行単位での逐次処理）
- **エラー耐性**: 1件の異常データが全体処理を停止させない

### ファイル形式

**入力**: JSONL形式（1行1JSON）
```
{"data": [...]}
{"data": [...]}
...
```

**出力**: コンソール表示（テキスト形式）

## 関連ファイル

### 後続処理
- **dump_questions.py**: 分析結果を基にした安全なデータ分類・抽出
- **conv_tengu.py**: 抽出されたデータの変換処理

### 設定ファイル
- **shaberi3-evaluations.json**: 分析対象の入力データファイル

### ドキュメント
- **dump_questions.md**: データ分類・抽出の詳細手順
- **README.md**: experimental ツール群の全体概要

## 制限事項

### 1. 分析範囲

- **表面的分析**: データ構造のみ、コンテンツの意味的分析は含まない
- **統計情報**: 基本的な頻度分析のみ
- **自動修正**: 問題の特定のみ、自動修正機能なし

### 2. 入力制限

- **ファイル名**: `shaberi3-evaluations.json`固定
- **ファイル形式**: JSONL形式必須
- **エンコーディング**: UTF-8前提

## 今後の展開

### 機能拡張

1. **詳細分析**: コンテンツの意味的重複検出
2. **自動修正**: 軽微な構造問題の自動修正機能
3. **レポート出力**: 分析結果のJSON/CSV出力
4. **可視化**: データ品質のグラフィカル表示

### 他データセット対応

1. **汎用化**: 任意のJSONLファイルへの対応
2. **設定ファイル**: 期待される構造の外部定義
3. **プラグイン**: データセット特有の検証ルール

## まとめ

`analyze_evaluations.py`は、Shaberi3データセットの品質管理において重要な役割を果たす調査ツールです。

**主要価値**:
- **品質保証**: データ前処理の安全性確保
- **トラブル予防**: 事前の問題発見と対策
- **効率化**: 手動確認作業の自動化
- **信頼性向上**: データ処理パイプラインの安定性向上

この分析により、後続の`dump_questions.py`での分類・抽出処理を安全かつ確実に実行でき、Shaberi評価フレームワーク全体の品質向上に貢献します。

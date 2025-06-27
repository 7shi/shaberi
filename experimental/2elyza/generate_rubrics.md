# generate_rubrics.py - ELYZA-tasks-100 評価基準自動コード化ツール

## 概要

`generate_rubrics.py`は、ELYZA-tasks-100の評価基準を自動的にPython関数としてコード化するツールです。既存のfew-shot例（`rubrics-001.py`, `rubrics-002.py`）を参考に、LLMを使って残りのタスクの評価関数を自動生成します。

## 目的

- **効率化**: 100個のタスクの評価関数を手動で書く労力を削減
- **一貫性**: Few-shot学習により統一されたコードスタイルを維持
- **保守性**: 評価基準の変更に対して自動的に対応可能
- **品質**: LLMによる高品質なコード生成

## 主要機能

### 1. 評価基準の自動抽出
- `data/XXX.md`ファイルから「問題固有の採点基準」セクションを抽出
- `check_criteria.py`の`extract_criteria`関数をインポートして使用

### 2. Few-shot学習によるコード生成
- `rubrics-001.py`と`rubrics-002.py`を例として提示
- 統一された関数署名とパターンで生成
- 関数名: `judge_XXX(score: int, judge: callable) -> int`

### 3. テストモード
- `--test`オプションでプロンプトの確認が可能
- 実際のLLM呼び出しなしでデバッグ可能

### 4. スキップ機能
- 既に生成済みのファイルは自動的にスキップ
- 部分的な再実行が効率的

## 技術仕様

### 依存関係
- `llm7shi.compat.generate_with_schema`: LLM呼び出し
- `llm7shi.do_show_params`: テストモード用プロンプト表示
- `check_criteria.extract_criteria`: 評価基準抽出機能
- `pathlib.Path`: ファイル操作

### データフロー

```
data/XXX.md → 評価基準抽出 → LLMプロンプト作成 → コード生成 → rubrics/XXX.md
```

### プロンプト構造

1. **Few-shot例**: `rubrics-001.py`, `rubrics-002.py`の内容
2. **実装ルール**: 関数署名、パラメータ、実装パターンの説明
3. **評価基準**: 対象タスクの具体的な採点基準

## 使用方法

### 基本的な使用例

```bash
# 全タスクを生成（001-100）
python generate_rubrics.py --all

# 特定範囲の生成
python generate_rubrics.py --start 3 --end 10

# 特定タスクのみ生成
python generate_rubrics.py --tasks 5 7 12

# 別のLLMモデルを使用
python generate_rubrics.py --all -m gpt-4o-mini

# テストモード（プロンプト確認）
python generate_rubrics.py --tasks 3 --test
```

### オプション詳細

| オプション | 説明 | 例 |
|------------|------|-----|
| `--all` | 001-100の全タスクを生成 | `--all` |
| `--start` | 開始タスク番号 | `--start 3` |
| `--end` | 終了タスク番号 | `--end 10` |
| `--tasks` | 特定タスクのリスト | `--tasks 5 7 12` |
| `-m, --model` | 使用するLLMモデル | `-m gpt-4o-mini` |
| `-o, --output-dir` | 出力ディレクトリ | `-o rubrics` |
| `--test` | テストモード | `--test` |

## 出力

### 個別ファイル
- **場所**: `rubrics/XXX.md`
- **形式**: Markdownファイル内にPythonコードブロック
- **内容**: 各タスクの評価関数

## 実装詳細

### 関数の生成パターン

```python
def judge_XXX(score: int, judge: callable) -> int:
    # 評価基準をコメントとして記載
    # - 条件1: 減点ルール
    # - 条件2: 特別処理
    
    if judge("条件1の説明"):
        score -= 1
    if judge("条件2の説明"):
        score = 3  # 固定スコア
    
    return score
```

### エラーハンドリング

- ファイル不存在: 適切なエラーメッセージを表示
- LLM呼び出し失敗: エラーを表示して次のタスクに進行
- プロンプト構築エラー: 詳細なエラー情報を提供

## 品質管理

### Few-shot例の品質
- `rubrics-001.py`と`rubrics-002.py`が高品質である必要
- 一貫したコードスタイルとコメント記述

### 生成コードの検証
- テストモードでプロンプトを事前確認
- 生成後のコードレビューが推奨

### 継続的改善
- 生成されたコードの品質に基づいてプロンプトを調整
- Few-shot例の更新による品質向上

## 制限事項

### 依存関係
- `data/`ディレクトリに分割済みタスクファイルが必要
- `rubrics-001.py`, `rubrics-002.py`の存在が必須
- `check_criteria.py`モジュールが必要

### LLMの制約
- モデルの性能に依存する生成品質
- プロンプトの長さ制限

### ファイル操作
- 既存ファイルの上書きリスク
- ディスク容量の要件

## トラブルシューティング

### よくある問題

1. **ファイルが見つからない**
   ```
   エラー: rubrics-001.py または rubrics-002.py が見つかりません
   ```
   → Few-shot例ファイルを正しい場所に配置

2. **データディレクトリが見つからない**
   ```
   エラー: dataディレクトリが見つかりません
   ```
   → `data/`ディレクトリとタスクファイルを確認

3. **LLM呼び出しエラー**
   → ネットワーク接続、API認証、モデル名を確認

### デバッグ方法

1. **テストモードの活用**
   ```bash
   python generate_rubrics.py --tasks 3 --test
   ```

2. **段階的実行**
   ```bash
   # 1つずつテスト
   python generate_rubrics.py --tasks 3
   # 問題なければ範囲を拡大
   python generate_rubrics.py --start 3 --end 5
   ```

## 今後の拡張

### 計画中の機能
- スキーマ検証によるコード品質チェック
- 生成コードの自動テスト実行
- バッチ処理の並列化

### 改善案
- プロンプトテンプレートの外部化
- カスタムFew-shot例の指定
- 生成ログの詳細化

## まとめ

`generate_rubrics.py`は、ELYZA-tasks-100の評価基準を効率的にコード化するための強力なツールです。Few-shot学習とLLMの組み合わせにより、高品質で一貫性のある評価関数を自動生成し、個別のMarkdownファイルとして出力することで、評価システムの開発・保守を大幅に効率化します。
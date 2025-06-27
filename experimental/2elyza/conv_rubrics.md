# conv_rubrics.py

ELYZA-tasks-100の評価基準（rubrics/*.md）をPythonコードに変換するスクリプト

## 概要

このスクリプトは、`generate_rubrics.py`で生成されたMarkdown形式の評価基準ファイル（rubrics/*.md）から：

1. Pythonコード部分を抽出
2. コメントを削除してコードを簡潔化
3. data/XXX.mdから元の評価基準を取得して関数定義の直後に挿入
4. .pyファイルとして保存

## 使用方法

```bash
# 001-100全て変換
python conv_rubrics.py --all

# 特定範囲を変換
python conv_rubrics.py --start 3 --end 10

# 特定のタスク番号のみ変換
python conv_rubrics.py --tasks 5 7 12

# 出力ディレクトリ指定
python conv_rubrics.py --all -o py

# 既存ファイルを上書き
python conv_rubrics.py --all --force
```

## オプション

- `--all`: 001-100の全タスクを変換
- `--start N`: 開始タスク番号
- `--end N`: 終了タスク番号（--startと組み合わせて使用）
- `--tasks N [N ...]`: 変換するタスク番号のリスト
- `-o`, `--output-dir`: 出力ディレクトリ（デフォルト: rubrics）
- `--force`: 既存ファイルを上書き

## 処理の流れ

1. **Pythonコード抽出**: Markdownファイルから\`\`\`python～\`\`\`ブロックを抽出
2. **コメント削除**: 
   - `#`で始まる行を削除
   - 行末コメントを削除
3. **評価基準の挿入**:
   - `data/XXX.md`から「問題固有の採点基準」セクションを抽出
   - 関数定義の直後にコメントとして挿入
4. **ファイル保存**: rubrics/XXX.py として保存

## 生成されるファイルの例

入力（rubrics/003.md）:
```python
def judge_003(score: int, judge: callable) -> int:
    # - 「独自の文化や哲学、神話が有名です」などのように具体例がない場合は-1点
    # - 事実と異なる内容の場合: -2点

    if judge("「独自の文化や哲学、神話が有名です」などのように具体例がない"):
        score -= 1
    if judge("事実と異なる内容である"):
        score -= 2
    return score
```

出力（rubrics/003.py）:
```python
def judge_003(score: int, judge: callable) -> int:
    # - 「独自の文化や哲学、神話が有名です」などのように具体例がない場合は-1点
    # - 事実と異なる内容の場合: -2点
    
    if judge("「独自の文化や哲学、神話が有名です」などのように具体例がない"):
        score -= 1
    if judge("事実と異なる内容である"):
        score -= 2
    return score
```

## 関連ファイル

- `generate_rubrics.py`: 評価基準をMarkdown形式で生成
- `data/XXX.md`: 各タスクの問題文と評価基準
- `rubrics/XXX.md`: 生成された評価関数（Markdown形式）
- `rubrics/XXX.py`: 変換された評価関数（Python形式）

## 注意事項

- `data/XXX.md`から評価基準を抽出するため、dataディレクトリが必要
- 文字列内の`#`の処理は簡易的な実装のため、複雑なケースでは誤動作の可能性あり
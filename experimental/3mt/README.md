# ja-mt-bench-1shot 構造化出力評価システム

## データ構造の分析

ja-mt-bench-1shotは以下の特徴を持っています：

1. **統一された評価基準**: 全60タスクで同じ評価指示
2. **標準化されたフォーマット**: 
   - [指示] - 評価者への指示（全タスク共通）
   - [質問] - ユーザーの質問（タスクごとに異なる）
   - [アシスタントの回答] - 評価対象の回答
3. **評価スケール**: 1-10点

## タスクタイプの分類

**質問の性質によるカテゴリ分け**:

- 分析・評価タスク（1-10）
- 知識・説明タスク（11-20）
- 論理・推論タスク（21-30）
- ロールプレイタスク（31-40）
- 科学・技術タスク（41-50）
- 創作・執筆タスク（51-60）

## ファイル構成

### 実行ファイル
- **conv_mt.py**: 3mt.jsonを個別ファイル（data/001.md～060.md）に分割
- **mt-004.py**: タスク004の単一タスク実証スクリプト
- **mt.py**: 全タスク対応の構造化出力評価システム

### 設定ファイル
- **mt-schema.json**: 構造化出力用JSONスキーマ（reasoning + score）
- **mt-004-answer.md**: タスク004のサンプル回答

### データディレクトリ
- **data/**: 分割されたタスクファイル（001.md～060.md）

### ドキュメント
- **conv_mt.md**: データ分割の実装理由
- **mt-004.md**: 単一タスク実証の実装理由  
- **mt.md**: 全タスク評価システムの実装理由

## 使用方法

### 1. データ分割
```bash
uv run conv_mt.py
```
3mt.jsonから60個のタスクファイルを生成します。

### 2. 単一タスク評価
```bash
# タスク004の評価（デフォルトモデル）
uv run mt-004.py

# 評価モデルを指定
uv run mt-004.py -m gpt-4.1-mini
uv run mt-004.py -m gemini-2.5-pro
```

### 3. 全タスク評価
```bash
# 単一タスクの評価
uv run mt.py ../../data/model_answers/shisa-ai__ja-mt-bench-1shot/model-name.json -n 4

# 全タスクの評価
uv run mt.py ../../data/model_answers/shisa-ai__ja-mt-bench-1shot/model-name.json --all

# 評価モデルを指定
uv run mt.py model-answers.json --all -m gpt-4.1-mini

# 既存結果を上書き
uv run mt.py model-answers.json --all --force

# 温度調整リトライを無効化（o4-mini推奨）
uv run mt.py model-answers.json --all -st -1
```

### オプション
- `-n, --task-number`: 評価するタスク番号（1-60）
- `--all`: 全タスク評価
- `-m, --model`: 評価用モデル名
- `--force`: 既存結果を上書き
- `-st, --start-temperature`: 開始温度（0-100、負値で無効化）
- `--max-length`: 最大トークン数

## 出力形式

評価結果は`judge/{評価モデル}/{回答モデル}/{タスク番号}.json`に保存されます：

```json
{
  "answer": "モデルの回答",
  "evaluation": {
    "reasoning": "評価理由",
    "score": "8"
  },
  "score": 8
}
```

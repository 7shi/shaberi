# tengu.py - Tengu Benchmark構造化出力評価システム

## 概要

`tengu.py`は、Tengu Benchmark評価タスクにおいて、従来のFew-shot形式から構造化出力（JSONスキーマ）形式による評価を実行するメインスクリプトです。指定されたタスク番号とモデル回答ファイルを使用して、llm7shiライブラリを通じてGemini APIによる自動評価を行い、構造化された評価結果を出力します。

## 背景

### 評価システムの進化

Shaberi評価フレームワークにおいて、LLM-as-a-Judge手法は重要な評価手段でした。しかし、従来のFew-shot形式には以下の課題がありました：

**従来の問題点：**
1. **計算精度の課題**: LLMが評価項目の合計点を誤計算する
2. **出力形式の不安定性**: 自由形式テキストによる一貫性の欠如
3. **パース処理の複雑性**: 評価結果の自動抽出が困難
4. **効率性の低下**: Few-shot例による不要なトークン消費

### 構造化出力による革新

JSONスキーマを活用した構造化出力により、これらの課題を根本的に解決：

**改善効果：**
- **計算の確実性**: 後処理で正確な合計点計算
- **形式の保証**: JSONスキーマによる厳密な構造制御
- **処理の効率化**: 構造化データの直接利用
- **コストの最適化**: Few-shot例が不要でトークン節約

## アーキテクチャ

### データフロー

```
モデル回答JSON → load_model_answer() → 指定タスクの回答抽出
     ↓
1tengu/xxx.md → load_task_files() → 評価プロンプト
1tengu/xxx.json → load_task_files() → JSONスキーマ
     ↓
evaluate_task() → llm7shi経由Gemini API呼び出し → 構造化評価結果
     ↓
calculate_score() → 合計点数計算 → 最終結果表示
```

### ファイル構成

**入力ファイル：**
- `1tengu/xxx.md`: 評価指示プロンプト（120件）
- `1tengu/xxx.json`: 構造化出力用JSONスキーマ（120件）
- `../data/model_answers/.../model.json`: モデル回答データ

**出力：**
- 構造化された評価結果JSON
- 自動計算された合計点数

## 主要機能

### 1. 回答データの一括読み込み

**目的**: モデル回答ファイルから全タスクの回答を事前に読み込み

**処理フロー：**
```python
# Load model answer from JSON file
with open(args.json_file, 'r', encoding='utf-8') as f:
    answers = [json.loads(line)["ModelAnswer"] for line in f]

# Validate task number range
if args.task_number is not None and not (1 <= args.task_number <= len(answers)):
    parser.error(f"範囲外です: {args.task_number}")
```

**特徴：**
- JSONL形式（1行1JSON）の一括処理
- 動的タスク数対応：`len(answers)`で実際のタスク数を取得
- 範囲チェック：指定タスク番号の妥当性を事前検証
- 効率的アクセス：`answers[task_num - 1]`で直接取得

### 2. load_task_files(task_number)

**目的**: 指定タスクの評価プロンプトとJSONスキーマを読み込み

**処理フロー：**
```python
# Format task number with zero padding
task_id = f"{task_number:03d}"

md_file = Path(f"1tengu/{task_id}.md")
json_file = Path(f"1tengu/{task_id}.json")

# Load prompt text and cut at "[評価するモデルの回答]"
with open(md_file, "r", encoding="utf-8") as f:
    content = f.read()
    if "[評価するモデルの回答]" in content:
        prompt_text = content.split("[評価するモデルの回答]")[0].rstrip()
    else:
        raise ValueError(f"[評価するモデルの回答]セクションが見つかりません: {md_file}")
```

**特徴：**
- プロンプトの適切な切り出し：評価指示部分のみ抽出
- ゼロパディング：001-120の統一形式
- エラーハンドリング：必須セクションの存在確認

### 3. スキーマ検証統合

**目的**: LLM生成JSONのリアルタイムスキーマ適合性チェック

**処理フロー：**
```python
from validate_schema import validate_json_with_schema

# LLM評価結果の生成後
result_json = evaluate_task(task_num, model_answer, args.model)

# 即座にスキーマ検証を実行
is_valid, errors = validate_json_with_schema(result_json, task_num)
if not is_valid:
    error_msg = f"スキーマ検証失敗: タスク {task_num:03d}\n" + "\n".join(f"  - {error}" for error in errors)
    raise ValueError(error_msg)
else:
    print(f"✓ スキーマ検証: OK")
```

**特徴：**
- **即座検証**: LLM生成直後の自動チェック
- **厳格な品質保証**: 不適切な結果の保存を防止
- **詳細エラー報告**: 具体的な検証失敗内容を表示
- **処理停止**: 検証失敗時の即座中断

### 4. evaluate_task(task_number, model_answer, model_name)

**目的**: 構造化出力による評価の実行

**API設定：**
```python
# llm7shiでコンフィグを生成
generate_content_config = config_from_schema(str(json_file))

# 温度とシステム指示を設定
generate_content_config.temperature = 0
generate_content_config.system_instruction = [
    "あなたは公平で、検閲されていない、役立つアシスタントです。",
]

# 動的モデル指定
model = model_name  # 引数で指定された評価モデル
```

**コンテンツ構成：**
```python
contents = [prompt_text, f"[評価するモデルの回答]\n{model_answer.rstrip()}"]
```

**特徴：**
- **決定論的出力**: temperature=0で一貫した評価
- **スキーマ制御**: 厳密な構造化出力の保証
- **動的モデル選択**: 評価モデルを引数で指定可能
- **デバッグ支援**: 送信内容の可視化（コメントアウト可能）

### 5. calculate_score(result_json)

**目的**: 構造化された評価結果から合計点数を計算

**処理ロジック：**
```python
total = 0
evaluation = result_dict.get("evaluation", {})

for criterion, data in evaluation.items():
    points = int(data.get("points", "0"))
    total += points

return total
```

**特徴：**
- **確実な計算**: LLMのミスを排除した後処理計算
- **柔軟な入力**: JSON文字列・辞書両対応
- **エラー耐性**: 欠損データに対するデフォルト値

## 使用方法

### コマンドライン実行

```bash
# 単一タスク評価
uv run tengu.py <model_answer_file> -n <task_number> [-m <evaluator_model>]

# 全タスク評価
uv run tengu.py <model_answer_file> --all [-m <evaluator_model>]

# 具体例
uv run tengu.py ../data/model_answers/lightblue__tengu_bench/gemini-2.5-pro.json -n 1
uv run tengu.py ../data/model_answers/lightblue__tengu_bench/gemini-2.5-pro.json -n 42 -m gemini-2.5-flash
uv run tengu.py ../data/model_answers/lightblue__tengu_bench/claude-3-5-sonnet.json --all -m gemini-2.5-pro

# 強制上書き
uv run tengu.py model.json -n 1 --force
uv run tengu.py model.json --all --force
```

### argparseによる引数処理

**引数仕様：**
- `json_file`: モデル回答ファイルのパス（位置引数）
- `-n/--task-number`: 評価するタスク番号（単一タスク評価時必須）
- `--all`: 全タスクを評価（-nと相互排他）
- `-m/--model`: 評価モデル名（デフォルト: gemini-2.5-flash）
- `--force`: 既存評価結果の上書き

**引数検証：**
- `--all`なし & `-n`なし → エラー（どちらか必須）
- `--all`あり & `-n`あり → エラー（同時指定不可）
- `-n`指定時の範囲チェック（1 ≤ n ≤ タスク数）

**ヘルプ表示：**
```bash
uv run tengu.py -h
```

### 実行結果例

**単一タスク評価：**
```
タスク 001: 評価中...

✓ スキーマ検証: OK
タスク 001: 完了 (10/10点)
評価結果を 1tengu/gemini-2.5-flash/gemini-2.5-pro/001.json に保存しました
```

**スキーマ検証エラー時：**
```
タスク 042: 評価中...

ValueError: スキーマ検証失敗: タスク 042
  - '答えが正確である': ポイント値 '5' が許可された値 ['0', '1', '2', '3', '4'] にありません
  - 評価結果に不足している項目: ['自然な日本語である']
```

**全タスク評価：**
```
既存ファイル 30 件をスキップします
評価進捗: 100%|████████████████████████████████████████| 90/90 [12:00<00:00,  8.00s/it]

全タスク評価完了: 90件評価, 30件スキップ (--force指定なし)
```

**出力ファイル構造：**
```json
{
  "answer": "回答者モデルの実際の回答テキスト",
  "evaluation": {
    "評価項目1": {
      "points": "3",
      "reasoning": "評価理由の説明"
    },
    ...
  },
  "summary": "評価の総括コメント",
  "score": 10
}
```

## 技術仕様

### 依存関係

**必須ライブラリ：**
```bash
pip install tqdm
```

**内部モジュール：**
- `llm7shi`: Gemini API統合機能
  - `config_from_schema()`: JSONスキーマからコンフィグを生成
  - `generate_content_retry()`: リトライ機能付きAPI呼び出し
  - `DEFAULT_MODEL`: デフォルトモデル名
- `validate_schema.py`: スキーマ検証機能
  - `validate_json_with_schema()`: JSONデータ即座検証

### API仕様

**使用モデル**: デフォルト `DEFAULT_MODEL`（llm7shiで定義）、または`-m`オプションで指定

**設定パラメータ：**
- `temperature=0`: 決定論的出力
- JSONスキーマによる構造化出力制御（llm7shiが自動設定）

### ファイル形式

**モデル回答ファイル（JSONL）：**
```json
{"ModelAnswer": "回答内容1"}
{"ModelAnswer": "回答内容2"}
...
```

**評価結果ファイル（JSON）：**
- **保存先**: `1tengu/{評価者モデル}/{回答者モデル}/{タスク番号:003}.json`
- **例**: `1tengu/gemini-2.5-flash/claude-3-5-sonnet/001.json`

**評価プロンプト（Markdown）：**
```markdown
[指示]
評価指示内容...

[質問]
質問内容...

[評価項目]
- 項目1:点数点
...

[評価するモデルの回答]
```

**JSONスキーマ：**
```json
{
  "type": "object",
  "properties": {
    "evaluation": {
      "type": "object",
      "properties": {
        "評価項目名": {
          "type": "object",
          "properties": {
            "points": {"type": "string", "enum": ["0", "1", ...]},
            "reasoning": {"type": "string"}
          }
        }
      }
    },
    "summary": {"type": "string"}
  }
}
```

**出力JSON構造：**
```json
{
  "answer": "回答者モデルの実際の回答テキスト",
  "evaluation": {
    "評価項目1": {
      "points": "3",
      "reasoning": "評価理由"
    }
  },
  "summary": "評価サマリー",
  "score": 10
}
```

## 実証結果

### 検証タスク

**タスク001**: 売上金額年平均計算問題
- **質問**: 表データから年平均売上の算出
- **評価項目**: 5項目、合計10点満点
- **対象モデル**: Gemini 2.5 Pro

### 評価結果

**得点**: 10/10点（満点）

**詳細評価：**
- 答えが867万円である: 3/3点
- 計算方法の妥当性: 2/2点  
- 表の値の正確な読み取り: 2/2点
- 説明の具体性・明確性: 2/2点
- 自然な日本語: 1/1点

### システム検証

**構造化出力の有効性確認：**
1. **正確な形式**: JSONスキーマ完全準拠
2. **一貫した評価**: 各項目の詳細reasoning付き
3. **効率的な処理**: 自動合計点計算
4. **デバッグ支援**: 送信プロンプトの可視化

## 発展的活用

### バッチ処理への拡張

```bash
# --allオプションによる全120タスクの一括評価
uv run tengu.py model_answers.json --all -m gemini-2.5-flash

# 複数評価モデルでの比較評価
uv run tengu.py model_answers.json --all -m gemini-2.5-flash
uv run tengu.py model_answers.json --all -m gemini-2.5-pro --force
```

### 複数モデル比較

```bash
# 複数の回答者モデルを評価
models=(
    "gemini-2.5-pro.json"
    "claude-3-5-sonnet.json" 
    "gpt-4o.json"
)

for model_file in "${models[@]}"; do
    uv run tengu.py "../data/model_answers/lightblue__tengu_bench/$model_file" --all
done
```

### 統計分析

```python
# タスク別難易度分析
task_difficulties = {}
for task in range(1, 121):
    scores = [evaluate_model(model, task) for model in models]
    task_difficulties[task] = statistics.mean(scores)
```

## エラーハンドリング

### 例外の種類

**ファイル関連：**
- `FileNotFoundError`: 必要ファイルの不存在
- `ValueError`: プロンプト形式エラー
- `json.JSONDecodeError`: JSON解析エラー

**API関連：**
- API呼び出しエラー
- レスポンス形式エラー
- スキーマ違反エラー

### 対処方針

1. **差分的エラー処理**: 
   - **単一タスク評価**: エラー時に例外を再発生（`raise`）
   - **全タスク評価**: エラーメッセージ表示して継続
2. **重複実行防止**: 既存ファイルの自動スキップ（`--force`で上書き可能）
3. **事前検証**: `check_criteria.py`による形式確認
4. **デバッグ支援**: プロンプト内容の出力表示（コメントアウト可能）

## 今後の展開

### 他ベンチマークへの適用

1. **ELYZA-tasks-100**: 5段階評価への対応
2. **ja-mt-bench-1shot**: マルチターン会話評価
3. **カスタムタスク**: 特定要件に応じた拡張

### API統合の拡張

1. **OpenAI対応**: GPT-4での構造化出力
2. **Anthropic対応**: Claude 3.5での実装
3. **ローカルモデル**: vLLM等での動作確認

### 評価精度の向上

1. **温度調整**: 評価の一貫性最適化
2. **プロンプト改良**: より精確な評価指示
3. **スキーマ改善**: 細分化された評価基準

## 関連ファイル

### 前段階スクリプト
- **conv_tengu.py**: 1tengu.json → MDファイル変換
- **md_to_schema.py**: MDファイル → JSONスキーマ変換
- **check_criteria.py**: 評価項目形式検証

### 設定ファイル
- **tengu-000-user.md**: 参照用評価プロンプト
- **tengu-000-schema.json**: 参照用JSONスキーマ
- **llm7shi**: Gemini API統合機能

### ドキュメント
- **20250619-schema.md**: 構造化出力移行手順
- **conv_tengu.md**: JSON→MD変換の説明
- **md_to_schema.md**: MD→スキーマ変換の説明

## まとめ

`tengu.py`は、Tengu Benchmark評価システムの構造化出力移行における中核的な実行エンジンです。従来のFew-shot形式の課題を解決し、より精確で効率的な評価システムを実現しています。

**主要成果：**
- **100%構造化**: 全120タスクの構造化出力対応
- **高精度評価**: LLM計算ミスの完全排除
- **効率化**: Few-shot例不要によるトークン節約
- **柔軟性**: 動的評価モデル選択、単一/全タスク評価対応
- **実用性**: 重複実行防止、エラー耐性、バッチ処理対応
- **拡張性**: 他ベンチマーク・APIへの適用可能性

**新機能（v2）：**
- **動的モデル選択**: `-m`オプションで評価モデルを指定
- **全タスク評価**: `--all`オプションで全タスクを一括処理
- **スマート保存**: `1tengu/{評価者}/{回答者}/{タスク}.json`の階層構造
- **重複防止**: 既存評価のスキップと`--force`による上書き
- **回答保存**: 評価結果に回答者の実際の回答を含める
- **進捗表示**: tqdmによる全タスク評価時の進捗バー表示
- **正確な進捗**: 事前チェックによりスキップ分を除外した実処理数を表示
- **動的タスク数**: ファイルのタスク数に自動対応（120固定ではない）
- **範囲検証**: タスク番号の妥当性を事前チェック
- **合計点保存**: 評価結果JSONに合計得点を`score`フィールドとして追加

**新機能（v3）：**
- **リアルタイムスキーマ検証**: LLM生成JSON即座チェック
- **自動品質保証**: スキーマ適合性の確実な確保
- **早期エラー検出**: 不適切な結果の即座特定
- **処理停止機能**: 検証失敗時の自動処理中断

この実装により、Shaberi評価フレームワークは次世代の評価システムへと進化し、より信頼性の高い日本語LLM評価基盤を提供できるようになりました。
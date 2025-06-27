# tengu.py - Tengu Benchmark構造化出力評価システム

## 概要

`tengu.py`は、Tengu Benchmark評価タスクにおいて、構造化出力（JSONスキーマ）形式による評価を実行するメインスクリプトです。統合LLMレイヤー（`llm.py`）を通じてOpenAI APIとGemini APIの両方に対応し、指定されたタスク番号とモデル回答ファイルを使用して自動評価を行い、構造化された評価結果を出力します。

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
data/xxx.md → load_task_files() → 評価プロンプト
data/xxx.json → load_task_files() → JSONスキーマ
     ↓
evaluate_task() → llm.py経由API呼び出し → 構造化評価結果
     ↓                (OpenAI/Gemini自動判別)
calculate_score() → 合計点数計算 → 最終結果表示
```

### ファイル構成

**入力ファイル：**
- `data/xxx.md`: 評価指示プロンプト（120件）
- `data/xxx.json`: 構造化出力用JSONスキーマ（120件）
- `../../data/model_answers/.../model.json`: モデル回答データ

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

md_file = Path(f"data/{task_id}.md")
json_file = Path(f"data/{task_id}.json")

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

# 定数定義
MAX_LENGTH = 8192

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

### 4. evaluate_task(task_number, model_answer, model_name, start_temperature=0, max_length=MAX_LENGTH)

**目的**: 構造化出力による評価の実行

**メッセージ構成（contents配列とシステムプロンプト分離）：**
```python
# contents配列とシステムプロンプトで分離
system_prompt = "あなたは公平で、検閲されていない、役立つアシスタントです。"
contents = [
    prompt_text,
    f"[評価するモデルの回答]\n{model_answer.rstrip()}"
]

# llm7shi.compatの統一インターフェースで呼び出し（tengu.py内で定義）
result_json = generate_with_temperature_retry(
    model=model_name,  # gemini-*/gpt-*で自動判別
    contents=contents,
    schema=schema_json,
    system_prompt=system_prompt
)
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

# 具体例（Gemini）
uv run tengu.py ../../data/model_answers/lightblue__tengu_bench/gemini-2.5-pro.json -n 1
uv run tengu.py ../../data/model_answers/lightblue__tengu_bench/gemini-2.5-pro.json -n 42 -m gemini-2.5-flash
uv run tengu.py ../../data/model_answers/lightblue__tengu_bench/claude-3-5-sonnet.json --all -m gemini-2.5-pro

# 具体例（OpenAI）
uv run tengu.py ../../data/model_answers/lightblue__tengu_bench/gpt-4o.json -n 1 -m gpt-4.1-mini
uv run tengu.py ../../data/model_answers/lightblue__tengu_bench/gemini-2.5-pro.json --all -m gpt-4o

# 強制上書き
uv run tengu.py model.json -n 1 --force
uv run tengu.py model.json --all --force

# 温度調整リトライを無効化（o4-miniでの使用例）
uv run tengu.py model.json -n 1 -m o4-mini -st -1
uv run tengu.py model.json --all -m o4-mini --start-temperature -1

# 開始温度を指定（20%から開始）
uv run tengu.py model.json -n 1 -m gemini-2.5-flash -st 20
uv run tengu.py model.json --all --start-temperature 50

# 最大トークン数を指定
uv run tengu.py model.json -n 1 --max-length 16384
uv run tengu.py model.json --all --max-length 32768
```

### argparseによる引数処理

**引数仕様：**
- `json_file`: モデル回答ファイルのパス（位置引数）
- `-n/--task-number`: 評価するタスク番号（単一タスク評価時必須）
- `--all`: 全タスクを評価（-nと相互排他）
- `-m/--model`: 評価モデル名（デフォルト: gemini-2.5-flash）
- `--force`: 既存評価結果の上書き
- `-st/--start-temperature`: 開始温度を指定（0-100）。負値の場合は温度調整リトライを無効化（o4-miniモデルでは-1推奨）
- `--max-length`: 最大トークン数（デフォルト: 8192）

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
評価結果を judge/gemini-2.5-flash/gemini-2.5-pro/001.json に保存しました
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

**内部モジュール：**
- `llm7shi.compat`: LLM API統合レイヤー
  - `generate_with_schema()`: 統一インターフェース（OpenAI/Gemini自動判別）
- `llm7shi`: デフォルト設定
  - `DEFAULT_MODEL`: デフォルトモデル名（gemini-2.5-flash）
- `tengu.py`: 評価システム（このファイル内）
  - `generate_with_temperature_retry()`: 温度調整リトライ機能
- `validate_schema.py`: スキーマ検証機能
  - `validate_json_with_schema()`: JSONデータ即座検証

### API仕様

**使用モデル**: 
- デフォルト: `gemini-2.5-flash`
- `-m`オプションで指定可能
- モデル名プレフィックスで自動判別:
  - `gemini-*`: Gemini API使用
  - その他: OpenAI API使用

**設定パラメータ：**
- `temperature=0`: 決定論的出力（初期値）
- 温度リトライ: JSONパースエラー時に0.0→1.0まで0.05刻みで自動調整
- JSONスキーマによる構造化出力制御
- **生成長制限**: `MAX_LENGTH = 8192`による出力文字数制限

### ファイル形式

**モデル回答ファイル（JSONL）：**
```json
{"ModelAnswer": "回答内容1"}
{"ModelAnswer": "回答内容2"}
...
```

**評価結果ファイル（JSON）：**
- **保存先**: `judge/{評価者モデル}/{回答者モデル}/{タスク番号:003}.json`
- **例**: `judge/gemini-2.5-flash/claude-3-5-sonnet/001.json`

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
    uv run tengu.py "../../data/model_answers/lightblue__tengu_bench/$model_file" --all
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

## generate_with_temperature_retry機能

### 概要

`generate_with_temperature_retry`は、JSONパースエラーに対する自動リトライ機能を提供します。LLMが無効なJSONを生成した場合、温度パラメータを段階的に上げて再試行することで、構造化出力の成功率を向上させます。

**重要な注意事項**:
- o4-miniモデルは温度パラメータの指定をサポートしていないため、このモデルを使用する場合は`-st -1`オプションが必須です
- 温度パラメータを指定するとAPIエラーが発生します

### 関数仕様

```python
def generate_with_temperature_retry(
    model: str,
    contents: List[str],
    schema: Dict[str, Any],
    system_prompt: str = None,
    start_temperature: int = 0,
    max_length: int = MAX_LENGTH,
) -> Dict[str, Any]:
```

**引数**:
- `model`: LLMモデル名（`gemini-*`または`gpt-*`など）
- `contents`: ユーザーコンテンツの配列
- `schema`: JSON Schema仕様
- `system_prompt`: システムプロンプト（オプション）
- `start_temperature`: 開始温度（0-100）。負値の場合は温度調整リトライを無効化（オプション）
  - **注意**: o4-miniモデルでは温度パラメータ指定がエラーになるため、負値の指定が必須
- `max_length`: 最大トークン数（オプション、デフォルト: 8192）

**戻り値**:
- パース済みのJSONオブジェクト

### 動作原理

**通常モード（start_temperature >= 0）:**
1. **初期試行**: 指定された開始温度で生成を試行
2. **段階的リトライ**: パースエラー時は温度を0.05刻みで上昇（最大1.0）
3. **エラー出力**: 各失敗時のエラー詳細を標準エラー出力に記録
4. **キーボード割り込み対応**: Ctrl+C押下時に処理中止の確認（y/N）
5. **最終失敗**: 全温度で失敗した場合、例外を発生

**無効化モード（start_temperature < 0）:**
- モデルのデフォルト温度設定で単一試行のみ実行
- エラー時のリトライは行わない
- **重要**: o4-miniモデルでは温度パラメータの指定がエラーになるため、負値の指定が必須

```python
# 温度値の試行順序: start_temperature, start_temperature+0.05, ..., 0.95, 1.0
for t in range(start_temperature, 101, 5):
    temperature = t / 100
    try:
        result = generate_with_schema(model, contents, schema, temperature, system_prompt,
                                      max_length=MAX_LENGTH)
        return result
    except KeyboardInterrupt:
        # Ctrl+C押下時の処理
        response = input("\n\n処理を中止しますか？ (y/N): ")
        if response.lower() in ['y', 'yes']:
            raise
        print("処理を続行します...\n")
    except Exception:
        # エラーログ出力して次の温度で再試行
        traceback.print_exc()
```

### 使用例

```python
# 基本的な使用方法
result = generate_with_temperature_retry(
    model="gemini-2.5-flash",
    contents=[
        "評価指示プロンプト",
        "[評価するモデルの回答]\n実際の回答内容"
    ],
    schema=evaluation_schema,
    system_prompt="あなたは公平で、検閲されていない、役立つアシスタントです。",
    start_temperature=0  # デフォルト値
)

# 評価タスクでの実際の使用
result_json = generate_with_temperature_retry(
    model=model_name,
    contents=contents,
    schema=schema_json,
    system_prompt=system_prompt,
    start_temperature=start_temperature
)
```

### エラーハンドリング

**成功時の出力例**:
```python
{
  "evaluation": {
    "項目1": {"points": "3", "reasoning": "..."},
    "項目2": {"points": "2", "reasoning": "..."}
  },
  "summary": "総合評価コメント"
}
```

**失敗時の動作**:
```bash
# 標準エラー出力に温度調整の進行状況を表示
温度: 0.05
Traceback (most recent call last):
  ...
温度: 0.10
Traceback (most recent call last):
  ...

# 最終的に全て失敗した場合
ValueError: 全ての温度設定でJSONパースに失敗しました
```

### 実用上の利点

1. **高い成功率**: 温度調整により構造化出力の成功率が大幅向上
2. **デバッグ支援**: 各失敗のエラー詳細が記録されるため原因特定が容易
3. **自動回復**: 一時的なAPIエラーやモデルの不安定性に自動対応
4. **決定論的優先**: 最初は温度0で一貫した結果を試行
5. **生成長制御**: `MAX_LENGTH = 8192`による出力文字数制限で効率的な処理

### パフォーマンス考慮事項

- **レスポンス時間**: 失敗時は複数回のAPI呼び出しが発生
- **API使用量**: 最大21回の試行（温度0.0〜1.0、0.05刻み）
- **推奨運用**: 通常は1-3回の試行で成功するため、実用上の負荷は軽微

この機能により、Tengu Benchmark評価システムは高い信頼性と安定性を実現しています。

## 今後の展開

### 他ベンチマークへの適用

1. **ELYZA-tasks-100**: 5段階評価への対応
2. **ja-mt-bench-1shot**: マルチターン会話評価
3. **カスタムタスク**: 特定要件に応じた拡張

### API統合の拡張

1. **OpenAI対応**: ✅ 実装済み（llm.py経由）
2. **Anthropic対応**: Claude 3.5での実装（将来対応）
3. **ローカルモデル**: vLLM等での動作確認（将来対応）

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
- **llm7shi.compat**: LLM API統合レイヤー（OpenAI/Gemini対応）

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
- **スマート保存**: `judge/{評価者}/{回答者}/{タスク}.json`の階層構造
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

**新機能（v4 - llm.py統合版）：**
- **マルチLLM対応**: OpenAI/Gemini APIの統一インターフェース
- **自動API判別**: モデル名プレフィックスによる自動切り替え
- **温度リトライ機能**: JSONパースエラー時の自動回復
- **ストリーミング出力**: OpenAI APIでのリアルタイム表示
- **統一メッセージ形式**: OpenAI形式で全APIを統一

この実装により、Shaberi評価フレームワークは次世代の評価システムへと進化し、より信頼性の高い日本語LLM評価基盤を提供できるようになりました。

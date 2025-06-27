# ELYZA評価ユーティリティ (elyza_utils.py)

## 背景

ELYZA-tasks-100評価システムでは、100個のタスクそれぞれに固有の評価基準を持つjudge関数が存在します。これらの関数は以下の構造を持ちます：

```python
def judge_001(score: int, judge: callable) -> int:
    if judge("熱意を取り戻すのではなく、仕事の効率化・スキルアップのような文脈になっている"):
        score -= 1
    if judge("出したアイデアが5つより多い、または少ない"):
        score -= 1
    if judge("5つのアイデアのうち、内容が重複しているものがある"):
        score -= 1
    return score
```

従来の課題：
- judge関数の引数（評価項目）を手動で管理する必要があった
- 動的にjudge関数を取得する仕組みが不足していた
- 評価項目の一覧を取得する統一的な方法がなかった

## 解決アプローチ

### 1. ASTベースの引数抽出

正規表現ではなくPythonのASTパーサーを使用してjudge()呼び出しの引数を確実に抽出：

```python
def extract_judge_args_from_ast(code: str) -> List[str]:
    """ASTを使ってjudge()呼び出しの引数を抽出"""
    tree = ast.parse(code)
    
    class JudgeCallVisitor(ast.NodeVisitor):
        def visit_Call(self, node):
            if (isinstance(node.func, ast.Name) and 
                node.func.id == 'judge' and 
                len(node.args) == 1):
                # 文字列リテラルを抽出
                if isinstance(node.args[0], ast.Constant):
                    judge_args.append(node.args[0].value)
```

**利点：**
- 構文解析エラーがない
- 複雑な文字列リテラルにも対応
- Pythonの言語仕様に完全準拠

### 2. 動的関数取得システム

`inspect`モジュールと`rubrics.py`のインポートを組み合わせた動的取得：

```python
def get_judge_function_and_args(task_number: int) -> Tuple[Optional[Callable], List[str]]:
    """タスク番号からcallableとjudge_argsを返す"""
    import rubrics
    
    function_name = f"judge_{task_number:03d}"
    if hasattr(rubrics, function_name):
        judge_function = getattr(rubrics, function_name)
        source_code = inspect.getsource(judge_function)
        judge_args = extract_judge_args_from_ast(source_code)
        return judge_function, judge_args
```

**利点：**
- 関数名の文字列lookup不要
- ソースコードからリアルタイムで引数抽出
- 型安全性の確保

## 機能概要

### 評価系機能

1. **`calculate_score(result_json, task_number)`**
   - 構造化出力から最終スコア（1-5点）を計算
   - judge関数による問題固有減点と共通減点を適用
   - KeyErrorで無効なjudgeクエリを検出

2. **`load_and_prepare_schema(task_number)`**
   - ベーススキーマを読み込み、タスク固有フィールドを動的追加
   - judge関数の引数をq1, q2, q3...として自動展開

3. **`log_calls(func)`**
   - judge関数の呼び出しをログ出力するデコレーター
   - デバッグとトレーシング用途

### judge関数管理機能

4. **`get_judge_function_and_args(task_number)`**
   - タスク番号から(judge関数, 引数リスト)のタプルを返す
   - 最も重要なAPI関数

5. **`extract_judge_args_from_ast(code)`**
   - ASTを使用したjudge()引数の抽出
   - 内部関数として使用

6. **`list_available_judges()`**
   - 利用可能なjudge関数の一覧取得
   - デバッグ・管理用途

7. **`test_judge_function(task_number)`**
   - judge関数のテスト実行
   - 開発・検証用途

### コマンドラインインターフェース

```bash
# 利用可能なjudge関数一覧
uv run elyza_utils.py --list

# 特定タスクの引数表示
uv run elyza_utils.py --get-args 1

# 特定タスクのテスト実行
uv run elyza_utils.py --test 1
```

## 使用例

### 基本的な使用方法

```python
from elyza_utils import calculate_score, load_and_prepare_schema

# 1. スキーマ生成とLLM評価
schema = load_and_prepare_schema(task_number=1)
result_json = llm_generate_with_schema(prompt, schema)

# 2. スコア計算
final_score = calculate_score(result_json, task_number=1)
print(f"最終スコア: {final_score}/5点")

# 3. 低レベルAPIの使用例
from elyza_utils import get_judge_function_and_args

judge_func, judge_args = get_judge_function_and_args(1)
if judge_func:
    print(f"関数名: {judge_func.__name__}")
    print(f"評価項目: {len(judge_args)}個")
    for i, arg in enumerate(judge_args):
        print(f"  {i+1}. {arg}")
```

### バッチ処理での活用

```python
# 全タスクの評価項目を一覧表示
from elyza_utils import list_available_judges, get_judge_function_and_args

available_tasks = list_available_judges()
for task_num in available_tasks:
    judge_func, judge_args = get_judge_function_and_args(task_num)
    print(f"タスク{task_num:03d}: {len(judge_args)}個の評価項目")
```

## 技術的な特徴

### ASTパーサーの活用

- **確実性**: 正規表現による文字列操作より確実
- **拡張性**: 将来的に複雑な式の解析も可能
- **保守性**: Pythonの構文変更に自動対応

### 動的インポートシステム

- **柔軟性**: rubrics.pyの変更に自動対応
- **型安全性**: 関数の存在確認とcallable検証
- **エラーハンドリング**: 適切な例外処理とフォールバック

### モジュラー設計

- **単一責任**: 各関数が明確な役割を持つ
- **テスタビリティ**: 独立したテスト関数を提供
- **再利用性**: 他のプロジェクトでも活用可能

## ファイル構成

```
experimental/2elyza/
├── elyza_utils.py          # メインユーティリティ
├── elyza_utils.md          # このドキュメント
├── rubrics.py              # 自動生成されたjudge関数集
├── conv_rubrics.py         # rubrics.py生成ツール
└── data/                   # 元となる評価基準ファイル
    ├── 001.md
    ├── 002.md
    └── ...
```

## 今後の拡張可能性

1. **評価項目の重み付け対応**
   - judge()呼び出しの重要度を解析
   - 重み付きスコア計算のサポート

2. **評価結果の詳細分析**
   - どの評価項目で減点されたかの追跡
   - 評価項目別の統計情報収集

3. **他の評価システムとの統合**
   - 汎用的な評価フレームワークへの拡張
   - 他のベンチマークへの適用

## 関連ファイル

- `conv_rubrics.py`: judge関数生成ツール
- `rubrics.py`: 自動生成されたjudge関数集
- `data/*.md`: 各タスクの評価基準定義
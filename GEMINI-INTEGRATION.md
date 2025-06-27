# Shaberi フレームワークの実用化：4段階の改修プロセスで実現したGemini完全対応

## はじめに

Shaberi（しゃべり）日本語LLM評価フレームワークにおけるGemini API対応改修は、「まず動作させてから整理する」という現実的なアプローチで段階的に進められました。mainブランチでは既にGemini APIの「対応」が行われていましたが、実際の運用では深刻な制約と問題が存在していました。本記事では、`for-gemini`ブランチで実施された4つのステップからなる改修プロセスを、実際の作業順序に沿って詳しく解説します。

## ステップ1：回答生成の実用化

最初のステップでは、コメントアウトされていたGeminiコードを手動で有効化することから始まりました。ハードコーディングされていたモデル名を動的指定に修正し、任意のGeminiモデルに対応できるようにしました。

```python
# コメントアウトされていたGeminiコードを手動で有効化
# + ハードコーディングされたモデル名を修正
response = completion(
    model=f"gemini/{model_name}",  # "gemini-1.5-flash" → 動的指定
    messages=[...],
    ...
)
```

しかし、実際にshaberi3（280問）で評価を実行すると、90-105個という大量のnull結果が発生することが判明しました。詳細な調査により、これは思考モデルがトークン制限によって途中で切断されていることが原因であることが分かりました。

```python
# mainブランチの制限
generation_max_tokens = 1500  # → null結果の原因

# 修正後（デフォルト値は互換性のため維持）
generation_max_tokens = 1500  # デフォルト値
# コマンドラインで指定可能
# uv run generate_answers.py -m model-name -t 131072
```

この問題を根本的に解決するため、トークン制限を131072まで大幅に拡張しました。ただし、過去の互換性を保つため、デフォルト値は従来の1500トークンのままとし、コマンドラインオプション`-t`/`--max-tokens`で柔軟に変更できる仕組みを導入しました。この修正により、null問題は完全に解決され、思考モデル時代における大容量トークン需要の実証にもつながりました。正常動作を確認した後、手動切り替えを自動化するため、モデル名に"gemini"が含まれているかどうかで自動的に適切なAPI関数を選択する仕組みを実装しました。

```python
# 手動切り替えの自動化
def get_answer(question: str, model_name: str) -> str | None:
    if "gemini" in model_name:
        content = get_answer_from_litellm_gemini(question, model_name)
    else:
        content = get_answer_from_openai(question, model_name)
    return content
```

また、この段階で以下の重要な変更も実装されました：

- **関数リネーム**: `get_answer`を`get_answer_from_openai`にリネームし、新しい`get_answer`で自動切り替えを実装
- **コメントアウト解除**: Geminiコードブロック全体をコメントアウトから解除し、独立した`get_answer_from_litellm_gemini`関数として実装
- **`get_model_answer`の簡略化**: `get_answerer`関数を削除し、直接`get_answer`を呼び出すシンプルな構造に変更
- **コマンドライン引数の追加**: `generate_answers.py`に`-t`/`--max-tokens`オプションを追加し、実行時にトークン数を動的に設定可能に

```python
# generate_answers.pyに追加されたコマンドライン引数
parser.add_argument('-t', '--max-tokens', type=int, default=llm_functions.generation_max_tokens)
# 設定の反映
llm_functions.generation_max_tokens = args.max_tokens
```

## ステップ2：評価生成への展開

回答生成での成功を受けて、次に評価ステップでも同様のトークン制限対応を実施しました。

```python
# 回答生成と同様に evaluation_max_tokens も拡張
evaluation_max_tokens = 1024  # → 制限的

# 修正後（デフォルト値は互換性のため維持）
evaluation_max_tokens = 1024  # デフォルト値
# コマンドラインで指定可能
# uv run judge_answers.py -m model-name -t 131072
```

また、この段階で評価用のGemini関数でもハードコーディングされたモデル名を動的指定に修正しました：

```python
# 評価用Gemini関数でも動的モデル名に対応
response = completion(
    model=f"gemini/{model_name}",  # "gemini-1.5-flash" → 動的指定
    messages=add_messages,
    ...
)
```

同時に、`judge_answers.py`にも同様の改良を実施しました：

- **llm_functionsのインポート追加**: 評価用トークン制限にアクセス可能に
- **`--max-tokens`オプション追加**: 評価時の最大トークン数を動的に設定可能
- **shaberi3対応**: 3つの主要ベンチマーク（tengu_bench、ELYZA-tasks-100、ja-mt-bench-1shot）をまとめて評価する機能

```python
# judge_answers.pyに追加されたコマンドライン引数
parser.add_argument('-t', '--max-tokens', type=int, default=llm_functions.evaluation_max_tokens)
# 設定の反映
llm_functions.evaluation_max_tokens = args.max_tokens

# shaberi3対応の評価データセット選択
if eval_dataset_name == "shaberi3":
    eval_dataset_names = [
        "lightblue/tengu_bench",
        "elyza/ELYZA-tasks-100", 
        "shisa-ai/ja-mt-bench-1shot"
    ]
```

しかし、トークン制限を解決しても新たな問題が発見されました。評価ステップでは、LLMが評価結果を指定されたフォーマットで出力できない場合にパース失敗が発生し、少数ながらもスコアがnullになるケースが残りました。この問題は単純なパラメータ調整では解決できない、より構造的な課題であることが明らかになりました。

## ステップ3：構造の見直し

第3ステップでは、パース失敗問題に対処するため、評価システムの根本的な構造見直しを行いました。mainブランチでは、ベンチマークごとに異なる評価出力フォーマットに対応するため、各評価関数内にスコア抽出処理が埋め込まれた構造になっていました。しかし、この設計では温度を変更してリトライする仕組みが実装できませんでした。

```python
# mainブランチの評価関数例（パースが埋め込まれた構造）
def elyza_evaluator(data: dict, model_name:str) -> int|None:
    prompt = get_elyza_prompt(data)
    messages = [{"role": "user", "content": prompt}]
    evaluation = get_model_response(messages, model_name)  # 固定温度で生の文字列を返す
    logger.info(evaluation)
    try:
        gpt4score = int(evaluation)  # パース処理が埋め込まれている
    except ValueError:
        try:
            logger.info('Parse error, trying again...')  # 手動リトライ（無意味）
            gpt4score = int(evaluation)  # 同じ結果を再度パース
        except ValueError:
            gpt4score = None
    return gpt4score
```

この構造的限界を解決するため、スコア抽出を独立した関数として分離し、それをパーサー関数として`get_model_response`に渡すという新しいアーキテクチャを構築しました。これにより、パース失敗時に温度を段階的に上げて再試行する温度調整リトライシステムの開発が可能になりました。

```python
# for-geminiブランチの改善された構造
def elyza_evaluator(data: dict, model_name:str) -> int|None:
    prompt = get_elyza_prompt(data)
    messages = [{"role": "user", "content": prompt}]
    
    # スコア抽出を独立した関数として定義
    def parse_int_with_log(evaluation):
        logger.info(evaluation)
        return int(evaluation)
    
    # パーサー関数を渡してリトライ機能付きで実行
    result = get_model_response(messages, model_name, parse_int_with_log)
    return result
```

具体的には、評価関数内でスコア抽出ロジックを独立した関数として定義し、それを`get_model_response`の`parser_func`パラメータとして渡すことで、LLMによる評価生成とスコア抽出を分離しました。

さらに、この改良で実装された重要な機能が温度調整リトライシステムです：

```python
def get_model_response(messages: list, model_name: str, parser_func):
    # 温度を段階的に上げながらリトライ
    for t in range(0, 101, 5):
        evaluation_temperature = t / 100
        response = answer_function(messages, model_name, evaluation_temperature)
        
        try:
            result = parser_func(response)
            if result:
                return result
        except Exception:
            if t < 100:
                logger.info("Parse error, trying again...")
            pass
    return None
```

パース失敗時に温度を0.0から1.0まで0.05刻みで段階的に上げながら再試行することで、評価の堅牢性が大幅に向上し、パース失敗による評価エラーを自動的に回復できるようになりました。

また、保守性向上のため`NO_RESPONSE = "No response received"`定数を導入し、ハードコーディングされた文字列をすべて統一しました。

この構造見直しにより、`evaluation_datasets_config.py`内のすべての評価関数が新しいアーキテクチャに移行されました：

- **tengu_bench_evaluator**: 正規表現ベースのパース処理を`get_tengu_eval_score`関数として分離
- **elyza_evaluator**: シンプルなint変換を`parse_int_with_log`関数として分離  
- **mt_evaluator**: MT-Bench特有のフォーマット処理を`parse_mt_score`関数として分離
- **rakuda_evaluator**: Rakuda特有のフォーマット処理を`parse_rakuda_score`関数として分離
- **do_not_answer_evaluator**: 安全性評価の特殊フォーマット処理を`parse_do_not_answer_score`関数として分離

各評価関数で無意味な手動リトライコードが削除され、代わりに`get_model_response`の温度調整リトライシステムに処理が委譲されるようになりました。これにより、評価の堅牢性が全ベンチマークで統一的に向上しました。

## ステップ4：ロギングシステムの整理

動作面での修正が完了した後、第4ステップとして品質向上とメンテナンス性改善を目的としたロギングシステムの包括的な整理を実施しました。mainブランチでは廃止予定のAPIを使用しており、膨大な詳細ログが無制限に出力されることで重要な情報が埋もれ、開発効率が低下していました。

```python
# mainブランチの問題
import litellm
litellm.set_verbose=True  # 廃止予定（obsolete）のAPI
# → 膨大な詳細ログが無制限に出力される
```

この問題を解決するため、まず廃止予定APIから現代的なログ制御方法への移行を行いました。

```python
# 廃止予定のAPIを現代的な方法に変更
import os
os.environ["LITELLM_LOG"] = "WARNING"  # 環境変数によるログレベル制御

import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")
```

さらに、ロガーレベルの体系的整理を実施し、統一されたログシステムを構築しました。

```python
# 統一されたログレベル管理
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
default_console_level = logging.WARNING  # コンソール出力を抑制

def setup_logging(model_name: str, log_prefix: str = "log", 
                  console_level: int = default_console_level):
    # ファイル: DEBUGレベル（詳細記録）
    # コンソール: WARNING/INFOレベル（重要情報のみ）
```

詳細なデバッグ情報はファイルに記録しつつ、コンソールには重要な情報のみを表示する仕組みを実装しました。この整理により、開発者は必要に応じて詳細ログを確認できる一方で、通常の作業では重要な情報に集中できるようになりました。

## 改修完了と成果

この4段階の改修プロセスにより、Shaberiはmainブランチの「一応対応」から「実用的な完全対応」へと進化しました。回答生成から評価まで完全なサイクルをGeminiで安定実行できるようになり、あらゆるGeminiモデルとバリアントに動的対応可能となりました。

特に重要な発見は、思考モデル時代では従来想定（1,500トークン）を大幅に超える容量（131,072トークン）が必要であることを実証できたことです。この知見を元に、コマンドラインオプションでトークン数を柔軟に設定できる機能を追加しました。温度調整リトライによる評価失敗の自動回復機能と、統一されたログシステムの導入により、フレームワークの堅牢性と保守性も大幅に向上しました。

この段階的改修アプローチは、複雑なシステムの実用化において「動作させてから整理する」という現実的な開発手法の有効性を示すケーススタディとしても価値があります。各ステップで発見された問題とその解決策は、今後の評価フレームワーク設計における重要な知見となるでしょう。

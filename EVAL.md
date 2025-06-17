# 評価システムのリファクタリング詳細

## 概要
2025年6月17日に実施した評価システムの大規模リファクタリングの詳細を記録します。

## 背景と課題
従来の実装では、評価結果のパース失敗時に同じ処理を単純に繰り返していました：

```python
# 旧実装例（意味のないリトライ）
try:
    score = int(evaluation)
except ValueError:
    try:
        logger.info('Parse error, trying again...')
        score = int(evaluation)  # 同じ値で再試行しても結果は変わらない
    except ValueError:
        logger.info("Parse error")
        score = None
```

この問題を解決するため、LLMの温度パラメータを段階的に上げながらリトライする仕組みを導入しました。

## 主な変更点

### 1. llm_functions.pyの変更

#### 1.1 OpenAI関数の温度パラメータ対応
```python
# 旧
def get_response_from_openai(messages: list, model_name: str) -> str:
    evaluation_temperature = 0  # 固定値

# 新
def get_response_from_openai(messages: list, model_name: str, evaluation_temperature: float = 0) -> str:
    # 温度パラメータを引数として受け取れるように変更
```

#### 1.2 get_model_response関数の拡張
```python
# 旧
def get_model_response(messages: list, model_name: str) -> str:
    answer_function = get_response_func(model_name)
    return answer_function(messages, model_name)

# 新
def get_model_response(messages: list, model_name: str, parser_func):
    """
    モデルの応答を取得し、パーサー関数で処理する
    パース成功まで温度を上げながらリトライ
    """
    answer_function = get_response_func(model_name)
    
    # 温度を段階的に上げながらリトライ
    for t in range(0, 101, 5):
        evaluation_temperature = t / 100
        logger.info(f"temperature: {evaluation_temperature:.2f}")
        
        # 関数に温度パラメータを渡す
        response = answer_function(messages, model_name, evaluation_temperature)
        if not response or response == NO_RESPONSE:
            continue
        
        try:
            # パース試行
            result = parser_func(response)
            if result:
                return result
        except Exception as e:
            # 次の温度で試行を続ける
            pass
        
        if t < 100:
            logger.info(f"Parse error, trying again...")
    
    return None
```

### 2. evaluation_datasets_config.pyの変更

#### 2.1 各評価関数の統一的な実装パターン
全ての評価関数を以下のパターンに統一しました：

```python
def xxx_evaluator(data: dict, model_name: str) -> int|None:
    prompt = get_xxx_prompt(data)
    messages = [{"role": "user", "content": prompt}]
    
    def parse_xxx_score(evaluation: str) -> int|None:
        """評価結果をパースしてスコアを抽出"""
        logger.info(evaluation)
        try:
            # 各評価タイプに応じた正規表現でスコアを抽出
            # ...
            return int(score)
        except (ValueError, AttributeError):
            return None
    
    result = get_model_response(messages, model_name, parse_xxx_score)
    if result is None:
        logger.info(f"Parse error.\n\nInput was {data}.")
    return result
```

#### 2.2 変更された評価関数
- `tengu_bench_evaluator`: `get_tengu_eval_score`をパーサーとして直接渡す形に変更
- `elyza_evaluator`: ログ出力付きのintパーサーをローカル関数として定義
- `mt_evaluator`: ローカルパーサー関数`parse_mt_score`を定義
- `rakuda_evaluator`: ローカルパーサー関数`parse_rakuda_score`を定義
- `do_not_answer_evaluator`: ローカルパーサー関数`parse_do_not_answer_score`を定義

## 技術的な設計判断

### 1. ジェネレーターからコールバックへ
当初はジェネレーターを使った実装を検討しましたが、最終的にコールバック（パーサー関数）方式を採用しました。理由：
- よりシンプルで理解しやすい
- 既存のコードとの互換性が高い
- パーサー関数を柔軟に定義できる

### 2. パーサー関数の必須化
`get_model_response`の新しい仕様では、`parser_func`を必須パラメータにしました。これにより：
- 呼び出し側で必ずパース処理を意識する必要がある
- 温度調整リトライの恩恵を受けられる
- コードの一貫性が向上

### 3. ローカル関数としてのパーサー
パーサー関数を各評価関数内のローカル関数として定義することで：
- 名前空間の汚染を防ぐ
- 各評価関数の独立性を保つ
- 必要に応じてクロージャーを活用できる

## 効果
このリファクタリングにより、以下の効果が期待されます：

1. **評価の成功率向上**: 温度を上げることで、より多様な応答フォーマットに対応
2. **コードの統一性**: 全ての評価関数が同じパターンで実装
3. **デバッグの容易さ**: 温度ログにより、どの段階で成功/失敗したかが明確
4. **拡張性**: 新しい評価関数を追加する際のパターンが明確

## 注意事項
- このリファクタリングにより、既存の`get_model_response`を直接呼び出すコードは動作しなくなります
- パーサー関数は必ず指定する必要があります
- 温度を上げすぎると、LLMの応答品質が低下する可能性があるため、最大温度は1.0に制限しています
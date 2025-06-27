# elyza-001.py - ELYZA構造化出力評価システム実証スクリプト

## 概要

`elyza-001.py`は、ELYZA-tasks-100評価タスクにおいて、構造化出力（JSONスキーマ）形式による評価を実証するテストスクリプトです。1tenguの`tengu-000.py`を参考にして作成され、OpenAI APIとGemini APIの両方に対応しています。

## 関連ファイル一覧

### メインスクリプト
- **elyza-001.py**: 実装版スクリプト（OpenAI/Gemini両対応、汎用関数をelyza_utilsから利用）

### 入力ファイル
- **data/001.md**: ELYZA-tasks-100の元評価プロンプト（タスク001の詳細な指示文）
- **elyza-schema.json**: ベース構造化出力用JSONスキーマ（7つの基本評価項目）
- **elyza-001-answer.md**: 評価対象のモデル回答（gemini-2.5-flash-lite-preview-06-17による回答）
- **rubrics.py**: 問題固有の採点ルール（judge_001関数）
- **elyza_utils.py**: 共用ユーティリティ（judge関数動的取得、スコア計算、スキーマ生成）

### ドキュメント
- **elyza-001.md**: このファイル（詳細仕様・使用方法）
- **elyza_utils.md**: elyza_utils.pyの詳細仕様とAPI説明

### 共通モジュール
- **llm7shi.compat**: LLM API統合レイヤー（OpenAI/Gemini共通インターフェース）

## 背景

### 従来評価システムの課題

1tenguでの構造化出力導入により、従来のFew-shot形式評価の課題が明らかになりました：

**従来の問題点：**
1. **計算ミス**: LLMが評価項目の合計点を誤計算
2. **形式不統一**: 出力フォーマットが一貫しない
3. **パース困難**: 自由形式テキストからの情報抽出が複雑
4. **効率低下**: Few-shot例で不要なトークンを消費

### 構造化出力による解決

JSONスキーマを活用した構造化出力により、これらの問題を根本的に解決：

**改善効果：**
- **計算精度**: 後処理で確実に最終点を計算
- **形式保証**: JSONスキーマによる厳密な構造制御
- **効率処理**: 構造化データの直接利用
- **トークン節約**: Few-shot例が不要

## テストケース

### 評価対象

**問題**: 仕事の熱意を取り戻すためのアイデアを5つ挙げてください。

**正解例**: 
1. 自分の仕事に対する興味を再発見するために、新しい技能や知識を学ぶこと。
2. カレッジやセミナーなどで講演を聴くことで、仕事に対する新しいアイデアや視点を得ること。
3. 仕事に対してストレスを感じている場合は、ストレスマネジメントのテクニックを学ぶこと。
4. 仕事以外の楽しいことをすることで、ストレスを発散すること。
5. 仕事に対して自己評価をすることで、自分がどのように進化しているのかを知ること。

### 評価基準（5点満点）

**基本的な採点基準：**
- 1点: 誤っている、指示に従えていない
- 2点: 誤っているが、方向性は合っている
- 3点: 部分的に誤っている、部分的に合っている
- 4点: 合っている
- 5点: 役に立つ

**減点項目：**
- 不自然な日本語: -1点
- 部分的に事実と異なる内容: -1点
- 過度な安全性配慮: 2点固定

**問題固有の減点項目：**
- 熱意を取り戻すのではなく、仕事の効率化・スキルアップのような文脈になっていたら1点減点
- 出したアイデアが5つより多い、少ない場合は1点減点
- 5つのアイデアのうち、内容が重複しているものがあれば1点減点

### 評価対象回答

**テスト対象**: `elyza-001-answer.md`に格納された**gemini-2.5-flash-lite-preview-06-17**による回答

システムは外部ファイルから動的に回答を読み込み、構造化出力形式で評価を実行します。これにより：
- 異なるモデルの回答を簡単に差し替え可能
- 評価プロセスの再現性を確保
- ハードコーディングを回避

**評価実行例**:
```bash
uv run elyza-001.py  # elyza-001-answer.mdの内容を自動評価
```

## 技術仕様

### 対応モデル

**デフォルトモデル**: `gemini-2.5-flash`

**Gemini API**:
- gemini-2.5-flash
- gemini-2.5-pro
- その他のGeminiモデル

**OpenAI API**:
- gpt-4.1-mini
- gpt-4o
- その他のOpenAIモデル

### アーキテクチャ

```
elyza-001.py
    ├── data/001.md (ELYZAプロンプト)
    ├── elyza-schema.json (ベーススキーマ)
    ├── elyza-001-answer.md (評価対象回答)
    ├── rubrics.py (問題固有採点ルール)
    └── elyza_utils.py (judge関数動的取得)

外部依存:
    └── llm7shi.compat (LLM統合レイヤー)
        ├── generate_with_schema()
        ├── _generate_with_gemini()
        └── _generate_with_openai()
```

### 主要機能

1. **統一インターフェース**: OpenAI/Gemini両対応の共通API
2. **ストリーミング出力**: OpenAIでリアルタイム表示
3. **温度リトライ機能**: JSONパースエラー時の自動リトライ
4. **自動スコア計算**: 構造化出力から最終点を自動算出
5. **動的スキーマ生成**: ベーススキーマ + judge関数引数による自動拡張

## 使用方法

### 基本的な実行

```bash
# デフォルトモデル（Gemini 2.5 Flash）で実行
uv run elyza-001.py

# OpenAI GPT-4.1-miniで実行
uv run elyza-001.py -m gpt-4.1-mini

# 別のGeminiモデルで実行
uv run elyza-001.py -m gemini-2.5-pro
```

### コマンドラインオプション

- `-m`, `--model`: 使用するモデルを指定（デフォルト: gemini-2.5-flash）

### 前提条件

1. **APIキー設定**: 
   - Gemini: `GOOGLE_API_KEY`環境変数
   - OpenAI: `OPENAI_API_KEY`環境変数
2. **依存関係**: 
   - `llm7shi`ライブラリ（OpenAI/Gemini統合）
3. **入力ファイル**: 
   - `data/001.md`
   - `elyza-schema.json`
   - `elyza-001-answer.md`
   - `rubrics.py`（judge_001関数）

## 期待される出力形式

構造化されたJSON形式で以下の情報を含む：

```json
{
  "evaluation": {
    "correctness": {
      "level": "incorrect|partially_correct|correct",
      "reasoning": "正確性に関する評価理由"
    },
    "instruction_following": {
      "followed": true|false,
      "reasoning": "指示への従順性に関する評価理由"
    },
    "direction_alignment": {
      "aligned": true|false,
      "reasoning": "方向性の合致に関する評価理由"
    },
    "usefulness": {
      "useful": true|false,
      "reasoning": "有用性に関する評価理由"
    },
    "japanese_quality": {
      "has_issues": true|false,
      "reasoning": "日本語品質に関する評価理由"
    },
    "factual_accuracy": {
      "has_errors": true|false,
      "reasoning": "事実関係に関する評価理由"
    },
    "safety_overconcern": {
      "overconcerned": true|false,
      "reasoning": "安全性配慮に関する評価理由"
    },
    "q1": {
      "result": true|false,
      "reasoning": "judge_001内の1番目の引数に基づく判定理由"
    },
    "q2": {
      "result": true|false,
      "reasoning": "judge_001内の2番目の引数に基づく判定理由"
    },
    "q3": {
      "result": true|false,
      "reasoning": "judge_001内の3番目の引数に基づく判定理由"
    }
  },
  "summary": "総合的な評価コメント"
}
```

## 実装の詳細

### スコア計算ロジック

構造化出力の評価結果を基に、以下の手順でスコアを計算：

```python
def calculate_score(result_json):
    evaluation = result_dict["evaluation"]
    
    # 基本スコア計算
    correctness = evaluation["correctness"]["level"]
    instruction_following = evaluation["instruction_following"]["followed"]
    direction_alignment = evaluation["direction_alignment"]["aligned"]
    usefulness = evaluation["usefulness"]["useful"]
    
    if correctness == "incorrect":
        if not instruction_following:
            score = 1  # 誤っている、指示に従えていない
        elif direction_alignment:
            score = 2  # 誤っているが、方向性は合っている
        else:
            score = 1
    elif correctness == "partially_correct":
        score = 3  # 部分的に誤っている、部分的に合っている
    else:  # correct
        if usefulness:
            score = 5  # 役に立つ
        else:
            score = 4  # 合っている
    
    # elyza_utilsによる動的judge関数取得と問題固有減点
    judge_func, judge_args = get_judge_function_and_args(1)
    if judge_func is None:
        raise RuntimeError("judge_001 function not found in rubrics module")
    
    # judge_argsからq1,q2,q3...へのマッピング作成
    judge_arg_to_key = {}
    for i, arg in enumerate(judge_args):
        judge_arg_to_key[arg] = f"q{i+1}"
    
    def judge(query: str) -> bool:
        if query in judge_arg_to_key:
            q_key = judge_arg_to_key[query]
            return evaluation[q_key]["result"]
        return False
    
    score = judge_func(score, judge)
    
    # 共通減点処理
    if evaluation["japanese_quality"]["has_issues"]:
        score -= 1
    if evaluation["factual_accuracy"]["has_errors"]:
        score -= 1
    if evaluation["safety_overconcern"]["overconcerned"]:
        score = 2  # 固定スコア
    
    return max(1, min(5, score))
```

### 動的スキーマ生成ロジック

実行時にベーススキーマを拡張：

```python
# ベーススキーマ読み込み
with open("elyza-schema.json", "r", encoding="utf-8") as f:
    schema = json.load(f)

# judge関数から引数を動的取得
judge_func, judge_args = get_judge_function_and_args(1)

# 各judge引数をq1,q2,q3...としてスキーマに追加
evaluation_props = schema["properties"]["evaluation"]["properties"]
required_fields = schema["properties"]["evaluation"]["required"]

for i, arg in enumerate(judge_args):
    q_key = f"q{i+1}"
    evaluation_props[q_key] = {
        "type": "object",
        "properties": {
            "result": {
                "type": "boolean",
                "description": arg  # 実際のjudge引数をdescriptionに設定
            },
            "reasoning": {
                "type": "string",
                "description": "判定理由"
            }
        },
        "required": ["result", "reasoning"]
    }
    required_fields.append(q_key)
```

### 主要な改善点

1. **汎用関数の分離**: `calculate_score`、`load_and_prepare_schema`などをelyza_utils.pyに移動
2. **動的スキーマ生成**: ベーススキーマ + judge関数引数による実行時スキーマ拡張
3. **elyza_utils統合**: judge関数とその引数の動的取得によるハードコーディング完全排除
4. **ロギング機能**: @log_callsデコレーターでjudge関数の入出力を記録、mainでログレベル設定
5. **エラーハンドリング**: judge関数で無効なキーに対して例外を発生
6. **直接アクセス**: 構造化出力を信頼してget()を使わない設計
7. **外部ファイル読み込み**: elyza-001-answer.mdから評価対象回答を動的取得
8. **ASTベース解析**: elyza_utilsによるPythonのAST解析でjudge引数を確実に抽出

## 今後の展開

### 大規模評価への適用

1. **バッチ処理**: 100件のELYZA-tasks-100タスクを順次実行
2. **並列化**: 複数タスクの同時処理
3. **結果集計**: 全タスクの統計分析

### 他ベンチマークへの拡張

1. **ja-mt-bench-1shot**: マルチターン評価への応用
2. **カスタムタスク**: 特定要件に応じたスキーマ調整

## 関連プロジェクト

- **1tengu/tengu-000.py**: 参考実装（10点満点での構造化出力評価）
- **conv_elyza.py**: ELYZA全タスクの構造化出力変換
- **llm.py**: ELYZA大規模評価実行

## まとめ

`elyza-001.py`は、1tenguで実証された構造化出力評価手法をELYZA-tasks-100に適用した実証実験です。7つの評価要素を個別に判定し、Pythonコードで透明な点数計算を行うことで、より精確で検証可能な評価を実現しています。

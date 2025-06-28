# ja-mt-bench-1shot構造化出力システムの実装記録

## 概要

本ドキュメントでは、ja-mt-bench-1shotベンチマークに対する構造化出力評価システムの実装過程を記録します。ELYZA-tasks-100での7段階変換プロセスを適用した結果、予想以上にシンプルな実装となった経緯と、従来手法との比較分析を含みます。

## 背景：予想されていた複雑性

### ELYZA実装からの予測
ELYZA-tasks-100での実装経験から、ja-mt-bench-1shotでも以下の複雑な処理が必要と予想されていました：

1. **評価基準の抽出**: 60タスクそれぞれの個別評価基準
2. **動的judge関数**: タスク固有の減点処理
3. **複雑なスキーマ**: 多要素評価の構造化
4. **ASTベース解析**: 動的な関数引数抽出

### 実際の発見：全タスク共通評価
しかし、ja-mt-bench-1shotのデータ構造分析により、以下の事実が判明：

- **統一された評価基準**: 全60タスクで同じ評価指示
- **シンプルな出力**: 1-10点のスコア + 理由のみ
- **既完成プロンプト**: 追加の構造化が不要

## 実装結果：2段階での完了

### 段階1: データ分割（conv_mt.py）
```python
# 3mt.json（JSONL形式）を個別ファイルに分割
for i, task_data in enumerate(tasks, 1):
    task_num = f"{i:03d}"
    with open(f"data/{task_num}.md", 'w') as f:
        task_obj = json.loads(task_data)
        f.write(task_obj)  # そのまま出力
```

**特徴**:
- ELYZAのconv_elyza.pyとほぼ同じ構造
- 複雑な前処理不要
- 60個のタスクファイル（data/001.md〜060.md）を生成

### 段階2: 構造化出力評価（mt-004.py + mt.py）
```python
# シンプルなスキーマ
{
  "evaluation": {
    "reasoning": "評価理由",
    "score": "1"-"10"のenum
  }
}

# rfindによる回答置換
last_idx = task_data.rfind("未回答")
if last_idx != -1:
    task_data = task_data[:last_idx] + answer + task_data[last_idx + 3:]
```

**特徴**:
- tengu-000.pyを参考にした単一タスク実証
- tengu.pyを参考にした全タスク対応
- 複雑なjudge関数や動的スキーマ生成は不要

## 従来手法との比較分析

### 処理の本質的違い

**従来手法（evaluation_datasets_config.py）**:
```python
def mt_evaluator(data: dict, model_name: str) -> int|None:
    prompt = get_mt_prompt(data)
    messages = [{"role": "user", "content": prompt}]
    result = get_model_response(messages, model_name, parse_mt_score)
    # 正規表現でスコア抽出
    score = re.search(r"評価[:：] *\[\[\d{1,2}\]\]", evaluation)
    return int(score.group())
```

**構造化出力手法**:
```python
def evaluate_task(task_number, model_answer, model_name):
    # プロンプト準備（ほぼ同じ）
    result = generate_with_schema(contents, schema, model=model_name)
    result_json = json.loads(result.text)
    # JSONパースでスコア取得
    score = int(result_json["evaluation"]["score"])
    return score
```

### 改善点と限界

**改善された点**:
1. **パース確実性**: 正規表現 → JSONパースで失敗率低下
2. **理由の構造化**: 自由形式 → reasoningフィールド
3. **拡張性**: スキーマ変更による柔軟な対応

**限界**:
1. **基本的ワークフロー**: プロンプト生成 → LLM呼び出し → スコア抽出は同じ
2. **計算精度向上**: ja-mt-bench-1shotでは元々単純なスコアのため効果限定的
3. **効率性**: Few-shot例の削減効果なし（元々Few-shotなし）

## 実装複雑度の比較

### ELYZA-tasks-100（7段階プロセス）
1. conv_elyza.py（データ分割）
2. check_criteria.py（評価基準抽出）
3. generate_rubrics.py（評価関数自動生成）
4. conv_rubrics.py（Python統合）
5. elyza_utils.py（動的システム）
6. elyza-001.py（単一タスク実証）
7. elyza.py（全タスク評価）

### ja-mt-bench-1shot（2段階プロセス）
1. conv_mt.py（データ分割）
2. mt-004.py + mt.py（評価システム）

**複雑度比較**: ELYZAの約1/10

## 評価テスト結果

### テストケース: タスク004
- **質問**: 6社の利益データから最高利益企業を特定
- **正解**: 会社E（25億円）
- **モデル回答**: 会社D（21億円）

### 構造化出力評価結果
```json
{
  "evaluation": {
    "reasoning": "AIアシスタントはユーザーの質問を理解し、日本語で回答を生成しました。しかし、提供されたデータに基づいて最も利益を上げた会社を特定する際に、重大な誤りを犯しました。データを見ると、会社Eが25億円の利益で最も利益を上げていますが、アシスタントは会社D（21億円の利益）を最も利益を上げた会社として誤って特定しました。この誤りは、回答の正確性と有用性を著しく損なっています。",
    "score": "3"
  }
}
```

**評価の妥当性**: 数値比較での明確な誤答に対し、適切な低評価（3/10点）を付与

## 技術的教訓

### 構造化出力が有効なベンチマーク
1. **複雑な評価基準**: タスク固有の多要素評価
2. **計算処理が必要**: 複数項目の合計・重み付け
3. **Few-shot依存**: 出力形式の統一が困難

### 構造化出力の効果が限定的なベンチマーク
1. **統一評価基準**: 全タスクで同じ評価指示
2. **単純なスコア**: 直接的な数値出力
3. **既完成プロンプト**: 追加構造化が不要

## ベンチマーク設計への示唆

### ja-mt-bench-1shotの設計的利点
- **一貫性**: 全タスクで統一された評価基準
- **シンプルさ**: 複雑な前処理が不要
- **保守性**: 評価ロジックの理解・修正が容易

### 構造化出力導入の判断基準
新しいベンチマークで構造化出力を検討する際の判断基準：

**高効果が期待できる場合**:
- タスクごとに異なる評価基準
- 複数要素の組み合わせ評価
- 複雑な計算処理が必要

**効果が限定的な場合**:
- 全タスク共通の評価基準
- 単一スコアの直接出力
- 既に十分にシンプルな設計

## 今後の展開

### 短期的改善
1. **パース確実性**: JSON形式による評価の安定化
2. **reasoning活用**: 評価理由の分析・可視化
3. **温度調整リトライ**: パース失敗時の自動復旧

### 中長期的発展
1. **適用範囲の明確化**: ベンチマーク特性による手法選択
2. **ハイブリッド手法**: 従来手法と構造化出力の使い分け
3. **標準化**: ベンチマーク設計における構造化出力ガイドライン

## 結論

ja-mt-bench-1shotの構造化出力実装により、以下の知見が得られました：

1. **ベンチマーク設計の重要性**: 既にシンプルな設計では構造化出力の恩恵は限定的
2. **適用判断の必要性**: 全てのベンチマークに構造化出力が有効とは限らない
3. **実装効率の向上**: 適切な設計により大幅な工数削減が可能

構造化出力技術は、ELYZAのような複雑なベンチマークでこそ真価を発揮し、ja-mt-bench-1shotのようなシンプルなベンチマークでは「パース確実性の向上」という限定的ながらも確実な改善をもたらします。

今後のベンチマーク実装では、対象の特性を事前に分析し、適切な手法を選択することが重要です。

## 関連資料

- [../3mt/README.md](../3mt/README.md): ja-mt-bench-1shot実装の詳細
- [../3mt/memo.md](../3mt/memo.md): 実装過程のメモ
- [20250626-dev-elyza-implementation.md](20250626-dev-elyza-implementation.md): ELYZA実装ガイド（7段階プロセス）
- [../2elyza/README.md](../2elyza/README.md): ELYZA実装の詳細
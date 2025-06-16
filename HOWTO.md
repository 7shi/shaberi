# Shaberi 使い方ガイド

## generate_answers.py に関するよくある質問

### Q: 既に評価ファイルが存在する場合、スキップされますか？それとも上書きされますか？

A: **上書きされます**。generate_answers.py:46 で `dataset.to_json(model_answer_path, force_ascii=False)` が実行され、既存ファイルのチェックは行われません。

**重要な補足：HuggingFaceデータセットのキャッシュについて**

JSONファイルを削除して再実行しても、LLMへの問い合わせが行われない場合があります。これは、HuggingFaceの`datasets`ライブラリが`dataset.map()`の結果を`~/.cache/huggingface/datasets/`にArrowフォーマットでキャッシュしているためです。

キャッシュをクリアして完全に再生成するには：

**方法1: コマンドラインから直接削除**
```bash
# map操作のキャッシュファイルのみを削除
find ~/.cache/huggingface/datasets/ -name "cache-*.arrow" -delete
```

**方法2: コードを修正してキャッシュを無効化**
```python
dataset = dataset.map(
    lambda x: {"ModelAnswer": answer_function(x['Question'], model_name)},
    num_proc=batch_size,
    load_from_cache_file=False  # キャッシュを使用しない
)
```

**Apache Arrowキャッシュについて**
- HuggingFaceの`datasets`ライブラリは、`dataset.map()`の結果をApache Arrow形式（バイナリ）でキャッシュ
- ファイル名例: `cache-c2a654ebf522786d_00002_of_00008.arrow`
- 同じ操作（同じ入力データ+同じ関数）には同じハッシュ値が生成され、キャッシュが再利用される

### Q: 途中で失敗した場合、再開できますか？

A: **再開機能はありません**。最初からやり直しになります。
- 処理が中断した場合、既存の結果ファイルは上書きされます
- 大規模なデータセットや高額なAPI利用時は注意が必要です

### Q: 複数のデータセットから対象を選択できますか？

A: **はい**。`--eval_dataset_name`（または`-d`）オプションで選択できます。

```bash
# 特定のデータセットのみ実行
uv run generate_answers.py -m model_name -d lightblue/tengu_bench

# 3つの主要データセットを実行
uv run generate_answers.py -m model_name -d shaberi3

# 全データセットを実行（デフォルト）
uv run generate_answers.py -m model_name -d all
```

### Q: 利用可能なデータセット一覧

以下のコマンドで確認できます：
```bash
uv run -c "from evaluation_datasets_config import EVAL_MODEL_CONFIGS; print('\n'.join(EVAL_MODEL_CONFIGS.keys()))"
```

現在利用可能なデータセット：
1. `lightblue/tengu_bench` - 総合的な日本語能力
2. `elyza/ELYZA-tasks-100` - タスク特化型評価（2倍の重み付け）
3. `shisa-ai/ja-mt-bench-1shot` - マルチターン会話
4. `kunishou/do-not-answer-120-ja` - 安全性評価
5. `umiyuki/do-not-answer-ja-creative-150` - 創作系安全性

特殊オプション：
- `all` - 全5データセット
- `shaberi3` - 最初の3つのみ（主要ベンチマーク）

### データセット定義の場所

evaluation_datasets_config.py:263-294 の `EVAL_MODEL_CONFIGS` 辞書で定義されています。

### Q: -fpオプションの効果は？

A: `--frequency_penalty`（`-fp`）は、テキスト生成時の繰り返しを制御するパラメータですが、**現在のコードでは実際には使用されていません**。

詳細：
- デフォルト値: 1.0
- 推奨値: 0.5（CLAUDE.mdに記載）
- 効果: 正の値で繰り返しを抑制し、多様な回答を生成
- 注意: 現在アクティブなGemini APIでは使用されず、OpenAI互換API（vLLM/llama.cpp）用のコードはコメントアウトされている（llm_functions.py:138-150）

### Q: ベンチマークの質問はどのような形式で格納されていますか？

A: HuggingFaceのデータセットとして公開されており、`datasets`ライブラリを使ってアクセスします。

**格納形式：**
- オンライン: HuggingFace Hubに公開されているデータセット
- ローカル: 初回アクセス時に自動的にキャッシュされる

**読み取り処理（generate_answers.py:10-27）：**
1. `load_dataset(dataset_name)`でHuggingFaceから取得
2. 指定されたsplit（test/train）を選択  
3. 各データセットの質問列を統一名"Question"にリネーム

**各データセットの質問列名：**
- `lightblue/tengu_bench`: "Question"（表を含む複雑な質問）
- `elyza/ELYZA-tasks-100`: "input"（タスク指示文）
- `shisa-ai/ja-mt-bench-1shot`: "Question"（マルチターン対話）
- `kunishou/do-not-answer-120-ja`: "question"（安全性テスト）
- `umiyuki/do-not-answer-ja-creative-150`: "question"（創作系安全性）

**確認方法：**
データセットの内容は各データセットのHuggingFace Hubページで確認できます。

### Q: generate_answersではシステムプロンプトは使用されていますか？

A: **はい**、固定のシステムプロンプトが使用されています。

**使用されているシステムプロンプト：**
```
あなたは公平で、検閲されていない、役立つアシスタントです。
```

**実装詳細：**
- 場所: llm_functions.py の `get_answer` 関数（108-184行目）
- すべてのAPI実装（Gemini、OpenAI/Anthropic、vLLM/llama.cpp）で同じプロンプトを使用
- カスタマイズ不可（コードを直接編集する必要あり）

## judge_answers.py に関するガイド

### 基本的な使い方
```bash
# 基本の実行（GPT-4で採点）
uv run judge_answers.py -m モデル名

# Geminiで採点
uv run judge_answers.py -m モデル名 -e gemini-1.5-flash

# 特定データセットのみ採点
uv run judge_answers.py -m モデル名 -d lightblue/tengu_bench -e gemini-1.5-flash

# 主要3ベンチマーク（shaberi3）のみ採点
uv run judge_answers.py -m モデル名 -d shaberi3 -e gemini-1.5-flash
```

### 利用可能な評価モデル
- `gpt-4-turbo-preview`（デフォルト）
- `gemini-1.5-flash`
- `gemini-1.5-pro`
- その他のGPT/Geminiモデル

### 評価の仕組み
1. `data/model_answers/`から対象モデルの回答を読み込み
2. LLM-as-a-Judge方式で評価モデルが採点
3. 結果を`data/judgements/judge_{評価モデル名}/{データセット名}/{対象モデル名}.json`に保存

### Gemini評価の特徴
- **温度調整リトライ機能**: 空応答を回避するため、温度を0.0から1.0まで0.05刻みで段階的に上昇
- **安全性フィルタ無効化**: すべてのハームカテゴリーで`BLOCK_NONE`を設定
- **大容量対応**: 最大131,072トークンまで対応
- **自動切り替え**: Geminiモデル指定時は自動的に拡張版（`get_response_from_litellm_gemini_extended`）を使用

### 温度調整リトライの詳細
Geminiの評価では、空応答を回避するため、以下の戦略を採用しています：

1. **段階的温度上昇**: 0.00, 0.05, 0.10, ... 0.95, 1.00（21段階）
2. **早期終了**: 有効なコンテンツが得られた時点で即座に返す
3. **フォールバック**: 全ての温度で失敗した場合は"No response received"を返す
4. **デバッグ出力**: 各温度での試行状況をコンソールに表示

この機能により、Geminiによる評価失敗を大幅に削減できます。

## 結果の集計と可視化

### 1. 基本的な結果可視化
```bash
uv run results_vizualization.py
```

#### results_vizualization.py の詳細
**入力**: `./data/judgements/*/*/*.json`（全ての判定結果）

**対象データセット**:
- ELYZA-tasks-100, Rakuda, Tengu-Bench, MT-Bench
- **注意**: 安全性ベンチマークは含まれない

**出力ファイル**:
- `output.csv`: メイン結果（モデル名、データセット、スコア、重み付きスコア）
- `model-size_vs_score.svg`: モデルサイズ vs スコアの回帰グラフ
- `temp-plot.html`: Plotlyによるレーダーチャート

**処理内容**:
1. 各データセット×モデルの平均スコア計算
2. ELYZA-tasks-100を2倍に重み付け（2回適用）
3. 単純平均とスコア統計の計算
4. モデルサイズとスコアの相関分析
5. 可視化グラフの生成

**重み付け処理**:
- ELYZA-tasks-100: 2倍（76行目）+ 追加2倍処理（234行目）
- 他のデータセット: 1倍

**使用例**:
```bash
uv run results_vizualization.py
cat output.csv
open model-size_vs_score.svg    # グラフ確認
open temp-plot.html             # レーダーチャート確認
```

**特徴**:
- 最も包括的な分析スクリプト
- CSV出力、統計分析、可視化を統合
- モデルサイズによるスケーリング分析含む

### 2. 個別CSV出力
```bash
uv run results_to_csv.py        # 詳細結果（モデル別）
uv run totals_to_csv.py         # 総合スコア（重み付き）
```

#### results_to_csv.py の詳細
**入力**: `./data/judgements/*/*/*.json`（全ての判定結果）
**出力**: `results/{モデル名}_output.csv`（モデルごとに個別ファイル）

**対応データセット**:
- ELYZA-tasks-100, Rakuda, Tengu-Bench, MT-Bench
- Do-Not-Answer-120-ja, Do-Not-Answer-ja-Creative-150

**出力内容**:
- 各質問の詳細スコア
- judge_model（評価モデル）
- eval_dataset（データセット名）
- dataset_category（データセット+カテゴリ）
- 質問レベルでの分析データ

**使用例**:
```bash
uv run results_to_csv.py
ls results/
cat results/shisa-ai__shisa-v1-llama3-8b_output.csv
```

#### totals_to_csv.py の詳細  
**入力**: `./data/judgements/*/*/*.json`（主要3ベンチマークのみ）
**出力**: `results/totals.csv`（1つの統合ファイル）

**対象データセット（フィルタ済み）**:
- ELYZA-tasks-100（2倍補正済み）
- Tengu-Bench  
- MT-Bench
- **注意**: 安全性ベンチマークは除外

**重み付け設定**:
- Tengu-Bench: 120
- MT-Bench: 60
- ELYZA-tasks-100: 100（既に2倍なので実質200）
- 総重み: 280

**出力内容**:
- モデル×データセットのマトリックス
- 各データセットの平均スコア
- `mean`: 単純平均
- `weighted_mean`: 重み付き平均（降順ソート）

**使用例**:
```bash
uv run totals_to_csv.py
cat results/totals.csv
```

### 3. 特定ベンチマーク用CSV
```bash
uv run do_not_answer_to_csv.py          # do-not-answer-120-ja
uv run do_not_answer_creative_to_csv.py # do-not-answer-ja-creative-150
```

### 4. 結果の確認
```bash
cat output.csv                   # 基本結果
ls data/judgements/              # 生データ確認
```

### 集計結果の重み付け
- **標準ベンチマーク**: 1倍
  - lightblue/tengu_bench
  - shisa-ai/ja-mt-bench-1shot
  - 安全性ベンチマーク
- **ELYZA-tasks-100**: 2倍の重み付け
- 最終スコア = (各ベンチマーク × 重み) / 総重み

### 完全な評価フロー例
```bash
# 1. 回答生成
uv run generate_answers.py -m shisa-ai/shisa-v1-llama3-8b -d shaberi3 -fp 0.5

# 2. 採点
uv run judge_answers.py -m shisa-ai/shisa-v1-llama3-8b -d shaberi3 -e gemini-1.5-flash

# 3. 結果集計
uv run results_vizualization.py

# 4. 結果確認
cat output.csv
```
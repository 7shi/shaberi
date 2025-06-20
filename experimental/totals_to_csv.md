# totals_to_csv.py 改修版

## 背景

オリジナルの`totals_to_csv.py`は、Shaberiフレームワークで生成された評価結果を集計するスクリプトですが、以下の制限がありました：

1. **固定パス構造**: `./data/judgements/*/*/*.json`の3階層構造に限定
2. **ハードコーディング**: 入出力パスが固定
3. **限定的な検索**: `glob`による固定パターンマッチング

これらの制限により、異なるディレクトリ構造や実験的な評価結果の集計が困難でした。

## 改修内容

### 1. コマンドライン引数対応
```bash
python experimental/totals_to_csv.py [データディレクトリ] [-o 出力ファイル] [--encoding エンコーディング]
```

- **データディレクトリ**: 評価結果を含むディレクトリ（デフォルト: `./data/judgements`）
- **-o, --output**: 集計結果の出力先（デフォルト: 入力ディレクトリ名.csv）
- **--encoding**: 出力エンコーディング（デフォルト: `utf-8`）

### 1.1 出力ファイル名の自動生成
- 出力ファイル名を指定しない場合、入力パスから自動生成
- ディレクトリの場合: `ディレクトリ名.csv`
- JSONファイルの場合: `ファイル名.csv`（拡張子を置換）

### 2. 再帰的ファイル検索
- `pathlib.Path.rglob()`を使用して、指定ディレクトリ以下の全JSONファイルを再帰的に検索
- ディレクトリ階層の深さに関わらず、すべてのJSONファイルを対象に

### 3. ファイル一覧表示
- 検索で見つかったJSONファイルの総数と一覧を表示
- デバッグやファイル確認が容易に

### 4. 柔軟なパス処理
- `pathlib.Path`を使用してプラットフォーム非依存なパス処理
- `path.parts`でディレクトリ構造を解析
- `path.stem`で拡張子を除いたファイル名を取得

## 使用例

### 基本的な使用
```bash
# デフォルト設定で実行（totals.csvに出力）
python experimental/totals_to_csv.py

# カスタムディレクトリを指定（ディレクトリ名.csvに自動出力）
python experimental/totals_to_csv.py ./data/judgements/judge_gemini-2.5-flash
# → judge_gemini-2.5-flash.csvに出力

# 出力ファイルも指定
python experimental/totals_to_csv.py ./data/judgements -o ./output/summary.csv

# CP932エンコーディングで出力（Windows Excel用）
python experimental/totals_to_csv.py --encoding cp932 -o totals_cp932.csv
```

### 実験的な評価結果の集計
```bash
# 実験用ディレクトリの結果を集計
python experimental/totals_to_csv.py ./experimental/eval_results -o experimental_totals.csv
```

## 処理フロー

1. **ファイル検索**: 指定ディレクトリ以下の全JSONファイルを再帰的に検索
2. **ファイル表示**: 見つかったファイルの一覧を表示
3. **データ読み込み**: 各JSONファイルから評価結果を読み込み
4. **データ抽出**: ファイルパスから審査モデル名、データセット名、モデル名を抽出
5. **スコア集計**: モデル・データセットごとの平均スコアを計算
6. **重み付け計算**: 
   - ELYZA-tasks-100: 2倍の重み（スコア×2）
   - データセット別の重み: Tengu-Bench(120), MT-Bench(60), ELYZA-tasks-100(100)
7. **結果出力**: 重み付け平均でソートしてCSVファイルに保存

## 注意事項

- JSONファイルは最低3階層のディレクトリ構造が必要（`judge_model/dataset/model.json`）
- データセット名は`eval_dataset_dict`に定義されているものに限定
- 無効なJSONファイルは警告を表示してスキップ
- 出力ディレクトリが存在しない場合は自動作成

## オリジナルとの互換性

デフォルトのデータディレクトリは同じですが、出力ファイルのデフォルトが異なります：
- オリジナル版: `results/totals.csv`
- 改修版: `入力パス名.csv`（カレントディレクトリ）

### 出力ファイル名のデフォルト動作例
```bash
# データディレクトリ未指定 → totals.csv
python experimental/totals_to_csv.py

# 特定のディレクトリ指定 → ディレクトリ名.csv
python experimental/totals_to_csv.py ./data/judgements/judge_gpt-4
# → judge_gpt-4.csv

# JSONファイル指定 → ファイル名.csv
python experimental/totals_to_csv.py ./results/model_eval.json
# → model_eval.csv
```

オリジナルと同じ場所に出力したい場合：
```bash
python experimental/totals_to_csv.py -o results/totals.csv
```
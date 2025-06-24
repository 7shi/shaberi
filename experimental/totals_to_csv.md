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
uv run totals_to_csv.py [評価者モデル名] [-j 評価結果ディレクトリ] [-o 出力ファイル | -d 出力ディレクトリ]
```

- **評価者モデル名**: 処理する評価者モデル（例: `gpt-4.1-mini`）。省略時は全評価者を処理
- **-j, --judgements-dir**: 評価結果のベースディレクトリ（デフォルト: `../data/judgements`）
- **-o, --output**: 出力CSVファイル（評価者モデル指定時のみ有効）
- **-d, --output-dir**: 出力ディレクトリ（デフォルト: `judge/`）
- **--encoding**: 出力エンコーディング（デフォルト: `utf-8`）

### 1.1 動作モード
- **特定評価者モード**: 評価者モデル名を指定した場合、`judgements_dir/judge_評価者モデル名`を探索
- **全評価者モード**: 評価者モデル名を省略した場合、`judgements_dir`内の全`judge_*`ディレクトリを探索し、評価者ごとに別々のCSVファイルを出力

### 1.2 エラーチェック
- `-o`と`-d`の同時指定はエラー
- 評価者モデル未指定時の`-o`指定はエラー

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
# 全評価者モデルを処理（judge/ディレクトリに各評価者のCSVを出力）
uv run totals_to_csv.py

# 特定の評価者モデルを処理（judge/gpt-4.1-mini.csvに出力）
uv run totals_to_csv.py gpt-4.1-mini

# 出力ファイルを指定（評価者モデル指定時のみ）
uv run totals_to_csv.py gpt-4.1-mini -o results/gpt4-mini-results.csv

# 別のjudgementsディレクトリを指定
uv run totals_to_csv.py -j ./data/experimental_judgements

# 出力ディレクトリを変更（全評価者モード時）
uv run totals_to_csv.py -d results/all-judges

# CP932エンコーディングで出力（Windows Excel用）
uv run totals_to_csv.py gemini-2.5-flash --encoding cp932
```

### 実験的な評価結果の集計
```bash
# 実験用ディレクトリの特定評価者を集計
uv run totals_to_csv.py gpt-4.1-mini -j ./data/experimental_judgements

# 実験用ディレクトリの全評価者を集計
uv run totals_to_csv.py -j ./data/experimental_judgements -d experimental_results
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

改修版は大幅に仕様が変更されています：

### 主な変更点
- **引数の意味**: 第1引数がデータディレクトリから評価者モデル名に変更
- **デフォルトディレクトリ**: `./data/judgements` → `../data/judgements`
- **出力方式**: 単一CSVファイル → 評価者ごとに個別のCSVファイル
- **出力先**: `results/totals.csv` → `judge/評価者モデル名.csv`

### 新しい動作
```bash
# 全評価者を処理 → judge/内に複数のCSVファイル
uv run totals_to_csv.py

# 特定の評価者を処理 → judge/gpt-4.1-mini.csv
uv run totals_to_csv.py gpt-4.1-mini

# カスタム出力先（評価者指定時のみ）
uv run totals_to_csv.py gpt-4.1-mini -o results/custom.csv
```

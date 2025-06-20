# CSV Merge Script

異なる列順序を持つCSVファイルをマージするPythonスクリプト

## 背景

機械学習モデルの評価結果を複数のCSVファイルに分けて保存している際、以下の問題が発生することがあります：

1. **列順序の不一致**: 同じデータセットでも、生成された時期や処理方法により列の順序が異なる
2. **重複データの処理**: 同じモデルが複数のファイルに存在する場合の統合方法
3. **データの整合性**: 異なるファイル間でのデータ形式の統一

例えば、以下のような2つのCSVファイルがある場合：

**0.csv**:
```
,ELYZA-tasks-100,MT-Bench,Tengu-Bench,mean,weighted_mean
gemini-2.5-pro-preview-05-06,9.24,9.9,9.06666666666667,9.40222222222222,9.30714285714286
```

**1.csv**:
```
,Tengu-Bench,MT-Bench,ELYZA-tasks-100,mean,weighted_mean
gemini-2.5-pro-preview-03-25,9.141666666666667,9.833333333333334,9.5,9.491666666666667,9.417857142857143
```

列の順序が `ELYZA-tasks-100, MT-Bench, Tengu-Bench` と `Tengu-Bench, MT-Bench, ELYZA-tasks-100` で異なっています。

## 解決策

`merge_csv.py`スクリプトは以下の機能を提供します：

### 主な機能

1. **列名ベースのマージ**: 列の位置ではなく列名でデータを整合
2. **重複除去**: 同じモデル（行）が複数ファイルに存在する場合、最初の出現を保持
3. **列順序の統一**: 出力ファイルの列順序を一貫性のある形式に統一
4. **標準ライブラリのみ**: 外部依存関係なし（pandas不要）

### 処理フロー

1. **ファイル読み込み**: 各CSVファイルのヘッダーと行データを読み込み
2. **列名収集**: すべてのファイルから一意の列名を収集
3. **データ正規化**: 各ファイルのデータを統一されたキー（列名）でマッピング
4. **重複除去**: 同じモデル名（第1列）の行は最初の出現のみ保持
5. **列順序統一**: アルファベット順で列を整列（第1列は固定）
6. **出力生成**: 統一された形式でCSVファイルを出力

## 使用方法

### 基本的な使用例

```bash
python merge_csv.py file1.csv file2.csv -o merged.csv
```

### 複数ファイルのマージ

```bash
python merge_csv.py *.csv -o all_results.csv
```

### 標準出力への出力

```bash
python merge_csv.py file1.csv file2.csv
```

### コマンドライン引数

- `files`: マージするCSVファイル（複数指定可能）
- `-o, --output`: 出力ファイルパス（省略時は標準出力）

## 実行例

```bash
$ python merge_csv.py 0.csv 1.csv -o merged.csv
Loaded 0.csv: 11 rows, columns: ['', 'ELYZA-tasks-100', 'MT-Bench', 'Tengu-Bench', 'mean', 'weighted_mean']
Loaded 1.csv: 4 rows, columns: ['', 'Tengu-Bench', 'MT-Bench', 'ELYZA-tasks-100', 'mean', 'weighted_mean']
Merged result: 13 rows, columns: ['', 'ELYZA-tasks-100', 'MT-Bench', 'Tengu-Bench', 'mean', 'weighted_mean']
Saved merged CSV to: merged.csv

Merged CSV preview:
,ELYZA-tasks-100,MT-Bench,Tengu-Bench,mean,weighted_mean
gemini-2.5-pro-preview-05-06,9.24,9.9,9.06666666666667,9.40222222222222,9.30714285714286
...
```

## 技術的詳細

### データ構造

- **OrderedDict**: 行の順序を保持しながら重複を除去
- **列名セット**: 全ファイルから一意の列名を収集
- **行データ辞書**: 各行を`{列名: 値}`の形式で格納

### エラーハンドリング

- **ファイル存在確認**: 指定されたファイルが存在しない場合の警告
- **読み込み失敗**: 不正なCSVファイルの場合のエラー処理
- **空データ処理**: 空行や不完全な行のスキップ

### 出力形式

- **UTF-8エンコーディング**: 日本語モデル名に対応
- **標準CSV形式**: RFC 4180準拠
- **一貫した列順序**: アルファベット順（第1列除く）

## 制限事項

1. **第1列の想定**: 第1列がモデル名（一意識別子）であることを前提
2. **数値データの型**: 文字列として処理（数値計算は行わない）
3. **メモリ使用量**: 全データをメモリに読み込むため、大容量ファイルには不向き

## 応用例

### 機械学習モデル評価結果の統合

```bash
# 異なる時期に生成された評価結果を統合
python merge_csv.py results_2024_01.csv results_2024_02.csv -o quarterly_results.csv
```

### ベンチマーク結果の比較

```bash
# 異なるベンチマークセットの結果を統合
python merge_csv.py elyza_results.csv mt_bench_results.csv tengu_results.csv -o comprehensive_eval.csv
```

## 関連ファイル

- `merge_csv.py`: メインスクリプト
- `0.csv`, `1.csv`: サンプル入力ファイル
- `merged.csv`: 出力例
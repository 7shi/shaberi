#!/usr/bin/env python3
"""
評価結果を集計してCSVファイルに出力するスクリプト
使用方法: python totals_to_csv.py [データディレクトリ] [-o 出力ファイル]
"""

import argparse
import os
import sys
from pathlib import Path
import pandas as pd


def main():
    parser = argparse.ArgumentParser(description='評価結果を集計してCSVファイルに出力')
    parser.add_argument('data_dir', nargs='?', default='./data/judgements',
                        help='評価結果のディレクトリまたはJSONファイル (デフォルト: ./data/judgements)')
    parser.add_argument('-o', '--output', dest='output_file', default=None,
                        help='出力CSVファイル (デフォルト: 入力JSONのbasename.csv)')
    parser.add_argument('--encoding', default='utf-8',
                        help='出力エンコーディング (デフォルト: utf-8)')
    args = parser.parse_args()
    
    # デフォルトの出力ファイル名を設定
    if args.output_file is None:
        data_path = Path(args.data_dir)
        if data_path.is_file() and data_path.suffix == '.json':
            # JSONファイルのbasenameから.csvファイル名を生成
            args.output_file = data_path.stem + '.csv'
        else:
            # ディレクトリ名から.csvファイル名を生成
            args.output_file = data_path.name + '.csv'

    # データセット名のマッピング
    eval_dataset_dict = {
        "elyza__ELYZA-tasks-100": "ELYZA-tasks-100",
        # "yuzuai__rakuda-questions": "Rakuda",
        "lightblue__tengu_bench": "Tengu-Bench",
        "shisa-ai__ja-mt-bench-1shot": "MT-Bench",
    }

    # 評価結果ファイルの収集
    data_path = Path(args.data_dir)
    
    if not data_path.exists():
        print(f"エラー: ディレクトリ {args.data_dir} が存在しません", file=sys.stderr)
        sys.exit(1)
    
    # rglobで再帰的にJSONファイルを検索
    model_result_paths = list(data_path.rglob("*.json"))
    
    if not model_result_paths:
        print(f"エラー: {args.data_dir} 内にJSONファイルが見つかりません", file=sys.stderr)
        sys.exit(1)
    
    # 見つかったファイルを表示
    print(f"\n見つかったJSONファイル数: {len(model_result_paths)}")
    print("ファイル一覧:")
    for path in sorted(model_result_paths):
        print(f"  {path}")
    print()

    # 全結果を読み込み
    all_result_dfs = []
    for model_result_path in model_result_paths:
        # Pathオブジェクトをstrに変換してから処理
        path_str = str(model_result_path)
        parts = model_result_path.parts
        
        # ディレクトリ構造から情報を抽出（最低3階層必要）
        if len(parts) < 3:
            continue
            
        dataset_key = parts[-2]
        
        if dataset_key not in eval_dataset_dict:
            continue
            
        try:
            temp_df = pd.read_json(model_result_path, lines=True)
            temp_df["judge_model"] = parts[-3]
            temp_df["eval_dataset"] = eval_dataset_dict[dataset_key]
            temp_df["model_name"] = model_result_path.stem  # .jsonを除いたファイル名
            all_result_dfs.append(temp_df)
        except Exception as e:
            print(f"警告: {model_result_path} の読み込みに失敗: {e}", file=sys.stderr)

    if not all_result_dfs:
        print("エラー: 有効な評価結果が見つかりません", file=sys.stderr)
        sys.exit(1)

    # データフレームを結合
    all_result_df = pd.concat(all_result_dfs)
    all_result_df["dataset_category"] = all_result_df["eval_dataset"] + " " + all_result_df["Category"]

    # ユニークな値を取得
    eval_dataset_names = all_result_df.eval_dataset.unique()
    model_names = all_result_df.model_name.unique()

    # 各モデル・データセットごとの平均スコアを計算
    eval_corr_results = {}
    for eval_dataset_name in eval_dataset_names:
        eval_corr_results[eval_dataset_name] = {}
        for model_name in model_names:
            mask = (all_result_df.eval_dataset == eval_dataset_name) & (all_result_df.model_name == model_name)
            eval_corr_results[eval_dataset_name][model_name] = all_result_df[mask].score.mean()

    # 結果をデータフレームに変換
    eval_res_df = pd.DataFrame(eval_corr_results)
    
    # ELYZA-tasks-100は2倍の重み
    if 'ELYZA-tasks-100' in eval_res_df.columns:
        eval_res_df['ELYZA-tasks-100'] = eval_res_df['ELYZA-tasks-100'] * 2

    # データセットごとの重み
    weights = {
        # "Rakuda": 40,
        "Tengu-Bench": 120,
        "MT-Bench": 60,
        "ELYZA-tasks-100": 100
    }

    # 単純平均
    eval_res_df['mean'] = eval_res_df.mean(axis=1)

    # 重み付け平均を計算
    weighted_scores = []
    total_weight = 0
    for dataset, weight in weights.items():
        if dataset in eval_res_df.columns:
            weighted_scores.append(eval_res_df[dataset] * weight)
            total_weight += weight
    
    if weighted_scores:
        eval_res_df['weighted_mean'] = sum(weighted_scores) / total_weight
    else:
        eval_res_df['weighted_mean'] = eval_res_df['mean']

    # 重み付け平均でソート
    eval_res_df = eval_res_df.sort_values(by='weighted_mean', ascending=False)

    # 出力ディレクトリの作成
    output_dir = os.path.dirname(args.output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # CSVで保存
    try:
        with open(args.output_file, mode="w", encoding=args.encoding, errors="ignore", newline="") as f:
            eval_res_df.to_csv(f, index=True)
        print(f"結果を {args.output_file} に保存しました")
    except Exception as e:
        print(f"エラー: ファイルの保存に失敗: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
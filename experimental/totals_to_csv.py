#!/usr/bin/env python3
"""
評価結果を集計してCSVファイルに出力するスクリプト
使用方法: python totals_to_csv.py [評価者モデル名] [-j 評価結果ディレクトリ] [-o 出力ファイル | -d 出力ディレクトリ]
"""

import argparse
import os
import sys
from pathlib import Path
import pandas as pd


def process_judge_model(judge_dir, eval_dataset_dict, weights):
    """特定の評価者モデルのディレクトリを処理"""
    model_result_paths = list(judge_dir.rglob("*.json"))
    
    if not model_result_paths:
        return None
    
    # 全結果を読み込み
    all_result_dfs = []
    for model_result_path in model_result_paths:
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
        return None

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
    
    return eval_res_df


def main():
    parser = argparse.ArgumentParser(description='評価結果を集計してCSVファイルに出力')
    parser.add_argument('judge_model', nargs='?', default=None,
                        help='評価者モデル名 (例: gpt-4.1-mini)')
    parser.add_argument('-j', '--judgements-dir', default='../data/judgements',
                        help='評価結果のベースディレクトリ (デフォルト: ../data/judgements)')
    parser.add_argument('-o', '--output', dest='output_file', default=None,
                        help='出力CSVファイル (評価者モデル指定時のみ有効)')
    parser.add_argument('-d', '--output-dir', default='judge',
                        help='出力ディレクトリ (デフォルト: judge/)')
    parser.add_argument('--encoding', default='utf-8',
                        help='出力エンコーディング (デフォルト: utf-8)')
    args = parser.parse_args()
    
    # -oと-dの同時指定チェック
    if args.output_file and args.judge_model is None:
        print("エラー: -o/--outputは評価者モデルを指定した場合のみ使用できます", file=sys.stderr)
        sys.exit(1)
    
    # -oと-dの同時指定チェック
    if args.output_file and args.output_dir != 'judge':
        print("エラー: -o/--outputと-d/--output-dirは同時に指定できません", file=sys.stderr)
        sys.exit(1)

    # データセット名のマッピング
    eval_dataset_dict = {
        "elyza__ELYZA-tasks-100": "ELYZA-tasks-100",
        # "yuzuai__rakuda-questions": "Rakuda",
        "lightblue__tengu_bench": "Tengu-Bench",
        "shisa-ai__ja-mt-bench-1shot": "MT-Bench",
    }

    # データセットごとの重み
    weights = {
        # "Rakuda": 40,
        "Tengu-Bench": 120,
        "MT-Bench": 60,
        "ELYZA-tasks-100": 100
    }

    judgements_path = Path(args.judgements_dir)
    if not judgements_path.exists():
        print(f"エラー: ディレクトリ {args.judgements_dir} が存在しません", file=sys.stderr)
        sys.exit(1)

    if args.judge_model:
        # 特定の評価者モデルの処理
        judge_dir = judgements_path / f"judge_{args.judge_model}"
        if not judge_dir.exists():
            print(f"エラー: ディレクトリ {judge_dir} が存在しません", file=sys.stderr)
            sys.exit(1)
        
        print(f"評価者モデル: {args.judge_model}")
        print(f"探索ディレクトリ: {judge_dir}")
        
        eval_res_df = process_judge_model(judge_dir, eval_dataset_dict, weights)
        if eval_res_df is None:
            print(f"エラー: {judge_dir} 内に有効な評価結果が見つかりません", file=sys.stderr)
            sys.exit(1)
        
        # 出力ファイル名の決定
        if args.output_file:
            output_file = args.output_file
        else:
            output_file = Path(args.output_dir) / f"{args.judge_model}.csv"
        
        # 出力ディレクトリの作成
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)

        # CSVで保存
        try:
            with open(output_file, mode="w", encoding=args.encoding, errors="ignore", newline="") as f:
                eval_res_df.to_csv(f, index=True)
            print(f"結果を {output_file} に保存しました")
        except Exception as e:
            print(f"エラー: ファイルの保存に失敗: {e}", file=sys.stderr)
            sys.exit(1)
    
    else:
        # 全評価者モデルの処理
        judge_dirs = [d for d in judgements_path.iterdir() if d.is_dir() and d.name.startswith("judge_")]
        
        if not judge_dirs:
            print(f"エラー: {judgements_path} 内にjudge_で始まるディレクトリが見つかりません", file=sys.stderr)
            sys.exit(1)
        
        print(f"見つかった評価者モデル: {len(judge_dirs)}")
        
        # 出力ディレクトリの作成
        output_dir = Path(args.output_dir)
        if not output_dir.exists():
            output_dir.mkdir(parents=True, exist_ok=True)
        
        # 各評価者モデルを処理
        for judge_dir in sorted(judge_dirs):
            judge_model_name = judge_dir.name[6:]  # "judge_"を削除
            print(f"\n処理中: {judge_model_name}")
            
            eval_res_df = process_judge_model(judge_dir, eval_dataset_dict, weights)
            if eval_res_df is None:
                print(f"警告: {judge_dir} 内に有効な評価結果が見つかりません", file=sys.stderr)
                continue
            
            output_file = output_dir / f"{judge_model_name}.csv"
            
            try:
                with open(output_file, mode="w", encoding=args.encoding, errors="ignore", newline="") as f:
                    eval_res_df.to_csv(f, index=True)
                print(f"結果を {output_file} に保存しました")
            except Exception as e:
                print(f"エラー: {output_file} の保存に失敗: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
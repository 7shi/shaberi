#!/usr/bin/env python3

import argparse
import json
import sys
import logging
from pathlib import Path

import llm_functions
from evaluation_datasets_config import EVAL_MODEL_CONFIGS

def check_null_scores(filename):
    """JSONLファイルを読み込み、scoreがnullの行数を表示する"""
    null_score_lines = {}
    judge_model = None
    dataset_name = None
    
    # パスからjudge_modelとdataset_nameを抽出
    path = Path(filename)
    if len(path.parts) >= 3:
        grandparent_dir = path.parts[-3]
        if grandparent_dir.startswith('judge_'):
            judge_model = grandparent_dir[6:]  # "judge_"の後の部分を取得
            print(f"Judge model: {judge_model}")
    
    if len(path.parts) >= 2:
        # ディレクトリ名から__を/に戻してデータセット名を復元
        parent_dir = path.parts[-2]
        dataset_name = parent_dir.replace("__", "/")
        print(f"Dataset: {dataset_name}")
    
    # judge_modelが取得できない場合はエラー終了
    if not judge_model:
        print("エラー: ファイルパスからjudge_modelを抽出できませんでした。")
        print("ファイルは data/judgements/judge_*/... の形式である必要があります。")
        sys.exit(1)
    
    with open(filename, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            data = json.loads(line)
            if data.get('score') is None:
                null_score_lines[line_num] = data
    
    if not null_score_lines:
        print("scoreがnullの行はありません。")
        return
    
    print(f"scoreがnullの行数: {len(null_score_lines)}行")
    print(f"該当行番号: {list(null_score_lines.keys())}")
    
    # データセットに対応する評価関数を取得
    if dataset_name not in EVAL_MODEL_CONFIGS:
        print(f"エラー: データセット '{dataset_name}' に対応する評価関数が見つかりません。")
        sys.exit(1)
    
    evaluator_function = EVAL_MODEL_CONFIGS[dataset_name]["evaluator_function"]
    print(f"Evaluator: {evaluator_function.__name__}")
    
    # llm_functionsのロガーを設定
    llm_functions.setup_logging(judge_model, console_level=logging.DEBUG)
    
    # scoreがnullの各行について適切な評価関数を実行
    print(f"\n各行を再評価中...")
    for line_num, data in null_score_lines.items():
        print(f"\n行 {line_num} を評価中...")
        score = evaluator_function(data, judge_model)
        if score is not None:
            print(f"行 {line_num}: スコア = {score}")
            data['score'] = score
        else:
            print(f"行 {line_num}: 評価失敗")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="JSONLファイルを解析し、scoreがnullの行を検出します"
    )
    parser.add_argument(
        "filename",
        type=str,
        help="解析するJSONLファイルのパス（例: data/judgements/judge_*/...）"
    )
    parser.add_argument(
        "-t", "--max-tokens",
        type=int,
        default=llm_functions.evaluation_max_tokens,
        help=f"評価時の最大トークン数（デフォルト: {llm_functions.evaluation_max_tokens}）"
    )
    parser.add_argument(
        "-st", "--start-temperature",
        type=int,
        default=llm_functions.evaluation_start_temperature,
        help=f"評価時の開始温度（0-100の整数、デフォルト: {llm_functions.evaluation_start_temperature}）"
    )
    
    args = parser.parse_args()
    
    # max_tokensの設定
    llm_functions.evaluation_max_tokens = args.max_tokens
    llm_functions.evaluation_start_temperature = args.start_temperature
    
    print(f"ファイルを解析中: {args.filename}")
    print(f"最大トークン数: {args.max_tokens}")
    print(f"開始温度: {args.start_temperature / 100:.2f}")
    check_null_scores(args.filename)

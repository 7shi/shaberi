#!/usr/bin/env python3
"""
score_tool.py - スコア集計ツール

評価結果からevaluator/modelの組み合わせごとにスコア統計を集計し、TOML形式で出力します。
従来のJSONL形式と新しい構造化出力形式の両方に対応しています。

使用方法:
    # 既存の集計結果を表示
    python score_tool.py
    
    # 全てのベンチマークから自動収集して集計
    python score_tool.py -s
    
    # 特定のベンチマークのみから収集
    python score_tool.py -s0  # 従来形式のみ
    python score_tool.py -s1  # Tengu Benchのみ
    python score_tool.py -s2  # ELYZA-tasks-100のみ
    python score_tool.py -s3  # MT-Benchのみ
    
出力形式:
    benchmark_name:
      evaluator/model:
        total: X
        scores: [0, 1, 2, 3, ...]
"""

import argparse
import json
import os
import sys
from pathlib import Path
from collections import defaultdict
import yaml

# evaluation_datasets_config.pyからベンチマーク情報をインポート
sys.path.append('..')
try:
    from evaluation_datasets_config import EVAL_MODEL_CONFIGS
except ImportError:
    # フォールバック: デフォルトのベンチマークリスト
    EVAL_MODEL_CONFIGS = {
        "lightblue/tengu_bench": {},
        "elyza/ELYZA-tasks-100": {},
        "shisa-ai/ja-mt-bench-1shot": {},
        "kunishou/do-not-answer-120-ja": {},
        "umiyuki/do-not-answer-ja-creative-150": {},
    }


def determine_benchmark_from_path(file_path):
    """
    ファイルパスからベンチマーク名を判定
    """
    path_str = str(file_path)
    
    # 新形式ディレクトリマッピング（優先）
    if '/1tengu/' in path_str or path_str.startswith('1tengu/'):
        return 'lightblue/tengu_bench'
    elif '/2elyza/' in path_str or path_str.startswith('2elyza/'):
        return 'elyza/ELYZA-tasks-100'
    elif '/3mt/' in path_str or path_str.startswith('3mt/'):
        return 'shisa-ai/ja-mt-bench-1shot'
    
    # 従来形式: ../data/judgements/judge_xxx/dataset_name/model.json
    for benchmark_key in EVAL_MODEL_CONFIGS.keys():
        dataset_part = benchmark_key.replace('/', '__')
        if dataset_part in path_str:
            return benchmark_key
    
    # フォールバック: パスから推定
    if 'tengu' in path_str.lower():
        return 'lightblue/tengu_bench'
    elif 'elyza' in path_str.lower():
        return 'elyza/ELYZA-tasks-100'
    elif 'mt-bench' in path_str.lower():
        return 'shisa-ai/ja-mt-bench-1shot'
    elif 'do-not-answer-120' in path_str.lower():
        return 'kunishou/do-not-answer-120-ja'
    elif 'do-not-answer-ja-creative' in path_str.lower():
        return 'umiyuki/do-not-answer-ja-creative-150'
    
    return 'unknown'


def extract_scores_from_directory(directory_path, benchmark_name=None):
    """
    指定されたディレクトリから直接JSONファイルを読み込み、スコアを集計
    
    Args:
        directory_path (str): 評価結果ディレクトリのパス
        benchmark_name (str): ベンチマーク名、省略時はパスから自動判定
        
    Returns:
        dict: {benchmark_name: {dir_name: {'total': int, 'scores': [int, ...]}}}
    """
    base_path = Path(directory_path)
    results = {}
    
    if not base_path.exists() or not base_path.is_dir():
        return results
    
    # 指定ディレクトリから直接JSONファイルを読み込み
    json_files = sorted(base_path.glob("*.json"))
    
    if not json_files:
        return results
    
    # ベンチマーク名を判定
    if benchmark_name is None:
        benchmark_name = determine_benchmark_from_path(base_path)
    
    # basename(dirname)/basename の形式でdir名を作成
    parent_path = base_path.parent
    dir_name = f"{parent_path.name}/{base_path.name}"
    
    scores = []
    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # scoreフィールドからスコアを取得
            score = data.get('score', 0)
            scores.append(int(score))
            
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Warning: {json_file} の読み込みに失敗: {e}")
            scores.append(0)  # エラー時は0として扱う
    
    if scores:
        results[benchmark_name] = {
            dir_name: {
                'total': sum(scores),
                'scores': scores
            }
        }
    
    return results


def extract_scores_from_jsonl_file(file_path):
    """
    従来の評価結果ファイル（JSONL形式）からスコアを集計
    
    Args:
        file_path (str): JSONLファイルのパス
        
    Returns:
        dict: {benchmark_name: {dir_name: {'total': int, 'scores': [int, ...]}}}
    """
    file_path = Path(file_path)
    results = {}
    
    if not file_path.exists() or not file_path.is_file():
        return results
    
    # ファイルパスから dir_name を作成
    # ../data/judgements/judge_gemini-2.5-flash-preview-05-20/lightblue__tengu_bench/gemini-2.5-pro.json
    # → judge_gemini-2.5-flash-preview-05-20/gemini-2.5-pro
    parts = file_path.parts
    if len(parts) >= 3 and 'judgements' in parts:
        judge_idx = None
        for i, part in enumerate(parts):
            if part == 'judgements':
                judge_idx = i
                break
        
        if judge_idx is not None and judge_idx + 3 < len(parts):
            evaluator = parts[judge_idx + 1]  # judge_XXX
            model = parts[judge_idx + 3]  # gemini-2.5-pro.json
            dir_name = f"{evaluator}/{model}"
        else:
            # fallback: ファイル名のみ使用
            dir_name = file_path.stem
    else:
        # fallback: ファイル名のみ使用
        dir_name = file_path.stem
    
    scores = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                
                try:
                    data = json.loads(line)
                    score = data.get('score', 0)
                    scores.append(int(score))
                    
                except json.JSONDecodeError as e:
                    print(f"Warning: {file_path}:{line_num} JSON解析エラー: {e}")
                    scores.append(0)
        
    except Exception as e:
        print(f"Warning: {file_path} の読み込みに失敗: {e}")
        return results
    
    if scores:
        # Noneチェック
        none_indices = []
        for i, score in enumerate(scores):
            if score is None:
                none_indices.append(i + 1)  # 行番号は1始まり
        
        if none_indices:
            print(f"Error: {file_path} に以下の行でscoreがNoneです:")
            for line_num in none_indices:
                print(f"  - 行 {line_num}")
            print("処理を中止します")
            return results
        
        # ベンチマーク名を判定
        benchmark_name = determine_benchmark_from_path(file_path)
        
        results[benchmark_name] = {
            dir_name: {
                'total': sum(scores),
                'scores': scores
            }
        }
    
    return results


def display_scores(output_file='scores.yaml'):
    """
    既存のYAMLファイルからスコア統計を表示
    
    Args:
        output_file (str): YAMLファイルのパス
    """
    if not os.path.exists(output_file):
        print(f"Error: {output_file} が存在しません")
        return False
    
    try:
        with open(output_file, 'r', encoding='utf-8') as f:
            yaml_data = yaml.safe_load(f)
        
        if not yaml_data:
            print(f"Warning: {output_file} にデータがありません")
            return True
        
        # 全ベンチマークでの総組み合わせ数を計算
        all_combinations = []
        for benchmark_name, benchmark_data in yaml_data.items():
            for evaluator_model, data in benchmark_data.items():
                total = data.get('total', 0)
                scores = data.get('scores', [])
                tasks = len(scores)
                avg = total / tasks if tasks > 0 else 0
                all_combinations.append({
                    'name': f"{benchmark_name}/{evaluator_model}",
                    'total': total,
                    'tasks': tasks,
                    'avg': avg
                })
        
        # スコア（total）の降順でソート
        all_combinations.sort(key=lambda x: x['total'], reverse=True)
        
        print(f"スコア統計表示: {output_file}")
        print(f"総組み合わせ数: {len(all_combinations)}")
        print("-" * 80)
        
        for combo in all_combinations:
            print(f"{combo['total']}/{combo['tasks']}={combo['avg']:.2f} {combo['name']}")
        
        return True
        
    except Exception as e:
        print(f"Error: {output_file} の読み込みに失敗しました: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="評価結果ディレクトリからスコア統計を集計します",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
    # 既存の集計結果を表示
    python score_tool.py
    
    # 全てのベンチマークから自動収集して集計
    python score_tool.py -s
    
    # 従来形式のみから収集
    python score_tool.py -s0
    
    # 特定のベンチマークのみから収集
    python score_tool.py -s1  # Tengu Bench
    python score_tool.py -s2  # ELYZA-tasks-100
    python score_tool.py -s3  # MT-Bench
    
    # カスタムディレクトリから収集
    python score_tool.py -s1 -j1 /custom/tengu
    python score_tool.py -s2 -j2 /custom/elyza
        
出力形式:
    benchmark_name:
      evaluator/model:
        total: X
        scores: [0, 1, 2, 3, ...]
        """
    )
    
    parser.add_argument(
        '-s', '--scan',
        action='store_true',
        help='全てのディレクトリから自動的に評価結果を収集して集計'
    )
    
    parser.add_argument(
        '-s0', '--scan0',
        action='store_true',
        help='従来形式のディレクトリ(-j0)からのみ収集'
    )
    
    parser.add_argument(
        '-s1', '--scan1',
        action='store_true',
        help='Tengu Benchディレクトリ(-j1)からのみ収集'
    )
    
    parser.add_argument(
        '-s2', '--scan2',
        action='store_true',
        help='ELYZA-tasks-100ディレクトリ(-j2)からのみ収集'
    )
    
    parser.add_argument(
        '-s3', '--scan3',
        action='store_true',
        help='MT-Benchディレクトリ(-j3)からのみ収集'
    )
    
    parser.add_argument(
        '-j0', '--judgements-dir0',
        default='../data/judgements',
        help='従来形式の評価結果ディレクトリ (デフォルト: ../data/judgements)'
    )
    
    parser.add_argument(
        '-j1', '--judgements-dir1',
        default='1tengu',
        help='Tengu Benchの評価結果ディレクトリ (デフォルト: 1tengu)'
    )
    
    parser.add_argument(
        '-j2', '--judgements-dir2',
        default='2elyza',
        help='ELYZA-tasks-100の評価結果ディレクトリ (デフォルト: 2elyza)'
    )
    
    parser.add_argument(
        '-j3', '--judgements-dir3',
        default='3mt',
        help='MT-Benchの評価結果ディレクトリ (デフォルト: 3mt)'
    )
    
    parser.add_argument(
        '-o', '--output',
        default='scores.yaml',
        help='出力ファイル名 (デフォルト: scores.yaml)'
    )
    
    args = parser.parse_args()
    
    # スキャンオプションが指定されていない場合は表示のみ
    if not (args.scan or args.scan0 or args.scan1 or args.scan2 or args.scan3):
        success = display_scores(args.output)
        return 0 if success else 1
    
    # 処理対象のパスを収集
    paths_to_process = []
    
    # -s0 または -s の場合、j0ディレクトリから従来形式のファイルを収集
    if args.scan0 or args.scan:
        j0_path = Path(args.judgements_dir0)
        if j0_path.exists():
            # judge_*/dataset/model.json のパターンでファイルを検索
            jsonl_files = list(j0_path.glob("judge_*/*/*.json"))
            if jsonl_files:
                print(f"{args.judgements_dir0} から {len(jsonl_files)} 個の従来形式評価結果ファイルを発見")
                paths_to_process.extend([str(f) for f in jsonl_files])
            else:
                print(f"Warning: {args.judgements_dir0} に評価結果ファイルが見つかりません")
        else:
            print(f"Warning: {args.judgements_dir0} が存在しません")
    
    # -s1 または -s の場合、j1ディレクトリからTengu Benchのディレクトリを収集
    if args.scan1 or args.scan:
        j1_path = Path(args.judgements_dir1)
        if j1_path.exists():
            # evaluator/model のディレクトリパターンを検索
            eval_dirs = []
            for evaluator_dir in j1_path.iterdir():
                if evaluator_dir.is_dir():
                    for model_dir in evaluator_dir.iterdir():
                        if model_dir.is_dir() and list(model_dir.glob("*.json")):
                            eval_dirs.append(str(model_dir))
            
            if eval_dirs:
                print(f"{args.judgements_dir1} から {len(eval_dirs)} 個のTengu Bench評価結果ディレクトリを発見")
                paths_to_process.extend(eval_dirs)
            else:
                print(f"Warning: {args.judgements_dir1} に評価結果ディレクトリが見つかりません")
        else:
            print(f"Warning: {args.judgements_dir1} が存在しません")
    
    # -s2 または -s の場合、j2ディレクトリからELYZA-tasks-100のディレクトリを収集
    if args.scan2 or args.scan:
        j2_path = Path(args.judgements_dir2)
        if j2_path.exists():
            # evaluator/model のディレクトリパターンを検索
            eval_dirs = []
            for evaluator_dir in j2_path.iterdir():
                if evaluator_dir.is_dir():
                    for model_dir in evaluator_dir.iterdir():
                        if model_dir.is_dir() and list(model_dir.glob("*.json")):
                            eval_dirs.append(str(model_dir))
            
            if eval_dirs:
                print(f"{args.judgements_dir2} から {len(eval_dirs)} 個のELYZA-tasks-100評価結果ディレクトリを発見")
                paths_to_process.extend(eval_dirs)
            else:
                print(f"Warning: {args.judgements_dir2} に評価結果ディレクトリが見つかりません")
        else:
            print(f"Warning: {args.judgements_dir2} が存在しません")
    
    # -s3 または -s の場合、j3ディレクトリからMT-Benchのディレクトリを収集
    if args.scan3 or args.scan:
        j3_path = Path(args.judgements_dir3)
        if j3_path.exists():
            # evaluator/model のディレクトリパターンを検索
            eval_dirs = []
            for evaluator_dir in j3_path.iterdir():
                if evaluator_dir.is_dir():
                    for model_dir in evaluator_dir.iterdir():
                        if model_dir.is_dir() and list(model_dir.glob("*.json")):
                            eval_dirs.append(str(model_dir))
            
            if eval_dirs:
                print(f"{args.judgements_dir3} から {len(eval_dirs)} 個のMT-Bench評価結果ディレクトリを発見")
                paths_to_process.extend(eval_dirs)
            else:
                print(f"Warning: {args.judgements_dir3} に評価結果ディレクトリが見つかりません")
        else:
            print(f"Warning: {args.judgements_dir3} が存在しません")
    
    if not paths_to_process:
        print("Error: 処理対象のファイル/ディレクトリが見つかりません")
        return 1
    
    # 複数パスの処理
    all_results = {}
    processed_count = 0
    
    for path in paths_to_process:
        # パスの存在確認
        if not os.path.exists(path):
            print(f"Error: パスが存在しません: {path}")
            continue
        
        # ファイルかディレクトリかで処理を分岐
        if os.path.isfile(path):
            # JSONLファイルとして処理
            print(f"評価結果ファイルを集計中: {path}")
            results = extract_scores_from_jsonl_file(path)
        elif os.path.isdir(path):
            # ディレクトリとして処理
            print(f"評価結果ディレクトリを集計中: {path}")
            results = extract_scores_from_directory(path)
        else:
            print(f"Warning: {path} はファイルでもディレクトリでもありません")
            continue
        
        if results:
            # ベンチマーク別のデータを統合
            for benchmark_name, benchmark_data in results.items():
                if benchmark_name not in all_results:
                    all_results[benchmark_name] = {}
                all_results[benchmark_name].update(benchmark_data)
                processed_count += len(benchmark_data)
        else:
            print(f"Warning: {path} から評価結果が見つかりませんでした")
    
    if not all_results:
        print("Warning: すべてのパスで評価結果が見つかりませんでした")
        return 0
    
    print(f"合計 {processed_count} 組み合わせを処理しました")
    
    # 既存のYAMLファイルを読み込み（存在する場合）
    yaml_data = {}
    if os.path.exists(args.output):
        try:
            with open(args.output, 'r', encoding='utf-8') as f:
                yaml_data = yaml.safe_load(f) or {}
            print(f"既存の {args.output} を読み込みました")
        except Exception as e:
            print(f"Warning: 既存ファイルの読み込みに失敗: {e}")
            yaml_data = {}
    
    # 新しいデータで更新
    for benchmark_name in sorted(all_results.keys()):
        if benchmark_name not in yaml_data:
            yaml_data[benchmark_name] = {}
        yaml_data[benchmark_name].update(all_results[benchmark_name])
    
    # YAMLファイルに書き込み（ベンチマーク別にスコア降順でソート）
    try:
        # 各ベンチマーク内でスコア降順ソート
        sorted_yaml_data = {}
        for benchmark_name in sorted(yaml_data.keys()):
            benchmark_data = yaml_data[benchmark_name]
            sorted_items = sorted(benchmark_data.items(), 
                                key=lambda x: x[1]['total'], reverse=True)
            sorted_yaml_data[benchmark_name] = dict(sorted_items)
        
        with open(args.output, 'w', encoding='utf-8') as f:
            # 配列（scoresのみ）をインライン形式で出力
            yaml.add_representer(list, lambda dumper, data: dumper.represent_sequence('tag:yaml.org,2002:seq', data, flow_style=True))
            yaml.dump(sorted_yaml_data, f, 
                     default_flow_style=False, 
                     allow_unicode=True, 
                     sort_keys=False,
                     indent=2)
        
        # 結果の統計情報を表示
        total_combinations = sum(len(benchmark_data) for benchmark_data in yaml_data.values())
        print(f"スコア集計結果を {args.output} に保存しました")
        print(f"更新された組み合わせ: {processed_count}")
        print(f"ファイル内の総組み合わせ数: {total_combinations}")
        
        # コンソールにも詳細表示（ベンチマーク別）
        print("-" * 80)
        for benchmark_name in sorted(sorted_yaml_data.keys()):
            print(f"[{benchmark_name}]")
            for evaluator_model, data in sorted_yaml_data[benchmark_name].items():
                total = data['total']
                tasks = len(data['scores'])
                avg = total / tasks if tasks > 0 else 0
                print(f"  {total}/{tasks}={avg:.2f} {evaluator_model}")
            print()
            
    except Exception as e:
        print(f"Error: ファイル出力に失敗しました: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
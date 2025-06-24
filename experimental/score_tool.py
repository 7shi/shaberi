#!/usr/bin/env python3
"""
score_tool.py - スコア集計ツール

評価結果からevaluator/modelの組み合わせごとにスコア統計を集計し、YAML形式で出力します。
従来のJSONL形式と新しい構造化出力形式の両方に対応しています。

使用方法:
    # 既存の集計結果を表示
    uv run score_tool.py list
    
    # 全てのデフォルトパスから自動収集して集計
    uv run score_tool.py add
    
    # 特定のディレクトリのみから収集
    uv run score_tool.py add -j ../data/judgements    # 従来形式のみ
    uv run score_tool.py add --tengu 1tengu           # Tengu Benchのみ
    uv run score_tool.py add --elyza 2elyza           # ELYZA-tasks-100のみ
    uv run score_tool.py add --mt 3mt                 # MT-Benchのみ
    uv run score_tool.py add -j ../data/judgements --tengu 1tengu/judge  # 複数指定
    
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

# デフォルトのベンチマークリスト
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


def display_scores(output_file='scores.yaml', patterns=None, benchmark=None, exclude_patterns=None):
    """
    既存のYAMLファイルからスコア統計を表示
    
    Args:
        output_file (str): YAMLファイルのパス
        patterns (list): 表示対象のパターンリスト（AND条件）
        benchmark (str): 指定したベンチマーク名、省略時は全ベンチマークを対象
        exclude_patterns (list): 除外パターンのリスト（grep -v相当）
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
        
        # パターンフィルタリングまたはベンチマーク指定がある場合
        if patterns or benchmark or exclude_patterns:
            # patternsが空の場合は空リストとして扱う
            patterns = patterns or []
            matches = find_matching_entries(yaml_data, patterns, benchmark, exclude_patterns)
            if not matches:
                if patterns or exclude_patterns:
                    desc_parts = []
                    if patterns:
                        pattern_str = "', '".join(patterns)
                        desc_parts.append(f"パターン '{pattern_str}'")
                    if exclude_patterns:
                        exclude_str = "', '".join(exclude_patterns)
                        desc_parts.append(f"除外パターン '{exclude_str}'")
                    print(f"{' および '.join(desc_parts)} に一致するエントリが見つかりません")
                else:
                    print(f"ベンチマーク '{benchmark}' が見つかりません")
                return True
            
            # マッチしたエントリのみでYAMLデータを再構築
            filtered_yaml_data = {}
            for benchmark_name, evaluator_model, full_path in matches:
                if benchmark_name not in filtered_yaml_data:
                    filtered_yaml_data[benchmark_name] = {}
                filtered_yaml_data[benchmark_name][evaluator_model] = yaml_data[benchmark_name][evaluator_model]
            yaml_data = filtered_yaml_data
        
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
        
        # ベンチマーク別に表示するために再構築
        benchmark_display = {}
        for benchmark_name, benchmark_data in yaml_data.items():
            benchmark_display[benchmark_name] = []
            for evaluator_model, data in benchmark_data.items():
                total = data.get('total', 0)
                scores = data.get('scores', [])
                tasks = len(scores)
                avg = total / tasks if tasks > 0 else 0
                benchmark_display[benchmark_name].append((total, tasks, avg, evaluator_model))
            # ベンチマーク内でスコア降順ソート
            benchmark_display[benchmark_name].sort(key=lambda x: x[0], reverse=True)
        
        for benchmark_name in sorted(benchmark_display.keys()):
            print(f"[{benchmark_name}]")
            for total, tasks, avg, evaluator_model in benchmark_display[benchmark_name]:
                print(f"{total:4d}/{tasks}={avg:.2f} {evaluator_model}")
            print()
        
        total_combinations = sum(len(all_combinations) for all_combinations in benchmark_display.values())
        print(f"総組み合わせ数: {total_combinations}")
        
        return True
        
    except Exception as e:
        print(f"Error: {output_file} の読み込みに失敗しました: {e}")
        return False


def _collect_judgements_files(judgements_dir):
    """
    従来形式のディレクトリからJSONLファイルを収集
    """
    paths = []
    j0_path = Path(judgements_dir)
    if j0_path.exists():
        # judge_*/dataset/model.json のパターンでファイルを検索
        jsonl_files = list(j0_path.glob("judge_*/*/*.json"))
        if jsonl_files:
            print(f"{judgements_dir} から {len(jsonl_files)} 個の従来形式評価結果ファイルを発見")
            paths.extend([str(f) for f in jsonl_files])
        else:
            print(f"Warning: {judgements_dir} に評価結果ファイルが見つかりません")
    else:
        print(f"Warning: {judgements_dir} が存在しません")
    return paths


def _collect_benchmark_dirs(benchmark_dir, benchmark_type):
    """
    ベンチマーク用ディレクトリから評価結果ディレクトリを収集
    """
    paths = []
    benchmark_path = Path(benchmark_dir)
    if benchmark_path.exists():
        # evaluator/model のディレクトリパターンを検索
        eval_dirs = []
        for evaluator_dir in benchmark_path.iterdir():
            if evaluator_dir.is_dir():
                for model_dir in evaluator_dir.iterdir():
                    if model_dir.is_dir() and list(model_dir.glob("*.json")):
                        eval_dirs.append(str(model_dir))
        
        if eval_dirs:
            benchmark_name = {'tengu': 'Tengu Bench', 'elyza': 'ELYZA-tasks-100', 'mt': 'MT-Bench'}.get(benchmark_type, benchmark_type)
            print(f"{benchmark_dir} から {len(eval_dirs)} 個の{benchmark_name}評価結果ディレクトリを発見")
            paths.extend(eval_dirs)
        else:
            print(f"Warning: {benchmark_dir} に評価結果ディレクトリが見つかりません")
    else:
        print(f"Warning: {benchmark_dir} が存在しません")
    return paths


def cmd_list(args):
    """
    既存の集計結果を表示する
    """
    patterns = getattr(args, 'pattern', None)
    benchmark = getattr(args, 'benchmark', None)
    exclude_patterns = getattr(args, 'exclude', None)
    output_file = getattr(args, 'output_file', 'scores.yaml')
    success = display_scores(output_file, patterns, benchmark, exclude_patterns)
    return 0 if success else 1


def find_matching_entries(yaml_data, patterns, benchmark=None, exclude_patterns=None):
    """
    指定されたパターンに基づいてエントリを検索する共通関数
    
    Args:
        yaml_data (dict): YAMLデータ
        patterns (list): 検索パターンのリスト（AND条件）
        benchmark (str): 指定したベンチマーク名、省略時は全ベンチマークを対象
        exclude_patterns (list): 除外パターンのリスト（AND条件、grep -v相当）
        
    Returns:
        list: マッチした(benchmark_name, evaluator_model, full_path)のリスト
    """
    exclude_patterns = exclude_patterns or []
    matches = []
    for benchmark_name, benchmark_data in yaml_data.items():
        if benchmark:
            # 指定したベンチマーク内で部分一致検索
            if benchmark_name == benchmark:
                for evaluator_model in benchmark_data.keys():
                    # 包含パターンマッチング（AND条件）
                    include_match = all(pattern in evaluator_model for pattern in patterns) if patterns else True
                    # 除外パターンマッチング（AND条件）- いずれかが含まれていれば除外
                    exclude_match = any(pattern in evaluator_model for pattern in exclude_patterns) if exclude_patterns else False
                    
                    if include_match and not exclude_match:
                        full_path = f"{benchmark_name}/{evaluator_model}"
                        matches.append((benchmark_name, evaluator_model, full_path))
        else:
            # 全ベンチマークから項目名での部分一致検索
            for evaluator_model in benchmark_data.keys():
                # 包含パターンマッチング（AND条件）
                include_match = all(pattern in evaluator_model for pattern in patterns) if patterns else True
                # 除外パターンマッチング（AND条件）- いずれかが含まれていれば除外
                exclude_match = any(pattern in evaluator_model for pattern in exclude_patterns) if exclude_patterns else False
                
                if include_match and not exclude_match:
                    full_path = f"{benchmark_name}/{evaluator_model}"
                    matches.append((benchmark_name, evaluator_model, full_path))
    
    return matches


def cmd_remove(args):
    """
    指定された前方一致パターンに基づいてエントリを削除する
    """
    # パターンが空でベンチマークも除外パターンも指定されていない場合はエラー
    exclude_patterns = getattr(args, 'exclude', None)
    if not args.pattern and not args.benchmark and not exclude_patterns:
        print("Error: 削除対象のパターン、ベンチマーク、または除外パターンを指定してください")
        return 1
    
    if not os.path.exists(args.output):
        print(f"Error: {args.output} が存在しません")
        return 1
    
    try:
        with open(args.output, 'r', encoding='utf-8') as f:
            yaml_data = yaml.safe_load(f) or {}
    except Exception as e:
        print(f"Error: {args.output} の読み込みに失敗しました: {e}")
        return 1
    
    if not yaml_data:
        print(f"Warning: {args.output} にデータがありません")
        return 0
    
    # 削除対象を検索
    to_remove = find_matching_entries(yaml_data, args.pattern, args.benchmark, exclude_patterns)
    
    if not to_remove:
        if args.pattern or exclude_patterns:
            desc_parts = []
            if args.pattern:
                pattern_str = "', '".join(args.pattern)
                desc_parts.append(f"パターン '{pattern_str}'")
            if exclude_patterns:
                exclude_str = "', '".join(exclude_patterns)
                desc_parts.append(f"除外パターン '{exclude_str}'")
            print(f"{' および '.join(desc_parts)} に一致するエントリが見つかりません")
        else:
            print(f"ベンチマーク '{args.benchmark}' が見つかりません")
        return 0
    
    # 削除対象データの準備（ベンチマーク別にグループ化）
    grouped_remove = {}
    for benchmark_name, evaluator_model, full_path in to_remove:
        if benchmark_name not in grouped_remove:
            grouped_remove[benchmark_name] = []
        data = yaml_data[benchmark_name][evaluator_model]
        total = data.get('total', 0)
        tasks = len(data.get('scores', []))
        avg = total / tasks if tasks > 0 else 0
        grouped_remove[benchmark_name].append((total, tasks, avg, evaluator_model))
    
    for benchmark_name in sorted(grouped_remove.keys()):
        print(f"[{benchmark_name}]")
        for total, tasks, avg, evaluator_model in grouped_remove[benchmark_name]:
            print(f"  {total:4d}/{tasks}={avg:.2f} {evaluator_model}")
    
    print()
    print(f"{len(to_remove)} 個のエントリを削除します。")
    
    # 確認プロンプト（--force オプションがない場合）
    if not args.force:
        response = input("削除を実行しますか? (y/N): ").strip().lower()
        if response.strip().lower() not in ['y', 'yes']:
            print("削除をキャンセルしました")
            return 0
    
    # 削除実行
    removed_count = 0
    for benchmark_name, evaluator_model, full_path in to_remove:
        del yaml_data[benchmark_name][evaluator_model]
        removed_count += 1
        
        # ベンチマークが空になった場合は削除
        if not yaml_data[benchmark_name]:
            del yaml_data[benchmark_name]
    
    # ファイルに書き戻し
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
        
        print(f"\n{removed_count} 個のエントリを削除しました")
        print(f"更新された {args.output} を保存しました")
        
        # 残りの統計情報を表示
        total_combinations = sum(len(benchmark_data) for benchmark_data in sorted_yaml_data.values())
        print(f"残りの組み合わせ数: {total_combinations}")
        
    except Exception as e:
        print(f"Error: ファイル出力に失敗しました: {e}")
        return 1
    
    return 0


def cmd_add(args):
    """
    評価結果を収集して集計する
    """
    
    # 処理対象のパスを収集
    paths_to_process = []
    
    # 指定されたディレクトリが何もない場合はデフォルトパスを全て試行
    if not any([args.judgements_dir, args.tengu, args.elyza, args.mt]):
        default_paths = [
            ('judgements', '../data/judgements'),
            ('tengu', '1tengu/judge'),
            ('elyza', '2elyza/judge'),
            ('mt', '3mt/judge')
        ]
        
        for path_type, default_path in default_paths:
            if path_type == 'judgements':
                paths_to_process.extend(_collect_judgements_files(default_path))
            else:
                paths_to_process.extend(_collect_benchmark_dirs(default_path, path_type))
    
    # 従来形式ディレクトリが指定された場合
    if args.judgements_dir:
        paths_to_process.extend(_collect_judgements_files(args.judgements_dir))
    
    # Tengu Benchディレクトリが指定された場合
    if args.tengu:
        paths_to_process.extend(_collect_benchmark_dirs(args.tengu, 'tengu'))
    
    # ELYZA-tasks-100ディレクトリが指定された場合
    if args.elyza:
        paths_to_process.extend(_collect_benchmark_dirs(args.elyza, 'elyza'))
    
    # MT-Benchディレクトリが指定された場合
    if args.mt:
        paths_to_process.extend(_collect_benchmark_dirs(args.mt, 'mt'))
    
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
            
    except Exception as e:
        print(f"Error: ファイル出力に失敗しました: {e}")
        return 1
    
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="評価結果ディレクトリからスコア統計を集計します",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
    # 既存の集計結果を表示（デフォルト: scores.yaml）
    uv run score_tool.py list                                         # 全エントリを表示
    uv run score_tool.py list "gemini"                                # geminiを含むエントリのみ表示
    uv run score_tool.py my-score.yaml list "judge_gpt" "gemini"      # カスタムファイルでjudge_gptとgeminiの両方を含むエントリのみ表示
    uv run score_tool.py list -b "lightblue/tengu_bench" "gemini"     # 指定ベンチマーク内でgeminiを含むエントリのみ表示
    uv run score_tool.py list -b "lightblue/tengu_bench" "gemini-2.5-pro" -v "preview"  # gemini-2.5-proを含み、previewを含まないエントリ
    
    # 部分一致パターンでエントリを削除
    uv run score_tool.py remove "gemini-2.0-flash"                    # 全ベンチマークから項目名の部分一致
    uv run score_tool.py my-score.yaml remove "judge_gpt" "gemini"    # カスタムファイルでAND条件で削除
    uv run score_tool.py remove -b "lightblue/tengu_bench"            # 指定ベンチマーク全体を削除
    uv run score_tool.py remove -b "lightblue/tengu_bench" "gemini"   # 指定ベンチマーク内での部分一致
    uv run score_tool.py remove "gemini" -v "preview" -v "lite"       # geminiを含み、previewとliteを含まないエントリを削除
    
    # 全てのデフォルトパスから自動収集して集計
    uv run score_tool.py add                                          # デフォルトファイルに集計
    uv run score_tool.py my-score.yaml add                            # カスタムファイルに集計
    
    # 特定のディレクトリのみから収集
    uv run score_tool.py add -j ../data/judgements                    # 従来形式のみ
    uv run score_tool.py my-score.yaml add --tengu 1tengu/judge       # Tengu Benchのみ
    uv run score_tool.py add --elyza 2elyza/judge                     # ELYZA-tasks-100のみ
    uv run score_tool.py add --mt 3mt/judge                           # MT-Benchのみ
    
    # カスタムディレクトリから収集
    uv run score_tool.py add --tengu /custom/tengu
    uv run score_tool.py my-score.yaml add -j /custom/judgements --elyza /custom/elyza
        
出力形式:
    benchmark_name:
      evaluator/model:
        total: X
        scores: [0, 1, 2, 3, ...]
        """
    )
    
    # メインの出力ファイル引数（オプション）
    parser.add_argument(
        'output_file',
        nargs='?',
        default='scores.yaml',
        help='操作対象のYAMLファイル名（デフォルト: scores.yaml）'
    )
    
    # サブコマンドの設定
    subparsers = parser.add_subparsers(dest='command', help='利用可能なコマンド')
    
    # list サブコマンド
    list_parser = subparsers.add_parser('list', help='既存の集計結果を表示')
    list_parser.add_argument(
        'pattern',
        nargs='*',
        help='表示対象パターン（項目名の部分一致、複数指定でAND条件）'
    )
    list_parser.add_argument(
        '-b', '--benchmark',
        metavar='BENCHMARK',
        help='指定したベンチマーク内でpatternの部分一致検索を実行'
    )
    list_parser.add_argument(
        '-v', '--exclude',
        action='append',
        metavar='PATTERN',
        help='除外パターン（grep -v相当、複数指定可能）'
    )
    
    # remove サブコマンド
    remove_parser = subparsers.add_parser('remove', help='部分一致パターンでエントリを削除')
    remove_parser.add_argument(
        'pattern',
        nargs='*',
        help='削除対象パターン（項目名の部分一致、複数指定でAND条件）'
    )
    remove_parser.add_argument(
        '-b', '--benchmark',
        metavar='BENCHMARK',
        help='指定したベンチマーク内でpatternの部分一致検索を実行'
    )
    remove_parser.add_argument(
        '-v', '--exclude',
        action='append',
        metavar='PATTERN',
        help='除外パターン（grep -v相当、複数指定可能）'
    )
    remove_parser.add_argument(
        '-f', '--force',
        action='store_true',
        help='確認なしで削除を実行'
    )
    
    # add サブコマンド
    add_parser = subparsers.add_parser('add', help='評価結果を収集して集計')
    add_parser.add_argument(
        '-j', '--judgements-dir',
        metavar='DIR',
        help='従来形式の評価結果ディレクトリを指定'
    )
    add_parser.add_argument(
        '--tengu',
        metavar='DIR',
        help='Tengu Benchの評価結果ディレクトリを指定'
    )
    add_parser.add_argument(
        '--elyza',
        metavar='DIR',
        help='ELYZA-tasks-100の評価結果ディレクトリを指定'
    )
    add_parser.add_argument(
        '--mt',
        metavar='DIR',
        help='MT-Benchの評価結果ディレクトリを指定'
    )
    
    args = parser.parse_args()
    
    # サブコマンドが指定されていない場合はヘルプを表示
    if args.command is None:
        parser.print_help()
        return 1
    
    
    # サブコマンドの実行
    if args.command == 'list':
        return cmd_list(args)
    elif args.command == 'remove':
        return cmd_remove(args)
    elif args.command == 'add':
        return cmd_add(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    exit(main())

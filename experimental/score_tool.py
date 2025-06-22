#!/usr/bin/env python3
"""
score_tool.py - スコア集計ツール

指定されたディレクトリ内の評価結果から、evaluator/model の2階層ディレクトリ構造を解析し、
各組み合わせのスコア統計を出力します。

使用方法:
    python score_tool.py <directory_path>
    
出力形式:
    ["evaluator/model"]
    total = X
    scores = [0, 1, 2, 3, ...]
"""

import argparse
import json
import os
from pathlib import Path
from collections import defaultdict
try:
    import tomllib
except ImportError:
    import tomli as tomllib


def extract_scores_from_directory(directory_path):
    """
    指定されたディレクトリから直接JSONファイルを読み込み、スコアを集計
    
    Args:
        directory_path (str): 評価結果ディレクトリのパス
        
    Returns:
        dict: {dir_name: {'total': int, 'scores': [int, ...]}}
    """
    base_path = Path(directory_path)
    results = {}
    
    if not base_path.exists() or not base_path.is_dir():
        return results
    
    # 指定ディレクトリから直接JSONファイルを読み込み
    json_files = sorted(base_path.glob("*.json"))
    
    if not json_files:
        return results
    
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
            scores.append(score)
            
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Warning: {json_file} の読み込みに失敗: {e}")
            scores.append(0)  # エラー時は0として扱う
    
    if scores:
        results[dir_name] = {
            'total': sum(scores),
            'scores': scores
        }
    
    return results


def extract_scores_from_jsonl_file(file_path):
    """
    従来の評価結果ファイル（JSONL形式）からスコアを集計
    
    Args:
        file_path (str): JSONLファイルのパス
        
    Returns:
        dict: {dir_name: {'total': int, 'scores': [int, ...]}}
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
                    scores.append(score)
                    
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
        
        results[dir_name] = {
            'total': sum(scores),
            'scores': scores
        }
    
    return results


def display_scores(output_file='scores.toml'):
    """
    既存のTOMLファイルからスコア統計を表示
    
    Args:
        output_file (str): TOMLファイルのパス
    """
    if not os.path.exists(output_file):
        print(f"Error: {output_file} が存在しません")
        return False
    
    try:
        with open(output_file, 'rb') as f:
            toml_data = tomllib.load(f)
        
        if not toml_data:
            print(f"Warning: {output_file} にデータがありません")
            return True
        
        # スコア（total）の降順でソート
        sorted_items = sorted(toml_data.items(), key=lambda x: x[1]['total'], reverse=True)
        
        print(f"スコア統計表示: {output_file}")
        print(f"総組み合わせ数: {len(toml_data)}")
        print("-" * 80)
        
        for dir_name, data in sorted_items:
            total = data.get('total', 0)
            scores = data.get('scores', [])
            tasks = len(scores)
            avg = total / tasks if tasks > 0 else 0
            
            print(f"{total}/{tasks}={avg:.2f} {dir_name}")
        
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
    python score_tool.py 1tengu
    python score_tool.py /path/to/evaluation/results
        
出力形式:
    ["evaluator/model"]
    total = X
    scores = [0, 1, 2, 3, ...]
        """
    )
    
    parser.add_argument(
        'paths',
        nargs='*',
        help='評価結果のディレクトリまたはJSONLファイルのパス（複数指定可能、省略時は表示のみ）'
    )
    
    parser.add_argument(
        '-o', '--output',
        default='scores.toml',
        help='出力ファイル名 (デフォルト: scores.toml)'
    )
    
    args = parser.parse_args()
    
    # 引数なしの場合は表示のみ
    if not args.paths:
        success = display_scores(args.output)
        return 0 if success else 1
    
    # 複数パスの処理
    all_results = {}
    processed_count = 0
    
    for path in args.paths:
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
            all_results.update(results)
            processed_count += len(results)
        else:
            print(f"Warning: {path} から評価結果が見つかりませんでした")
    
    if not all_results:
        print("Warning: すべてのパスで評価結果が見つかりませんでした")
        return 0
    
    print(f"合計 {processed_count} 組み合わせを処理しました")
    
    # 既存のTOMLファイルを読み込み（存在する場合）
    toml_data = {}
    if os.path.exists(args.output):
        try:
            with open(args.output, 'rb') as f:
                toml_data = tomllib.load(f)
            print(f"既存の {args.output} を読み込みました")
        except Exception as e:
            print(f"Warning: 既存ファイルの読み込みに失敗: {e}")
            toml_data = {}
    
    # 新しいデータで更新
    for dir_name in sorted(all_results.keys()):
        data = all_results[dir_name]
        toml_data[dir_name] = {
            'total': data['total'],
            'scores': data['scores']
        }
    
    # TOMLファイルに書き込み（手動フォーマット、スコア降順でソート）
    try:
        with open(args.output, 'w', encoding='utf-8') as f:
            # スコア（total）の降順でソート
            sorted_items = sorted(toml_data.items(), key=lambda x: x[1]['total'], reverse=True)
            
            for dir_name, data in sorted_items:
                f.write(f'["{dir_name}"]\n')
                f.write(f'total = {data["total"]}\n')
                # スコア配列を1行で出力
                scores_str = ', '.join(map(str, data['scores']))
                f.write(f'scores = [{scores_str}]\n\n')
        
        print(f"スコア集計結果を {args.output} に保存しました")
        print(f"更新された組み合わせ: {len(all_results)}")
        print(f"ファイル内の総組み合わせ数: {len(toml_data)}")
        
        # コンソールにも詳細表示（スコア降順）
        print("-" * 80)
        for dir_name, data in sorted_items:
            total = data['total']
            tasks = len(data['scores'])
            avg = total / tasks if tasks > 0 else 0
            print(f"{total}/{tasks}={avg:.2f} {dir_name}")
            
    except Exception as e:
        print(f"Error: ファイル出力に失敗しました: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
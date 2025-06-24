#!/usr/bin/env python3
"""
analyze_variance.py - 評価対象モデルごとの分散分析ツール

構造化出力による評価者間分散の減少効果を定量的に分析します。
従来形式（judge_*）と新形式（構造化出力）の分散を比較し、
構造化出力の品質向上効果を確認します。

使用方法:
    uv run analyze_variance.py -b lightblue/tengu_bench
    uv run analyze_variance.py --all-benchmarks
    uv run analyze_variance.py -b lightblue/tengu_bench --output variance_analysis.txt
"""

import argparse
import yaml
import sys
from collections import defaultdict
import statistics
from pathlib import Path


def load_scores_data(file_path="scores.yaml"):
    """YAMLファイルからスコアデータを読み込み"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}
    except FileNotFoundError:
        print(f"Error: {file_path} が見つかりません")
        return {}
    except Exception as e:
        print(f"Error: {file_path} の読み込みに失敗: {e}")
        return {}


def parse_evaluator_model(evaluator_model_path):
    """evaluator/model文字列をパースして評価者と評価対象モデルを分離"""
    # judge_xxx/model.json → (judge_xxx, model, "legacy")
    # evaluator/model → (evaluator, model, "structured")
    
    if evaluator_model_path.endswith('.json'):
        # 従来形式: judge_xxx/model.json
        parts = evaluator_model_path.replace('.json', '').split('/')
        if len(parts) >= 2:
            evaluator = parts[-2]  # judge_xxx
            model = parts[-1]      # model
            return evaluator, model, "legacy"
    else:
        # 新形式: evaluator/model
        parts = evaluator_model_path.split('/')
        if len(parts) >= 2:
            evaluator = parts[-2]  # evaluator
            model = parts[-1]      # model
            return evaluator, model, "structured"
    
    return None, None, None


def analyze_variance_by_target_model(benchmark_data, min_evaluators=3):
    """
    評価対象モデルごとに評価者間の分散を分析
    
    Args:
        benchmark_data: ベンチマークのスコアデータ
        min_evaluators: 分析に必要な最小評価者数
        
    Returns:
        dict: 分析結果
    """
    # 評価対象モデルごとにデータを整理
    target_models = defaultdict(lambda: {"legacy": [], "structured": []})
    
    for evaluator_model_path, data in benchmark_data.items():
        evaluator, target_model, eval_type = parse_evaluator_model(evaluator_model_path)
        
        if evaluator and target_model and eval_type:
            total = data.get('total', 0)
            tasks = len(data.get('scores', []))
            avg_score = total / tasks if tasks > 0 else 0
            
            target_models[target_model][eval_type].append({
                'evaluator': evaluator,
                'total': total,
                'tasks': tasks,
                'avg_score': avg_score
            })
    
    # 各評価対象モデルの分散を計算
    results = {}
    
    for target_model, eval_data in target_models.items():
        legacy_scores = [item['avg_score'] for item in eval_data['legacy']]
        structured_scores = [item['avg_score'] for item in eval_data['structured']]
        
        # 最小評価者数の条件をチェック
        if len(legacy_scores) < min_evaluators and len(structured_scores) < min_evaluators:
            continue
            
        result = {
            'target_model': target_model,
            'legacy': {
                'count': len(legacy_scores),
                'scores': legacy_scores,
                'evaluators': [item['evaluator'] for item in eval_data['legacy']]
            },
            'structured': {
                'count': len(structured_scores),
                'scores': structured_scores,
                'evaluators': [item['evaluator'] for item in eval_data['structured']]
            }
        }
        
        # 統計値を計算
        for eval_type in ['legacy', 'structured']:
            scores = result[eval_type]['scores']
            if len(scores) >= 2:
                result[eval_type].update({
                    'mean': statistics.mean(scores),
                    'stdev': statistics.stdev(scores),
                    'variance': statistics.variance(scores),
                    'min': min(scores),
                    'max': max(scores),
                    'range': max(scores) - min(scores)
                })
            elif len(scores) == 1:
                result[eval_type].update({
                    'mean': scores[0],
                    'stdev': 0.0,
                    'variance': 0.0,
                    'min': scores[0],
                    'max': scores[0],
                    'range': 0.0
                })
            else:
                result[eval_type].update({
                    'mean': 0.0,
                    'stdev': 0.0,
                    'variance': 0.0,
                    'min': 0.0,
                    'max': 0.0,
                    'range': 0.0
                })
        
        results[target_model] = result
    
    return results


def format_variance_analysis(results, benchmark_name):
    """分析結果をフォーマットして出力"""
    output = []
    output.append(f"# 評価対象モデル別 分散分析結果")
    output.append(f"ベンチマーク: {benchmark_name}")
    output.append("")
    
    if not results:
        output.append("分析対象のモデルが見つかりませんでした（最小評価者数: 3人）")
        return "\n".join(output)
    
    # 分散減少効果が大きい順にソート
    sorted_models = []
    for target_model, data in results.items():
        legacy_var = data['legacy'].get('variance', 0)
        structured_var = data['structured'].get('variance', 0)
        
        # 分散減少率を計算（従来形式の分散がベース）
        if legacy_var > 0 and structured_var is not None:
            variance_reduction = (legacy_var - structured_var) / legacy_var * 100
        else:
            variance_reduction = 0
            
        sorted_models.append((target_model, data, variance_reduction))
    
    # 分散減少率の降順でソート
    sorted_models.sort(key=lambda x: x[2], reverse=True)
    
    # サマリーテーブル
    output.append("## サマリー")
    output.append("")
    output.append("| 評価対象モデル | 従来分散 | 新形式分散 | 分散減少率 | 従来評価者数 | 新形式評価者数 |")
    output.append("|---------------|----------|------------|------------|-------------|-------------|")
    
    total_legacy_var = 0
    total_structured_var = 0
    count_with_both = 0
    
    for target_model, data, variance_reduction in sorted_models:
        legacy_var = data['legacy'].get('variance', 0)
        structured_var = data['structured'].get('variance', 0)
        legacy_count = data['legacy']['count']
        structured_count = data['structured']['count']
        
        if legacy_count > 0 and structured_count > 0:
            total_legacy_var += legacy_var
            total_structured_var += structured_var
            count_with_both += 1
        
        # 分散減少率の表示
        if variance_reduction > 0:
            reduction_str = f"{variance_reduction:+.1f}%"
        elif variance_reduction < 0:
            reduction_str = f"{variance_reduction:+.1f}%"
        else:
            reduction_str = "N/A"
        
        output.append(f"| {target_model} | {legacy_var:.4f} | {structured_var:.4f} | {reduction_str} | {legacy_count} | {structured_count} |")
    
    # 全体的な分散減少効果
    if count_with_both > 0:
        avg_legacy_var = total_legacy_var / count_with_both
        avg_structured_var = total_structured_var / count_with_both
        overall_reduction = (avg_legacy_var - avg_structured_var) / avg_legacy_var * 100 if avg_legacy_var > 0 else 0
        
        output.append("")
        output.append(f"**全体平均分散減少率: {overall_reduction:.1f}%**")
        output.append(f"- 従来形式平均分散: {avg_legacy_var:.4f}")
        output.append(f"- 新形式平均分散: {avg_structured_var:.4f}")
        output.append(f"- 両形式を持つモデル数: {count_with_both}")
    
    # 詳細分析
    output.append("")
    output.append("## 詳細分析")
    output.append("")
    
    for target_model, data, variance_reduction in sorted_models:
        output.append(f"### {target_model}")
        output.append("")
        
        # 従来形式の統計
        if data['legacy']['count'] > 0:
            legacy = data['legacy']
            output.append(f"**従来形式（judge_*）**: {legacy['count']} 評価者")
            if legacy['count'] >= 2:
                output.append(f"- 平均スコア: {legacy['mean']:.2f}")
                output.append(f"- 標準偏差: {legacy['stdev']:.4f}")
                output.append(f"- 分散: {legacy['variance']:.4f}")
                output.append(f"- 範囲: {legacy['min']:.2f} - {legacy['max']:.2f} (差: {legacy['range']:.2f})")
            output.append(f"- 評価者: {', '.join(legacy['evaluators'])}")
            output.append("")
        
        # 新形式の統計
        if data['structured']['count'] > 0:
            structured = data['structured']
            output.append(f"**新形式（構造化出力）**: {structured['count']} 評価者")
            if structured['count'] >= 2:
                output.append(f"- 平均スコア: {structured['mean']:.2f}")
                output.append(f"- 標準偏差: {structured['stdev']:.4f}")
                output.append(f"- 分散: {structured['variance']:.4f}")
                output.append(f"- 範囲: {structured['min']:.2f} - {structured['max']:.2f} (差: {structured['range']:.2f})")
            output.append(f"- 評価者: {', '.join(structured['evaluators'])}")
            output.append("")
        
        # 改善効果
        if data['legacy']['count'] >= 2 and data['structured']['count'] >= 2:
            legacy_var = data['legacy']['variance']
            structured_var = data['structured']['variance']
            if legacy_var > 0:
                improvement = (legacy_var - structured_var) / legacy_var * 100
                output.append(f"**分散改善効果**: {improvement:+.1f}%")
                if improvement > 0:
                    output.append("→ 構造化出力により評価者間の一貫性が向上")
                elif improvement < 0:
                    output.append("→ 構造化出力で分散が増加（要調査）")
                else:
                    output.append("→ 分散に変化なし")
            output.append("")
    
    return "\n".join(output)


def main():
    parser = argparse.ArgumentParser(
        description="評価対象モデルごとの評価者間分散を分析",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
    # 特定ベンチマークの分析
    uv run analyze_variance.py -b lightblue/tengu_bench
    
    # 全ベンチマークの分析
    uv run analyze_variance.py --all-benchmarks
    
    # 結果をファイルに保存
    uv run analyze_variance.py -b lightblue/tengu_bench --output variance_analysis.txt
    
    # 最小評価者数を変更
    uv run analyze_variance.py -b lightblue/tengu_bench --min-evaluators 2
        """
    )
    
    parser.add_argument(
        '-b', '--benchmark',
        help='分析対象のベンチマーク名（例: lightblue/tengu_bench）'
    )
    parser.add_argument(
        '--all-benchmarks',
        action='store_true',
        help='全ベンチマークを分析'
    )
    parser.add_argument(
        '--min-evaluators',
        type=int,
        default=3,
        help='分析に必要な最小評価者数（デフォルト: 3）'
    )
    parser.add_argument(
        '-i', '--input',
        default='scores.yaml',
        help='入力YAMLファイル（デフォルト: scores.yaml）'
    )
    parser.add_argument(
        '-o', '--output',
        help='結果を保存するファイル（指定がない場合は標準出力）'
    )
    
    args = parser.parse_args()
    
    # ベンチマーク指定の検証
    if not args.benchmark and not args.all_benchmarks:
        print("Error: -b/--benchmark または --all-benchmarks を指定してください")
        return 1
    
    # スコアデータを読み込み
    yaml_data = load_scores_data(args.input)
    if not yaml_data:
        return 1
    
    # 分析対象のベンチマークを決定
    if args.all_benchmarks:
        target_benchmarks = list(yaml_data.keys())
    else:
        if args.benchmark not in yaml_data:
            print(f"Error: ベンチマーク '{args.benchmark}' が見つかりません")
            print(f"利用可能なベンチマーク: {', '.join(yaml_data.keys())}")
            return 1
        target_benchmarks = [args.benchmark]
    
    # 各ベンチマークを分析
    all_results = []
    
    for benchmark_name in target_benchmarks:
        benchmark_data = yaml_data[benchmark_name]
        results = analyze_variance_by_target_model(benchmark_data, args.min_evaluators)
        
        if results:
            analysis_text = format_variance_analysis(results, benchmark_name)
            all_results.append(analysis_text)
        else:
            all_results.append(f"# {benchmark_name}\n\n分析対象のモデルが見つかりませんでした（最小評価者数: {args.min_evaluators}）")
    
    # 結果の出力
    final_output = "\n\n".join(all_results)
    
    if args.output:
        try:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(final_output)
            print(f"分析結果を {args.output} に保存しました")
        except Exception as e:
            print(f"Error: ファイル出力に失敗: {e}")
            return 1
    else:
        print(final_output)
    
    return 0


if __name__ == "__main__":
    exit(main())

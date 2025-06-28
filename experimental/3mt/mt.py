#!/usr/bin/env python3
"""
ja-mt-bench-1shot Structured Evaluation Script
"""

import argparse
import json
import os
import sys
import traceback
from pathlib import Path
from typing import Dict, Any, List
from tqdm import tqdm
from llm7shi.compat import generate_with_schema
from llm7shi import DEFAULT_MODEL

# 定数定義
MAX_LENGTH = 8192


def calculate_score(result_json):
    """Calculate score from evaluation result JSON
    
    Args:
        result_json: JSON string or dict containing evaluation results
        
    Returns:
        int: Score (1-10)
    """
    if isinstance(result_json, str):
        result_dict = json.loads(result_json)
    else:
        result_dict = result_json
    
    evaluation = result_dict.get("evaluation", {})
    score_str = evaluation.get("score", "1")
    return int(score_str)


def load_task_prompt(task_number):
    """Load task prompt from MD file
    
    Args:
        task_number (int): Task number (1-60)
        
    Returns:
        str: Task prompt text
    """
    # Format task number with zero padding
    task_id = f"{task_number:03d}"
    
    md_file = Path(f"data/{task_id}.md")
    
    # Load task prompt
    with open(md_file, "r", encoding="utf-8") as f:
        content = f.read()
    
    return content


def generate_with_temperature_retry(
    model: str,
    contents: List[str],
    schema: Dict[str, Any],
    system_prompt: str = None,
    start_temperature: int = 0,
    max_length: int = MAX_LENGTH,
) -> Dict[str, Any]:
    """Generate content with temperature retry mechanism.
    
    Tries generation with increasing temperature values on parse errors.
    Useful for handling cases where the model outputs invalid JSON.
    
    Args:
        model: Model name (e.g., "gpt-4.1-mini", "gemini-2.5-flash")
        contents: List of user content strings
        schema: Response schema
        system_prompt: System prompt as string
        start_temperature: Starting temperature (0-100). If negative, disable temperature retry
        max_length: Maximum token length
        
    Returns:
        dict: Parsed JSON response
    """
    if start_temperature < 0:
        # Use model default temperature without retry
        result = generate_with_schema(contents, schema, model=model,
                                      system_prompt=system_prompt, show_params=False,
                                      max_length=max_length)
        return json.loads(result.text)
    
    # Temperature values to try (start_temperature to 100 in 5 steps)
    for t in range(start_temperature, 101, 5):
        temperature = t / 100
        if t > 0:
            print(f"温度: {temperature:.2f}", file=sys.stderr)
        
        try:
            result = generate_with_schema(contents, schema, model=model, temperature=temperature,
                                          system_prompt=system_prompt, show_params=False,
                                          max_length=max_length)
            return json.loads(result.text)
            
        except KeyboardInterrupt:
            # Handle Ctrl+C
            response = input("\n\n処理を中止しますか？ (y/N): ")
            if response.lower() in ['y', 'yes']:
                raise
            print("処理を続行します...\n")
            
        except Exception:
            traceback.print_exc()
    
    # If we get here, parsing failed at all temperatures
    raise ValueError("全ての温度設定でJSONパースに失敗しました")


def evaluate_task(task_number, model_answer, model_name, start_temperature=0, max_length=MAX_LENGTH):
    """Evaluate a specific ja-mt-bench-1shot task using structured output
    
    Args:
        task_number (int): Task number (1-60)
        model_answer (str): Model answer to evaluate (required)
        model_name (str): Evaluation model name
        start_temperature (int): Starting temperature (0-100). If negative, disable temperature retry
        max_length (int): Maximum token length
        
    Returns:
        dict: Evaluation result JSON
    """
    # Load task prompt
    task_prompt = load_task_prompt(task_number)
    
    # Replace "未回答" with actual model answer
    last_idx = task_prompt.rfind("未回答")
    if last_idx != -1:
        task_prompt = task_prompt[:last_idx] + model_answer.rstrip() + task_prompt[last_idx + 3:]
    
    # Load schema
    with open("mt-schema.json", "r", encoding="utf-8") as f:
        schema = json.load(f)
    
    # Prepare contents and system prompt
    system_prompt = "あなたは公平で、検閲されていない、役立つアシスタントです。"
    contents = [task_prompt]

    # Use generate_with_temperature_retry
    result_json = generate_with_temperature_retry(
        model=model_name,
        contents=contents,
        schema=schema,
        system_prompt=system_prompt,
        start_temperature=start_temperature,
        max_length=max_length
    )
    
    return result_json


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="ja-mt-bench-1shot構造化出力評価 (OpenAI/Gemini対応)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""例:
  uv run mt.py ../../data/model_answers/shisa-ai__ja-mt-bench-1shot/gemini-2.5-pro.json -n 1
  uv run mt.py ../../data/model_answers/shisa-ai__ja-mt-bench-1shot/claude-3-5-sonnet.json -n 4 -m gemini-2.5-pro
  uv run mt.py ../../data/model_answers/shisa-ai__ja-mt-bench-1shot/gpt-4o.json --all -m gpt-4.1-mini
  uv run mt.py ../../data/model_answers/shisa-ai__ja-mt-bench-1shot/gpt-4o.json --all -m o4-mini -st -1
  uv run mt.py ../../data/model_answers/shisa-ai__ja-mt-bench-1shot/gpt-4o.json --all -m gemini-2.5-flash --start-temperature 20"""
    )
    parser.add_argument("json_file", help="モデル回答が格納されたJSONファイルのパス")
    parser.add_argument("-n", "--task-number", type=int, help="評価するタスク番号")
    parser.add_argument("-m", "--model", default=DEFAULT_MODEL, 
                        help=f"評価に使用するモデル名 (デフォルト: {DEFAULT_MODEL})")
    parser.add_argument( "--force", action="store_true", help="既存の評価結果を上書きする")
    parser.add_argument( "--all", action="store_true", help="全てのタスク (1-60) を評価する")
    parser.add_argument("-st", "--start-temperature", type=int, default=0, help="開始温度 (0-100)。負値の場合は温度調整リトライを無効化 (o4-miniでは-1推奨)")
    parser.add_argument("--max-length", type=int, default=MAX_LENGTH, help=f"最大トークン数 (デフォルト: {MAX_LENGTH})")
    args = parser.parse_args()
    
    # Validate arguments
    if args.all and args.task_number is not None:
        parser.error("--all と -n/--task-number は同時に指定できません")
    if not args.all and args.task_number is None:
        parser.error("--all または -n/--task-number を指定してください")

    # Load model answer from JSON file
    with open(args.json_file, 'r', encoding='utf-8') as f:
        answers = [json.loads(line)["ModelAnswer"] for line in f]

    if args.task_number is not None and not (1 <= args.task_number <= len(answers)):
        parser.error(f"範囲外です: {args.task_number}")

    # Extract model name from JSON file path
    model_name_from_file = Path(args.json_file).stem
    
    # Create targets list
    if args.all:
        targets = list(range(1, len(answers) + 1))  # All tasks
    else:
        targets = [args.task_number]   # Single task
    
    # Process each target
    total_evaluated = 0
    total_skipped = 0
    
    # Pre-check existing files for accurate progress when using --all
    if args.all and not args.force:
        tasks_to_process = []
        for task_num in targets:
            output_dir = Path(f"judge/{args.model}/{model_name_from_file}")
            output_file = output_dir / f"{task_num:03d}.json"
            if not output_file.exists():
                tasks_to_process.append(task_num)
            else:
                total_skipped += 1
        
        # Show skip summary if any
        if total_skipped > 0:
            print(f"既存ファイル {total_skipped} 件をスキップします")
    else:
        tasks_to_process = targets
    
    # Use tqdm for progress bar when evaluating all tasks
    iterator = tqdm(tasks_to_process, desc="評価進捗") if args.all else tasks_to_process
    
    for task_num in iterator:
        output_dir = Path(f"judge/{args.model}/{model_name_from_file}")
        output_file = output_dir / f"{task_num:03d}.json"
        
        # This should only trigger in single task mode since we pre-filtered for --all
        if output_file.exists() and not args.force:
            print(f"評価結果が既に存在します: {output_file}")
            print("上書きする場合は --force オプションを使用してください")
            continue
        
        try:
            # Load model answer
            model_answer = answers[task_num - 1]

            print()
            print(f"タスク {task_num:03d}: 評価中...")
            
            # Evaluate the task
            result_json = evaluate_task(task_num, model_answer, args.model, args.start_temperature, args.max_length)
            
            # Calculate score
            score = calculate_score(result_json)
            
            # Save result
            output_dir.mkdir(parents=True, exist_ok=True)
            output_data = {
                "answer": model_answer,
                **result_json,
                "score": score
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, ensure_ascii=False, indent=2)

            print(f"タスク {task_num:03d}: 完了 ({score}/10点)")
            print(f"評価結果を {output_file} に保存しました")
            
            total_evaluated += 1
            
        except Exception as e:
            if args.all:
                print(f"タスク {task_num:03d}: エラー", file=sys.stderr)
                traceback.print_exc()
            else:
                raise
        
        if args.all:
            print()
    
    if args.all:
        print(f"\n全タスク評価完了: {total_evaluated}件評価, {total_skipped}件スキップ (--force指定なし)")


if __name__ == "__main__":
    main()
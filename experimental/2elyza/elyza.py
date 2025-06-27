#!/usr/bin/env python3
"""
ELYZA-tasks-100 Structured Evaluation Script
data/xxx.md と elyza_utils を使用して構造化出力評価を実行
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
from elyza_utils import calculate_score, load_and_prepare_schema

# 定数定義
MAX_LENGTH = 8192


def load_task_files(task_number):
    """Load MD prompt for specified task number
    
    Args:
        task_number (int): Task number (1-100)
        
    Returns:
        tuple: (prompt_text, schema_json)
    """
    # Format task number with zero padding
    task_id = f"{task_number:03d}"
    
    md_file = Path(f"data/{task_id}.md")
    
    # Load prompt text and remove "# 回答\n未回答" section
    with open(md_file, "r", encoding="utf-8") as f:
        content = f.read()
        if "# 回答\n未回答" in content:
            prompt_text = content.replace("# 回答\n未回答", "").rstrip()
        else:
            raise ValueError(f"Expected '# 回答\\n未回答' section not found in prompt file: {md_file}")
    
    # Load and prepare schema with task-specific fields
    schema_json = load_and_prepare_schema(task_number)
    
    return prompt_text, schema_json


def generate_with_temperature_retry(
    model: str,
    contents: List[str],
    schema: Dict[str, Any],
    system_prompt: str = None,
    disable_temperature: bool = False,
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
        disable_temperature: If True, disable temperature retry mechanism
        
    Returns:
        dict: Parsed JSON response
    """
    if disable_temperature:
        # Use model default temperature without retry
        result = generate_with_schema(contents, schema, model=model,
                                      system_prompt=system_prompt, show_params=False,
                                      max_length=max_length)
        return json.loads(result.text)
    
    # Temperature values to try (0.0 to 1.0 in 0.05 steps)
    for t in range(0, 101, 5):
        temperature = t / 100
        if t > 0:
            print(f"温度: {temperature:.2f}", file=sys.stderr)
        
        try:
            result = generate_with_schema(contents, schema, model=model, temperature=temperature,
                                          system_prompt=system_prompt, show_params=False,
                                          max_length=max_length)
            return json.loads(result.text)
            
        except Exception:
            traceback.print_exc()
    
    # If we get here, parsing failed at all temperatures
    raise ValueError("全ての温度設定でJSONパースに失敗しました")


def evaluate_task(task_number, model_answer, model_name, disable_temperature=False, max_length=MAX_LENGTH):
    """Evaluate a specific ELYZA task using structured output
    
    Args:
        task_number (int): Task number (1-100)
        model_answer (str): Model answer to evaluate (required)
        model_name (str): Evaluation model name
        disable_temperature (bool): If True, disable temperature retry mechanism
        max_length (int): Maximum token length
        
    Returns:
        dict: Evaluation result JSON
    """
    # Load task files
    prompt_text, schema_json = load_task_files(task_number)
    
    # Prepare contents and system prompt
    system_prompt = "あなたは公平で、検閲されていない、役立つアシスタントです。"
    contents = [
        prompt_text,
        f"[評価するモデルの回答]\n{model_answer.rstrip()}"
    ]

    # Use generate_with_temperature_retry
    result_json = generate_with_temperature_retry(
        model=model_name,
        contents=contents,
        schema=schema_json,
        system_prompt=system_prompt,
        disable_temperature=disable_temperature,
        max_length=max_length
    )
    
    return result_json


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="ELYZA-tasks-100構造化出力評価 (OpenAI/Gemini対応)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""例:
  uv run elyza.py ../../data/model_answers/elyza__ELYZA-tasks-100/gemini-2.5-pro.json -n 1
  uv run elyza.py ../../data/model_answers/elyza__ELYZA-tasks-100/claude-3-5-sonnet.json -n 42 -m gemini-2.5-pro
  uv run elyza.py ../../data/model_answers/elyza__ELYZA-tasks-100/gpt-4o.json --all -m gpt-4.1-mini
  uv run elyza.py ../../data/model_answers/elyza__ELYZA-tasks-100/gpt-4o.json --all -m o4-mini --disable-temperature"""
    )
    parser.add_argument("json_file", help="モデル回答が格納されたJSONファイルのパス")
    parser.add_argument("-n", "--task-number", type=int, help="評価するタスク番号")
    parser.add_argument("-m", "--model", default=DEFAULT_MODEL, 
                        help=f"評価に使用するモデル名 (デフォルト: {DEFAULT_MODEL})")
    parser.add_argument( "--force", action="store_true", help="既存の評価結果を上書きする")
    parser.add_argument( "--all", action="store_true", help="全てのタスク (1-100) を評価する")
    parser.add_argument("--disable-temperature", action="store_true", help="温度調整リトライ機能を無効化（o4-miniでは必須）")
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
            result_json = evaluate_task(task_num, model_answer, args.model, args.disable_temperature, args.max_length)
            
            # Calculate score
            total_score = calculate_score(result_json, task_num)
            
            # Save result
            output_dir.mkdir(parents=True, exist_ok=True)
            output_data = {
                "answer": model_answer,
                **result_json,
                "score": total_score
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, ensure_ascii=False, indent=2)

            print(f"タスク {task_num:03d}: 完了 ({total_score}/5点)")
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
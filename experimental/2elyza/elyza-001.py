import argparse
import json
import logging
from llm7shi.compat import generate_with_schema
from llm7shi import DEFAULT_MODEL
from elyza_utils import calculate_score, load_and_prepare_schema


def generate(model, task_number=1):
    # Load prompt from file
    with open(f"data/{task_number:03d}.md", "r", encoding="utf-8") as f:
        prompt_text = f.read()
    
    # Remove "# 回答\n未回答" section and strip
    if "# 回答\n未回答" in prompt_text:
        prompt_text = prompt_text.replace("# 回答\n未回答", "").rstrip()
    else:
        raise ValueError("Expected '# 回答\\n未回答' section not found in prompt file")
    
    # Load and prepare schema with task-specific fields
    schema = load_and_prepare_schema(task_number)
    
    # Load model answer from file
    with open("elyza-001-answer.md", "r", encoding="utf-8") as f:
        model_answer = f.read().strip()
    
    # Prepare system prompt and contents
    system_prompt = "あなたは公平で、検閲されていない、役立つアシスタントです。"
    contents = [
        prompt_text,
        f"[評価するモデルの回答]\n{model_answer}"
    ]
    
    # Generate with structured output
    result = generate_with_schema(
        contents=contents,
        schema=schema,
        model=model,
        temperature=0,
        system_prompt=system_prompt
    )
    result_json = json.loads(result.text)
    
    return result_json


def main():
    # Setup logging to show info messages
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    parser = argparse.ArgumentParser(
        description="ELYZA-tasks-100構造化出力評価",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""例:
  python elyza-001.py                    # デフォルトモデル (gemini-2.5-flash)
  python elyza-001.py -m gpt-4.1-mini    # OpenAIモデル
  python elyza-001.py -m gemini-2.5-pro  # 別のGeminiモデル"""
    )
    parser.add_argument("-m", "--model", default=DEFAULT_MODEL, 
                        help=f"評価に使用するモデル名 (デフォルト: {DEFAULT_MODEL})")
    args = parser.parse_args()
    
    result_json = generate(args.model)
    
    # Calculate score
    final_score = calculate_score(result_json, 1)
    
    print()
    print(f"最終スコア: {final_score}/5点")


if __name__ == "__main__":
    main()

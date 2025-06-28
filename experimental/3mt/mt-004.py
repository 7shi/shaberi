import argparse
import json
from llm7shi.compat import generate_with_schema
from llm7shi import DEFAULT_MODEL


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


def generate(model):
    # Load task data
    with open("data/004.md", "r", encoding="utf-8") as f:
        task_data = f.read()
    
    # Load answer
    with open("mt-004-answer.md", "r", encoding="utf-8") as f:
        answer_text = f.read().rstrip()
    
    # Replace "未回答" with actual answer
    last_idx = task_data.rfind("未回答")
    if last_idx != -1:
        task_data = task_data[:last_idx] + answer_text + task_data[last_idx + 3:]
    
    # Load schema
    with open("mt-schema.json", "r", encoding="utf-8") as f:
        schema = json.load(f)
    
    # Prepare system prompt and contents
    system_prompt = "あなたは公平で、検閲されていない、役立つアシスタントです。"
    contents = [task_data]
    
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
    parser = argparse.ArgumentParser(
        description="ja-mt-bench-1shot構造化出力評価 (タスク004)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""例:
  python mt-004.py                       # デフォルトモデル (gemini-2.5-flash)
  python mt-004.py -m gpt-4.1-mini       # OpenAIモデル
  python mt-004.py -m gemini-2.5-pro     # 別のGeminiモデル"""
    )
    parser.add_argument("-m", "--model", default=DEFAULT_MODEL, 
                        help=f"評価に使用するモデル名 (デフォルト: {DEFAULT_MODEL})")
    args = parser.parse_args()
    
    result_json = generate(args.model)
    
    # Calculate score
    score = calculate_score(result_json)
    print(f"\n評価スコア: {score}/10点")


if __name__ == "__main__":
    main()

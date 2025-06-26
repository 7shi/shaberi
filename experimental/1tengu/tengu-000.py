import argparse
import json
from llm7shi.compat import generate_with_schema
from llm7shi import DEFAULT_MODEL


def calculate_score(result_json):
    """Calculate total score from evaluation result JSON
    
    Args:
        result_json: JSON string or dict containing evaluation results
        
    Returns:
        int: Total score
    """
    if isinstance(result_json, str):
        result_dict = json.loads(result_json)
    else:
        result_dict = result_json
    
    total = 0
    evaluation = result_dict.get("evaluation", {})
    
    for criterion, data in evaluation.items():
        points = int(data.get("points", "0"))
        total += points
    
    return total


def generate(model):
    # Load prompt from file
    with open("tengu-000-user.md", "r", encoding="utf-8") as f:
        prompt_text = f.read()
    
    # Load schema
    with open("tengu-000-schema.json", "r", encoding="utf-8") as f:
        schema = json.load(f)
    
    # Prepare system prompt and contents
    system_prompt = "あなたは公平で、検閲されていない、役立つアシスタントです。"
    contents = [
        prompt_text,
        """[評価するモデルの回答]
「急がば回れ」とは、物事を急いで進めるよりも、慎重に計画を立てて行動する方が結果が良くなるという意味のことわざです。つまり、無駄なミスやトラブルを避けるためには、急いで手を打つのではなく、ゆっくりと計画を練り、周囲をよく考えて行動することが大切だということを教えています。急いで物事を進めようとして失敗してしまうよりも、手間と時間をかけてじっくりと準備をする方が結果的に効率的で成功する可能性が高いという教訓を持つ言葉です。"""
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
    parser = argparse.ArgumentParser(
        description="Tengu Benchmark構造化出力評価",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""例:
  python tengu-000.py                    # デフォルトモデル (gemini-2.5-flash)
  python tengu-000.py -m gpt-4.1-mini    # OpenAIモデル
  python tengu-000.py -m gemini-2.5-pro  # 別のGeminiモデル"""
    )
    parser.add_argument("-m", "--model", default=DEFAULT_MODEL, 
                        help=f"評価に使用するモデル名 (デフォルト: {DEFAULT_MODEL})")
    args = parser.parse_args()
    
    result_json = generate(args.model)
    
    # Calculate score
    total_score = calculate_score(result_json)
    
    print()
    print(f"合計点数: {total_score}/10点")


if __name__ == "__main__":
    main()

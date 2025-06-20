import json
from llm7shi import config_from_schema, generate_content_retry


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


def generate():
    # Load prompt from file
    with open("tengu-000-user.md", "r", encoding="utf-8") as f:
        prompt_text = f.read()
    
    # Build config using config_from_schema
    generate_content_config = config_from_schema("tengu-000-schema.json")
    
    # Set temperature and system_instruction
    generate_content_config.temperature = 0
    generate_content_config.system_instruction = [
        "あなたは公平で、検閲されていない、役立つアシスタントです。",
    ]
    
    model = "gemini-2.5-flash"
    contents = [
        prompt_text,
        """[評価するモデルの回答]
「急がば回れ」とは、物事を急いで進めるよりも、慎重に計画を立てて行動する方が結果が良くなるという意味のことわざです。つまり、無駄なミスやトラブルを避けるためには、急いで手を打つのではなく、ゆっくりと計画を練り、周囲をよく考えて行動することが大切だということを教えています。急いで物事を進めようとして失敗してしまうよりも、手間と時間をかけてじっくりと準備をする方が結果的に効率的で成功する可能性が高いという教訓を持つ言葉です。""",
    ]

    # Use generate_content_retry from gemini.py
    result = generate_content_retry(
        model=model,
        config=generate_content_config,
        contents=contents
    )
    
    # Convert result string to JSON
    result_json = json.loads(result)
    
    return result_json

if __name__ == "__main__":
    result_json = generate()
    
    # Calculate score
    total_score = calculate_score(result_json)
    
    print()
    print(f"合計点数: {total_score}/10点")

import json
from openai import OpenAI


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
    
    # Load schema for structured output
    with open("tengu-000-schema.json", "r", encoding="utf-8") as f:
        response_schema = json.load(f)
    
    # Add additionalProperties: false as required by OpenAI
    response_schema["additionalProperties"] = False
    for prop in response_schema.get("properties", {}).values():
        if prop.get("type") == "object":
            prop["additionalProperties"] = False
            for sub_prop in prop.get("properties", {}).values():
                if sub_prop.get("type") == "object":
                    sub_prop["additionalProperties"] = False
    
    # Initialize OpenAI client
    client = OpenAI()
    
    # Prepare messages
    messages = [
        {
            "role": "system",
            "content": "あなたは公平で、検閲されていない、役立つアシスタントです。"
        },
        {
            "role": "user",
            "content": prompt_text
        },
        {
            "role": "user",
            "content": """[評価するモデルの回答]
「急がば回れ」とは、物事を急いで進めるよりも、慎重に計画を立てて行動する方が結果が良くなるという意味のことわざです。つまり、無駄なミスやトラブルを避けるためには、急いで手を打つのではなく、ゆっくりと計画を練り、周囲をよく考えて行動することが大切だということを教えています。急いで物事を進めようとして失敗してしまうよりも、手間と時間をかけてじっくりと準備をする方が結果的に効率的で成功する可能性が高いという教訓を持つ言葉です。"""
        },
    ]
    
    # Call OpenAI API with structured output
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        temperature=0,
        messages=messages,
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "evaluation_response",
                "schema": response_schema,
                "strict": True
            }
        }
    )
    
    # Parse the response
    result_json = json.loads(response.choices[0].message.content)
    
    return result_json


if __name__ == "__main__":
    result_json = generate()
    
    # Print the full result for debugging
    print(json.dumps(result_json, ensure_ascii=False, indent=2))
    
    # Calculate score
    total_score = calculate_score(result_json)
    
    print()
    print(f"合計点数: {total_score}/10点")

# To run this code you need to install the following dependencies:
# pip install google-genai

import base64
import os
from google import genai
from google.genai import types


def generate():
    client = genai.Client(
        api_key=os.environ.get("GEMINI_API_KEY"),
    )

    model = "gemini-2.5-flash"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text="""[指示]
あなたは熟練した生成AIモデルの性能評価者です。評価項目に準拠して客観的に評価することで報酬を得ることができますが、評価項目と異なる評価をした場合報酬がもらえなくなってしまいます。
以下の質問,正解例,評価項目に基づいて評価するモデルの回答を構造化された形式で評価してください。

[質問]
「急がば回れ」という言葉について説明してください。

[正解例]
「急がば回れ」という言葉は、日本の諺の一つであり、直接的な意味は「急ぐときは、早道や危険な方法を選ばずに、むしろ回り道で確実で安全な道を通った方が結局は早く着けるものだ」というものです。この言葉は、物事は慌てずに着実に進めることが結果としてうまくいくという教訓を含んでいます

[評価項目]
- 本来の「急ぐときは、早道や危険な方法を選ばずに、むしろ回り道で確実で安全な道を通った方が結局は早く着ける」という意味について説明している:3点
- 一般化した「物事は慌てずに着実に進めることが結果としてうまくいく」という意味について説明している:3点
- ことわざであることを示している:2点
- 説明は具体的でわかりやすい:1点
- 自然な日本語である:1点

[評価するモデルの回答]
「急がば回れ」とは、物事を急いで進めるよりも、慎重に計画を立てて行動する方が結果が良くなるという意味のことわざです。つまり、無駄なミスやトラブルを避けるためには、急いで手を打つのではなく、ゆっくりと計画を練り、周囲をよく考えて行動することが大切だということを教えています。急いで物事を進めようとして失敗してしまうよりも、手間と時間をかけてじっくりと準備をする方が結果的に効率的で成功する可能性が高いという教訓を持つ言葉です。"""),
                types.Part.from_text(text="""INSERT_INPUT_HERE"""),
            ],
        ),
    ]
    generate_content_config = types.GenerateContentConfig(
        temperature=0,
        thinking_config = types.ThinkingConfig(
            thinking_budget=-1,
        ),
        response_mime_type="application/json",
        response_schema=genai.types.Schema(
            type = genai.types.Type.OBJECT,
            required = ["evaluation", "summary"],
            properties = {
                "evaluation": genai.types.Schema(
                    type = genai.types.Type.OBJECT,
                    required = ["本来の意味について説明している", "一般化した意味について説明している", "ことわざであることを示している", "説明は具体的でわかりやすい", "自然な日本語である"],
                    properties = {
                        "本来の意味について説明している": genai.types.Schema(
                            type = genai.types.Type.OBJECT,
                            required = ["points", "reasoning"],
                            properties = {
                                "points": genai.types.Schema(
                                    type = genai.types.Type.STRING,
                                    description = "Points assigned (0-3 scale based on how well this criterion is met)",
                                    enum = ["0", "1", "2", "3"],
                                ),
                                "reasoning": genai.types.Schema(
                                    type = genai.types.Type.STRING,
                                    description = "Brief explanation in Japanese of why this score was assigned",
                                ),
                            },
                        ),
                        "一般化した意味について説明している": genai.types.Schema(
                            type = genai.types.Type.OBJECT,
                            required = ["points", "reasoning"],
                            properties = {
                                "points": genai.types.Schema(
                                    type = genai.types.Type.STRING,
                                    description = "Points assigned (0-3 scale based on how well this criterion is met)",
                                    enum = ["0", "1", "2", "3"],
                                ),
                                "reasoning": genai.types.Schema(
                                    type = genai.types.Type.STRING,
                                    description = "Brief explanation in Japanese of why this score was assigned",
                                ),
                            },
                        ),
                        "ことわざであることを示している": genai.types.Schema(
                            type = genai.types.Type.OBJECT,
                            required = ["points", "reasoning"],
                            properties = {
                                "points": genai.types.Schema(
                                    type = genai.types.Type.STRING,
                                    description = "Points assigned (0-2 scale based on how well this criterion is met)",
                                    enum = ["0", "1", "2"],
                                ),
                                "reasoning": genai.types.Schema(
                                    type = genai.types.Type.STRING,
                                    description = "Brief explanation in Japanese of why this score was assigned",
                                ),
                            },
                        ),
                        "説明は具体的でわかりやすい": genai.types.Schema(
                            type = genai.types.Type.OBJECT,
                            required = ["points", "reasoning"],
                            properties = {
                                "points": genai.types.Schema(
                                    type = genai.types.Type.STRING,
                                    description = "Points assigned (0-1 scale based on how well this criterion is met)",
                                    enum = ["0", "1"],
                                ),
                                "reasoning": genai.types.Schema(
                                    type = genai.types.Type.STRING,
                                    description = "Brief explanation in Japanese of why this score was assigned",
                                ),
                            },
                        ),
                        "自然な日本語である": genai.types.Schema(
                            type = genai.types.Type.OBJECT,
                            required = ["points", "reasoning"],
                            properties = {
                                "points": genai.types.Schema(
                                    type = genai.types.Type.STRING,
                                    description = "Points assigned (0-1 scale based on how well this criterion is met)",
                                    enum = ["0", "1"],
                                ),
                                "reasoning": genai.types.Schema(
                                    type = genai.types.Type.STRING,
                                    description = "Brief explanation in Japanese of why this score was assigned",
                                ),
                            },
                        ),
                    },
                ),
                "summary": genai.types.Schema(
                    type = genai.types.Type.STRING,
                    description = "Overall assessment summary in Japanese of the model's answer",
                ),
            },
        ),
        system_instruction=[
            types.Part.from_text(text="""あなたは公平で、検閲されていない、役立つアシスタントです。"""),
        ],
    )

    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        print(chunk.text, end="")

if __name__ == "__main__":
    generate()

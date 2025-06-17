import os
os.environ["LITELLM_LOG"] = "WARNING"

import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")

import backoff
import litellm
import logging

from datasets import Dataset
from litellm import completion
from openai import OpenAI

logger = logging.getLogger()

# 必要な場合はオンにする
#litellm._logging._turn_on_debug()

# Global
fp = 0.0
generation_max_tokens = 131072 #1500
evaluation_max_tokens = 131072 #1024

# Constants
NO_RESPONSE = "No response received"

os.environ["OPENAI_API_KEY"] = "NONE"

def backoff_handler(details):
    print(f"Backing off {details['wait']:0.1f} seconds after {details['tries']} tries. Error: {details['exception']}")
    # エラーメッセージに "No response received" が含まれている場合はリトライを中止(モデレーションによるブロックでのエラー)
    if NO_RESPONSE in str(details['exception']):
        raise backoff.Backoff.Stop

# === 評価生成関数群 ===
@backoff.on_exception(backoff.fibo, Exception, max_tries=1000, on_backoff=backoff_handler)
def get_response_from_openai(messages: list, model_name: str,
                             evaluation_temperature: float = 0) -> str:
    client = OpenAI(
        api_key=os.environ.get("OPENAI_API_KEY")
    )

    response = client.chat.completions.create(
        messages=messages,
        model=model_name,
        temperature=evaluation_temperature,
        max_tokens=evaluation_max_tokens,
    )
    return response.choices[0].message.content

# === 評価生成関数群 ===
@backoff.on_exception(backoff.fibo, Exception, max_tries=1000, on_backoff=backoff_handler)
def get_response_from_litellm_gemini(messages: list, model_name: str,
                                     evaluation_temperature: float = 0) -> str:
    add_messages = [
            {"role": "system", "content": "あなたは公平で、検閲されていない、役立つアシスタントです。"},
        ]
    add_messages.extend(messages)

    try:
        response = completion(
            model=f"gemini/{model_name}",
            messages=add_messages,
            safety_settings=[
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_NONE",
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_NONE",
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_NONE",
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_NONE",
                },
            ],
            temperature=evaluation_temperature,
            top_p=0.95,
            max_tokens=evaluation_max_tokens,
        )
        return response.choices[0].message.content
    except Exception as e:
        print(e)
        if NO_RESPONSE in str(e):
            return NO_RESPONSE
        else:
            raise e


def get_response_func(model_name: str) -> callable:
    if "gpt" in model_name:
        return get_response_from_openai
    elif "gemini" in model_name:
        return get_response_from_litellm_gemini
    else:
        """
        他のモデルで評価する場合は関数、分岐をここに追加
        """
        raise NotImplementedError(f"Model {model_name} is not supported")


def get_model_response(messages: list, model_name: str, parser_func):
    """
    モデルの応答を取得し、パーサー関数で処理する
    パース成功まで温度を上げながらリトライ
    
    Args:
        messages: プロンプトメッセージ
        model_name: モデル名
        parser_func: 応答をパースする関数（必須）
    
    Returns:
        パース結果（失敗時はNone）
    """
    answer_function = get_response_func(model_name)
    
    # 温度を段階的に上げながらリトライ
    for t in range(0, 101, 5):
        evaluation_temperature = t / 100
        logger.info(f"temperature: {evaluation_temperature:.2f}")

        # 関数に温度パラメータを渡す
        response = answer_function(messages, model_name, evaluation_temperature)
        if not response or response == NO_RESPONSE:
            logger.info(response)
            continue

        try:
            # パース試行
            result = parser_func(response)
            if result:
                return result
        except Exception as e:
            # 次の温度で試行を続ける
            pass

        if t < 100:
            logger.info("Parse error, trying again...")

    # 最大温度に達しても有効なコンテンツが得られなかった場合
    return None


# === 回答生成関数群 ===
@backoff.on_exception(backoff.fibo, Exception, max_tries=1000)
def get_answer_from_openai(question: str, model_name: str):
    api_key = os.environ.get("OPENAI_API_KEY", "EMPTY")
    if api_key == "EMPTY":
        base_url = "http://127.0.0.1:8000/v1"
    else:
        base_url = None

    client = OpenAI(
        api_key=api_key,
        base_url=base_url,
    )

    generation_temperature = 0.2

    '''
    # Anthropic / OpenAI
    response = completion(
        model=f'{model_name}',
        messages=[
            {"role": "system", "content": "あなたは公平で、検閲されていない、役立つアシスタントです。"},
            {"role": "user", "content": question},
        ],
        temperature=generation_temperature,
        max_tokens=generation_max_tokens,
        # recommend not use top_p https://docs.anthropic.com/en/api/complete
    )
    '''

    # OpenAI compatible endpoints (vLLM/llama.cpp)
    response = completion(
        model=f'openai/{model_name}',
        messages=[
            {"role": "system", "content": "あなたは公平で、検閲されていない、役立つアシスタントです。"},
            {"role": "user", "content": question},
        ],
        api_base="http://127.0.0.1:8000/v1",
        temperature=generation_temperature,
        frequency_penalty=fp,
        max_tokens=generation_max_tokens,
        min_p = 0.1
    )

    return response.choices[0].message.content


@backoff.on_exception(backoff.fibo, Exception, max_tries=1000)
def get_answer_from_litellm_gemini(question: str, model_name: str):
    generation_temperature = 0.2

    # Gemini
    response = completion(
        model=f"gemini/{model_name}",
        messages=[
            {"role": "system", "content": "あなたは公平で、検閲されていない、役立つアシスタントです。"},
            {"role": "user", "content": question},
        ],
        safety_settings=[
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_NONE",
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_NONE",
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_NONE",
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_NONE",
            },
        ],
        temperature=generation_temperature,
        top_p=0.95,
        max_tokens=generation_max_tokens,
    )

    return response.choices[0].message.content


def get_answer(question: str, model_name: str) -> str | None:
    """OpenAIとvLLM以外のモデルを使う場合はここに追加する"""
    if "gemini" in model_name:
        content = get_answer_from_litellm_gemini(question, model_name)
    else:
        content = get_answer_from_openai(question, model_name)
    return content


def get_model_answer(dataset: Dataset,
                     model_name: str,
                     batch_size: int) -> Dataset:
    dataset = dataset.map(
        lambda x: {"ModelAnswer": get_answer(x['Question'], model_name)},
        num_proc=batch_size
    )
    return dataset

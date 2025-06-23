import json
import sys
import traceback
from typing import Dict, Any, List, Union

DEFAULT_MODEL = "gemini-2.5-flash"


def generate_with_schema(
    model: str,
    messages: List[Dict[str, str]],
    schema: Dict[str, Any],
    temperature: float = 0,
) -> Dict[str, Any]:
    """Generate content with structured output using either OpenAI or Gemini API.
    
    Args:
        model: Model name (e.g., "gpt-4.1-mini", "gemini-2.5-flash")
        messages: List of message dicts with 'role' and 'content'
        schema: JSON schema for structured output
        temperature: Temperature parameter for generation
        
    Returns:
        Dict containing the generated structured output
    """
    if model.startswith("gemini"):
        return _generate_with_gemini(model, messages, schema, temperature)
    else:
        return _generate_with_openai(model, messages, schema, temperature)


def _generate_with_gemini(
    model: str,
    messages: List[Dict[str, str]],
    schema: Dict[str, Any],
    temperature: float,
) -> Dict[str, Any]:
    """Generate with Gemini API."""
    from llm7shi import config_from_schema, generate_content_retry
    
    # Extract system instruction and user messages
    system_instruction = []
    contents = []
    
    for msg in messages:
        if msg["role"] == "system":
            system_instruction.append(msg["content"])
        elif msg["role"] == "user":
            contents.append(msg["content"])
    
    # Build config from schema
    generate_content_config = config_from_schema(schema)
    generate_content_config.temperature = temperature
    if system_instruction:
        generate_content_config.system_instruction = system_instruction
    
    # Generate content
    result = generate_content_retry(
        model=model,
        config=generate_content_config,
        contents=contents
    )
    
    # Parse and return result
    return json.loads(result.text)


def _generate_with_openai(
    model: str,
    messages: List[Dict[str, str]],
    schema: Dict[str, Any],
    temperature: float,
) -> Dict[str, Any]:
    """Generate with OpenAI API with streaming."""
    from openai import OpenAI
    
    # Display parameters in do_show_params style
    print(f"- model: {model}")
    
    # Display user prompts quoted with ">"
    for msg in messages:
        if msg["role"] == "user":
            print()
            for line in msg['content'].splitlines():
                print(">", line)
    print()
    
    # Add additionalProperties: false as required by OpenAI
    schema = _add_additional_properties_false(schema)
    
    # Initialize client
    client = OpenAI()
    
    # Call API with structured output and streaming
    stream = client.chat.completions.create(
        model=model,
        temperature=temperature,
        messages=messages,
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "evaluation_response",
                "schema": schema,
                "strict": True
            }
        },
        stream=True
    )
    
    # Collect streamed response
    collected_content = ""
    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            content = chunk.choices[0].delta.content
            collected_content += content
            print(content, end='', flush=True)
    
    print()  # New line after streaming
    
    # Parse and return result
    return json.loads(collected_content)


def _add_additional_properties_false(schema: Dict[str, Any]) -> Dict[str, Any]:
    """Add additionalProperties: false to schema for OpenAI compatibility."""
    schema = schema.copy()
    schema["additionalProperties"] = False
    
    for prop in schema.get("properties", {}).values():
        if prop.get("type") == "object":
            prop["additionalProperties"] = False
            for sub_prop in prop.get("properties", {}).values():
                if sub_prop.get("type") == "object":
                    sub_prop["additionalProperties"] = False
    
    return schema


def generate_with_temperature_retry(
    model: str,
    messages: List[Dict[str, str]],
    schema: Dict[str, Any],
) -> Dict[str, Any]:
    """Generate content with temperature retry mechanism.
    
    Tries generation with increasing temperature values on parse errors.
    Useful for handling cases where the model outputs invalid JSON.
    
    Args:
        model: Model name (e.g., "gpt-4.1-mini", "gemini-2.5-flash")
        messages: Messages for chat completion
        schema: Response schema
        
    Returns:
        dict: Parsed JSON response
    """
    # Temperature values to try (0.0 to 1.0 in 0.05 steps)
    for t in range(0, 101, 5):
        temperature = t / 100
        if t > 0:
            print(f"温度: {temperature:.2f}", file=sys.stderr)
        
        try:
            result = generate_with_schema(model, messages, schema, temperature)
            return result
            
        except Exception:
            traceback.print_exc()
    
    # If we get here, parsing failed at all temperatures
    raise ValueError("全ての温度設定でJSONパースに失敗しました")

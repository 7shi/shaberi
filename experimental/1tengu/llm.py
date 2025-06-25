import json
import sys
import traceback
from typing import Dict, Any, List, Union

DEFAULT_MODEL = "gemini-2.5-flash"


def contents_to_openai_messages(contents: List[str], system_prompt: str = None) -> List[Dict[str, str]]:
    """Convert contents and system prompt to OpenAI message format.
    
    Args:
        contents: List of user content strings
        system_prompt: System prompt as string
        
    Returns:
        List of OpenAI format messages
    """
    openai_messages = []
    
    if system_prompt:
        openai_messages.append({"role": "system", "content": system_prompt})
    
    for content in contents:
        openai_messages.append({"role": "user", "content": content})
    
    return openai_messages


def generate_with_schema(
    model: str,
    contents: List[str],
    schema: Dict[str, Any],
    temperature: float = None,
    system_prompt: str = None,
) -> Dict[str, Any]:
    """Generate content with structured output using either OpenAI or Gemini API.
    
    Args:
        model: Model name (e.g., "gpt-4.1-mini", "gemini-2.5-flash")
        contents: List of user content strings
        schema: JSON schema for structured output
        temperature: Temperature parameter for generation (None = use model default)
        system_prompt: System prompt as string
        
    Returns:
        Dict containing the generated structured output
    """
    if model.startswith("gemini"):
        return _generate_with_gemini(model, contents, schema, temperature, system_prompt)
    else:
        return _generate_with_openai(model, contents, schema, temperature, system_prompt)


def _generate_with_gemini(
    model: str,
    contents: List[str],
    schema: Dict[str, Any],
    temperature: float = None,
    system_prompt: str = None,
) -> Dict[str, Any]:
    """Generate with Gemini API."""
    from llm7shi import config_from_schema, generate_content_retry
    
    # Build config from schema
    generate_content_config = config_from_schema(schema)
    if temperature is not None:
        generate_content_config.temperature = temperature
    if system_prompt:
        generate_content_config.system_instruction = [system_prompt]
    
    # Generate content
    result = generate_content_retry(
        model=model,
        config=generate_content_config,
        contents=contents,
        show_params=False
    )
    
    # Parse and return result
    return json.loads(result.text)


def _generate_with_openai(
    model: str,
    contents: List[str],
    schema: Dict[str, Any],
    temperature: float = None,
    system_prompt: str = None,
) -> Dict[str, Any]:
    """Generate with OpenAI API with streaming."""
    from openai import OpenAI
    
    # Convert contents to OpenAI format messages
    openai_messages = contents_to_openai_messages(contents, system_prompt)
    
    # Add additionalProperties: false as required by OpenAI
    schema = _add_additional_properties_false(schema)
    
    # Initialize client
    client = OpenAI()
    
    # Build kwargs
    kwargs = {
        "model": model,
        "messages": openai_messages,
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": "evaluation_response",
                "schema": schema,
                "strict": True
            }
        },
        "stream": True
    }
    
    # Add temperature only if provided
    if temperature is not None:
        kwargs["temperature"] = temperature
    
    # Call API with structured output and streaming
    stream = client.chat.completions.create(**kwargs)
    
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

from openai import OpenAI
import os
import json
from dotenv import load_dotenv
from typing import List, Dict

# Load environment variables
load_dotenv()

# Define a default base URL or fetch it from the environment if available
base_url = os.getenv("DEEPSEEK_BASE_URL")

# Initialize DeepSeek client with dynamic base URL
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"), base_url=base_url
)

DEEPSEEK_V3_MODEL = os.getenv("DEEPSEEK_MODEL")

def prompt(prompt: str, model: str = DEEPSEEK_V3_MODEL) -> str:
    """
    Send a prompt to DeepSeek and get detailed benchmarking response.
    """
    response = client.chat.completions.create(
        model=model, messages=[{"role": "user", "content": prompt}], stream=False
    )
    return response.choices[0].message.content

def fill_in_the_middle_prompt(
    prompt: str, suffix: str, model: str = DEEPSEEK_V3_MODEL
) -> str:
    """
    Send a fill-in-the-middle prompt to DeepSeek and get response.

    The max tokens of FIM completion is 4K.

    example:
        prompt="def fib(a):",
        suffix="    return fib(a-1) + fib(a-2)",
    """
    response = client.completions.create(model=model, prompt=prompt, suffix=suffix)
    return prompt + response.choices[0].text + suffix

def json_prompt(prompt: str, model: str = DEEPSEEK_V3_MODEL) -> dict:
    """
    Send a prompt to DeepSeek and get JSON response.

    Args:
        prompt: The user prompt to send
        system_prompt: Optional system prompt to set context
        model: The model to use, defaults to deepseek-chat

    Returns:
        dict: The parsed JSON response
    """
    messages = [{"role": "user", "content": prompt}]

    response = client.chat.completions.create(
        model=model, messages=messages, response_format={"type": "json_object"}
    )
    return json.loads(response.choices[0].message.content)

def prefix_prompt(
    prompt: str, prefix: str, model: str = DEEPSEEK_V3_MODEL, no_prefix: bool = False
) -> str:
    """
    Send a prompt to DeepSeek with a prefix constraint and get 'prefix + response'

    Args:
        prompt: The user prompt to send
        prefix: The required prefix for the response
        model: The model to use, defaults to deepseek-chat
        no_prefix: If True, the prefix is not added to the response
    Returns:
        str: The model's response constrained by the prefix
    """
    messages = [
        {"role": "user", "content": prompt},
        {"role": "assistant", "content": prefix, "prefix": True},
    ]

    response = client.chat.completions.create(model=model, messages=messages)
    if no_prefix:
        return response.choices[0].message.content
    else:
        return prefix + response.choices[0].message.content

def prefix_then_stop_prompt(
    prompt: str, prefix: str, suffix: str, model: str = DEEPSEEK_V3_MODEL
) -> str:
    """
    Send a prompt to DeepSeek with a prefix and suffix constraint and get 'response' only that will have started with prefix and ended with suffix

    Args:
        prompt: The user prompt to send
        prefix: The required prefix for the response
        suffix: The required suffix for the response
        model: The model to use, defaults to deepseek-chat

    Returns:
        str: The model's response constrained by the prefix and suffix
    """
    messages = [
        {"role": "user", "content": prompt},
        {"role": "assistant", "content": prefix, "prefix": True},
    ]
    response = client.chat.completions.create(
        model=model, messages=messages, stop=[suffix]
    )
    return response.choices[0].message.content
def conversational_prompt(
    messages: List[Dict[str, str]],
    system_prompt: str = "You are a helpful conversational assistant. Respond in a short, concise, friendly manner.",
    model: str = DEEPSEEK_V3_MODEL,
) -> str:
    """
    Send a conversational prompt to DeepSeek with message history.

    Args:
        messages: List of message dicts with 'role' and 'content' keys
        model: The model to use, defaults to deepseek-chat

    Returns:
        str: The model's response
    """
    try:
        messages = [
            {"role": "system", "content": system_prompt},
            *messages,
        ]
        response = client.chat.completions.create(
            model=model, messages=messages, stream=False
        )
        return response.choices[0].message.content
    except Exception as e:
        raise Exception(f"Error in conversational prompt: {str(e)}")

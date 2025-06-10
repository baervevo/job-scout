import re
from html import unescape

import requests

from src.constants.processing_constants import OLLAMA_API_URL


def clean_html_text(text: str) -> str:
    if not text:
        return ""

    text = unescape(text)
    text = re.sub(r'<[^>]+>', '', text)
    text = ' '.join(text.split())

    return text


def ollama_api_call(prompt: str, model: str = 'llama2') -> str:
    headers = {"Content-Type": "application/json"}
    data = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }

    response = requests.post(OLLAMA_API_URL, json=data, headers=headers)
    response.raise_for_status()
    result = response.json()
    return result.get("response", "").strip()


def format_lines(text):
    """
       Removes numbering and dots from the start of each line and adds a comma at the end,
       handling various starting patterns.

       Args:
           text: A string containing multiple lines.

       Returns:
           A formatted string with the specified changes.
       """
    lines = text.strip().split('\n')
    formatted_lines = []
    for line in lines:
        formatted_line = re.sub(r'^\s*\d+\.?\s*', '', line).strip()

        if formatted_line:
            if not formatted_line.endswith(','):
                formatted_line += ','
        formatted_lines.append(formatted_line)

    return '\n'.join(filter(None, formatted_lines))

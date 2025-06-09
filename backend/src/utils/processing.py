import re
from html import unescape

import requests


def clean_html_text(text: str) -> str:
    """
    Cleans HTML-formatted text without BeautifulSoup.
    Removes tags, unescapes entities, and normalizes whitespace.
    """
    if not text:
        return ""

    text = unescape(text)
    text = re.sub(r'<[^>]+>', '', text)
    text = ' '.join(text.split())

    return text


def ollama_api_call(model: str, prompt: str) -> str:
    url = "http://localhost:11434/api/generate"
    headers = {"Content-Type": "application/json"}
    data = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }

    response = requests.post(url, json=data, headers=headers)
    response.raise_for_status()
    result = response.json()
    return result.get("response", "").strip()

import re
from html import unescape
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Optional

import ollama
from config import settings


def clean_html_text(text: str) -> str:
    if not text:
        return ""

    text = unescape(text)
    text = re.sub(r'<[^>]+>', '', text)
    text = ' '.join(text.split())

    return text


_ollama_executor = ThreadPoolExecutor(
    max_workers=settings.OLLAMA_MAX_WORKERS, 
    thread_name_prefix="ollama_"
)

def ollama_api_call(prompt: str, model: str = None, temperature: float = 0.2) -> str:
    if not settings.OLLAMA_ENABLED:
        raise RuntimeError("Ollama is disabled")
        
    response = ollama.chat(
        model=model or settings.OLLAMA_MODEL,
        messages=[
            {'role': 'user', 'content': prompt}
        ],
        options={
            'temperature': temperature,
            'num_ctx': settings.OLLAMA_CONTEXT_SIZE,
            'num_predict': settings.OLLAMA_MAX_TOKENS,
        }
    )
    return response['message']['content'].strip()

async def ollama_api_call_async(prompt: str, model: str = None, temperature: float = 0.2) -> Optional[str]:
    if not settings.OLLAMA_ENABLED:
        return None
        
    try:
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            _ollama_executor,
            lambda: ollama_api_call(prompt, model, temperature)
        )
        return result
    except Exception as e:
        import logging
        logging.warning(f"Ollama API call failed: {str(e)}")
        return None


def kw_text_to_list(text: str) -> list[str]:
    lines = text.splitlines()
    cleaned_lines = [
        re.sub(r'[^\w\s]', '', line).strip()
        for line in lines if line.strip()
    ]
    return cleaned_lines


def format_keywords(text: str) -> str:
    """
       Removes numbering and dots from the start of each line and adds a comma at the end,
       handling various starting patterns.

       Args:
           text: A string containing multiple lines.

       Returns:
           A formatted string with the specified changes.
       """
    lines = text.strip().split('\n')

    if lines and check_llm_commentary(lines[0]):
        lines = lines[1:]
    if lines and check_llm_commentary(lines[-1]):
        lines = lines[:-1]

    formatted_lines = []
    for line in lines:
        formatted_line = re.sub(r'^\s*\d+\.?\s*', '', line).strip()
        formatted_line = re.sub(r'[\d\(\)\s]+$', '', formatted_line)

        if formatted_line:
            if not formatted_line.endswith(','):
                formatted_line += ','
        formatted_lines.append(formatted_line)

    return '\n'.join(filter(None, formatted_lines))


def check_llm_commentary(line: str) -> bool:
    """
    Checks if the line starts with a comment from the LLM, such as 'Here are the keywords:'.

    Args:
        line (str): The line to check.

    Returns:
        bool: True if the line is a commentary, False otherwise.
    """
    commentary_patterns = [
        r'\bhere (are|is)\b',
        r'\bthe following\b',
        r'\bkeywords?\b',
        r'\bkeyword?\b',
        r'\bskills?\b',
        r'\bthis list\b',
        r'\bincludes\b',
        r'\bare:\b',
        r'^note\b',
        r'\bbelow\b',
    ]

    return any(re.match(pattern, line, re.IGNORECASE) for pattern in commentary_patterns)

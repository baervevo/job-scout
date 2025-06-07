import re
from html import unescape


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

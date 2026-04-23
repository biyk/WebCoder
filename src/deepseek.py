from src.browser import get_page_ws_url
from src.page import select_expert, send_message


def ask(text: str, url: str = None) -> str:
    if not url:
        url = "https://chat.deepseek.com"
    ws_url = get_page_ws_url(url)
    return send_message(ws_url, text)
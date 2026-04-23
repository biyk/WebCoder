from src.browser import get_page_ws_url
from src.page import select_expert, send_message

DEEPSEEK_URL = "https://chat.deepseek.com"


def ask(text: str) -> str:
    ws_url = get_page_ws_url(DEEPSEEK_URL)
    return send_message(ws_url, text)
from dotenv import load_dotenv
import os
from src.browser import get_page_ws_url
from src.page import select_expert, send_message
from src.timer import measure, reset, get_summary

load_dotenv()

DEEPSEEK_URL = "https://chat.deepseek.com"
USE_EXPERT = os.getenv("DEEPSEEK_USE_EXPERT", "false").lower() == "true"


def ask(text: str) -> str:
    reset()
    with measure("ask"):
        ws_url = get_page_ws_url(DEEPSEEK_URL)
        if USE_EXPERT:
            with measure("select_expert"):
                select_expert(ws_url)
        response = send_message(ws_url, text)
    return response
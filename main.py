import json
import os
import sys
from src.browser import get_page_ws_url
from src.page import select_expert, send_message


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    settings_path = os.path.join(script_dir, 'settings.json')

    if not os.path.exists(settings_path):
        print(f"Файл {settings_path} не найден.")
        sys.exit(1)

    with open(settings_path, 'r', encoding='utf-8') as f:
        settings = json.load(f)

    url = settings.get('url')
    if not url:
        print("Ключ 'url' отсутствует в settings.json.")
        sys.exit(1)

    ws_url = get_page_ws_url(url)
    select_expert(ws_url)
    response = send_message(ws_url, "Расскажи анекдот")
    print(f"Ответ:\n{response}")


if __name__ == "__main__":
    main()
import json
import os
import sys
from src.browser import select_expert_and_type

BRAVE_PATH = r"C:\Program Files\BraveSoftware\Brave-Browser-Beta\Application\brave.exe"


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

    if not os.path.exists(BRAVE_PATH):
        print(f"Brave Beta не найден по пути: {BRAVE_PATH}")
        sys.exit(1)

    response = select_expert_and_type(url, "Привет мир!")
    print(f"Ответ:\n{response}")


if __name__ == "__main__":
    main()
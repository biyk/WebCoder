# Запуск проекта

## Установка зависимостей

```bash
pip install websocket-client
```

## Запуск

```bash
set PYTHONIOENCODING=utf-8 && C:\Users\Name\AppData\Local\Programs\Python\Python310\python.exe main.py
```

Скрипт откроет URL из `settings.json` в браузере Brave Beta.

## Требования

- Python 3.10+
- Brave Browser Beta (путь в коде: `C:\Program Files\BraveSoftware\Brave-Browser-Beta\Application\brave.exe`)
- Файл `settings.json` с ключом `url`
# Запуск проекта

## Установка зависимостей

```bash
pip install websocket-client flask flask-cors
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

## MCP Server

 pm2 start mcp_deepseek_server.py --interpreter .\venv\Scripts\python.exe --name deepseek-mcp

## Flask API сервер

Запуск сервера на порту 9999:

```bash
 set PYTHONIOENCODING=utf-8; python server.py
```

### Запрос из консоли браузера

```javascript
fetch('http://localhost:9999/ask', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json; charset=utf-8' },
  body: JSON.stringify({ text: 'Ваш вопрос' })
}).then(r => r.json()).then(console.log);
```

### Запрос из PowerShell

```powershell
chcp 65001
Invoke-RestMethod -Uri "http://localhost:9999/ask" -Method POST -ContentType "application/json; charset=utf-8" -Body ([System.Text.Encoding]::UTF8.GetBytes('{"text": "Ваш вопрос"}'))
```
# AGENTS.md

## Running

```bash
set PYTHONIOENCODING=utf-8 && C:\Users\Name\AppData\Local\Programs\Python\Python310\python.exe main.py
```

CLI: `python ask.py "question"`

## Dependencies

- `websocket-client`

## Architecture

- `main.py` / `ask.py` - entry points
- `src/deepseek.py` - public API: `ask(text)` returns response
- `src/browser.py` - CDP: port check, target discovery, browser launch
- `src/page.py` - page interaction: click, type, wait, select expert, send message
- `settings.json` - URL config

## CDP quirks

1. Responses: `result.result.value` (double nesting)
2. Loop in `send_cdp_command` to filter by `id`
3. Textarea: `Input.insertText` + `focus()` (not JS value)
4. Browser: `--remote-debugging-port=9222` + `--user-data-dir=profile`

## DeepSeek response extraction

- Find last `.ds-message` in `.ds-virtual-list-items`
- Check parent for `.ds-flex` sibling (completion flag)
- Get text from `.ds-message` child element

## Skills

`.opencode/skills/deepseek_expert/SKILL.md` - ask questions to save tokens
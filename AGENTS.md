# AGENTS.md

## Running the project

```bash
set PYTHONIOENCODING=utf-8 && C:\Users\Name\AppData\Local\Programs\Python\Python310\python.exe main.py
```

- `PYTHONIOENCODING=utf-8` is required for Russian text output
- Full path to Python is required (not just `python`)

## Dependencies

- `websocket-client` (install via `pip install websocket-client`)

## Key files

- `main.py` - entry point
- `src/browser.py` - CDP automation functions
- `settings.json` - URL configuration with key `url`

## CDP quirks (hard-learned)

1. CDP responses have double nesting: `result.result.value`, not `result.value`
2. Always use a loop in `send_cdp_command` to filter by `id` - events arrive before responses
3. To input text in textarea, use `Input.insertText` CDP command (not JavaScript value assignment)
4. Browser must be started with `--remote-debugging-port=9222` and `--user-data-dir=profile`

## Git workflow

Commands must be run separately (no `&&` in PowerShell):
```bash
git add -A
git commit -m "message"
```

## Testing

Run `main.py` - it loads URL from `settings.json` and executes the full automation flow.
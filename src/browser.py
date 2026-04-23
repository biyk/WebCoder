import json
import subprocess
import sys
import os
import socket
import time
import urllib.request
import websocket
from src.timer import start, stop, lap, measure

CDP_PORT = 9222
BRAVE_PATH = r"C:\Program Files\BraveSoftware\Brave-Browser-Beta\Application\brave.exe"


def is_port_open(port: int) -> bool:
    """Проверяет, открыт ли порт CDP."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0


def get_cdp_targets():
    """Получает список CDP targets через HTTP endpoint."""
    req = urllib.request.Request(f"http://localhost:{CDP_PORT}/json")
    with urllib.request.urlopen(req, timeout=3) as resp:
        return json.load(resp)


def send_cdp_command(ws, method, params=None, msg_id=1, timeout=30):
    """Отправляет CDP команду через WebSocket и возвращает ответ."""
    cmd = {"id": msg_id, "method": method, "params": params or {}}
    ws.settimeout(timeout)
    ws.send(json.dumps(cmd))
    while True:
        raw = ws.recv()
        response = json.loads(raw)
        if response.get("id") == msg_id:
            return response


def navigate_to_url(ws_url, url):
    """Переходит по URL в текущей вкладке через CDP."""
    ws = websocket.create_connection(ws_url, timeout=30)
    resp = send_cdp_command(ws, "Page.navigate", {"url": url})
    ws.close()
    return resp


def get_page_ws_url(url: str) -> str:
    """Получает WebSocket URL для страницы. Запускает браузер если нужно."""
    ensure_browser_running()

    # Получаем список всех CDP targets
    targets = get_cdp_targets()
    page_targets = [t for t in targets if t.get("type") == "page"]

    # Ищем существующую вкладку с нужным URL
    existing = next((t for t in page_targets if url in t.get("url", "")), None)

    if existing:
        # Нашли существующую вкладку - используем её
        ws_url = existing["webSocketDebuggerUrl"]
    elif page_targets:
        # Нет вкладки с URL, но есть другие страницы - открываем в первой
        ws_url = page_targets[0]["webSocketDebuggerUrl"]
        navigate_to_url(ws_url, url)
        targets = get_cdp_targets()
        existing = next((t for t in targets if t.get("type") == "page" and url in t.get("url", "")), None)
    else:
        # Нет ни одной страницы - создаём новую вкладку
        browser_target = next((t for t in targets if t.get("type") == "browser"), targets[0])
        ws = websocket.create_connection(browser_target["webSocketDebuggerUrl"], timeout=10)
        send_cdp_command(ws, "Target.createTarget", {"url": url})
        ws.close()
        targets = get_cdp_targets()
        existing = next((t for t in targets if t.get("type") == "page" and url in t.get("url", "")), None)

    return existing["webSocketDebuggerUrl"]


def ensure_browser_running():
    """Проверяет и запускает Brave Browser с CDP если нужно."""
    with measure("browser_launch"):
        if not is_port_open(CDP_PORT):
            print("Запуск Brave Browser с удалённой отладкой...")
            user_data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "profile"))
            cmd = [
                BRAVE_PATH,
                f"--remote-debugging-port={CDP_PORT}",
                f"--user-data-dir={user_data_dir}",
                "--no-first-run",
                "--no-default-browser-check",
                "--remote-allow-origins=*"
            ]
            subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            # Ждём пока браузер откроет CDP порт
            start("wait_port_open")
            for _ in range(20):
                time.sleep(1)
                lap("wait_port_open")
                if is_port_open(CDP_PORT):
                    break
            else:
                print("Не удалось дождаться запуска браузера.")
                sys.exit(1)
            stop("wait_port_open")

            # Фиксированная пауза после запуска браузера
            start("browser_warmup")
            time.sleep(3)
            lap("browser_warmup")
            time.sleep(2)
            lap("browser_warmup")
            stop("browser_warmup")
            print("Браузер запущен.")


def open_tab(url: str):
    """Открывает URL в браузере. Создаёт вкладку или использует существующую."""
    get_page_ws_url(url)
    print(f"Вкладка: {url}")
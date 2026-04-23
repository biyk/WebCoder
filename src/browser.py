import json
import subprocess
import sys
import os
import socket
import time
import urllib.request
import websocket

CDP_PORT = 9222
BRAVE_PATH = r"C:\Program Files\BraveSoftware\Brave-Browser-Beta\Application\brave.exe"


def is_port_open(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0


def get_cdp_targets():
    req = urllib.request.Request(f"http://localhost:{CDP_PORT}/json")
    with urllib.request.urlopen(req, timeout=3) as resp:
        return json.load(resp)


def send_cdp_command(ws, method, params=None, msg_id=1):
    cmd = {"id": msg_id, "method": method, "params": params or {}}
    ws.send(json.dumps(cmd))
    while True:
        raw = ws.recv()
        response = json.loads(raw)
        if response.get("id") == msg_id:
            return response


def navigate_to_url(ws_url, url):
    ws = websocket.create_connection(ws_url, timeout=10)
    resp = send_cdp_command(ws, "Page.navigate", {"url": url})
    ws.close()
    return resp


def click_element(ws_url, selector: str):
    ws = websocket.create_connection(ws_url, timeout=10)
    send_cdp_command(ws, "Runtime.evaluate", {"expression": f"document.querySelector('{selector}').click()"})
    ws.close()


def get_attribute(ws_url, selector: str, attr: str) -> str:
    ws = websocket.create_connection(ws_url, timeout=10)
    result = send_cdp_command(ws, "Runtime.evaluate", {"expression": f"(document.querySelector('{selector}') || {{}}).getAttribute('{attr}')"})
    ws.close()
    return result.get("result", {}).get("result", {}).get("value", "")


def select_expert(ws_url: str):
    wait_for_element(ws_url, '[data-model-type]')
    time.sleep(1)
    click_element(ws_url, '[data-model-type="expert"]')
    time.sleep(1)
    checked = get_attribute(ws_url, '[data-model-type="expert"]', 'aria-checked')
    print(f"Эксперт выбран: {checked}")
    return checked == "true"


def type_text(ws_url: str, selector: str, text: str):
    wait_for_element(ws_url, selector)
    set_textarea(ws_url, selector, text)
    print(f"Введен текст: {text}")


def wait_for_element(ws_url, selector, timeout=10):
    start = time.time()
    while time.time() - start < timeout:
        try:
            ws = websocket.create_connection(ws_url, timeout=5)
            resp = send_cdp_command(ws, "Runtime.evaluate", {
                "expression": f"!!document.querySelector('{selector}')"
            })
            ws.close()
            if resp.get("result", {}).get("value"):
                return True
        except Exception:
            pass
        time.sleep(0.5)
    return False


def set_textarea(ws_url, selector: str, text: str):
    ws = websocket.create_connection(ws_url, timeout=10)
    send_cdp_command(ws, "Runtime.evaluate", {"expression": f"document.querySelector('{selector}').focus()"})
    send_cdp_command(ws, "Input.insertText", {"text": text})
    ws.close()


def get_page_ws_url(url: str) -> str:
    ensure_browser_running()

    targets = get_cdp_targets()
    page_target = next((t for t in targets if t.get("type") == "page"), None)

    current_url = page_target.get("url", "") if page_target else ""
    should_navigate = not current_url or url not in current_url

    if should_navigate:
        if page_target is None:
            browser_target = next((t for t in targets if t.get("type") == "browser"), targets[0])
            ws = websocket.create_connection(browser_target["webSocketDebuggerUrl"], timeout=10)
            send_cdp_command(ws, "Target.createTarget", {"url": url})
            ws.close()
        else:
            ws_url = page_target["webSocketDebuggerUrl"]
            navigate_to_url(ws_url, url)
        targets = get_cdp_targets()
        page_target = next((t for t in targets if t.get("type") == "page" and url in t.get("url", "")), None)
        print(f"Открыто: {url}")
    else:
        print(f"Вкладка уже открыта: {current_url}")

    return page_target["webSocketDebuggerUrl"]


def select_expert_and_type(url: str, text: str):
    ws_url = get_page_ws_url(url)
    select_expert(ws_url)
    type_text(ws_url, 'textarea', text)


def ensure_browser_running():
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
        for _ in range(20):
            time.sleep(1)
            if is_port_open(CDP_PORT):
                break
        else:
            print("Не удалось дождаться запуска браузера.")
            sys.exit(1)
        print("Браузер запущен.")
        time.sleep(3)
        time.sleep(2)


def open_tab(url: str):
    get_page_ws_url(url)
    print(f"Вкладка: {url}")
import time
import websocket
from src.browser import send_cdp_command


def click_element(ws_url: str, selector: str):
    ws = websocket.create_connection(ws_url, timeout=10)
    send_cdp_command(ws, "Runtime.evaluate", {"expression": f"document.querySelector('{selector}').click()"})
    ws.close()


def get_attribute(ws_url: str, selector: str, attr: str) -> str:
    ws = websocket.create_connection(ws_url, timeout=10)
    result = send_cdp_command(ws, "Runtime.evaluate", {"expression": f"(document.querySelector('{selector}') || {{}}).getAttribute('{attr}')"})
    ws.close()
    return result.get("result", {}).get("result", {}).get("value", "")


def wait_for_element(ws_url: str, selector: str, timeout: int = 10) -> bool:
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


def set_textarea(ws_url: str, selector: str, text: str):
    ws = websocket.create_connection(ws_url, timeout=10)
    send_cdp_command(ws, "Runtime.evaluate", {"expression": f"document.querySelector('{selector}').focus()"})
    send_cdp_command(ws, "Input.insertText", {"text": text})
    ws.close()


def type_text(ws_url: str, selector: str, text: str):
    wait_for_element(ws_url, selector)
    set_textarea(ws_url, selector, text)


def press_enter_and_verify(ws_url: str, selector: str) -> bool:
    ws = websocket.create_connection(ws_url, timeout=10)
    send_cdp_command(ws, "Input.dispatchKeyEvent", {"key": "Enter", "type": "keyDown"})
    send_cdp_command(ws, "Input.dispatchKeyEvent", {"key": "Enter", "type": "keyUp"})
    ws.close()
    time.sleep(1)
    ws = websocket.create_connection(ws_url, timeout=10)
    result = send_cdp_command(ws, "Runtime.evaluate", {
        "expression": f"document.querySelector('{selector}').value"
    })
    ws.close()
    remaining = result.get("result", {}).get("result", {}).get("value", "")
    return remaining == ""


def get_last_response(ws_url: str, timeout: int = 60) -> str:
    start = time.time()
    while time.time() - start < timeout:
        ws = websocket.create_connection(ws_url, timeout=10)
        result = send_cdp_command(ws, "Runtime.evaluate", {
            "expression": """
                (function() {
                    const items = document.querySelector('.ds-virtual-list-items');
                    if (!items) return null;
                    const messages = items.querySelectorAll('.ds-message');
                    if (!messages.length) return null;
                    const lastMsg = messages[messages.length - 1];
                    const parent = lastMsg.parentElement;
                    if (!parent) return null;
                    const flex = Array.from(parent.children).find(c => c.classList.contains('ds-flex'));
                    if (!flex) return null;
                    const msgEl = lastMsg.querySelector('.ds-message') || lastMsg;
                    return msgEl.textContent.trim();
                })()
            """
        })
        ws.close()
        text = result.get("result", {}).get("result", {}).get("value")
        if text:
            return text
        time.sleep(2)
    return ""


def select_expert(ws_url: str) -> bool:
    wait_for_element(ws_url, '[data-model-type]')
    time.sleep(1)
    click_element(ws_url, '[data-model-type="expert"]')
    time.sleep(1)
    checked = get_attribute(ws_url, '[data-model-type="expert"]', 'aria-checked')
    print(f"Эксперт выбран: {checked}")
    return checked == "true"


def send_message(ws_url: str, text: str) -> str:
    type_text(ws_url, 'textarea', text)
    sent = press_enter_and_verify(ws_url, 'textarea')
    print(f"Текст отправлен: {sent}")
    return get_last_response(ws_url)
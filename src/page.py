import time
import websocket
from src.browser import send_cdp_command
from src.timer import start, stop, lap, measure


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
    start("wait_element", f"selector={selector}")
    start_time = time.time()
    ws = websocket.create_connection(ws_url, timeout=5)
    while time.time() - start_time < timeout:
        try:
            resp = send_cdp_command(ws, "Runtime.evaluate", {
                "expression": f"!!document.querySelector('{selector}')"
            })
            if resp.get("result", {}).get("result", {}).get("value"):
                ws.close()
                stop("wait_element")
                return True
        except Exception:
            pass
        time.sleep(0.5)
    ws.close()
    stop("wait_element")
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
    start("press_enter")
    ws = websocket.create_connection(ws_url, timeout=10)
    send_cdp_command(ws, "Input.dispatchKeyEvent", {"key": "Enter", "type": "keyDown"})
    send_cdp_command(ws, "Input.dispatchKeyEvent", {"key": "Enter", "type": "keyUp"})
    ws.close()
    start("enter_verify_pause")
    time.sleep(1)
    stop("enter_verify_pause")
    ws = websocket.create_connection(ws_url, timeout=10)
    result = send_cdp_command(ws, "Runtime.evaluate", {
        "expression": f"document.querySelector('{selector}').value"
    })
    ws.close()
    remaining = result.get("result", {}).get("result", {}).get("value", "")
    stop("press_enter")
    return remaining == ""


def get_last_response(ws_url: str, timeout: int = 60) -> str:
    start("get_response_polling")
    start_time = time.time()
    iteration = 0
    ws = websocket.create_connection(ws_url, timeout=10)
    while time.time() - start_time < timeout:
        iteration += 1
        result = send_cdp_command(ws, "Runtime.evaluate", {
            "expression": """
    (function() {
                    const msgs = document.querySelectorAll('.ds-message');
                    if (!msgs.length) return null;
                    const lastMsg = msgs[msgs.length - 1];
                    return lastMsg.textContent.trim();
                })()
            """
        })
        text = result.get("result", {}).get("result", {}).get("value")
        if text:
            lap("get_response_polling", f"iter={iteration} got {len(text)} chars")
            ws.close()
            stop("get_response_polling")
            return text
        time.sleep(2)
    lap("get_response_polling", "timeout")
    ws.close()
    stop("get_response_polling")
    return ""


def select_expert(ws_url: str) -> bool:
    with measure("select_expert"):
        with measure("wait_model_type"):
            wait_for_element(ws_url, '[data-model-type]')
        start("select_expert_pause")
        time.sleep(1)
        stop("select_expert_pause")
        with measure("click_expert"):
            click_element(ws_url, '[data-model-type="expert"]')
        start("select_expert_verify_pause")
        time.sleep(1)
        stop("select_expert_verify_pause")
        with measure("check_expert"):
            checked = get_attribute(ws_url, '[data-model-type="expert"]', 'aria-checked')
        print(f"Эксперт выбран: {checked}")
        return checked == "true"


def send_message(ws_url: str, text: str) -> str:
    with measure("send_message"):
        with measure("type_text"):
            type_text(ws_url, 'textarea', text)
        with measure("press_enter"):
            sent = press_enter_and_verify(ws_url, 'textarea')
        print(f"Текст отправлен: {sent}")
        with measure("get_response"):
            response = get_last_response(ws_url)
        return response
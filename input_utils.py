import threading
from pynput import keyboard, mouse

# 全局输入状态
pressed_keys = set()
mouse_buttons = {"left": False}
state_lock = threading.Lock()

def on_press(key):
    with state_lock:
        pressed_keys.add(key)

def on_release(key):
    with state_lock:
        pressed_keys.discard(key)

def on_click(x, y, button, pressed):
    with state_lock:
        if button == mouse.Button.left:
            mouse_buttons["left"] = pressed

kb_listener = keyboard.Listener(on_press=on_press, on_release=on_release)
kb_listener.daemon = True

ms_listener = mouse.Listener(on_click=on_click)
ms_listener.daemon = True

def start_listeners():
    kb_listener.start()
    ms_listener.start()

def stop_listeners():
    kb_listener.stop()
    ms_listener.stop()

def get_active_chars():
    chars = set()
    with state_lock:
        for key in pressed_keys:
            if hasattr(key, 'char') and key.char:
                chars.add(key.char.upper())
            elif key == keyboard.Key.space:
                chars.add("SPACE")
    return chars

def get_input_state():
    with state_lock:
        is_typing = len(pressed_keys) > 0
        is_clicking = mouse_buttons["left"]
    return is_typing, is_clicking
import threading
from pynput import keyboard, mouse

pressed_keys = set()
mouse_buttons = {"left": False}
state_lock = threading.Lock()

# 插件事件回调钩子
_key_press_callback = None

def set_key_press_callback(cb):
    global _key_press_callback
    _key_press_callback = cb

def get_key_identifier(key):
    try:
        if hasattr(key, 'char') and key.char is not None:
            return key.char.lower()
    except AttributeError:
        pass
    if hasattr(key, 'name') and key.name is not None:
        return key.name.lower()
    return str(key).replace("Key.", "").lower()

def on_press(key):
    key_id = get_key_identifier(key)
    with state_lock:
        pressed_keys.add(key_id)
    
    # 触发插件事件
    if _key_press_callback:
        try:
            _key_press_callback(key_id)
        except: pass

def on_release(key):
    key_id = get_key_identifier(key)
    with state_lock:
        pressed_keys.discard(key_id)

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
        for key_id in pressed_keys:
            if len(key_id) == 1 and key_id.isalpha():
                chars.add(key_id.upper())
            elif len(key_id) == 1 and key_id.isdigit():
                chars.add(key_id)
            elif key_id == 'space':
                chars.add("SPACE")
    return chars

def get_input_state():
    with state_lock:
        is_typing = len(pressed_keys) > 0
        is_clicking = mouse_buttons["left"]
    return is_typing, is_clicking
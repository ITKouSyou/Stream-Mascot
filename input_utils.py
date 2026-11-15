import threading
from pynput import keyboard, mouse

# 全局输入状态
pressed_keys = set()
mouse_buttons = {"left": False}
state_lock = threading.Lock()

def get_key_identifier(key):
    """将 pynput 的按键对象转换为一个统一的小写字符串标识符"""
    try:
        # 处理字符键 (w, a, s, d, 1, 2 等，统一转小写)
        if hasattr(key, 'char') and key.char is not None:
            return key.char.lower()
    except AttributeError:
        pass
    
    # 处理特殊键 (space, shift, ctrl 等)
    if hasattr(key, 'name') and key.name is not None:
        return key.name.lower()
        
    # 其他兜底
    return str(key).replace("Key.", "").lower()

def on_press(key):
    key_id = get_key_identifier(key)
    with state_lock:
        pressed_keys.add(key_id)

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
            if len(key_id) == 1 and key_id.isalpha():  # 单个字母 (a-z)
                chars.add(key_id.upper())
            elif len(key_id) == 1 and key_id.isdigit(): # 数字 (0-9)
                chars.add(key_id)
            elif key_id == 'space':
                chars.add("SPACE")
    return chars

def get_input_state():
    with state_lock:
        is_typing = len(pressed_keys) > 0
        is_clicking = mouse_buttons["left"]
    return is_typing, is_clicking
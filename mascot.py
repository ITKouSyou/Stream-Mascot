# mascot.py
import sys
import random
import threading
import time
import win32api
import win32gui
import win32con
import pygame
from pynput import keyboard, mouse
import urllib.request
import io
import os
import json

# ---------------- 配置加载 ----------------
CONFIG_FILE = "config.json"

DEFAULT_CONFIG = {
    "width": 600, "height": 400, "fps": 60,
    "character_path": "", "character_width": 180,
    "colors": {
        "bg": [0, 0, 0], "desk": [245, 245, 245], "cat": [255, 255, 255],
        "outline": [15, 15, 15], "paw": [255, 160, 170],
        "mousepad": [180, 180, 180], "mouse": [60, 60, 65], "mouse_hl": [255, 80, 80],
        "key_base": [45, 45, 50], "key": [75, 75, 80], "key_hl": [100, 200, 255]
    }
}

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                user_cfg = json.load(f)
                cfg = {**DEFAULT_CONFIG, **user_cfg}
                cfg["colors"] = {**DEFAULT_CONFIG["colors"], **user_cfg.get("colors", {})}
                return cfg
        except Exception as e:
            print(f"读取配置文件失败: {e}，将使用默认配置。")
    else:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_CONFIG, f, indent=2, ensure_ascii=False)
        print(f"已生成默认配置文件 {CONFIG_FILE}")
    return DEFAULT_CONFIG

CFG = load_config()

WIDTH = CFG["width"]
HEIGHT = CFG["height"]
FPS = CFG["fps"]
CHARACTER_PATH = CFG["character_path"]
CHARACTER_WIDTH = CFG["character_width"]

COLOR_BG = tuple(CFG["colors"]["bg"])
COLOR_DESK = tuple(CFG["colors"]["desk"])
COLOR_CAT = tuple(CFG["colors"]["cat"])
COLOR_OUTLINE = tuple(CFG["colors"]["outline"])
COLOR_PAW = tuple(CFG["colors"]["paw"])

COLOR_MOUSEPAD = tuple(CFG["colors"]["mousepad"])
COLOR_MOUSE = tuple(CFG["colors"]["mouse"])
COLOR_MOUSE_HL = tuple(CFG["colors"]["mouse_hl"])

COLOR_KEY_BASE = tuple(CFG["colors"]["key_base"])
COLOR_KEY = tuple(CFG["colors"]["key"])
COLOR_KEY_HL = tuple(CFG["colors"]["key_hl"])

# ---------------- 全局状态 ----------------
pressed_keys = set()
mouse_buttons = {"left": False}
state_lock = threading.Lock()

is_dragging = False
drag_start_global = (0, 0)
window_start_pos = (0, 0)

next_blink = time.time() + random.uniform(2, 5)
blink_until = 0.0

# 鼠标平滑追踪
current_hand_x = 115
current_hand_y = 297

# ---------------- 监听器 ----------------
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
kb_listener.start()

ms_listener = mouse.Listener(on_click=on_click)
ms_listener.daemon = True
ms_listener.start()

# ---------------- 窗口操作 ----------------
def get_hwnd():
    return pygame.display.get_wm_info()["window"]

def set_window_transparent():
    hwnd = get_hwnd()
    ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
    win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, ex_style | win32con.WS_EX_LAYERED)
    win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, WIDTH, HEIGHT, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
    win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(*COLOR_BG), 0, win32con.LWA_COLORKEY)

def move_window(x, y):
    hwnd = get_hwnd()
    win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, x, y, 0, 0, win32con.SWP_NOSIZE | win32con.SWP_SHOWWINDOW)

def get_window_pos():
    hwnd = get_hwnd()
    rect = win32gui.GetWindowRect(hwnd)
    return rect[0], rect[1]

# ---------------- 键盘布局数据 ----------------
keys_data = []
keys_data.append({"char": "SPACE", "rect": pygame.Rect(410, 250, 130, 24)})

for i, char in enumerate("ZXCVBNM"):
    keys_data.append({"char": char, "rect": pygame.Rect(360 + i*26, 282, 22, 24)})
for i, char in enumerate("ASDFGHJKL"):
    keys_data.append({"char": char, "rect": pygame.Rect(346 + i*26, 314, 22, 24)})
for i, char in enumerate("QWERTYUIOP"):
    keys_data.append({"char": char, "rect": pygame.Rect(332 + i*26, 346, 22, 24)})

def get_active_chars():
    chars = set()
    with state_lock:
        for key in pressed_keys:
            if hasattr(key, 'char') and key.char:
                chars.add(key.char.upper())
            elif key == keyboard.Key.space:
                chars.add("SPACE")
    return chars

# ---------------- 图片加载 ----------------
def load_custom_character(path):
    if not path:
        return None
        
    try:
        if path.startswith("http"):
            req = urllib.request.Request(path, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=3) as response:
                image_data = response.read()
            image = pygame.image.load(io.BytesIO(image_data))
        else:
            if not os.path.exists(path):
                print(f"找不到本地图片: {path}")
                return None
            image = pygame.image.load(path)
            
        image = image.convert_alpha()
        
        if image.get_at((0, 0)).a == 255:  
            bg_color = image.get_at((0, 0))
            image.set_colorkey(bg_color)
            
        ratio = CHARACTER_WIDTH / image.get_width()
        target_height = int(image.get_height() * ratio)
        image = pygame.transform.smoothscale(image, (CHARACTER_WIDTH, target_height))
        
        return image
    except Exception as e:
        print(f"加载角色失败: {e}。回退到默认白猫。")
        return None

# ---------------- 绘制函数 ----------------
def draw_background_and_cat(surface, is_blinking, char_image):
    if char_image:
        rect = char_image.get_rect(center=(WIDTH//2, 130))
        surface.blit(char_image, rect)
    else:
        # 猫耳朵
        pygame.draw.polygon(surface, COLOR_CAT, [(160, 70), (190, -10), (250, 60)])
        pygame.draw.lines(surface, COLOR_OUTLINE, False, [(160, 70), (190, -10), (250, 60)], 4)
        
        pygame.draw.polygon(surface, COLOR_CAT, [(350, 60), (410, -10), (440, 70)])
        pygame.draw.lines(surface, COLOR_OUTLINE, False, [(350, 60), (410, -10), (440, 70)], 4)
        
        # 猫脸
        pygame.draw.circle(surface, COLOR_CAT, (WIDTH//2, 120), 120)
        pygame.draw.circle(surface, COLOR_OUTLINE, (WIDTH//2, 120), 120, 4)
        
        # 五官
        if is_blinking:
            pygame.draw.line(surface, COLOR_OUTLINE, (250, 120), (265, 120), 4)
            pygame.draw.line(surface, COLOR_OUTLINE, (335, 120), (350, 120), 4)
        else:
            pygame.draw.circle(surface, COLOR_OUTLINE, (255, 120), 8)
            pygame.draw.circle(surface, COLOR_OUTLINE, (345, 120), 8)
            
        pygame.draw.arc(surface, COLOR_OUTLINE, (285, 120, 15, 15), 3.14, 0, 3)
        pygame.draw.arc(surface, COLOR_OUTLINE, (300, 120, 15, 15), 3.14, 0, 3)

    # 桌面
    pygame.draw.rect(surface, COLOR_DESK, (0, 240, WIDTH, HEIGHT-240))
    pygame.draw.line(surface, COLOR_OUTLINE, (0, 240), (WIDTH, 240), 4)

def draw_mouse_hand(surface, mx, my, is_pressed):
    pygame.draw.ellipse(surface, COLOR_MOUSEPAD, (20, 245, 190, 105))
    pygame.draw.ellipse(surface, COLOR_OUTLINE, (20, 245, 190, 105), 2)

    # 放大鼠标本体 (宽 40, 高 60)
    m_rect = pygame.Rect(mx - 20, my - 30, 40, 60)
    pygame.draw.ellipse(surface, COLOR_MOUSE, m_rect)
    pygame.draw.ellipse(surface, COLOR_OUTLINE, m_rect, 3)
    pygame.draw.line(surface, COLOR_OUTLINE, (mx, my), (mx, m_rect.bottom-5), 2)

    if is_pressed:
        pygame.draw.ellipse(surface, COLOR_MOUSE_HL, (m_rect.right-19, m_rect.bottom-31, 18, 28))

    # 鼠标手 (稍微缩小，并往上提，让鼠标下半部分露出来)
    paw_cy = my - 15
    if is_pressed:
        paw_cy += 4 
        
    # 手背
    pygame.draw.circle(surface, COLOR_CAT, (mx, paw_cy), 14)
    pygame.draw.circle(surface, COLOR_OUTLINE, (mx, paw_cy), 14, 3)
    
    # 小手指朝下
    for i in range(3): 
        px = mx - 9 + i * 9
        py = paw_cy + 10
        pygame.draw.circle(surface, COLOR_CAT, (px, py), 6)
        pygame.draw.circle(surface, COLOR_OUTLINE, (px, py), 6, 3)

def draw_keyboard_hand(surface, is_typing, active_chars, font):
    pygame.draw.polygon(surface, COLOR_KEY_BASE, [(310, 235), (590, 235), (600, 400), (280, 400)])
    
    for k in keys_data:
        rect = k["rect"]
        char = k["char"]
        is_active = char in active_chars
        
        bg_color = COLOR_KEY_HL if is_active else COLOR_KEY
        pygame.draw.rect(surface, bg_color, rect, border_radius=4)
        pygame.draw.rect(surface, COLOR_OUTLINE, rect, 1, border_radius=4)
        
        text_surf = font.render(char, True, (255, 255, 255))
        text_surf = pygame.transform.rotate(text_surf, 180)
        text_rect = text_surf.get_rect(center=rect.center)
        surface.blit(text_surf, text_rect)

    # 键盘手默认位置
    target_x, target_y = 450, 295 
    
    if is_typing and active_chars:
        target_char = list(active_chars)[0]
        for k in keys_data:
            if k["char"] == target_char:
                target_x = k["rect"].centerx
                target_y = k["rect"].centery - 5 
                break
                
    jitter = random.randint(-1, 1) if is_typing else 0
    cx, cy = target_x, target_y + jitter
    
    if is_typing:
        # 按下时：手背
        pygame.draw.ellipse(surface, COLOR_CAT, (cx - 20, cy - 15, 40, 40))
        pygame.draw.ellipse(surface, COLOR_OUTLINE, (cx - 20, cy - 15, 40, 40), 4)
        for i in range(3):
            px = cx - 10 + i * 10
            pygame.draw.circle(surface, COLOR_CAT, (px, cy + 12), 7)
            pygame.draw.circle(surface, COLOR_OUTLINE, (px, cy + 12), 7, 3)
    else:
        # 松开时：肉垫
        pygame.draw.ellipse(surface, COLOR_CAT, (cx - 22, cy - 22, 44, 44))
        pygame.draw.ellipse(surface, COLOR_OUTLINE, (cx - 22, cy - 22, 44, 44), 4)
        pygame.draw.ellipse(surface, COLOR_PAW, (cx - 9, cy - 4, 18, 22))
        for i in range(4):
            px = cx - 13 + i * 9
            py = cy + 12
            pygame.draw.circle(surface, COLOR_PAW, (px, py), 5)

def main():
    global is_dragging, drag_start_global, window_start_pos
    global next_blink, blink_until
    global current_hand_x, current_hand_y
    
    pygame.init()
    pygame.font.init()
    font = pygame.font.Font(None, 20) 
    
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.NOFRAME)
    set_window_transparent()

    char_image = load_custom_character(CHARACTER_PATH)

    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    is_dragging = True
                    drag_start_global = win32api.GetCursorPos()
                    window_start_pos = get_window_pos()
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    is_dragging = False

        if is_dragging:
            cur_x, cur_y = win32api.GetCursorPos()
            dx = cur_x - drag_start_global[0]
            dy = cur_y - drag_start_global[1]
            move_window(window_start_pos[0] + dx, window_start_pos[1] + dy)

        # --- 鼠标按屏幕比例追踪映射 ---
        cur_x, cur_y = win32api.GetCursorPos()
        screen_w = win32api.GetSystemMetrics(0)
        screen_h = win32api.GetSystemMetrics(1)

        # 计算目标位置
        pct_x = (cur_x / screen_w) - 0.5
        pct_y = (cur_y / screen_h) - 0.5

        # 鼠标垫活动范围 (x: 55 ~ 175, y: 270 ~ 325)
        target_mx = 115 - (pct_x * 120)
        target_my = 297 - (pct_y * 55)

        target_mx = max(55, min(175, target_mx))
        target_my = max(270, min(325, target_my))

        # 加入平滑缓动 (0.2 的插值系数，数值越小越有延迟感)
        current_hand_x += (target_mx - current_hand_x) * 0.2
        current_hand_y += (target_my - current_hand_y) * 0.2

        now = time.time()
        if now > next_blink:
            blink_until = now + 0.15
            next_blink = now + random.uniform(2, 5)
        is_blinking = now < blink_until

        with state_lock:
            is_typing = len(pressed_keys) > 0
            is_clicking = mouse_buttons["left"]
        
        active_chars = get_active_chars()

        screen.fill(COLOR_BG)

        draw_background_and_cat(screen, is_blinking, char_image)
        draw_mouse_hand(screen, current_hand_x, current_hand_y, is_clicking)
        draw_keyboard_hand(screen, is_typing, active_chars, font)

        pygame.display.flip()
        clock.tick(FPS)

    kb_listener.stop()
    ms_listener.stop()
    pygame.quit()

if __name__ == "__main__":
    main()
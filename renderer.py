import os
import io
import random
import urllib.request
import pygame
from config import (
    WIDTH, COLOR_DESK, COLOR_CAT, COLOR_OUTLINE, COLOR_PAW,
    COLOR_MOUSEPAD, COLOR_MOUSE, COLOR_MOUSE_HL,
    COLOR_KEY_BASE, COLOR_KEY, COLOR_KEY_HL, CHARACTER_WIDTH
)

# ---------------- 键盘布局数据 ----------------
keys_data = []
keys_data.append({"char": "SPACE", "rect": pygame.Rect(410, 250, 130, 24)})
for i, char in enumerate("ZXCVBNM"):
    keys_data.append({"char": char, "rect": pygame.Rect(360 + i*26, 282, 22, 24)})
for i, char in enumerate("ASDFGHJKL"):
    keys_data.append({"char": char, "rect": pygame.Rect(346 + i*26, 314, 22, 24)})
for i, char in enumerate("QWERTYUIOP"):
    keys_data.append({"char": char, "rect": pygame.Rect(332 + i*26, 346, 22, 24)})

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

def draw_background_and_cat(surface, is_blinking, is_talking, mouth_open, char_image):
    if char_image:
        y_offset = -4 if is_talking else 0
        rect = char_image.get_rect(center=(WIDTH//2, 130 + y_offset))
        surface.blit(char_image, rect)
    else:
        # 耳朵
        pygame.draw.polygon(surface, COLOR_CAT, [(160, 70), (190, -10), (250, 60)])
        pygame.draw.lines(surface, COLOR_OUTLINE, False, [(160, 70), (190, -10), (250, 60)], 4)
        pygame.draw.polygon(surface, COLOR_CAT, [(350, 60), (410, -10), (440, 70)])
        pygame.draw.lines(surface, COLOR_OUTLINE, False, [(350, 60), (410, -10), (440, 70)], 4)
        
        # 脸
        pygame.draw.circle(surface, COLOR_CAT, (WIDTH//2, 120), 120)
        pygame.draw.circle(surface, COLOR_OUTLINE, (WIDTH//2, 120), 120, 4)
        
        # 眼睛
        if is_blinking and not mouth_open:
            pygame.draw.line(surface, COLOR_OUTLINE, (250, 120), (265, 120), 4)
            pygame.draw.line(surface, COLOR_OUTLINE, (335, 120), (350, 120), 4)
        elif is_talking:
            pygame.draw.arc(surface, COLOR_OUTLINE, (240, 105, 30, 20), 3.14, 0, 4)
            pygame.draw.arc(surface, COLOR_OUTLINE, (330, 105, 30, 20), 3.14, 0, 4)
        else:
            pygame.draw.circle(surface, COLOR_OUTLINE, (255, 120), 8)
            pygame.draw.circle(surface, COLOR_OUTLINE, (345, 120), 8)
            
        # 嘴巴
        if mouth_open:
            pygame.draw.ellipse(surface, COLOR_OUTLINE, (280, 118, 40, 30))
            pygame.draw.ellipse(surface, (200, 80, 100), (284, 122, 32, 22))
            pygame.draw.ellipse(surface, COLOR_PAW, (290, 134, 20, 8))
        else:
            pygame.draw.arc(surface, COLOR_OUTLINE, (285, 120, 15, 15), 3.14, 0, 4)
            pygame.draw.arc(surface, COLOR_OUTLINE, (300, 120, 15, 15), 3.14, 0, 4)

    # 桌面
    pygame.draw.rect(surface, COLOR_DESK, (0, 240, WIDTH, 400-240))
    pygame.draw.line(surface, COLOR_OUTLINE, (0, 240), (WIDTH, 240), 4)

def draw_mouse_hand(surface, mx, my, is_pressed):
    pygame.draw.ellipse(surface, COLOR_MOUSEPAD, (20, 245, 190, 105))
    pygame.draw.ellipse(surface, COLOR_OUTLINE, (20, 245, 190, 105), 2)

    m_rect = pygame.Rect(mx - 20, my - 30, 40, 60)
    pygame.draw.ellipse(surface, COLOR_MOUSE, m_rect)
    pygame.draw.ellipse(surface, COLOR_OUTLINE, m_rect, 3)
    pygame.draw.line(surface, COLOR_OUTLINE, (mx, my), (mx, m_rect.bottom-5), 2)

    if is_pressed:
        pygame.draw.ellipse(surface, COLOR_MOUSE_HL, (m_rect.right-19, m_rect.bottom-31, 18, 28))

    paw_cy = my - 15
    if is_pressed:
        paw_cy += 4 
        
    pygame.draw.circle(surface, COLOR_CAT, (mx, paw_cy), 14)
    pygame.draw.circle(surface, COLOR_OUTLINE, (mx, paw_cy), 14, 3)
    
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
        pygame.draw.ellipse(surface, COLOR_CAT, (cx - 20, cy - 15, 40, 40))
        pygame.draw.ellipse(surface, COLOR_OUTLINE, (cx - 20, cy - 15, 40, 40), 4)
        for i in range(3):
            px = cx - 10 + i * 10
            pygame.draw.circle(surface, COLOR_CAT, (px, cy + 12), 7)
            pygame.draw.circle(surface, COLOR_OUTLINE, (px, cy + 12), 7, 3)
    else:
        pygame.draw.ellipse(surface, COLOR_CAT, (cx - 22, cy - 22, 44, 44))
        pygame.draw.ellipse(surface, COLOR_OUTLINE, (cx - 22, cy - 22, 44, 44), 4)
        pygame.draw.ellipse(surface, COLOR_PAW, (cx - 9, cy - 4, 18, 22))
        for i in range(4):
            px = cx - 13 + i * 9
            py = cy + 12
            pygame.draw.circle(surface, COLOR_PAW, (px, py), 5)
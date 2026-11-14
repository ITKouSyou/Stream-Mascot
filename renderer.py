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
# 新增：数字按键排 (倒置键盘的最外侧一排)
for i, char in enumerate("1234567890"):
    keys_data.append({"char": char, "rect": pygame.Rect(318 + i*26, 378, 22, 24)})

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
        rect = char_image.get_rect(center=(300, 130 + y_offset))
        surface.blit(char_image, rect)
    else:
        # ---------------- 1. 绘制 Bongo Cat 风格的完整头部轮廓 ----------------
        def get_bezier(p0, p1, p2, num=20):
            pts = []
            for i in range(num + 1):
                t = i / num
                x = (1 - t)**2 * p0[0] + 2 * (1 - t) * t * p1[0] + t**2 * p2[0]
                y = (1 - t)**2 * p0[1] + 2 * (1 - t) * t * p1[1] + t**2 * p2[1]
                pts.append((x, y))
            return pts

        outline_pts = []
        
        # 左侧脸颊 (从下往上画)
        outline_pts += get_bezier((180, 250), (120, 180), (160, 90))
        # 左耳外侧 (更圆润)
        outline_pts += get_bezier((160, 90), (165, 40), (195, 20))
        # 左耳内侧 (更深的凹陷)
        outline_pts += get_bezier((195, 20), (215, 55), (240, 70))
        # 头顶 (微平)
        outline_pts += get_bezier((240, 70), (300, 60), (360, 70))
        # 右耳内侧 (更深的凹陷)
        outline_pts += get_bezier((360, 70), (385, 55), (405, 20))
        # 右耳外侧 (更圆润)
        outline_pts += get_bezier((405, 20), (435, 40), (440, 90))
        # 右侧脸颊 (向下延伸)
        outline_pts += get_bezier((440, 90), (480, 180), (420, 250))
        
        # 底部闭合
        outline_pts.append((420, 260))
        outline_pts.append((180, 260))

        # 绘制底色和粗黑边
        pygame.draw.polygon(surface, COLOR_CAT, outline_pts)
        pygame.draw.lines(surface, COLOR_OUTLINE, True, outline_pts, 4)
        
        # ---------------- 2. 绘制五官 ----------------
        # 眼睛
        if is_blinking and not mouth_open:
            pygame.draw.line(surface, COLOR_OUTLINE, (240, 135), (260, 135), 4)
            pygame.draw.line(surface, COLOR_OUTLINE, (340, 135), (360, 135), 4)
        elif is_talking:
            pygame.draw.arc(surface, COLOR_OUTLINE, (230, 120, 30, 20), 3.14, 0, 4)
            pygame.draw.arc(surface, COLOR_OUTLINE, (340, 120, 30, 20), 3.14, 0, 4)
        else:
            pygame.draw.circle(surface, COLOR_OUTLINE, (250, 135), 7)
            pygame.draw.circle(surface, COLOR_OUTLINE, (350, 135), 7)
            
        # 嘴巴
        if mouth_open:
            pygame.draw.ellipse(surface, COLOR_OUTLINE, (285, 135, 30, 22))
            pygame.draw.ellipse(surface, (200, 80, 100), (288, 138, 24, 16))
            pygame.draw.ellipse(surface, COLOR_PAW, (293, 145, 14, 7))
        else:
            # 用多段线画出完美的连贯 w 嘴
            mouth_pts = [
                (285, 140),  # 左上起点
                (292, 148),  # 左下凹点
                (300, 140),  # 中间凸点
                (308, 148),  # 右下凹点
                (315, 140)   # 右上终点
            ]
            pygame.draw.lines(surface, COLOR_OUTLINE, False, mouth_pts, 4)

    # 桌面 (把下半部分切平，形成趴在桌子上的效果)
    pygame.draw.rect(surface, COLOR_DESK, (0, 240, 600, 160))
    pygame.draw.line(surface, COLOR_OUTLINE, (0, 240), (600, 240), 4)

import math

def draw_paw(surface, cx, cy, w, h, is_pressed, show_paw_pad=True):
    """通用半圆平底手背 (cx, cy 为底边中点)"""
    r = w // 2
    
    # 1. 填充白色底色
    # 上半圆
    pygame.draw.circle(surface, COLOR_CAT, (cx, cy - h + r), r)
    # 下半矩形
    pygame.draw.rect(surface, COLOR_CAT, (cx - r, cy - h + r, w, h - r))
    
    # 2. 绘制粗黑边
    # 顶部半圆弧
    pygame.draw.arc(surface, COLOR_OUTLINE, (cx - r, cy - h, w, w), 0, math.pi, 4)
    # 左右两侧竖线
    pygame.draw.line(surface, COLOR_OUTLINE, (cx - r, cy - h + r), (cx - r, cy), 4)
    pygame.draw.line(surface, COLOR_OUTLINE, (cx + r, cy - h + r), (cx + r, cy), 4)
    # 底部平直横线
    pygame.draw.line(surface, COLOR_OUTLINE, (cx - r, cy), (cx + r, cy), 4)

    # 3. 绘制肉垫
    if not is_pressed and show_paw_pad:
        # 中心大肉垫 (稍微靠下)
        pygame.draw.ellipse(surface, COLOR_PAW, (cx - 8, cy - 11, 16, 9))
        # 三个小肉垫 (完美扇形)
        pygame.draw.circle(surface, COLOR_PAW, (cx - 7, cy - 16), 3.5) # 左
        pygame.draw.circle(surface, COLOR_PAW, (cx + 7, cy - 16), 3.5) # 右
        pygame.draw.circle(surface, COLOR_PAW, (cx, cy - 19), 3.5)     # 上

def draw_mouse_hand(surface, mx, my, is_pressed):
    # 鼠标垫
    pygame.draw.ellipse(surface, COLOR_MOUSEPAD, (20, 245, 190, 105))
    pygame.draw.ellipse(surface, COLOR_OUTLINE, (20, 245, 190, 105), 2)

    # 1. 鼠标本体 (36x56)
    m_rect = pygame.Rect(mx - 18, my - 28, 36, 56)
    pygame.draw.rect(surface, COLOR_MOUSE, m_rect, border_radius=18)
    
    # 2. 左键高亮 (在右下角)
    if is_pressed:
        hl_rect = pygame.Rect(mx, my, 18, 28)
        pygame.draw.rect(surface, COLOR_MOUSE_HL, hl_rect, border_bottom_right_radius=18)

    # 3. 鼠标外边框
    pygame.draw.rect(surface, COLOR_OUTLINE, m_rect, 3, border_radius=18)
    
    # 4. 鼠标中缝 (画在下半部，用来区分下方的左右键)
    pygame.draw.line(surface, COLOR_OUTLINE, (mx, my), (mx, my + 28), 3)

    # 5. 鼠标手 (从上方伸下来，盖住上半部)
    cy = my + 2
    if is_pressed:
        cy += 2 # 按下时下压
        
    # 宽 28，高 24，无肉垫
    draw_paw(surface, mx, cy, 28, 24, True, False)


def draw_keyboard_hand(surface, is_typing_all, active_chars_all, font):
    pygame.draw.polygon(surface, COLOR_KEY_BASE, [(310, 235), (590, 235), (600, 400), (280, 400)])
    
    valid_chars = {k["char"] for k in keys_data}
    active_chars = active_chars_all.intersection(valid_chars)
    is_typing = len(active_chars) > 0

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

    # 默认待机位置：靠右脸颊，搭在桌子边缘 (y=240 附近)
    target_x, target_y = 380, 255 
    
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
        # 键盘手 - 按下 (宽 28，高压扁为 24)
        draw_paw(surface, cx, cy + 4, 28, 24, True, False)
    else:
        # 键盘手 - 松开 (宽 28，高 34，与鼠标手 1:1 一致)
        # 底部垫在 cy = 255，正好搭在桌面边缘
        draw_paw(surface, cx, cy - 2, 28, 34, False, True)
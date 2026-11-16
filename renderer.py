import os
import io
import random
import math
import time
import urllib.request
import pygame
from PIL import Image, ImageSequence
from config import (
    WIDTH, COLOR_DESK, COLOR_CAT, COLOR_OUTLINE, COLOR_PAW,
    COLOR_MOUSEPAD, COLOR_MOUSE, COLOR_MOUSE_HL,
    COLOR_KEY_BASE, COLOR_KEY, COLOR_KEY_HL, CFG
)

# ---------------- 键盘布局数据 ----------------
keys_data = []
keys_data.append({"char": "SPACE", "rect": pygame.Rect(410, 250, 130, 24)})
for i, char in enumerate("MNBVCXZ"):
    keys_data.append({"char": char, "rect": pygame.Rect(360 + i*26, 282, 22, 24)})
for i, char in enumerate("LKJHGFDSA"):
    keys_data.append({"char": char, "rect": pygame.Rect(346 + i*26, 314, 22, 24)})
for i, char in enumerate("POIUYTREWQ"):
    keys_data.append({"char": char, "rect": pygame.Rect(332 + i*26, 346, 22, 24)})
for i, char in enumerate("0987654321"):
    keys_data.append({"char": char, "rect": pygame.Rect(318 + i*26, 378, 22, 24)})


class GifPlayer:
    def __init__(self, frames, durations):
        self.frames = frames
        self.durations = durations
        self.current_frame = 0
        self.last_update = time.time()

    def get_current_surface(self):
        now = time.time()
        if now - self.last_update > self.durations[self.current_frame]:
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.last_update = now
        return self.frames[self.current_frame]


def load_image_by_path(path, width=180):
    if not path:
        return None
    try:
        if path.lower().endswith('.gif'):
            with Image.open(path) as img:
                frames = []
                durations = []
                for frame in ImageSequence.Iterator(img):
                    frame = frame.convert("RGBA")
                    bg_color = frame.getpixel((0, 0))
                    surf = pygame.image.fromstring(frame.tobytes(), frame.size, frame.mode).convert_alpha()
                    surf.set_colorkey(bg_color)
                    
                    ratio = width / surf.get_width()
                    target_height = int(surf.get_height() * ratio)
                    surf = pygame.transform.smoothscale(surf, (width, target_height))
                    
                    frames.append(surf)
                    durations.append(frame.info.get("duration", 100) / 1000.0)
                
                return GifPlayer(frames, durations)
        else:
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
                
            ratio = width / image.get_width()
            target_height = int(image.get_height() * ratio)
            image = pygame.transform.smoothscale(image, (width, target_height))
            return image
    except Exception as e:
        print(f"加载图片失败 ({path}): {e}")
        return None


def draw_face_overlay(surface, cx, cy, is_blinking, is_talking, mouth_open, expression):
    """自带的颜文字绘制系统"""
    eye_color = COLOR_OUTLINE
    pink = (255, 100, 150)
    l_eye = (cx - 50, cy + 5)
    r_eye = (cx + 50, cy + 5)
    mouth_cx, mouth_cy = cx, cy + 10
    
    if expression == "heart":
        for px, py in [l_eye, r_eye]:
            pygame.draw.circle(surface, pink, (px - 4, py - 5), 6)
            pygame.draw.circle(surface, pink, (px + 4, py - 5), 6)
            pygame.draw.polygon(surface, pink, [(px - 10, py - 2), (px + 10, py - 2), (px, py + 10)])
        pygame.draw.lines(surface, eye_color, False, [(mouth_cx - 15, mouth_cy), (mouth_cx - 8, mouth_cy + 8), (mouth_cx, mouth_cy), (mouth_cx + 8, mouth_cy + 8), (mouth_cx + 15, mouth_cy)], 4)
    elif expression == "angry":
        pygame.draw.line(surface, eye_color, (l_eye[0] - 10, l_eye[1] - 10), (l_eye[0] + 10, l_eye[1] + 3), 5)
        pygame.draw.line(surface, eye_color, (r_eye[0] + 10, r_eye[1] - 10), (r_eye[0] - 10, r_eye[1] + 3), 5)
        pygame.draw.line(surface, eye_color, (mouth_cx - 10, mouth_cy + 10), (mouth_cx + 10, mouth_cy + 10), 4)
    elif expression == "cry":
        pygame.draw.arc(surface, eye_color, (l_eye[0] - 10, l_eye[1] - 10, 20, 15), 3.14, 0, 3)
        pygame.draw.arc(surface, eye_color, (r_eye[0] - 10, r_eye[1] - 10, 20, 15), 3.14, 0, 3)
        pygame.draw.ellipse(surface, (100, 200, 255), (l_eye[0] - 5, l_eye[1] + 5, 6, 12))
        pygame.draw.ellipse(surface, (100, 200, 255), (r_eye[0] - 5, r_eye[1] + 5, 6, 12))
        pygame.draw.arc(surface, eye_color, (mouth_cx - 10, mouth_cy + 5, 10, 10), 3.14, 0, 3)
        pygame.draw.arc(surface, eye_color, (mouth_cx, mouth_cy + 5, 10, 10), 0, 3.14, 3)
    elif expression == "surprised":
        pygame.draw.circle(surface, eye_color, l_eye, 10, 4)
        pygame.draw.circle(surface, eye_color, r_eye, 10, 4)
        pygame.draw.circle(surface, eye_color, (mouth_cx, mouth_cy + 10), 7, 3)
    elif expression == "speechless":
        pygame.draw.line(surface, eye_color, (l_eye[0] - 10, l_eye[1]), (l_eye[0] + 10, l_eye[1]), 4)
        pygame.draw.line(surface, eye_color, (r_eye[0] - 10, r_eye[1]), (r_eye[0] + 10, r_eye[1]), 4)
        pygame.draw.line(surface, eye_color, (mouth_cx - 10, mouth_cy + 5), (mouth_cx + 10, mouth_cy + 5), 3)
        pygame.draw.ellipse(surface, (100, 200, 255), (r_eye[0] + 15, r_eye[1] - 25, 6, 12))
    else:
        if is_talking:
            pygame.draw.arc(surface, eye_color, (l_eye[0] - 15, l_eye[1] - 10, 30, 20), 3.14, 0, 4)
            pygame.draw.arc(surface, eye_color, (r_eye[0] - 15, r_eye[1] - 10, 30, 20), 3.14, 0, 4)
            if mouth_open:
                pygame.draw.ellipse(surface, eye_color, (mouth_cx - 15, mouth_cy + 5, 30, 22))
                pygame.draw.ellipse(surface, (200, 80, 100), (mouth_cx - 12, mouth_cy + 8, 24, 16))
                pygame.draw.ellipse(surface, COLOR_PAW, (mouth_cx - 7, mouth_cy + 15, 14, 7))
            else:
                pygame.draw.lines(surface, eye_color, False, [(mouth_cx - 15, mouth_cy), (mouth_cx - 8, mouth_cy + 8), (mouth_cx, mouth_cy), (mouth_cx + 8, mouth_cy + 8), (mouth_cx + 15, mouth_cy)], 4)
        elif is_blinking:
            pygame.draw.line(surface, eye_color, (l_eye[0] - 10, l_eye[1]), (l_eye[0] + 10, l_eye[1]), 4)
            pygame.draw.line(surface, eye_color, (r_eye[0] - 10, r_eye[1]), (r_eye[0] + 10, r_eye[1]), 4)
            pygame.draw.lines(surface, eye_color, False, [(mouth_cx - 15, mouth_cy), (mouth_cx - 8, mouth_cy + 8), (mouth_cx, mouth_cy), (mouth_cx + 8, mouth_cy + 8), (mouth_cx + 15, mouth_cy)], 4)
        else:
            pygame.draw.circle(surface, eye_color, l_eye, 7)
            pygame.draw.circle(surface, eye_color, r_eye, 7)
            pygame.draw.lines(surface, eye_color, False, [(mouth_cx - 15, mouth_cy), (mouth_cx - 8, mouth_cy + 8), (mouth_cx, mouth_cy), (mouth_cx + 8, mouth_cy + 8), (mouth_cx + 15, mouth_cy)], 4)


# 增加 is_typing 参数
def draw_background_and_cat(surface, is_blinking, is_talking, is_typing, mouth_open, char_images, show_code_face, expression="normal"):
    now = time.time()
    offset = CFG.get("global", {}).get("character_offset", [300, 130])
    base_x, base_y = offset[0], offset[1]
    
    idle_sway_x = math.sin(now * 2.0) * 3
    idle_breath_y = math.sin(now * 1.5) * 1.5
    angle = math.sin(now * 2.0) * 1.5
    
    active_bounce_y = 0
    if is_talking:
        active_bounce_y = math.sin(now * 35) * 3.5 - 3 
        idle_sway_x = 0
        angle = 0
    elif is_typing:
        active_bounce_y = math.sin(now * 20) * 2 - 1.5
        
    draw_cx = base_x + idle_sway_x
    draw_cy = base_y + idle_breath_y + active_bounce_y

    char_layer = pygame.Surface((600, 400), pygame.SRCALPHA)
    base_cx, base_cy = 300, 130

    img = None
    if char_images:
        if not show_code_face and expression in char_images and char_images[expression]:
            img = char_images[expression]
        elif "normal" in char_images:
            img = char_images["normal"]
    
    if img:
        if isinstance(img, GifPlayer):
            current_surf = img.get_current_surface()
        else:
            current_surf = img
        rect = current_surf.get_rect(center=(base_cx, base_cy))
        char_layer.blit(current_surf, rect)
    else:
        def get_bezier(p0, p1, p2, num=20):
            pts = []
            for i in range(num + 1):
                t = i / num
                x = (1 - t)**2 * p0[0] + 2 * (1 - t) * t * p1[0] + t**2 * p2[0]
                y = (1 - t)**2 * p0[1] + 2 * (1 - t) * t * p1[1] + t**2 * p2[1]
                pts.append((x, y))
            return pts

        outline_pts = []
        outline_pts += get_bezier((180, 250), (120, 180), (160, 90))
        outline_pts += get_bezier((160, 90), (165, 40), (195, 20))
        outline_pts += get_bezier((195, 20), (215, 55), (240, 70))
        outline_pts += get_bezier((240, 70), (300, 60), (360, 70))
        outline_pts += get_bezier((360, 70), (385, 55), (405, 20))
        outline_pts += get_bezier((405, 20), (435, 40), (440, 90))
        outline_pts += get_bezier((440, 90), (480, 180), (420, 250))
        outline_pts.append((420, 260))
        outline_pts.append((180, 260))

        pygame.draw.polygon(char_layer, COLOR_CAT, outline_pts)
        pygame.draw.lines(char_layer, COLOR_OUTLINE, True, outline_pts, 4)
        show_code_face = True

    if show_code_face:
        draw_face_overlay(char_layer, base_cx, base_cy, is_blinking, is_talking, mouth_open, expression)

    if angle != 0:
        rotated_layer = pygame.transform.rotate(char_layer, angle)
        rect = rotated_layer.get_rect(center=(draw_cx, draw_cy + 70))
        surface.blit(rotated_layer, rect)
    else:
        rect = char_layer.get_rect(center=(draw_cx, draw_cy + 70))
        surface.blit(char_layer, rect)

    pygame.draw.rect(surface, COLOR_DESK, (0, 240, 600, 160))
    pygame.draw.line(surface, COLOR_OUTLINE, (0, 240), (600, 240), 4)


def draw_paw(surface, cx, cy, w, h, is_pressed, show_paw_pad=True):
    r = w // 2
    pygame.draw.circle(surface, COLOR_CAT, (cx, cy - h + r), r)
    pygame.draw.rect(surface, COLOR_CAT, (cx - r, cy - h + r, w, h - r))
    pygame.draw.arc(surface, COLOR_OUTLINE, (cx - r, cy - h, w, w), 0, math.pi, 4)
    pygame.draw.line(surface, COLOR_OUTLINE, (cx - r, cy - h + r), (cx - r, cy), 4)
    pygame.draw.line(surface, COLOR_OUTLINE, (cx + r, cy - h + r), (cx + r, cy), 4)
    pygame.draw.line(surface, COLOR_OUTLINE, (cx - r, cy), (cx + r, cy), 4)

    if not is_pressed and show_paw_pad:
        pygame.draw.ellipse(surface, COLOR_PAW, (cx - 8, cy - 11, 16, 9))
        pygame.draw.circle(surface, COLOR_PAW, (cx - 7, cy - 16), 3.5)
        pygame.draw.circle(surface, COLOR_PAW, (cx + 7, cy - 16), 3.5)
        pygame.draw.circle(surface, COLOR_PAW, (cx, cy - 19), 3.5)

def draw_mouse_hand(surface, mx, my, is_pressed):
    pygame.draw.ellipse(surface, COLOR_MOUSEPAD, (20, 245, 190, 105))
    pygame.draw.ellipse(surface, COLOR_OUTLINE, (20, 245, 190, 105), 2)
    m_rect = pygame.Rect(mx - 18, my - 28, 36, 56)
    pygame.draw.rect(surface, COLOR_MOUSE, m_rect, border_radius=18)
    if is_pressed:
        hl_rect = pygame.Rect(mx, my, 18, 28)
        pygame.draw.rect(surface, COLOR_MOUSE_HL, hl_rect, border_bottom_right_radius=18)
    pygame.draw.rect(surface, COLOR_OUTLINE, m_rect, 3, border_radius=18)
    pygame.draw.line(surface, COLOR_OUTLINE, (mx, my), (mx, my + 28), 3)
    cy = my + 2
    if is_pressed: cy += 2
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

    target_x, target_y = 380, 255 
    if is_typing and active_chars:
        target_char = sorted(list(active_chars))[0]
        for k in keys_data:
            if k["char"] == target_char:
                target_x = k["rect"].centerx
                target_y = k["rect"].centery - 5 
                break
    jitter = random.randint(-1, 1) if is_typing else 0
    cx, cy = target_x, target_y + jitter
    
    if is_typing: draw_paw(surface, cx, cy + 4, 28, 24, True, False)
    else: draw_paw(surface, cx, cy - 2, 28, 34, False, True)
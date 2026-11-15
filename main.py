import ctypes
try:
    # 告诉 Windows 该程序不缩放，按真实像素渲染
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

import time
import random
import win32api
import pygame
import os
import numpy as np
import config  # 动态导入模块以支持实时修改缩放
from pynput import keyboard

from config import BASE_WIDTH, BASE_HEIGHT, SCALE, FPS, CHARACTER_PATH, CFG
from window_utils import set_window_transparent, move_window, get_window_pos, set_click_through
from input_utils import start_listeners, stop_listeners, get_active_chars, get_input_state
from audio_utils import start_mic, stop_mic, get_volume, MIC_ENABLED
from renderer import load_custom_character, draw_background_and_cat, draw_mouse_hand, draw_keyboard_hand
from effects import ParticleSystem, ContextMenu
from stt_utils import SpeechRecognizer

def remove_scale_artifacts(surface):
    """去除平滑缩放产生的边缘杂色（粉边/紫边），保证Win32透明抠图干净"""
    # 获取像素数组
    arr = pygame.surfarray.pixels3d(surface)
    # 找到紫红色过渡带 (R>180, B>180, G<100)
    mask = (arr[:, :, 0] > 180) & (arr[:, :, 2] > 180) & (arr[:, :, 1] < 100)
    # 强制刷回纯品红
    arr[mask] = [255, 0, 255]
    del arr

def main():
    global next_blink, blink_until, current_hand_x, current_hand_y, is_talking, last_talk_time
    
    pygame.init()
    pygame.font.init()
    
    # 尝试加载支持中文的系统字体
    font_paths = [
        "C:/Windows/Fonts/msyh.ttc",    # 微软雅黑
        "C:/Windows/Fonts/simhei.ttf",  # 黑体
        "C:/Windows/Fonts/simsun.ttc"   # 宋体
    ]
    font = None
    for path in font_paths:
        if os.path.exists(path):
            font = pygame.font.Font(path, 20)
            break
    if not font:
        font = pygame.font.Font(None, 20)
    
    # 实际显示的窗口
    screen = pygame.display.set_mode((config.WIDTH, config.HEIGHT), pygame.NOFRAME)
    pygame.display.set_caption("Stream-Mascot")
    set_window_transparent()

    # 离屏画布 (固定基础大小 600x400)
    canvas = pygame.Surface((BASE_WIDTH, BASE_HEIGHT))

    char_image = load_custom_character(CHARACTER_PATH)
    mic_stream = start_mic()
    start_listeners()

    is_dragging = False
    drag_start_global = (0, 0)
    window_start_pos = (0, 0)
    
    next_blink = time.time() + random.uniform(2, 5)
    blink_until = 0.0
    current_hand_x, current_hand_y = 115, 297
    is_talking, last_talk_time, mouth_open = False, 0.0, False
    
    current_expression = "normal"
    expression_end_time = 0.0
    particle_sys = ParticleSystem()
    active_menu = None
    
    is_click_through = False
    toggle_click_through_flag = False

    # ======== 语音关键词映射 ========
    EMOTION_KEYWORDS = {
        "heart": ["谢谢", "哇", "爱你", "喜欢", "么么哒", "牛逼"],
        "angry": ["靠", "无语", "生气", "烦", "傻逼", "操", "滚"],
        "cry": ["呜呜", "哭", "委屈", "可怜", "难过"],
        "surprised": ["卧槽", "居然", "竟然", "妈呀", "真的假的"],
        "speechless": ["服了", "醉了", "搞笑", "离谱"]
    }

    def on_speech_recognized(text):
        nonlocal current_expression, expression_end_time
        text = text.replace(" ", "")
        
        for emotion, keywords in EMOTION_KEYWORDS.items():
            for kw in keywords:
                if kw in text:
                    current_expression = emotion
                    expression_end_time = time.time() + 3.0
                    
                    if emotion == "heart":
                        particle_sys.emit(300, 100, count=15, color=(255, 100, 150), ptype="heart")
                    elif emotion == "angry":
                        particle_sys.emit(300, 100, count=5, color=(255, 50, 50), ptype="star")
                    elif emotion == "cry":
                        particle_sys.emit(300, 100, count=8, color=(100, 200, 255), ptype="star")
                    break

    stt = SpeechRecognizer(callback=on_speech_recognized)

    def on_hotkey_press(key):
        nonlocal toggle_click_through_flag
        if key == keyboard.Key.f8:
            toggle_click_through_flag = True

    hotkey_listener = keyboard.Listener(on_press=on_hotkey_press)
    hotkey_listener.daemon = True
    hotkey_listener.start()

    clock = pygame.time.Clock()
    running = True

    while running:
        wx, wy = get_window_pos()
        cur_x, cur_y = win32api.GetCursorPos()
        
        # 获取当前的缩放比例
        current_scale = config.SCALE
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # 【核心】将鼠标事件坐标映射回 600x400 的逻辑画布坐标
                logical_pos = (event.pos[0] / current_scale, event.pos[1] / current_scale)
                
                if event.button == 3 and not is_click_through: # 右键
                    if active_menu:
                        active_menu = None
                    else:
                        mx = min(logical_pos[0], BASE_WIDTH - 120)
                        my = min(logical_pos[1], BASE_HEIGHT - 200)
                        # 扩展右键菜单：增加缩放选项
                        options = [
                            ("比个心", "heart"), ("生气了", "angry"), ("恢复原状", "normal"),
                            ("缩放 0.8x", "scale_0.8"), ("缩放 1.0x", "scale_1.0"), ("缩放 1.5x", "scale_1.5")
                        ]
                        active_menu = ContextMenu(mx, my, options)
                        
                elif event.button == 1: # 左键
                    if active_menu:
                        action = active_menu.check_click(logical_pos)
                        if action:
                            if action.startswith("scale_"):
                                # 动态调整缩放
                                new_scale = float(action.split("_")[1])
                                config.SCALE = new_scale
                                config.WIDTH = int(BASE_WIDTH * new_scale)
                                config.HEIGHT = int(BASE_HEIGHT * new_scale)
                                # 重建窗口并应用透明
                                screen = pygame.display.set_mode((config.WIDTH, config.HEIGHT), pygame.NOFRAME)
                                set_window_transparent()
                            else:
                                # 表情
                                current_expression = action
                                if action == "heart":
                                    particle_sys.emit(300, 100, count=15, color=(255, 100, 150), ptype="heart")
                                    expression_end_time = time.time() + 3.0
                                elif action == "angry":
                                    expression_end_time = time.time() + 3.0
                                else:
                                    expression_end_time = 0
                        active_menu = None
                    else:
                        if not is_click_through:
                            is_dragging = True
                            drag_start_global = win32api.GetCursorPos()
                            window_start_pos = get_window_pos()
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    is_dragging = False
            elif event.type == pygame.MOUSEMOTION:
                if active_menu:
                    logical_pos = (event.pos[0] / current_scale, event.pos[1] / current_scale)
                    active_menu.update_hover(logical_pos)

        if toggle_click_through_flag:
            toggle_click_through_flag = False
            is_click_through = not is_click_through
            set_click_through(is_click_through)
            print(f"\n[状态切换] 鼠标穿透: {'开启' if is_click_through else '关闭'}")
            if is_click_through:
                active_menu = None

        if is_dragging and not is_click_through:
            dx = cur_x - drag_start_global[0]
            dy = cur_y - drag_start_global[1]
            move_window(window_start_pos[0] + dx, window_start_pos[1] + dy)

        # --- 鼠标追踪 (逻辑坐标) ---
        screen_w = win32api.GetSystemMetrics(0)
        screen_h = win32api.GetSystemMetrics(1)
        pct_x = (cur_x / screen_w) - 0.5
        pct_y = (cur_y / screen_h) - 0.5
        target_mx = 115 - (pct_x * 120)
        target_my = 297 - (pct_y * 55)
        target_mx = max(55, min(175, target_mx))
        target_my = max(270, min(325, target_my))
        current_hand_x += (target_mx - current_hand_x) * 0.2
        current_hand_y += (target_my - current_hand_y) * 0.2

        # --- 时间与表情逻辑 ---
        now = time.time()
        if current_expression != "normal" and now > expression_end_time:
            current_expression = "normal"

        if now > next_blink:
            blink_until = now + 0.15
            next_blink = now + random.uniform(2, 5)
        is_blinking = now < blink_until

        # --- 麦克风逻辑 ---
        if MIC_ENABLED:
            if get_volume() > CFG["mic"]["threshold"]:
                is_talking = True
                last_talk_time = now
            if now - last_talk_time < CFG["mic"]["release_time"]:
                is_talking = True
                mouth_open = (int(now * CFG["mic"]["mouth_speed"]) % 2 == 0)
            else:
                is_talking = False
                mouth_open = False

        # --- 外设状态 ---
        is_typing, is_clicking = get_input_state()
        active_chars = get_active_chars()
        
        if is_typing and random.random() < 0.1:
            particle_sys.emit(450, 300, count=1, color=(100, 200, 255), ptype="star")

        # ======== 渲染到逻辑画布 ========
        canvas.fill((255, 0, 255))

        draw_background_and_cat(canvas, is_blinking, is_talking, mouth_open, char_image, current_expression)
        draw_mouse_hand(canvas, current_hand_x, current_hand_y, is_clicking)
        draw_keyboard_hand(canvas, is_typing, active_chars, font)
        particle_sys.update_and_draw(canvas)
        
        if active_menu:
            active_menu.draw(canvas, font)

        # ======== 动态缩放并处理边缘杂色 ========
        if config.SCALE != 1.0:
            # 1. 平滑缩放
            scaled_canvas = pygame.transform.smoothscale(canvas, (config.WIDTH, config.HEIGHT))
            # 2. 强制清理半透明产生的粉边
            remove_scale_artifacts(scaled_canvas)
            screen.blit(scaled_canvas, (0, 0))
        else:
            screen.blit(canvas, (0, 0))

        pygame.display.flip()
        clock.tick(FPS)

    stop_listeners()
    stop_mic(mic_stream)
    hotkey_listener.stop()
    stt.stop()
    pygame.quit()

if __name__ == "__main__":
    main()
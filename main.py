import ctypes
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception: pass

import time
import random
import win32api
import pygame
import os
import sys
import numpy as np
import threading
import config
from pynput import keyboard

from config import BASE_WIDTH, BASE_HEIGHT, SCALE, FPS, CFG
from window_utils import set_window_transparent, move_window, get_window_pos, set_click_through
from input_utils import start_listeners, stop_listeners, get_active_chars, get_input_state
from audio_utils import start_mic, stop_mic, get_volume, MIC_ENABLED
from renderer import load_image_by_path, draw_background_and_cat, draw_mouse_hand, draw_keyboard_hand
from effects import ParticleSystem, ContextMenu
from stt_utils import SpeechRecognizer
from settings_ui import SettingsWindow

def remove_scale_artifacts(surface):
    arr = pygame.surfarray.pixels3d(surface)
    mask = (arr[:, :, 0] > 180) & (arr[:, :, 2] > 180) & (arr[:, :, 1] < 100)
    arr[mask] = [255, 0, 255]
    del arr

def main():
    global reload_requested
    reload_requested = False
    
    # --- 软重载触发函数，仅修改标志位 ---
    def trigger_reload():
        global reload_requested
        reload_requested = True

    pygame.init()
    pygame.font.init()
    
    font_paths = ["C:/Windows/Fonts/msyh.ttc", "C:/Windows/Fonts/simhei.ttf", "C:/Windows/Fonts/simsun.ttc"]
    font = None
    for path in font_paths:
        if os.path.exists(path):
            font = pygame.font.Font(path, 20)
            break
    if not font: font = pygame.font.Font(None, 20)
    
    screen = pygame.display.set_mode((config.WIDTH, config.HEIGHT), pygame.NOFRAME)
    pygame.display.set_caption("Stream-Mascot")
    set_window_transparent()
    canvas = pygame.Surface((BASE_WIDTH, BASE_HEIGHT))

    # --- 封装资源加载逻辑，方便软重载 ---
    char_images = {}
    show_code_face = True
    stt = None
    mic_stream = None

    def load_assets_and_services():
        nonlocal char_images, show_code_face, stt, mic_stream
        
        # 1. 重新读取配置文件
        config.CFG = config.load_config()
        active_name = config.CFG["active_profile"]
        active_profile = config.CFG["profiles"].get(active_name, config.CFG["profiles"]["默认白猫"])
        
        # 2. 重新加载角色图片
        char_images = {}
        show_code_face = active_profile.get("show_code_face", True)
        if active_profile.get("character_path"):
            img = load_image_by_path(active_profile["character_path"])
            if img: char_images["normal"] = img
            
        for exp_name, path in active_profile.get("expressions", {}).items():
            if path:
                img = load_image_by_path(path)
                if img: char_images[exp_name] = img
                
        # 3. 重启语音识别（先停旧的，再起新的以应用新词库）
        if stt:
            stt.stop()
            
        def on_speech_recognized(text):
            text = text.replace(" ", "")
            keywords_dict = active_profile.get("keywords", {})
            for emotion, keywords in keywords_dict.items():
                for kw in keywords:
                    if kw in text:
                        trigger_expression(emotion)
                        break
        stt = SpeechRecognizer(callback=on_speech_recognized)

    def trigger_expression(emotion):
        nonlocal current_expression, expression_end_time
        current_expression = emotion
        
        if emotion == "heart":
            particle_sys.emit(300, 100, count=15, color=(255, 100, 150), ptype="heart")
            expression_end_time = time.time() + 3.0
        elif emotion == "angry":
            particle_sys.emit(300, 100, count=5, color=(255, 50, 50), ptype="star")
            expression_end_time = time.time() + 3.0
        elif emotion == "cry":
            particle_sys.emit(300, 100, count=8, color=(100, 200, 255), ptype="star")
            expression_end_time = time.time() + 3.0
        elif emotion in ["surprised", "speechless"]:
            expression_end_time = time.time() + 3.0
        else:
            expression_end_time = 0

    def open_settings():
        nonlocal active_menu
        active_menu = None
        def run_ui():
            app = SettingsWindow(on_save_callback=trigger_reload, on_interact_callback=trigger_expression)
            app.show()
        threading.Thread(target=run_ui, daemon=True).start()

    # 初始化加载一次
    mic_stream = start_mic()
    start_listeners()
    load_assets_and_services()

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
        # ======== 处理软重载 ========
        if reload_requested:
            reload_requested = False
            print("\n[系统] 正在执行软重载...")
            
            # 1. 重载资源与服务
            load_assets_and_services()
            
            # 2. 重新适配窗口大小 (用户可能修改了缩放)
            new_w = int(BASE_WIDTH * config.CFG["global"]["scale"])
            new_h = int(BASE_HEIGHT * config.CFG["global"]["scale"])
            if new_w != config.WIDTH or new_h != config.HEIGHT:
                config.WIDTH, config.HEIGHT = new_w, new_h
                config.SCALE = config.CFG["global"]["scale"]
                screen = pygame.display.set_mode((new_w, new_h), pygame.NOFRAME)
                set_window_transparent()
                
            print("[系统] 软重载完成！")

        wx, wy = get_window_pos()
        cur_x, cur_y = win32api.GetCursorPos()
        current_scale = config.CFG["global"]["scale"]
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                logical_pos = (event.pos[0] / current_scale, event.pos[1] / current_scale)
                if event.button == 3 and not is_click_through:
                    if active_menu: active_menu = None
                    else:
                        mx = min(logical_pos[0], BASE_WIDTH - 150)
                        my = min(logical_pos[1], BASE_HEIGHT - 150)
                        options = [("设置与互动", "settings"), ("重新加载桌宠", "reload"), ("退出程序", "quit")]
                        active_menu = ContextMenu(mx, my, options, font)
                elif event.button == 1:
                    if active_menu:
                        action = active_menu.check_click(logical_pos)
                        if action:
                            if action == "settings": open_settings()
                            elif action == "reload": trigger_reload()
                            elif action == "quit": running = False
                        active_menu = None
                    else:
                        if not is_click_through:
                            is_dragging = True
                            drag_start_global = win32api.GetCursorPos()
                            window_start_pos = get_window_pos()
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1: is_dragging = False
            elif event.type == pygame.MOUSEMOTION:
                if active_menu:
                    logical_pos = (event.pos[0] / current_scale, event.pos[1] / current_scale)
                    active_menu.update_hover(logical_pos)

        if toggle_click_through_flag:
            toggle_click_through_flag = False
            is_click_through = not is_click_through
            set_click_through(is_click_through)
            if is_click_through: active_menu = None

        if is_dragging and not is_click_through:
            dx = cur_x - drag_start_global[0]
            dy = cur_y - drag_start_global[1]
            move_window(window_start_pos[0] + dx, window_start_pos[1] + dy)

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

        now = time.time()
        if current_expression != "normal" and now > expression_end_time:
            current_expression = "normal"

        if now > next_blink:
            blink_until = now + 0.15
            next_blink = now + random.uniform(2, 5)
        is_blinking = now < blink_until

        if MIC_ENABLED:
            if get_volume() > config.CFG["global"]["mic"]["threshold"]:
                is_talking = True
                last_talk_time = now
            if now - last_talk_time < config.CFG["global"]["mic"]["release_time"]:
                is_talking = True
                mouth_open = (int(now * config.CFG["global"]["mic"]["mouth_speed"]) % 2 == 0)
            else:
                is_talking = False
                mouth_open = False

        is_typing, is_clicking = get_input_state()
        active_chars = get_active_chars()
        
        if is_typing and random.random() < 0.1:
            particle_sys.emit(450, 300, count=1, color=(100, 200, 255), ptype="star")

        canvas.fill((255, 0, 255))
        draw_background_and_cat(canvas, is_blinking, is_talking, is_typing, mouth_open, char_images, show_code_face, current_expression)
        draw_mouse_hand(canvas, current_hand_x, current_hand_y, is_clicking)
        draw_keyboard_hand(canvas, is_typing, active_chars, font)
        particle_sys.update_and_draw(canvas)
        
        if active_menu:
            active_menu.draw(canvas, font)

        if current_scale != 1.0:
            scaled_canvas = pygame.transform.smoothscale(canvas, (config.WIDTH, config.HEIGHT))
            remove_scale_artifacts(scaled_canvas)
            screen.blit(scaled_canvas, (0, 0))
        else:
            screen.blit(canvas, (0, 0))

        pygame.display.flip()
        clock.tick(FPS)

    stop_listeners()
    stop_mic(mic_stream)
    hotkey_listener.stop()
    if stt: stt.stop()
    pygame.quit()

if __name__ == "__main__":
    main()
import time
import random
import win32api
import pygame
from pynput import keyboard

from config import (
    BASE_WIDTH, BASE_HEIGHT, WIDTH, HEIGHT, SCALE, FPS, 
    CHARACTER_PATH, CFG
)
from window_utils import set_window_transparent, move_window, get_window_pos, set_click_through
from input_utils import start_listeners, stop_listeners, get_active_chars, get_input_state
from audio_utils import start_mic, stop_mic, get_volume, MIC_ENABLED
from renderer import load_custom_character, draw_background_and_cat, draw_mouse_hand, draw_keyboard_hand

def main():
    global next_blink, blink_until, current_hand_x, current_hand_y, is_talking, last_talk_time
    
    pygame.init()
    pygame.font.init()
    font = pygame.font.Font(None, 20) 
    
    # 真实窗口
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.NOFRAME)
    pygame.display.set_caption("Stream-Mascot")
    set_window_transparent()

    # 逻辑画布 (永远保持 600x400)
    canvas = pygame.Surface((BASE_WIDTH, BASE_HEIGHT))

    char_image = load_custom_character(CHARACTER_PATH)
    mic_stream = start_mic()
    start_listeners()

    # 内部状态变量
    is_dragging = False
    drag_start_global = (0, 0)
    window_start_pos = (0, 0)
    
    next_blink = time.time() + random.uniform(2, 5)
    blink_until = 0.0
    
    current_hand_x = 115
    current_hand_y = 297
    
    is_talking = False
    last_talk_time = 0.0
    mouth_open = False
    mic_threshold = CFG["mic"]["threshold"]
    mic_release = CFG["mic"]["release_time"]
    mic_speed = CFG["mic"].get("mouth_speed", 10) 

    # 鼠标穿透状态
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
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and not is_click_through:
                    is_dragging = True
                    drag_start_global = win32api.GetCursorPos()
                    window_start_pos = get_window_pos()
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    is_dragging = False

        if toggle_click_through_flag:
            toggle_click_through_flag = False
            is_click_through = not is_click_through
            set_click_through(is_click_through)
            print(f"\n[状态切换] 鼠标穿透: {'开启 (不挡操作)' if is_click_through else '关闭 (可拖拽)'}")

        if is_dragging and not is_click_through:
            cur_x, cur_y = win32api.GetCursorPos()
            dx = cur_x - drag_start_global[0]
            dy = cur_y - drag_start_global[1]
            move_window(window_start_pos[0] + dx, window_start_pos[1] + dy)

        # --- 鼠标追踪 ---
        cur_x, cur_y = win32api.GetCursorPos()
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

        # --- 眨眼逻辑 ---
        now = time.time()
        if now > next_blink:
            blink_until = now + 0.15
            next_blink = now + random.uniform(2, 5)
        is_blinking = now < blink_until

        # --- 麦克风逻辑 ---
        if MIC_ENABLED:
            if get_volume() > mic_threshold:
                is_talking = True
                last_talk_time = now
            
            if now - last_talk_time < mic_release:
                is_talking = True
                mouth_open = (int(now * mic_speed) % 2 == 0)
            else:
                is_talking = False
                mouth_open = False
        else:
            is_talking = False
            mouth_open = False

        # --- 获取外设状态 ---
        is_typing, is_clicking = get_input_state()
        active_chars = get_active_chars()

        # --- 渲染到逻辑画布 Canvas ---
        canvas.fill((255, 0, 255)) # 品红色背景

        draw_background_and_cat(canvas, is_blinking, is_talking, mouth_open, char_image)
        draw_mouse_hand(canvas, current_hand_x, current_hand_y, is_clicking)
        draw_keyboard_hand(canvas, is_typing, active_chars, font)

        # --- 缩放到真实屏幕 Screen ---
        if SCALE != 1.0:
            # 如果设置了缩放，平滑放大并贴到屏幕
            scaled_canvas = pygame.transform.smoothscale(canvas, (WIDTH, HEIGHT))
            screen.blit(scaled_canvas, (0, 0))
        else:
            # 原尺寸直接贴图
            screen.blit(canvas, (0, 0))

        pygame.display.flip()
        clock.tick(FPS)

    # 清理
    stop_listeners()
    stop_mic(mic_stream)
    hotkey_listener.stop()
    pygame.quit()

if __name__ == "__main__":
    main()
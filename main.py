import time
import random
import win32api
import pygame

from config import WIDTH, HEIGHT, FPS, CHARACTER_PATH, CFG
from window_utils import set_window_transparent, move_window, get_window_pos
from input_utils import start_listeners, stop_listeners, get_active_chars, get_input_state
from audio_utils import start_mic, stop_mic, get_volume, MIC_ENABLED
from renderer import load_custom_character, draw_background_and_cat, draw_mouse_hand, draw_keyboard_hand

def main():
    global next_blink, blink_until, current_hand_x, current_hand_y, is_talking, last_talk_time
    
    pygame.init()
    pygame.font.init()
    font = pygame.font.Font(None, 20) 
    
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.NOFRAME)
    pygame.display.set_caption("Stream-Mascot")
    set_window_transparent()

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
    mic_threshold = CFG["mic"]["threshold"]
    mic_release = CFG["mic"]["release_time"]

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

        # 拖拽处理
        if is_dragging:
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

        # 平滑缓动
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
            elif now - last_talk_time > mic_release:
                is_talking = False

        # --- 获取外设状态 ---
        is_typing, is_clicking = get_input_state()
        active_chars = get_active_chars()

        # --- 渲染 ---
        screen.fill(CFG["colors"]["bg"])

        draw_background_and_cat(screen, is_blinking, is_talking, char_image)
        draw_mouse_hand(screen, current_hand_x, current_hand_y, is_clicking)
        draw_keyboard_hand(screen, is_typing, active_chars, font)

        pygame.display.flip()
        clock.tick(FPS)

    # 清理
    stop_listeners()
    stop_mic(mic_stream)
    pygame.quit()

if __name__ == "__main__":
    main()
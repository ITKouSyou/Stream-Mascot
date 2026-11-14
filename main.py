import time
import random
import win32api
import pygame
import os
from pynput import keyboard

from config import WIDTH, HEIGHT, FPS, CHARACTER_PATH, CFG
from window_utils import set_window_transparent, move_window, get_window_pos, set_click_through
from input_utils import start_listeners, stop_listeners, get_active_chars, get_input_state
from audio_utils import start_mic, stop_mic, get_volume, MIC_ENABLED
from renderer import load_custom_character, draw_background_and_cat, draw_mouse_hand, draw_keyboard_hand
# 导入新加的模块
from effects import ParticleSystem, ContextMenu

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
        # 如果都没找到，退回默认英文字体（中文会变方块）
        font = pygame.font.Font(None, 20)
    
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.NOFRAME)
    pygame.display.set_caption("Stream-Mascot")
    set_window_transparent()

    char_image = load_custom_character(CHARACTER_PATH)
    mic_stream = start_mic()
    start_listeners()

    # ... (状态变量保持不变) ...
    is_dragging = False
    drag_start_global = (0, 0)
    window_start_pos = (0, 0)
    
    next_blink = time.time() + random.uniform(2, 5)
    blink_until = 0.0
    current_hand_x, current_hand_y = 115, 297
    is_talking, last_talk_time, mouth_open = False, 0.0, False
    
    # 新增：表情与特效状态
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
        # 获取鼠标在窗口内的相对坐标 (用于菜单)
        wx, wy = get_window_pos()
        cur_x, cur_y = win32api.GetCursorPos()
        rel_mouse = (cur_x - wx, cur_y - wy)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            
            # 右键菜单触发
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 3 and not is_click_through: # 3 是右键
                    if active_menu:
                        active_menu = None # 再次右键关闭
                    else:
                        # 弹出菜单，限制在窗口边界内
                        mx, my = event.pos
                        mx = min(mx, WIDTH - 100)
                        my = min(my, HEIGHT - 80)
                        options = [("比个心", "heart"), ("生气了", "angry"), ("恢复原状", "normal")]
                        active_menu = ContextMenu(mx, my, options)
                elif event.button == 1:
                    if active_menu:
                        action = active_menu.check_click(event.pos)
                        if action:
                            current_expression = action
                            if action == "heart":
                                # 触发爱心粒子
                                particle_sys.emit(300, 100, count=15, color=(255, 100, 150), ptype="heart")
                                expression_end_time = time.time() + 3.0
                            elif action == "angry":
                                expression_end_time = time.time() + 3.0
                            else:
                                expression_end_time = 0
                        active_menu = None
                    else:
                        # 正常拖拽逻辑
                        if not is_click_through:
                            is_dragging = True
                            drag_start_global = win32api.GetCursorPos()
                            window_start_pos = get_window_pos()
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    is_dragging = False
            elif event.type == pygame.MOUSEMOTION:
                if active_menu:
                    active_menu.update_hover(event.pos)

        if toggle_click_through_flag:
            toggle_click_through_flag = False
            is_click_through = not is_click_through
            set_click_through(is_click_through)
            print(f"\n[状态切换] 鼠标穿透: {'开启' if is_click_through else '关闭'}")
            if is_click_through:
                active_menu = None # 穿透时关闭菜单

        if is_dragging and not is_click_through:
            cur_x, cur_y = win32api.GetCursorPos()
            dx = cur_x - drag_start_global[0]
            dy = cur_y - drag_start_global[1]
            move_window(window_start_pos[0] + dx, window_start_pos[1] + dy)

        # --- 鼠标追踪 ---
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
            current_expression = "normal" # 表情倒计时结束恢复

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
        
        # 打字时偶尔冒星星
        if is_typing and random.random() < 0.1:
            particle_sys.emit(450, 300, count=1, color=(100, 200, 255), ptype="star")

        # ======== 渲染 ========
        screen.fill((255, 0, 255)) # 品红透明背景

        # 1. 猫和桌面 (传入 current_expression)
        draw_background_and_cat(screen, is_blinking, is_talking, mouth_open, char_image, current_expression)
        
        # 2. 鼠标和键盘手
        draw_mouse_hand(screen, current_hand_x, current_hand_y, is_clicking)
        draw_keyboard_hand(screen, is_typing, active_chars, font)
        
        # 3. 粒子系统更新与渲染 (在最上层)
        particle_sys.update_and_draw(screen)
        
        # 4. 右键菜单 (在最最上层)
        if active_menu:
            active_menu.draw(screen, font)

        pygame.display.flip()
        clock.tick(FPS)

    stop_listeners()
    stop_mic(mic_stream)
    hotkey_listener.stop()
    pygame.quit()

if __name__ == "__main__":
    main()
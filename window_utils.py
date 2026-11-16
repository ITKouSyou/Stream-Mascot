import sys
import win32api
import win32gui
import win32con
import pygame
import config

def get_hwnd():
    return pygame.display.get_wm_info()["window"]

def get_topmost_flag():
    """根据配置动态返回置顶或非置顶标志"""
    always_on_top = config.CFG["global"].get("always_on_top", True)
    return win32con.HWND_TOPMOST if always_on_top else win32con.HWND_NOTOPMOST

def set_window_transparent():
    if sys.platform != "win32":
        return
    hwnd = get_hwnd()
    ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
    win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, ex_style | win32con.WS_EX_LAYERED)
    
    # 动态应用置顶/非置顶
    topmost_flag = get_topmost_flag()
    win32gui.SetWindowPos(hwnd, topmost_flag, 0, 0, config.WIDTH, config.HEIGHT, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
    win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(255, 0, 255), 0, win32con.LWA_COLORKEY)

def set_click_through(enable):
    if sys.platform != "win32":
        return
    hwnd = get_hwnd()
    ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
    if enable:
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, ex_style | win32con.WS_EX_TRANSPARENT)
    else:
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, ex_style & ~win32con.WS_EX_TRANSPARENT)

def move_window(x, y):
    if sys.platform != "win32":
        return
    hwnd = get_hwnd()
    # 拖拽时也应用置顶/非置顶状态
    topmost_flag = get_topmost_flag()
    win32gui.SetWindowPos(hwnd, topmost_flag, x, y, 0, 0, win32con.SWP_NOSIZE | win32con.SWP_SHOWWINDOW)

def get_window_pos():
    if sys.platform != "win32":
        return 0, 0
    hwnd = get_hwnd()
    rect = win32gui.GetWindowRect(hwnd)
    return rect[0], rect[1]
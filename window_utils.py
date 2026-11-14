import sys
import win32api
import win32gui
import win32con
import pygame
from config import WIDTH, HEIGHT

def get_hwnd():
    return pygame.display.get_wm_info()["window"]

def set_window_transparent():
    if sys.platform != "win32":
        return
    hwnd = get_hwnd()
    ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
    win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, ex_style | win32con.WS_EX_LAYERED)
    win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, WIDTH, HEIGHT, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
    # 使用品红 (255, 0, 255) 作为抠图透明色
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
    win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, x, y, 0, 0, win32con.SWP_NOSIZE | win32con.SWP_SHOWWINDOW)

def get_window_pos():
    if sys.platform != "win32":
        return 0, 0
    hwnd = get_hwnd()
    rect = win32gui.GetWindowRect(hwnd)
    return rect[0], rect[1]
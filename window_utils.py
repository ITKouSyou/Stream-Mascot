import sys
import win32api
import win32gui
import win32con
import pygame
from config import WIDTH, HEIGHT, COLOR_BG

def get_hwnd():
    return pygame.display.get_wm_info()["window"]

def set_window_transparent():
    if sys.platform != "win32":
        return
    hwnd = get_hwnd()
    ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
    win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, ex_style | win32con.WS_EX_LAYERED)
    win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, WIDTH, HEIGHT, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
    win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(*COLOR_BG), 0, win32con.LWA_COLORKEY)

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
import threading
import pystray
from PIL import Image, ImageDraw

class TrayManager:
    def __init__(self, on_settings, on_reload, on_quit, on_toggle_click_through):
        self.on_settings = on_settings
        self.on_reload = on_reload
        self.on_quit = on_quit
        self.on_toggle_click_through = on_toggle_click_through
        
        self.icon_image = self._create_icon()
        self.icon = None
        self.thread = None

    def _create_icon(self):
        img = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        d.ellipse([4, 12, 60, 60], fill=(255, 255, 255, 255), outline=(0, 0, 0, 255), width=3)
        d.polygon([(10, 20), (20, 0), (30, 20)], fill=(255, 255, 255, 255), outline=(0, 0, 0, 255))
        d.polygon([(34, 20), (44, 0), (54, 20)], fill=(255, 255, 255, 255), outline=(0, 0, 0, 255))
        d.ellipse([20, 30, 26, 36], fill=(0, 0, 0, 255))
        d.ellipse([38, 30, 44, 36], fill=(0, 0, 0, 255))
        return img

    def _setup_menu(self):
        menu = pystray.Menu(
            pystray.MenuItem('显示/打开设置', lambda: self.on_settings()),
            pystray.MenuItem('开启/关闭鼠标穿透', lambda: self.on_toggle_click_through()),
            pystray.MenuItem('重新加载桌宠', lambda: self.on_reload()),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem('彻底退出程序', lambda: self.on_quit())
        )
        return menu

    def start(self):
        self.icon = pystray.Icon("StreamMascot", self.icon_image, "Stream-Mascot", self._setup_menu())
        self.thread = threading.Thread(target=self.icon.run, daemon=True)
        self.thread.start()

    def stop(self):
        if self.icon:
            self.icon.stop()
import os
import json

CONFIG_FILE = "config.json"

DEFAULT_CONFIG = {
    "width": 600, "height": 400, "fps": 60,
    "character_path": "", "character_width": 180,
    "mic": {
        "enabled": True,
        "threshold": 0.04,
        "release_time": 0.15
    },
    "colors": {
        "bg": [0, 0, 0], "desk": [245, 245, 245], "cat": [255, 255, 255],
        "outline": [15, 15, 15], "paw": [255, 160, 170],
        "mousepad": [180, 180, 180], "mouse": [60, 60, 65], "mouse_hl": [255, 80, 80],
        "key_base": [45, 45, 50], "key": [75, 75, 80], "key_hl": [100, 200, 255]
    }
}

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                user_cfg = json.load(f)
                cfg = {**DEFAULT_CONFIG, **user_cfg}
                cfg["colors"] = {**DEFAULT_CONFIG["colors"], **user_cfg.get("colors", {})}
                cfg["mic"] = {**DEFAULT_CONFIG["mic"], **user_cfg.get("mic", {})}
                return cfg
        except Exception as e:
            print(f"读取配置文件失败: {e}，将使用默认配置。")
    else:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_CONFIG, f, indent=2, ensure_ascii=False)
        print(f"已生成默认配置文件 {CONFIG_FILE}")
    return DEFAULT_CONFIG

CFG = load_config()

WIDTH = CFG["width"]
HEIGHT = CFG["height"]
FPS = CFG["fps"]
CHARACTER_PATH = CFG["character_path"]
CHARACTER_WIDTH = CFG["character_width"]

COLOR_BG = tuple(CFG["colors"]["bg"])
COLOR_DESK = tuple(CFG["colors"]["desk"])
COLOR_CAT = tuple(CFG["colors"]["cat"])
COLOR_OUTLINE = tuple(CFG["colors"]["outline"])
COLOR_PAW = tuple(CFG["colors"]["paw"])

COLOR_MOUSEPAD = tuple(CFG["colors"]["mousepad"])
COLOR_MOUSE = tuple(CFG["colors"]["mouse"])
COLOR_MOUSE_HL = tuple(CFG["colors"]["mouse_hl"])

COLOR_KEY_BASE = tuple(CFG["colors"]["key_base"])
COLOR_KEY = tuple(CFG["colors"]["key"])
COLOR_KEY_HL = tuple(CFG["colors"]["key_hl"])
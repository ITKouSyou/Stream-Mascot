import os
import json
import copy

__version__ = "1.4.0"
CONFIG_FILE = "config.json"
CUSTOM_DIR = "custom_assets"

if not os.path.exists(CUSTOM_DIR):
    os.makedirs(CUSTOM_DIR)

DEFAULT_PROFILE = {
    "name": "默认白猫",
    "character_path": "",
    "show_code_face": True,
    "expressions": {
        "normal": "", "heart": "", "angry": "", "cry": "", "surprised": "", "speechless": ""
    },
    "keywords": {
        "heart": ["谢谢", "哇", "爱你", "喜欢", "么么哒", "牛逼"],
        "angry": ["靠", "无语", "生气", "烦", "傻逼", "操", "滚"],
        "cry": ["呜呜", "哭", "委屈", "可怜", "难过"],
        "surprised": ["卧槽", "居然", "竟然", "妈呀", "真的假的"],
        "speechless": ["服了", "醉了", "搞笑", "离谱"]
    }
}

DEFAULT_CONFIG = {
    "active_profile": "默认白猫",
    "profiles": {
        "默认白猫": DEFAULT_PROFILE
    },
    "global": {
        "scale": 1.0, 
        "fps": 60,
        "always_on_top": True,
        "singing_sensitivity": 50.0,
        "performance_mode": False,
        "bilibili_room_id": "", # 【新增】B站直播间房间号
        "mic": {
            "enabled": True,
            "device_id": -1,
            "denoise": True,
            "threshold": 0.15,
            "release_time": 0.2,
            "mouth_speed": 10
        },
        "colors": {
            "bg": [255, 0, 255], "desk": [245, 245, 245], "cat": [255, 255, 255],
            "outline": [15, 15, 15], "paw": [255, 160, 170],
            "mousepad": [180, 180, 180], "mouse": [60, 60, 65], "mouse_hl": [255, 80, 80],
            "key_base": [45, 45, 50], "key": [75, 75, 80], "key_hl": [100, 200, 255]
        }
    }
}

def deep_merge(default, user):
    if not isinstance(user, dict) or not isinstance(default, dict):
        return user if user is not None else default
    result = copy.deepcopy(default)
    for k, v in user.items():
        if k in result and isinstance(result[k], dict) and isinstance(v, dict):
            result[k] = deep_merge(result[k], v)
        else:
            result[k] = v
    return result

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                user_cfg = json.load(f)
            cfg = deep_merge(DEFAULT_CONFIG, user_cfg)
            return cfg
        except Exception as e:
            print(f"⚠️ 配置文件损坏 ({e})，将使用默认配置并备份旧文件。")
            try:
                os.rename(CONFIG_FILE, CONFIG_FILE + ".bak")
            except: pass
            return copy.deepcopy(DEFAULT_CONFIG)
    else:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_CONFIG, f, indent=2, ensure_ascii=False)
    return copy.deepcopy(DEFAULT_CONFIG)

CFG = load_config()

BASE_WIDTH = 600
BASE_HEIGHT = 400
SCALE = CFG["global"].get("scale", 1.0)
WIDTH = int(BASE_WIDTH * SCALE)
HEIGHT = int(BASE_HEIGHT * SCALE)
FPS = CFG["global"]["fps"]

COLOR_BG = tuple(CFG["global"]["colors"]["bg"])
COLOR_DESK = tuple(CFG["global"]["colors"]["desk"])
COLOR_CAT = tuple(CFG["global"]["colors"]["cat"])
COLOR_OUTLINE = tuple(CFG["global"]["colors"]["outline"])
COLOR_PAW = tuple(CFG["global"]["colors"]["paw"])
COLOR_MOUSEPAD = tuple(CFG["global"]["colors"]["mousepad"])
COLOR_MOUSE = tuple(CFG["global"]["colors"]["mouse"])
COLOR_MOUSE_HL = tuple(CFG["global"]["colors"]["mouse_hl"])
COLOR_KEY_BASE = tuple(CFG["global"]["colors"]["key_base"])
COLOR_KEY = tuple(CFG["global"]["colors"]["key"])
COLOR_KEY_HL = tuple(CFG["global"]["colors"]["key_hl"])

def save_config(cfg):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)
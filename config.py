import os
import json

# 项目版本号
__version__ = "1.0.0"

CONFIG_FILE = "config.json"
CUSTOM_DIR = "custom_assets"

# 确保自定义素材文件夹存在
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
        "always_on_top": True,  # 新增：默认开启窗口置顶
        "mic": {
            "enabled": True,
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

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                user_cfg = json.load(f)
                
            # 兼容旧版配置结构迁移
            if "global" not in user_cfg:
                print("检测到旧版配置文件，正在自动迁移...")
                old_profile = {
                    "name": "默认白猫",
                    "character_path": user_cfg.get("character_path", ""),
                    "show_code_face": user_cfg.get("show_code_face", True),
                    "expressions": {"normal": "", "heart": "", "angry": "", "cry": "", "surprised": "", "speechless": ""},
                    "keywords": user_cfg.get("keywords", DEFAULT_PROFILE["keywords"])
                }
                new_cfg = {
                    "active_profile": "默认白猫",
                    "profiles": {"默认白猫": old_profile},
                    "global": {
                        "scale": user_cfg.get("scale", 1.0),
                        "fps": user_cfg.get("fps", 60),
                        "always_on_top": True,
                        "mic": user_cfg.get("mic", DEFAULT_CONFIG["global"]["mic"]),
                        "colors": user_cfg.get("colors", DEFAULT_CONFIG["global"]["colors"])
                    }
                }
                with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                    json.dump(new_cfg, f, indent=2, ensure_ascii=False)
                return new_cfg
            
            # 兼容某些字段缺失的情况
            if "always_on_top" not in user_cfg["global"]:
                user_cfg["global"]["always_on_top"] = True
                
            return user_cfg
        except Exception as e:
            print(f"读取配置文件失败: {e}，将使用默认配置。")
    else:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_CONFIG, f, indent=2, ensure_ascii=False)
        print(f"已生成默认配置文件 {CONFIG_FILE}")
    return DEFAULT_CONFIG

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
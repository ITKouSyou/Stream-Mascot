# Stream-Mascot (直播桌宠)

一个可以悬浮在桌面、实时响应键鼠和麦克风声音、可自定义外观的二次元桌宠/直播虚拟挂件。

纯 Python + Pygame 实现，**无需任何外部图片素材（开箱即用）**。非常适合在游戏直播、写代码或日常使用电脑时，挂在屏幕角落增加陪伴感。

## ✨ 核心特性

- **全局输入监听**：无视窗口焦点，无论你在玩游戏还是敲代码，桌宠都能精准响应。
- **麦克风语音互动**：实时捕获麦克风音量，当你说话时，桌宠会张嘴互动（自定义图片则会上下跳动）。
- **透明置顶与拖拽**：背景全透明、始终置顶，按住鼠标左键即可无缝拖拽，不挡视线。
- **键盘可视化**：倒置布局的虚拟键盘，敲击真实按键时，对应键帽亮起冰蓝色，猫爪会自动“跳”到按键上方砸下。
- **反向追踪与缓动**：鼠标移动时，鼠标手会反向平滑追踪，速度比例自适应屏幕分辨率，有生动的延迟感。
- **生动细节**：自动随机眨眼、鼠标点击变色、打字敲击抖动、手背/肉垫形态切换。
- **配置分离**：大小、FPS、所有颜色、甚至角色图像，全都在 `config.json` 中一键修改。

## 🚀 快速开始

### 环境要求
- Windows 10/11
- Python 3.9+
- 依赖库：`pygame`, `pynput`, `pywin32`, `sounddevice`, `numpy`

### 安装运行

**1. 克隆或下载本项目到本地：**
```bash
git clone <your-repo-url>
cd Stream-Mascot
```

**2. 创建并激活虚拟环境（推荐）：**

*Windows (PowerShell)：*
```powershell
# 创建虚拟环境
python -m venv .venv
# 激活虚拟环境
.\.venv\Scripts\Activate.ps1
```
*(注：如果提示“禁止运行脚本”，请先以管理员身份运行 `Set-ExecutionPolicy RemoteSigned`，或者改用下方的 CMD 方式)*

*Windows (CMD)：*
```cmd
python -m venv .venv
.\.venv\Scripts\activate.bat
```

*macOS / Linux：*
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**3. 安装依赖：**
```bash
pip install -r requirements.txt
```

**4. 运行程序：**
```bash
python main.py
```
*提示：按 `Esc` 键退出程序。*

## 📁 项目结构

项目已采用模块化拆分，方便后续扩展新功能：

```text
Stream-Mascot/
├── main.py             # 主程序入口，运行主循环
├── config.py           # 配置加载模块
├── window_utils.py     # 窗口操作模块（置顶、透明、拖拽）
├── input_utils.py      # 键盘鼠标全局监听模块
├── audio_utils.py      # 麦克风音量监听模块
├── renderer.py         # 所有的绘制逻辑（猫、手、键盘）
├── config.json         # 运行时配置文件（首次运行自动生成）
├── requirements.txt    # Python 依赖清单
├── README.md           # 项目说明文档
└── .gitignore          # Git 忽略规则
```

## ⚙️ 配置说明 (`config.json`)

程序首次运行会自动生成一份默认的 `config.json`，你可以随时修改并重启程序生效。

```json
{
  "width": 600,
  "height": 400,
  "fps": 60,
  
  "character_path": "",
  "character_width": 180,

  "mic": {
    "enabled": true,
    "threshold": 0.04,
    "release_time": 0.15
  },

  "colors": {
    "bg": [0, 0, 0],
    "desk": [245, 245, 245],
    "cat": [255, 255, 255],
    "outline": [15, 15, 15],
    "paw": [255, 160, 170],
    
    "mousepad": [180, 180, 180],
    "mouse": [60, 60, 65],
    "mouse_hl": [255, 80, 80],
    
    "key_base": [45, 45, 50],
    "key": [75, 75, 80],
    "key_hl": [100, 200, 255]
  }
}
```

| 字段 | 说明 |
|---|---|
| `width` / `height` | 窗口的宽高（默认 600x400） |
| `fps` | 渲染帧率，默认 60 |
| `character_path` | **自定义角色图片**，支持网络链接或本地路径。留空 `""` 则使用默认白猫。 |
| `character_width` | 自定义图片的缩放宽度。 |
| `mic.enabled` | 是否开启麦克风互动（默认为 `true`）。 |
| `mic.threshold` | 麦克风触发张嘴巴的**音量阈值**（数值越小越敏感，建议在 `0.03 - 0.08` 之间微调）。 |
| `mic.release_time` | 停止说话后，嘴巴闭合的**延迟时间**（秒），防止换气时嘴巴抽搐。 |
| `colors` | 所有元素的 RGB 颜色配置。`bg` 必须保持为 `[0, 0, 0]`，因为透明抠图基于此色值。 |

## 📦 打包为独立可执行文件 (.exe)

如果你不想每次都开命令行，可以使用 PyInstaller 将其打包成 exe：

```bash
pip install pyinstaller
pyinstaller -F -w main.py
```

打包完成后，在 `dist` 文件夹中会生成 `main.exe`（你可以手动将它重命名为 `Stream-Mascot.exe`）。
**注意：** 请将 `config.json` 复制到与 `.exe` 同级的目录下，以便修改配置。

## 💡 进阶玩法

- **开机自启**：按 `Win + R` 输入 `shell:startup`，将 `.exe` 的快捷方式放入该文件夹即可。
- **使用自定义形象**：把喜欢的透明 PNG 图片（或者 JPG）放到项目目录，在 `config.json` 里把 `character_path` 改为 `"my_cat.png"`，它就会顶替掉原本的白猫。说话时，自定义图片会产生 Q 弹的上下跳动。
- **鼠标延迟微调**：如果你觉得鼠标手的跟随过于迟钝，可以在 `main.py` 找到 `current_hand_x += (target_mx - current_hand_x) * 0.2`，把 `0.2` 改大（例如 `0.4`）即可更跟手。

## 🙏 致谢

- 创意灵感来源于原版 [bongocat-osu](https://github.com/kuroni/bongocat-osu) 及各大直播平台的 PNGTuber 挂件。
- 基于 `pygame` 矢量绘图，感谢开源社区的文档支持。

## 📝 License

MIT
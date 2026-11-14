# Stream-Mascot (直播桌宠)

一个可以悬浮在桌面、实时响应键鼠与麦克风操作、可自定义外观与互动表情的二次元桌宠/直播虚拟挂件。

纯 Python + Pygame 实现，**无需任何外部图片素材（开箱即用）**。不仅支持极简的 Bongo Cat 风格渲染，还内置了全局输入监听、麦克风互动、右键菜单与粒子特效系统。

## ✨ 核心特性

- **全局键鼠监听**：无视窗口焦点，无论是打游戏还是敲代码，猫猫都能精准响应键盘敲击与鼠标点击。
- **麦克风语音互动**：实时捕获麦克风音量，说话时猫猫会自动张嘴，并伴有生动的表情变化。
- **互动右键菜单**：在窗口内右键，可触发表情互动（比心、生气），并伴随专属的粒子动效。
- **粒子特效系统**：支持“比心”时爱心飘落，以及打字时偶尔冒出蓝色小星星，增加码字爽快感。
- **F8 鼠标穿透**：按 `F8` 即可让鼠标直接穿透桌宠去点击背后的网页/游戏；再按一次恢复拖拽。
- **倒置键盘可视化**：完全符合猫猫视角的倒置键盘（含数字区），敲击真实按键时，对应键帽亮起冰蓝光，猫爪自动跃迁敲击。
- **反向平滑追踪**：鼠标移动时，鼠标手会反向平滑追踪，完美匹配真实物理直觉。
- **完美透明与抗锯齿**：采用品红色色键抠图，完美保留黑边描边，且支持中文菜单显示（自动适配系统字体）。
- **模块化架构**：拆分多个模块，配置全分离，极度方便二次开发。

## 🚀 快速开始

### 环境要求
- Windows 10/11
- Python 3.9+
- 依赖库：`pygame`, `pynput`, `pywin32`, `sounddevice`, `numpy`

### 安装运行

**1. 克隆或下载本项目到本地：**
```bash
git clone https://github.com/ITKouSyou/Stream-Mascot.git
cd Stream-Mascot
```

**2. 创建并激活虚拟环境（推荐）：**

*Windows (PowerShell)：*
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```
*(注：如果提示“禁止运行脚本”，请先运行 `Set-ExecutionPolicy RemoteSigned`，或改用 CMD 方式)*

*Windows (CMD)：*
```cmd
python -m venv .venv
.\.venv\Scripts\activate.bat
```

**3. 安装依赖：**
```bash
pip install -r requirements.txt
```

**4. 运行程序：**
```bash
python main.py
```

### ⌨️ 交互与快捷键
- **`鼠标左键`**：点击猫猫可拖拽移动窗口；点击菜单项进行互动。
- **`鼠标右键`**：呼出互动菜单（比个心、生气了、恢复原状）。
- **`F8`**：开启/关闭鼠标穿透（开启后鼠标可穿过桌宠点击后方应用）。
- **`Esc`**：退出程序。

## 📁 项目结构

```text
Stream-Mascot/
├── main.py             # 主程序入口，游戏主循环与逻辑调度
├── config.py           # 配置加载模块
├── window_utils.py     # 窗口操作模块（置顶、透明、穿透、拖拽）
├── input_utils.py      # 键盘鼠标全局监听模块
├── audio_utils.py      # 麦克风音量监听模块
├── renderer.py         # 核心绘制逻辑（猫脸、身体、键盘、双手）
├── effects.py          # 粒子特效与右键菜单UI模块
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
    "threshold": 0.15,
    "release_time": 0.2,
    "mouth_speed": 10
  },

  "colors": {
    "bg": [255, 0, 255],
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
| `mic.enabled` | 是否开启麦克风互动。 |
| `mic.threshold` | 麦克风触发张嘴的**音量阈值**（数值越小越敏感，建议在 `0.1 - 0.25` 之间微调）。 |
| `mic.release_time` | 停止说话后，嘴巴闭合的**延迟时间**（秒）。 |
| `mic.mouth_speed` | 说话时嘴巴开合的**频率**（数值越大张合越快）。 |
| `colors.bg` | 背景抠图色，**必须保持为 `[255, 0, 255]`（品红）**，以防止黑色描边被系统当成透明色抠掉。 |

## 📦 打包为独立可执行文件 (.exe)

如果你不想每次都开命令行，可以使用 PyInstaller 将其打包成 exe：

```bash
pip install pyinstaller
pyinstaller -F -w main.py
```

打包完成后，在 `dist` 文件夹中会生成 `main.exe`（你可以手动将它重命名为 `Stream-Mascot.exe`）。
**注意：** 请将 `config.json` 复制到与 `.exe` 同级的目录下，以便修改配置。

## 💡 进阶玩法与常见问题

- **开机自启**：按 `Win + R` 输入 `shell:startup`，将 `.exe` 的快捷方式放入该文件夹即可。
- **自定义形象**：把喜欢的透明 PNG 图片放到项目目录，在 `config.json` 里把 `character_path` 改为 `"my_cat.png"`。说话时，自定义图片会产生 Q 弹的上下跳动。
- **麦克风不灵敏 / 一直张嘴**：打开 `main.py`，在麦克风逻辑处加上 `print(get_volume())` 观察终端数值。若正常说话是 `0.2`，就把 `config.json` 里的 `threshold` 设为 `0.15` 左右。
- **中文字体显示方块**：代码已默认加载 Windows 的微软雅黑/黑体。如果是 Mac/Linux，请修改 `main.py` 顶部 `font_paths` 列表，填入系统自带的中文字体路径。
- **游戏内无法监听键盘**：很多游戏使用了 DirectInput 或反作弊系统，会屏蔽普通系统钩子。请尝试以**管理员身份**运行终端或打包后的 EXE。

## 🙏 致谢

- 创意灵感来源于原版 [bongocat-osu](https://github.com/kuroni/bongocat-osu) 及各大直播平台的 PNGTuber 挂件。
- 基于 `pygame` 矢量绘图，感谢开源社区的文档支持。

## 📝 License

MIT
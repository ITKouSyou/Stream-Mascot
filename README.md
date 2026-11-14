# Stream-Mascot (直播桌宠)

一个可以悬浮在桌面、实时响应键鼠与**麦克风语音**、可自定义外观与互动表情的二次元桌宠/直播虚拟挂件。

纯 Python + Pygame 实现，**无需任何外部图片素材（开箱即用）**。内置 Bongo Cat 风格渲染、全局输入监听、麦克风互动、离线语音识别、右键菜单与粒子特效系统，是你直播或写代码时的完美陪伴。

## ✨ 核心特性

- **全局键鼠监听**：无视窗口焦点，无论是打游戏还是敲代码，猫猫都能精准响应键盘敲击与鼠标点击。
- **离线语音识别互动**：内置 Vosk 离线语音引擎（支持流式极速响应），说出特定词汇（如“谢谢”、“靠”）即可瞬间触发颜文字表情（爱心眼、生气脸、哭泣等）与专属粒子特效。
- **麦克风语音联动**：实时捕获麦克风音量，说话时猫猫会自动张嘴，并伴有生动的表情变化。
- **互动右键菜单**：在窗口内右键，可手动触发表情互动，并伴随特效。
- **粒子特效系统**：支持“比心”时爱心飘落，以及打字时偶尔冒出蓝色小星星。
- **F8 鼠标穿透**：按 `F8` 即可让鼠标直接穿透桌宠去点击背后的网页/游戏；再按一次恢复拖拽。
- **倒置键盘可视化**：完全符合猫猫视角的倒置键盘（含数字区），敲击真实按键时，键帽亮起冰蓝光，猫爪自动跃迁敲击。
- **反向平滑追踪**：鼠标移动时，鼠标手会反向平滑追踪，完美匹配真实物理直觉。
- **完美透明与抗锯齿**：采用品红色色键抠图，完美保留黑边描边，且自动加载系统字体完美支持中文菜单。

## 🚀 快速开始

### 环境要求
- Windows 10/11
- Python 3.9+
- 依赖库：`pygame`, `pynput`, `pywin32`, `sounddevice`, `numpy`, `vosk`

### 安装运行

**1. 克隆本项目到本地：**
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

**4. 下载离线语音模型（必需）：**
- 点击下载轻量级中文模型（约 40MB）：[vosk-model-small-cn-0.22.zip](https://alphacephei.com/vosk/models/vosk-model-small-cn-0.22.zip)
- 解压后，将文件夹**重命名为 `model`**，并放在项目根目录下（与 `main.py` 同级）。
- 正确结构：`Stream-Mascot/model/am/...` （注意：不要解压成 `model/vosk-model-small-cn-0.22/...`，请将里面的文件直接放入 `model`）。

**5. 运行程序：**
```bash
python main.py
```

### 🎙️ 语音互动指令示例
当程序启动并看到 `麦克风监听已启动` 时，对着麦克风说话即可触发：
- **夸赞/开心**：说“谢谢”、“哇”、“爱你” ➡ 触发 **爱心眼 (♥ω♥)** + 爱心粒子雨。
- **吐槽/生气**：说“靠”、“无语”、“烦” ➡ 触发 **生气脸 (╬▔皿▔)**。
- **委屈/伤心**：说“呜呜”、“哭” ➡ 触发 **哭泣脸 (ಥ_ಥ)** + 蓝色眼泪粒子。
- **震惊**：说“卧槽”、“居然” ➡ 触发 **惊讶脸 (⊙_⊙)**。
- **无奈**：说“服了”、“离谱” ➡ 触发 **无语脸 (￣_￣)** + 汗滴。

### ⌨️ 快捷键与操作
- **`鼠标左键`**：点击猫猫可拖拽移动窗口；点击菜单项进行互动。
- **`鼠标右键`**：呼出互动菜单。
- **`F8`**：开启/关闭鼠标穿透（开启后鼠标可穿过桌宠点击后方应用）。
- **`Esc`**：退出程序。

## 📁 项目结构

```text
Stream-Mascot/
├── main.py             # 主程序入口，游戏主循环与逻辑调度
├── config.py           # 配置加载模块
├── window_utils.py     # 窗口操作模块（置顶、透明、穿透、拖拽）
├── input_utils.py      # 键盘鼠标全局监听模块
├── audio_utils.py      # 麦克风音量监听模块（用于嘴巴开合）
├── stt_utils.py        # Vosk 离线语音识别模块（用于关键词表情触发）
├── renderer.py         # 核心绘制逻辑（猫脸、颜文字、键盘、双手）
├── effects.py          # 粒子特效与右键菜单UI模块
├── config.json         # 运行时配置文件（首次运行自动生成）
├── requirements.txt    # Python 依赖清单
└── model/              # Vosk 离线语音模型文件夹（需手动下载）
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
| `character_path` | **自定义角色图片**，支持网络链接或本地路径。留空 `""` 则使用默认白猫。 |
| `character_width` | 自定义图片的缩放宽度。 |
| `mic.enabled` | 是否开启麦克风嘴型互动。 |
| `mic.threshold` | 触发嘴巴张开的**音量阈值**（数值越小越敏感，建议 `0.1 - 0.25` 之间）。 |
| `mic.release_time` | 停止说话后，嘴巴闭合的**延迟时间**（秒）。 |
| `colors.bg` | 背景抠图色，**必须保持为 `[255, 0, 255]`（品红）**，以防止黑色描边被抠掉。 |

## 📦 打包为独立可执行文件 (.exe)

```bash
pip install pyinstaller
pyinstaller -F -w main.py
```

打包完成后，在 `dist` 文件夹中会生成 `main.exe`。请将 `config.json` 以及 **`model` 文件夹** 复制到与 `.exe` 同级的目录下才能正常使用语音功能。

## 💡 进阶玩法与常见问题

- **语音反应慢**：代码中已使用 `PartialResult` 流式识别，正常在 0.3 秒内即可触发。如果觉得还是慢，可以尝试更换为 Vosk 官网更大的 `vosk-model-cn-0.22` 模型。
- **误触发太多**：打开 `main.py`，找到 `EMOTION_KEYWORDS` 字典，删除容易在日常对话中误触发的词汇。
- **游戏内无法监听键盘**：很多游戏使用了 DirectInput 或反作弊系统会屏蔽普通系统钩子。请尝试以**管理员身份**运行终端或打包后的 EXE。
- **开机自启**：按 `Win + R` 输入 `shell:startup`，将打包好的 `.exe` 快捷方式放入该文件夹即可。

## 🙏 致谢

- 创意灵感来源于原版 [bongocat-osu](https://github.com/kuroni/bongocat-osu) 及各大直播平台的 PNGTuber 挂件。
- 离线语音识别基于 [Vosk](https://alphacephei.com/vosk/)。

## 📝 License

MIT
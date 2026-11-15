# Stream-Mascot (直播桌宠)

一个可以悬浮在桌面、实时响应键鼠与**麦克风语音**、可自定义外观与互动表情的二次元桌宠/直播虚拟挂件。

纯 Python + Pygame 实现，**无需任何外部图片素材（开箱即用）**。内置 Bongo Cat 风格渲染、全局输入监听、麦克风互动、离线语音识别、右键菜单与粒子特效系统，是你直播或写代码时的完美陪伴。

## ✨ 核心特性

- **全局键鼠监听**：无视窗口焦点，无论是打游戏还是敲代码，猫猫都能精准响应键盘敲击与鼠标点击。
- **离线语音识别互动**：内置 Vosk 离线语音引擎（支持流式极速响应），说出特定词汇（如“谢谢”、“靠”）即可瞬间触发颜文字表情（爱心眼、生气脸、哭泣等）与专属粒子特效。
- **自定义语音词库**：可通过设置界面自由增删触发表情的关键词（内置防重复与最少保留一项校验）。
- **麦克风语音联动**：实时捕获麦克风音量，说话时猫猫会自动张嘴，并伴有生动的表情变化。
- **互动右键菜单**：在窗口内右键，可呼出设置界面、重新加载桌宠或退出程序。
- **深度设置界面**：内置基于 Tkinter 的深色设置面板，支持调整缩放比例、麦克风灵敏度，并可手动触发互动表情。
- **完美透明与平滑缩放**：采用品红色色键抠图，配合独家的边缘杂色过滤算法，在任意缩放比例下都能完美保留黑边描边。
- **F8 鼠标穿透**：按 `F8` 即可让鼠标直接穿透桌宠去点击背后的网页/游戏；再按一次恢复拖拽。

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
- 正确结构：`Stream-Mascot/model/am/...` 

**5. 运行程序：**
```bash
python main.py
```

### 🎙️ 语音互动指令示例
当程序启动并看到 `麦克风监听已启动` 时，对着麦克风说话即可触发：
- **夸赞/开心**：说“谢谢”、“哇” ➡ 触发 **爱心眼 (♥ω♥)** + 爱心粒子雨。
- **吐槽/生气**：说“靠”、“无语” ➡ 触发 **生气脸 (╬▔皿▔)**。
- **委屈/伤心**：说“呜呜”、“哭” ➡ 触发 **哭泣脸 (ಥ_ಥ)** + 蓝色眼泪粒子。
- **震惊**：说“卧槽”、“居然” ➡ 触发 **惊讶脸 (⊙_⊙)**。
- **无奈**：说“服了”、“离谱” ➡ 触发 **无语脸 (￣_￣)** + 汗滴。

*(以上词汇均可在右键 -> 设置 -> 语音词库中自由修改)*

### ⌨️ 快捷键与操作
- **`鼠标左键`**：拖拽桌宠移动窗口。
- **`鼠标右键`**：呼出主菜单。
- **`F8`**：开启/关闭鼠标穿透。
- **`Esc`**：退出程序。

## 📁 项目结构

```text
Stream-Mascot/
├── main.py             # 主程序入口，游戏主循环与逻辑调度
├── config.py           # 配置加载模块
├── window_utils.py     # 窗口操作模块（置顶、透明、穿透、拖拽）
├── input_utils.py      # 键盘鼠标全局监听模块
├── audio_utils.py      # 麦克风音量监听模块（用于嘴巴开合）
├── stt_utils.py        # Vosk 离线语音识别模块
├── renderer.py         # 核心绘制逻辑（猫脸、颜文字、键盘、双手）
├── effects.py          # 粒子特效与右键菜单UI模块
├── settings_ui.py      # 深色设置界面模块（Tkinter）
├── config.json         # 运行时配置文件
├── requirements.txt    # Python 依赖清单
└── model/              # Vosk 离线语音模型文件夹
```

## 👨‍💻 作者信息

- **作者**：ITKouSyou
- **B站主页**：[https://space.bilibili.com/7243785](https://space.bilibili.com/7243785)
- **GitHub 仓库**：[https://github.com/ITKouSyou/Stream-Mascot](https://github.com/ITKouSyou/Stream-Mascot)

如果这个项目给你带来了便利或欢乐，欢迎去 GitHub 点个 Star，或者在 B 站关注支持一下！

## 🙏 致谢

- 创意灵感来源于原版 [bongocat-osu](https://github.com/kuroni/bongocat-osu) 及各大直播平台的 PNGTuber 挂件。
- 离线语音识别基于 [Vosk](https://alphacephei.com/vosk/)。

## 📝 License

MIT
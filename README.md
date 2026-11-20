# Stream-Mascot (直播桌宠)

![Version](https://img.shields.io/badge/version-1.1.0-blue)
![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

一个可以悬浮在桌面、实时响应键鼠与**麦克风语音**、支持**多套方案切换**、可自定义角色与互动表情的二次元桌宠/直播虚拟挂件。

纯 Python + Pygame 实现，**无需任何外部图片素材（开箱即用）**。内置 Bongo Cat 风格渲染、全局输入监听、麦克风互动、离线语音识别、多套角色方案管理以及专属粒子特效系统，是你直播或写代码时的完美陪伴。

## ✨ 核心特性

- **多套方案管理 (Profile)**：你可以为不同的角色/直播场景创建不同的方案。每个方案拥有独立的角色图片、表情配置和语音词库，互不干扰。
- **自定义角色与表情**：支持上传静态图片（PNG/JPG）或**动态图片（GIF）**。你可以让它展示自带的极简颜文字表情，也可以关闭颜文字，上传对应状态（爱心眼、生气等）的专属立绘图片。
- **生动的动态反馈**：角色在待机时会像呼吸一样轻微浮动和左右摇摆；打字时会中频弹动；说话时会高频上下抖动，让角色真正“活”过来。
- **离线语音识别互动**：内置 Vosk 离线语音引擎，说出特定词汇（如“谢谢”、“靠”）即可瞬间触发专属表情与粒子特效。词库完全由你自定义（支持防重复校验）。
- **全局键鼠监听**：无视窗口焦点，无论是打游戏还是敲代码，猫猫都能精准响应键盘敲击与鼠标点击。
- **软重载机制**：在右键菜单点击“重新加载”时，程序会在不重启进程的情况下，瞬间重新读取配置、重载图片并刷新画面。彻底告别传统重载导致的文件占用和黑屏闪烁。
- **完美透明与平滑缩放**：采用品红色色键抠图，配合独家的边缘杂色过滤算法，在任意缩放比例下都能完美保留黑边描边。
- **F8 鼠标穿透**：按 `F8` 即可让鼠标直接穿透桌宠去点击背后的网页/游戏；再按一次恢复拖拽。

## 🚀 快速开始

### 环境要求
- Windows 10/11
- Python 3.9+
- 依赖库：`pygame`, `pynput`, `pywin32`, `sounddevice`, `numpy`, `vosk`, `Pillow`

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

## 🎮 使用指南

- **呼出设置**：在桌宠窗口内点击 **鼠标右键**，选择“设置与互动”。
- **上传自定义角色**：在 `角色与表情` 标签页，点击“选择图片”上传基础立绘。如果你上传了 GIF 动图，程序会自动将其逐帧解析并播放！
- **上传自定义表情**：如果你关闭了“使用自带颜文字表情”，你可以为爱心眼、生气等状态上传独立的图片。
- **多方案切换**：在界面最上方，你可以 `+ 新建` 一个方案，系统会自动给你一套纯净的白猫初始配置，你可以为其配置专属的角色。

### ⌨️ 快捷键与操作
- **`鼠标左键`**：拖拽桌宠移动窗口。
- **`鼠标右键`**：呼出主菜单（设置、重载、退出）。
- **`F8`**：开启/关闭鼠标穿透。
- **`Esc`**：退出程序。

## 📦 打包为独立可执行文件 (.exe)

由于本项目依赖了 `Vosk`（包含底层的 C 语言动态链接库 DLL）、`Pillow`（用于 GIF 解析）以及 `Tkinter`（设置界面），打包时需要特殊处理以确保所有依赖都被正确收集。

请先安装打包工具：
```bash
pip install pyinstaller
```

### 方式一：使用定制的 spec 文件（🌟 强烈推荐）
项目根目录已经为你准备好了经过深度定制的 `main.spec` 文件。它能够完美收集 Vosk 的 DLL 和 Pillow 的扩展模块，打包出的程序稳定性最高。

1. 直接执行：
   ```bash
   pyinstaller main.spec
   ```

### 方式二：使用命令行参数
如果你更习惯命令行，可以使用 `--collect-all` 参数强制收集全部依赖：

```bash
pyinstaller -F -w --collect-all vosk --collect-all PIL main.py
```

### 📁 整理发布文件夹（重要！）
无论使用哪种方式，打包完成后，进入 `dist` 文件夹。你需要将以下文件/文件夹与生成的 `.exe` 放在同一个目录下才能正常运行：

- **必须**将项目根目录下的 `model` 文件夹复制过去。
- **必须**将 `config.json` 复制过去（如果你已经配置好了设置的话）。
- （可选）如果你在设置里上传过自定义图片，请将 `custom_assets` 文件夹也一并复制过去。

最终发布文件夹的结构应该如下：
```text
发布文件夹/
├── Stream-Mascot.exe    # 打包好的程序
├── config.json          # 配置文件
├── model/               # 语音模型文件夹
└── custom_assets/       # (可选) 自定义图片/GIF 文件夹
```

## 📁 项目结构

```text
Stream-Mascot/
├── main.py             # 主程序入口，游戏主循环与逻辑调度（含软重载逻辑）
├── config.py           # 配置加载模块
├── window_utils.py     # 窗口操作模块（置顶、透明、穿透、拖拽）
├── input_utils.py      # 键盘鼠标全局监听模块
├── audio_utils.py      # 麦克风音量监听模块（用于嘴巴开合）
├── stt_utils.py        # Vosk 离线语音识别模块
├── renderer.py         # 核心绘制逻辑（动画、GIF解码、颜文字、双手）
├── effects.py          # 粒子特效与右键菜单UI模块
├── settings_ui.py      # 深色设置界面模块（Tkinter）
├── main.spec           # PyInstaller 打包配置文件
├── custom_assets/      # 【自动生成】用户上传的自定义角色/表情图片存放处
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
- GIF 动图支持基于 [Pillow](https://python-pillow.org/)。

## 📝 License

MIT
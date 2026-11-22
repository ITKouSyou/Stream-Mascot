# Stream-Mascot (直播桌宠)

![Version](https://img.shields.io/badge/version-1.2.0-blue)
![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

一个可以悬浮在桌面、实时响应键鼠与**麦克风语音**、支持**插件扩展**与**自定义角色**的二次元桌宠/直播虚拟挂件。

纯 Python + Pygame 实现，**无需任何外部图片素材（开箱即用）**。内置 Bongo Cat 风格渲染、全局键鼠监听、麦克风语音联动、离线语音识别、多套角色方案管理、**独立表情系统**以及**极客级插件架构**。

## ✨ 核心特性

- **🧩 无限扩展的插件系统**：支持外部 Python 脚本热加载。你可以轻松编写插件，让桌宠响应直播弹幕、触发特殊动画、甚至接入智能家居，代码完全解耦。
- **🎭 独立的表情管理器**：彻底重构了面部渲染逻辑，表情绘制与核心循环解耦。支持动态增加新的颜文字表情（如流口水、星星眼）。
- **🎙️ 专业级音频处理**：集成 `sounddevice` 与 `noisereduce` 降噪算法，过滤风扇底噪；结合 `Vosk` 离线语音引擎与流式识别，实现毫秒级的语音互动与“唱歌摇摆”检测。
- **🚀 软硬双重热重载**：在设置中点击“保存并重启”时，程序会彻底释放音频流与内存，瞬间重启进程，绝不残留僵尸线程；而在日常使用中支持设备热插拔自动重连。
- **多套方案管理 (Profile)**：你可以为不同的角色/直播场景创建不同的方案。每个方案拥有独立的角色图片、表情配置和语音词库。
- **🎨 自定义角色与 GIF**：支持上传 PNG/JPG/GIF，程序会自动逐帧解析并播放。你可以选择使用代码自带的颜文字，或者关闭颜文字，上传专属的立绘表情。
- **⚡ 性能模式**：在配置中开启后，将使用最近邻缩放代替平滑缩放，极大降低 CPU 占用，适合低配电脑或游戏直播时使用。
- **完美透明与平滑缩放**：采用品红色色键抠图，配合独家的边缘杂色过滤算法，在任意缩放比例下都能完美保留黑边描边。
- **F8 鼠标穿透**：按 `F8` 即可让鼠标直接穿透桌宠去点击背后的网页/游戏，并伴有屏幕飘浮文字提示。

## 🚀 快速开始

### 环境要求
- Windows 10/11
- Python 3.9+
- 依赖库：`pygame`, `pynput`, `pywin32`, `sounddevice`, `numpy`, `vosk`, `Pillow`, `librosa`, `noisereduce`

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

- **呼出设置**：在桌宠窗口内点击 **鼠标右键** -> “设置与互动”。
- **音频设备锁定**：如果发现系统切换设备失效，在“全局设置”里，可以直接下拉选择你想要的麦克风。点击“刷新设备”可以获取最新列表。
- **开启降噪**：建议勾选“启用 AI 降噪”，这能极大减少风扇、空调底噪引起的“幽灵唱歌”问题。
- **上传自定义角色**：在 `角色与表情` 标签页，点击“选择图片”上传基础立绘。

### ⌨️ 快捷键与操作
- **`鼠标左键`**：拖拽桌宠移动窗口。
- **`鼠标右键`**：呼出主菜单。
- **`F8`**：开启/关闭鼠标穿透（会有屏幕提示）。
- **`Esc`**：退出程序。

## 🧩 插件开发指南 (v1.2.0 新增)

你只需在根目录的 `plugins/` 文件夹下创建一个 `.py` 文件，程序启动时会自动加载。不需要修改任何核心代码。

**示例：`plugins/my_custom_plugin.py`**

```python
# 1. 插件加载时调用
def on_load(context):
    print("[我的插件] 加载成功！")

# 2. 监听全局事件
def on_event(event_type, data, context):
    # event_type 可以是: "key_press", "voice_trigger", "sing_start", "sing_stop"
    
    if event_type == "voice_trigger":
        text = data.get("text", "")
        emotion = data.get("emotion", "")
        print(f"听到语音：'{text}'，触发了 {emotion} 表情！")
        
    elif event_type == "sing_start":
        print("用户开始唱歌了！准备蹦迪！")
        
    elif event_type == "key_press":
        key = data.get("key", "")
        if key == "f2":
            # 3. 调用外部 API
            context["trigger_expression"]("heart")
            context["emit_text"]("按 F2 触发了比心！")
```

**插件 API 上下文 (`context`) 支持的能力：**
- `context["trigger_expression"](emotion)`：强制触发特定表情（如 `"heart"`, `"angry"`, `"cry"`, `"normal"`）。
- `context["emit_particle"](x, y, count, color, type)`：发射粒子特效。
- `context["emit_text"](text)`：在屏幕中央弹出一个飘浮文字。

## 📁 项目结构

```text
Stream-Mascot/
├── main.py             # 主程序入口，游戏主循环与逻辑调度（含插件挂载）
├── config.py           # 配置加载模块（防损毁合并逻辑）
├── window_utils.py     # 窗口操作模块（置顶、透明、穿透、拖拽）
├── input_utils.py      # 键盘鼠标全局监听模块（向插件广播事件）
├── audio_utils.py      # 麦克风音量、降噪与唱歌检测模块
├── stt_utils.py        # Vosk 离线语音识别模块（防僵尸线程机制）
├── renderer.py         # 核心绘制逻辑（动画、GIF解码、双手）
├── expression_manager.py # 独立表情管理器（便于无限扩展新表情）
├── plugin_manager.py   # 插件加载与事件调度中心
├── effects.py          # 粒子特效、菜单、飘浮文字UI模块
├── settings_ui.py      # 深色设置界面模块（Tkinter + 滚动条）
├── plugins/            # 【插件目录】放入 .py 文件即可自动加载
│   └── demo_chat.py    # 示例插件
├── main.spec           # PyInstaller 打包配置文件
├── custom_assets/      # 【自动生成】用户上传的自定义图片/GIF
├── config.json         # 运行时配置文件
├── requirements.txt    # Python 依赖清单
└── model/              # Vosk 离线语音模型文件夹
```

## 📦 打包为独立可执行文件 (.exe)

由于本项目依赖 `Vosk` (C++ DLL)、`Pillow` 等底层库，请**务必使用定制的 `main.spec` 文件**打包。

```bash
pip install pyinstaller
pyinstaller main.spec
```

**打包后整理：**
将 `dist` 目录下的 `Stream-Mascot.exe` 作为主程序，必须把 `model` 文件夹、`config.json` 以及（可选）`custom_assets`、`plugins` 文件夹复制到同一目录下。

## 👨‍💻 作者信息

- **作者**：ITKouSyou
- **B站主页**：[https://space.bilibili.com/7243785](https://space.bilibili.com/7243785)
- **GitHub 仓库**：[https://github.com/ITKouSyou/Stream-Mascot](https://github.com/ITKouSyou/Stream-Mascot)

如果这个项目给你带来了便利或欢乐，欢迎去 GitHub 点个 Star，或者在 B 站关注支持一下！

## 🙏 致谢

- 创意灵感来源于原版 [bongocat-osu](https://github.com/kuroni/bongocat-osu)。
- 离线语音识别基于 [Vosk](https://alphacephei.com/vosk/)。
- 实时降噪基于 [NoiseReduce](https://github.com/timsainb/noisereduce)。

## 📝 License

MIT
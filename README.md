# Stream-Mascot (直播桌宠)

![Version](https://img.shields.io/badge/version-1.4.0-blue)
![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

一个可以悬浮在桌面、实时响应键鼠与**麦克风语音**、支持**插件扩展**与**直播弹幕互动**的二次元桌宠/直播虚拟挂件。

纯 Python + Pygame 实现，**无需任何外部图片素材（开箱即用）**。内置 Bongo Cat 风格渲染、全局键鼠监听、麦克风语音联动、离线语音识别、多套角色方案管理、**系统托盘**以及**极客级插件架构（支持B站弹幕联动）**。

## ✨ 核心特性

- **📺 B站直播弹幕互动**：内置独立插件，自动监听指定直播间弹幕。观众发送“谢谢”、“比心”，桌宠会瞬间比心并飘出感谢弹幕！
- **🖥️ 系统托盘管理**：支持右下角托盘图标，随时呼出设置、切换鼠标穿透或彻底退出。
- **🧩 无限扩展的插件系统**：支持外部 Python 脚本热加载。你可以轻松编写插件，让桌宠响应特殊动画，或者接入其他直播平台。
- **🎭 独立的表情管理器**：表情绘制与核心循环解耦，支持动态增加新的颜文字表情。
- **🎙️ 专业级音频处理**：集成 `sounddevice` 与 `noisereduce` 降噪算法，过滤风扇底噪；结合 `Vosk` 离线语音引擎与流式识别，实现毫秒级的语音互动与“唱歌摇摆”检测。
- **🚀 软硬双重热重载**：彻底释放音频流与内存，绝不残留僵尸线程；支持设备热插拔自动重连。
- **多套方案管理 (Profile)**：可为不同的角色/直播场景创建不同方案，每个方案拥有独立图片、表情和词库。
- **⚡ 性能模式**：适合低配电脑或游戏直播时使用，极大降低 CPU 占用。

## 🚀 快速开始

### 环境要求
- Windows 10/11
- Python 3.9+ (推荐 3.10 - 3.12，本项目在 3.13 下也能运行，但需注意下方的 B 站依赖坑)
- 依赖库：`pygame`, `pynput`, `pywin32`, `sounddevice`, `numpy`, `vosk`, `Pillow`, `librosa`, `noisereduce`, `pystray`

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

**3. 安装基础依赖：**
```bash
pip install -r requirements.txt
```

**4. ⚠️ B站弹幕插件依赖安装（极其重要，必看）：**

由于 `blivedm` 官方在 PyPI 上的包已废弃，且其源码中强制锁死了老版本的 `aiohttp~=3.9.0`。如果你使用的是 **Python 3.13**，直接 `pip install` 会因为找不到预编译包而尝试本地编译，最终导致缺少 `Microsoft Visual C++ 14.0` 报错。

**请务必按以下步骤“曲线救国”安装：**

① 先手动安装 `blivedm`，并跳过它的依赖检查：
```bash
pip install --no-deps git+https://github.com/xfgryujk/blivedm.git
```

② 补齐 `blivedm` 实际运行需要的底层依赖：
```bash
pip install aiohttp yarl multidict frozenlist aiosignal attrs pure-protobuf Brotli
```
*(如果 Python 3.13 下依然提示 `aiohttp` 编译报错，请去 [PyPI 页面](https://pypi.org/project/aiohttp/#files) 下载 `cp313-win_amd64.whl` 结尾的预编译包，用 `pip install 下载的包路径` 本地安装。)*

**5. 下载离线语音模型（必需）：**
- 点击下载轻量级中文模型（约 40MB）：[vosk-model-small-cn-0.22.zip](https://alphacephei.com/vosk/models/vosk-model-small-cn-0.22.zip)
- 解压后，将文件夹**重命名为 `model`**，并放在项目根目录下。
- 正确结构：`Stream-Mascot/model/am/...` 

**6. 运行程序：**
```bash
python main.py
```

## 🎮 使用指南

### 📺 如何获取并配置 B 站直播间房间号（重要）
很多人会把个人 UID 和直播间房间号搞混，导致弹幕插件连接失败，请按以下步骤获取：
1. 打开浏览器，进入你的 B 站直播间主页（例如：`https://live.bilibili.com/21423607`）。
2. 浏览器地址栏**最后面的那串纯数字**（即 `21423607`）就是你的真实房间号。
3. 在桌宠身上点击**右键** -> `设置与互动` -> `全局设置`。
4. 找到 **“B站直播间房间号”**，填入那串数字，点击底部 **“保存并重启程序”** 即可生效。
5. **如何测试？** 对着直播间发送弹幕：“谢谢”，你的桌宠如果做出比心动作，说明连接成功！

### 其他操作
- **呼出设置**：点击鼠标右键 -> “设置与互动”。
- **系统托盘**：可在右下角托盘右键，随时切换穿透或退出。
- **音频设备锁定**：在“全局设置”里下拉选择麦克风，建议勾选“启用 AI 降噪”。

## 🧩 插件开发指南

你只需在根目录的 `plugins/` 文件夹下创建一个 `.py` 文件，程序启动时会自动加载。

```python
# plugins/my_custom_plugin.py
def on_load(context):
    print("[我的插件] 加载成功！")

def on_event(event_type, data, context):
    # event_type: "key_press", "voice_trigger", "sing_start", "sing_stop"
    if event_type == "voice_trigger":
        context["trigger_expression"]("heart")
        context["emit_text"]("自定义插件触发！")
```
**插件 API 上下文：**
- `context["trigger_expression"](emotion)`：触发指定表情（如 `"heart"`, `"angry"`）。
- `context["emit_particle"](x, y, count, color, type)`：发射粒子特效。
- `context["emit_text"](text)`：在屏幕上弹出一个飘浮文字。

## 📦 打包为独立可执行文件 (.exe)

由于项目涉及 `Vosk` (C++ DLL)、`librosa` (科学计算)、`blivedm` (异步网络) 等复杂依赖，请**务必使用项目根目录定制的 `main.spec` 文件**进行打包。

```bash
pip install pyinstaller
pyinstaller main.spec
```

**⚠️ `main.spec` 已为你处理了以下极其棘手的问题：**
1. 强制收集了 `librosa` 缺失的 `.pyi` 类型存根文件。
2. 针对 B 站插件通过 `importlib` 动态加载导致的“PyInstaller 扫不到模块”问题，强制收集了 `blivedm`、`aiohttp`、`brotli` 等全家桶隐藏包。
3. 考虑到 C 扩展 DLL 的完整性，**关闭了 UPX 压缩**（防止打包后的 exe 运行时提示 DLL 损坏）。

**打包后整理：**
将 `dist` 目录下的 `Stream-Mascot.exe` 作为主程序，必须把 `model` 文件夹、`config.json` 以及 `plugins`、`custom_assets` 文件夹复制到同一目录下。

## 📁 项目结构

```text
Stream-Mascot/
├── main.py             # 主程序入口（含托盘挂载、重载循环）
├── config.py           # 配置加载模块（防损毁合并逻辑）
├── window_utils.py     # 窗口操作模块
├── input_utils.py      # 键盘鼠标全局监听
├── audio_utils.py      # 麦克风音量、降噪与唱歌检测
├── stt_utils.py        # Vosk 离线语音识别
├── renderer.py         # 核心绘制逻辑
├── expression_manager.py # 独立表情管理器
├── plugin_manager.py   # 插件加载与事件调度中心
├── effects.py          # 粒子特效、菜单、飘浮文字UI
├── settings_ui.py      # 深色设置界面（Tkinter）
├── tray_manager.py     # 系统托盘管理器
├── plugins/            # 【插件目录】
│   ├── bilibili_danmaku.py # B站弹幕连接插件
│   └── demo_chat.py        # 示例插件
├── main.spec           # PyInstaller 深度定制打包配置
├── custom_assets/      # 【自动生成】自定义图片/GIF
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

- 创意灵感来源于原版 [bongocat-osu](https://github.com/kuroni/bongocat-osu)。
- 离线语音识别基于 [Vosk](https://alphacephei.com/vosk/)。
- 实时降噪基于 [NoiseReduce](https://github.com/timsainb/noisereduce)。
- B站弹幕连接基于 [blivedm](https://github.com/xfgryujk/blivedm)。

## 📝 License

MIT
# -*- mode: python ; coding: utf-8 -*-
import os
import librosa
from PyInstaller.utils.hooks import collect_all

# ================= 收集 Vosk =================
vosk_datas, vosk_binaries, vosk_hiddenimports = collect_all('vosk')

# ================= 收集 Pillow =================
pil_datas, pil_binaries, pil_hiddenimports = collect_all('PIL')

# ================= 收集 librosa 依赖 =================
librosa_datas, librosa_binaries, librosa_hiddenimports = collect_all('librosa')
nr_datas, nr_binaries, nr_hiddenimports = collect_all('noisereduce')

# ================= 🔧 核心修复：手动收集 librosa 的 .pyi 文件 =================
librosa_pyi_datas = []
librosa_dir = os.path.dirname(librosa.__file__)
for root, dirs, files in os.walk(librosa_dir):
    for f in files:
        if f.endswith('.pyi'):
            full_path = os.path.join(root, f)
            # 计算相对于 librosa 包根目录的路径，并放入 _MEI.../librosa/ 下
            rel_path = os.path.relpath(full_path, librosa_dir)
            dest_dir = os.path.join('librosa', os.path.dirname(rel_path))
            librosa_pyi_datas.append((full_path, dest_dir))

# ================= 🆕 修复 B站弹幕：手动收集 blivedm 全家桶 =================
# 插件通过 importlib 动态加载，PyInstaller 静态分析发现不了 blivedm，
# 必须把 blivedm 及其依赖包（含 C 扩展/子模块/数据文件）整个收集进 exe。
extra_pkgs = [
    'blivedm',
    'aiohttp',
    'brotli',
    'brotlicffi',
    'pure_protobuf',
    'yarl',
    'multidict',
    'frozenlist',
    'aiosignal',
    'attrs',
]
dm_datas, dm_binaries, dm_hiddenimports = [], [], []
for _pkg in extra_pkgs:
    try:
        _d, _b, _h = collect_all(_pkg)
        dm_datas += _d
        dm_binaries += _b
        dm_hiddenimports += _h
        print(f'[spec] 已收集: {_pkg}')
    except Exception as e:
        print(f'[spec] 跳过未安装的包 {_pkg}: {e}')

# cffi 相关 + blivedm 关键子模块再显式兜底
dm_hiddenimports += [
    'cffi',
    '_cffi_backend',
    'blivedm',
    'blivedm.models.web',
    'blivedm.models.open_live',
    'blivedm.models.pb',
    'blivedm.handlers',
    'blivedm.clients.web',
    'blivedm.clients.open_live',
    'blivedm.clients.ws_base',
]

# ================= 合并所有依赖 =================
a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=vosk_binaries + pil_binaries + librosa_binaries + nr_binaries + dm_binaries,
    # 将手动收集的 .pyi 文件追加到 datas 中
    datas=vosk_datas + pil_datas + librosa_datas + nr_datas + librosa_pyi_datas + dm_datas,
    hiddenimports=vosk_hiddenimports + pil_hiddenimports + librosa_hiddenimports + nr_hiddenimports + dm_hiddenimports + [
        'tkinter', 
        'tkinter.ttk', 
        'tkinter.messagebox', 
        'tkinter.filedialog', 
        'tkinter.simpledialog',
        'PIL._tkinter_finder',
        'lazy_loader',  # 确保 lazy_loader 也被包含
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Stream-Mascot',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,  # 🆕 cffi/C扩展较多，先关掉 UPX 避免 DLL 损坏；要减小体积再打开
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 调试时改成 True，能看到插件报错信息（如 "[B站插件] ..." / 加载失败堆栈）
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
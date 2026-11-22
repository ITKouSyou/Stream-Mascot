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

# ================= 合并所有依赖 =================
a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=vosk_binaries + pil_binaries + librosa_binaries + nr_binaries,
    # 将手动收集的 .pyi 文件追加到 datas 中
    datas=vosk_datas + pil_datas + librosa_datas + nr_datas + librosa_pyi_datas,
    hiddenimports=vosk_hiddenimports + pil_hiddenimports + librosa_hiddenimports + nr_hiddenimports + [
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
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
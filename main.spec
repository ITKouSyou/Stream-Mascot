# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all, collect_data_files, collect_dynamic_libs

# ================= 收集 Vosk 及其 DLL =================
# 强制收集 vosk 的数据、动态库和隐式导入
vosk_datas, vosk_binaries, vosk_hiddenimports = collect_all('vosk')

# ================= 收集 Pillow (PIL) 及其 C 扩展 =================
# 强制收集 PIL 的所有数据、二进制 (包括 _imaging.pyd) 和隐藏导入
pil_datas, pil_binaries, pil_hiddenimports = collect_all('PIL')

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=vosk_binaries + pil_binaries, # 合并所有动态链接库
    datas=vosk_datas + pil_datas,
    hiddenimports=vosk_hiddenimports + pil_hiddenimports + [
        'tkinter', 
        'tkinter.ttk', 
        'tkinter.messagebox', 
        'tkinter.filedialog', 
        'tkinter.simpledialog',
        'PIL._tkinter_finder'
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
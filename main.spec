# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs, collect_submodules

# 自动收集 vosk 的数据文件、动态链接库(DLL)和隐式导入模块
vosk_datas = collect_data_files('vosk')
vosk_binaries = collect_dynamic_libs('vosk')
vosk_hiddenimports = collect_submodules('vosk')

# 自动收集 Pillow 的图像格式支持数据（用于解析 GIF）
pil_datas = collect_data_files('PIL')

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=vosk_binaries,
    # 将 vosk 数据、PIL 数据打包，同时如果你想把默认的 config.json 也打进去，可以加在这里
    datas=vosk_datas + pil_datas,
    hiddenimports=vosk_hiddenimports + [
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
    name='Stream-Mascot',  # 直接输出为你想要的软件名
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,         # 隐藏黑色控制台窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # icon='icon.ico'      # 如果你准备了一个 icon.ico，取消这行注释即可给 exe 加图标
)
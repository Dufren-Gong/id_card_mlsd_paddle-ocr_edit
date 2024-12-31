# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=['D:\Always_softwares\Miniconda\envs\paddle-ocr\Lib\site-packages\paddleocr','D:\Always_softwares\Miniconda\envs\paddle-ocr\Lib\site-packages\paddle\libs'],
    binaries=[('D:\Always_softwares\Miniconda\envs\paddle-ocr\Lib\site-packages\paddle\libs','.')],
    datas=[('D:\Always_Softwares\Miniconda\envs\paddle-ocr\Lib\site-packages\paddleocr\ppocr','ppocr')],
    hiddenimports=[],
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
    [],
    exclude_binaries=True,
    name='身份证照片识别',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    icon='./files/icon/icon.ico',
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='main',
)

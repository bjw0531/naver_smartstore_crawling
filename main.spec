# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
    hiddenimports=[
        'Cython.Compiler.Main',
        'Cython.Compiler.Code',
        'Cython.Compiler.PyrexTypes',
        'Cython.Compiler.Symtab',
        'Cython.Compiler.ExprNodes',
        'imghdr',
        'imgaug',
        'pyclipper',
    ],
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='main',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['..\\icon.png'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='main',
    datas = (
        collect_data_files('paddleocr') +
        collect_data_files('paddlepaddle') +
        [('C:/Windows/Fonts/NanumGothic.ttf', 'fonts')]
    )
)

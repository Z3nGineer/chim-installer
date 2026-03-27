# -*- mode: python ; coding: utf-8 -*-
# CHIM Installer — PyInstaller spec (--onedir mode)
# patches/ is ~370MB so --onefile is impractical; --onedir keeps it alongside the exe.

import sys

a = Analysis(
    ['chim_installer.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('patches', 'patches'),
        ('7zzs', '.'),
        ('deck_engine.ini', '.'),
        ('deck_gameusersettings.ini', '.'),
    ],
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
    name='CHIM_Installer',
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
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='CHIM_Installer',
)

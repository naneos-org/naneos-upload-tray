# -*- mode: python ; coding: utf-8 -*-
import sys

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('img', 'img')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

icon_file = None
if sys.platform == "win32":
    icon_file = "img/naneos_icon.ico"

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='naneos_upload_tray',
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
    icon=icon_file,   # Windows: .ico, macOS: None
)


if sys.platform == "darwin":
    coll = COLLECT(
        exe,
        a.binaries,
        a.datas,
        strip=False,
        upx=True,
        upx_exclude=[],
        name='naneos_upload_tray',
    )

    app = BUNDLE(
        coll,
        name='naneos_upload_tray.app',
        icon='img/naneos_icon.icns',
        bundle_identifier='ch.naneos.uploadtray',
        info_plist={
            'NSBluetoothAlwaysUsageDescription': 'This app needs Bluetooth, to connect to naneos devices.',
        },
    )

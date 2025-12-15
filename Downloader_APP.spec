# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['Downloader_APP.py'],   # entry script
    pathex=[],
    binaries=[],
    datas=[
        ('security_check.py', '.'),   # include security module
    ],
    hiddenimports=[
        'requests',
        'urllib3',
        'certifi',
        'charset_normalizer',
        'idna'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='ImageScraper',     # internal executable
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,           # hide terminal on macOS
    disable_windowed_traceback=False,
    argv_emulation=True,     # REQUIRED for drag‑and‑drop on macOS
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='ImageScraper',
)

app = BUNDLE(
    coll,
    name='ImageScraper',
    icon=None,              
    bundle_identifier='com.roberto.imagescraper',
)

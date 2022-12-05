# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    ['clsh.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['ssh2.agent', 'ssh2.pkey', 'ssh2.exceptions', 'ssh2.sftp', 'ssh2.sftp_handle', 'ssh2.channel', 'ssh2.listener', 'ssh2.statinfo', 'ssh2.knownhost', 'ssh2.error_codes', 'ssh2.fileinfo', 'ssh2.utils', 'ssh2.publickey'],
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='clsh',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

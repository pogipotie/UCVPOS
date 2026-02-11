# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Pharmacy POS
Builds a standalone Windows .exe
"""

import os
import sys

block_cipher = None

# Get the directory containing the spec file
spec_dir = os.path.dirname(os.path.abspath(SPEC))

a = Analysis(
    ['main.py'],
    pathex=[spec_dir],
    binaries=[],
    datas=[
        ('assets', 'assets'),
        ('config.py', '.'),
        ('settings.json', '.'),
    ],
    hiddenimports=[
        'PyQt6.QtCore',
        'PyQt6.QtWidgets',
        'PyQt6.QtGui',
        'mysql.connector',
        'mysql.connector.plugins',
        'sqlite3',
        'openpyxl',
        'openpyxl.styles',
        'openpyxl.utils',
        'openpyxl.workbook',
        'openpyxl.worksheet',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'pandas',
        'scipy',
        'cv2',
        'torch', 
        'ultralytics',
    ],
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
    name='PharmacyPOS',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/POS.ico',
)

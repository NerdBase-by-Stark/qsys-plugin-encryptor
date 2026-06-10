# -*- mode: python ; coding: utf-8 -*-
#
# PyInstaller spec for the Q-SYS Plugin Encryptor (PySide6).
# Build on WINDOWS:  pyinstaller --noconfirm --clean QSYS-Plugin-Encryptor.spec
# Produces a single portable EXE:  dist\QSYS-Plugin-Encryptor.exe
#
from pathlib import Path

ROOT = Path(SPECPATH)
ICON = ROOT / "assets" / "icon.ico"
icon_arg = str(ICON) if ICON.is_file() else None
datas = [(str(ICON), ".")] if ICON.is_file() else []

# QtWidgets-only app: exclude the big Qt modules it never touches. These are
# safe to drop for a pure-widgets GUI and cut the EXE by ~100 MB. If a build
# ever fails complaining about one of these, remove it from the list.
EXCLUDES = [
    "PySide6.QtWebEngineCore", "PySide6.QtWebEngineWidgets", "PySide6.QtWebEngineQuick",
    "PySide6.QtWebChannel", "PySide6.QtWebSockets",
    "PySide6.QtQml", "PySide6.QtQuick", "PySide6.QtQuick3D", "PySide6.QtQuickWidgets",
    "PySide6.Qt3DCore", "PySide6.Qt3DRender", "PySide6.Qt3DExtras",
    "PySide6.QtCharts", "PySide6.QtDataVisualization", "PySide6.QtGraphs",
    "PySide6.QtMultimedia", "PySide6.QtMultimediaWidgets",
    "PySide6.QtPositioning", "PySide6.QtBluetooth", "PySide6.QtNfc",
    "PySide6.QtSensors", "PySide6.QtSerialPort", "PySide6.QtSql",
    "PySide6.QtTest", "PySide6.QtPdf", "PySide6.QtPdfWidgets",
]

a = Analysis(
    ["src/qplug_encryptor/app.py"],
    pathex=["src"],
    binaries=[],
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=EXCLUDES,
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="QSYS-Plugin-Encryptor",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,                         # Rule 46/34: avoid UPX (Qt DLL + AV issues)
    runtime_tmpdir=None,
    console=False,                     # windowed GUI app (no console flash)
    disable_windowed_traceback=False,
    icon=icon_arg,
    runtime_options=["utf8_mode=1"],   # Rule 44: non-ASCII paths safe when frozen
)

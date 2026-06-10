# Q-SYS Plugin Encryptor (PySide6)

A native Windows app that wraps QSC's `plugin_tool_release.exe`. Drag a `.qplug`
on, hit **Encrypt**, get a `.qplugx`. It only ever runs:

```
plugin_tool_release.exe encrypt  In.qplug  Out.qplugx
```

![icon](assets/icon-preview.png)

The built `.exe` is **self-contained** — QSC's tool and its DLLs are bundled inside it,
so there is nothing to locate or place.

## Use

1. Run `QSYS-Plugin-Encryptor.exe`. The **Tool** row shows "Built-in encryption tool (bundled)".
2. Drag your `.qplug` onto the window (or **Browse**). The output `.qplugx` path
   auto-fills (same folder, same name).
3. Click **Encrypt**. The status line shows the result; the log box shows the tool's
   exit code and output.

## Get the .exe

You don't build this locally — GitHub Actions builds it on a Windows runner. Download
the latest from the repo's **Releases**, or from a workflow run's **Artifacts**. See the
[repo README](../README.md) for the build triggers.

## Build locally (optional)

Requires **Python 3.10+ (64-bit)** and **git** on Windows. Double-click **`BUILD.bat`** —
it creates a venv, installs PySide6 + PyInstaller, fetches and checksum-verifies QSC's
tool, and runs PyInstaller. Output: `dist\QSYS-Plugin-Encryptor.exe` (~55 MB).
PyInstaller can't cross-compile, which is why CI does the Windows build.

To run from source instead (no build):

```
python -m pip install -r requirements.txt
python src\qplug_encryptor\app.py
```

## How the tool is bundled

QSC's binaries are **not** committed here. The build fetches them from our fork
[`NerdBase-by-Stark/PluginEncryptionTool`](https://github.com/NerdBase-by-Stark/PluginEncryptionTool)
at a pinned commit, verifies every file against `tool-checksums.sha256`, then PyInstaller
embeds them (`spec` → `_MEIPASS/tool/`). The app uses this bundled copy at startup.
QSC's MIT notice ships with them (`THIRD-PARTY-LICENSES/`).

To adopt a new upstream version: bump `QSC_TOOL_REF` (in `BUILD.bat` and the workflow)
and update `tool-checksums.sha256` together.

## First run on Windows

An unsigned `.exe` has no SmartScreen reputation yet. If it's blocked: right-click the
`.exe` → **Properties** → tick **Unblock** → **OK**, or **More info → Run anyway**.

## Layout

```
qplug-encryptor-pyside6/
├── BUILD.bat                     # local Windows build (fetch + verify + PyInstaller)
├── QSYS-Plugin-Encryptor.spec    # PyInstaller spec (one-file, windowed)
├── verify_tool.py                # checksum gate for the vendored tool
├── tool-checksums.sha256         # known-good SHA-256s of QSC's files
├── requirements.txt
├── THIRD-PARTY-LICENSES/         # QSC MIT notice
├── assets/icon.ico
└── src/qplug_encryptor/app.py    # the app
```

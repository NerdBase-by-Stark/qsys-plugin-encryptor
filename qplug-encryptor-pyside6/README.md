# Q-SYS Plugin Encryptor (PySide6 desktop app)

A polished native Windows app that wraps QSC's `plugin_tool_release.exe`.
Drag a `.qplug` on, hit **Encrypt**, get a `.qplugx`. It only ever runs:

```
plugin_tool_release.exe encrypt  In.qplug  Out.qplugx
```

![icon](assets/icon-preview.png)

## Build the .exe (do this once, on Windows)

The `.exe` must be built on a **Windows** machine — PyInstaller can't cross-compile,
so it can't be produced on Linux/Mac.

1. Install **Python 3.10+ (64-bit)** from python.org (tick *"Add to PATH"*).
2. Copy this folder to the Windows machine.
3. Double-click **`BUILD.bat`**.
   It makes a venv, installs PySide6 + PyInstaller, and runs PyInstaller.
4. Result: **`dist\QSYS-Plugin-Encryptor.exe`** — a single portable file (~60 MB).

That's the only build step. After that you just run the `.exe`.

## Use

1. Put `QSYS-Plugin-Encryptor.exe` **next to QSC's `release` folder** (the one with
   `plugin_tool_release.exe` and its `libssl*/libcrypto*` DLLs) — or anywhere; it
   remembers the tool location after you set it once.
2. Run the `.exe`.
3. **Tool** row should show "✓ Tool found". If not: **Auto-find** (scans
   Desktop/Downloads/Documents) or **Browse…**.
4. **Drag your `.qplug`** onto the window (or *Browse*). The output `.qplugx` path
   auto-fills (same folder, same name).
5. Click **Encrypt → .qplugx**. Status turns green with the output path + size;
   the dark log box shows the tool's real output and exit code.

Tip: you can also drag `plugin_tool_release.exe` itself onto the window to set the tool.

## Run from source (optional — for tweaking, no build)

```bat
python -m pip install -r requirements.txt
python src\qplug_encryptor\app.py
```

## First run on Windows (SmartScreen / antivirus)

A freshly-built, unsigned `.exe` has no reputation yet, so SmartScreen may say
*"Windows protected your PC"*, and some AV flags PyInstaller one-file builds:

- **SmartScreen:** click **More info → Run anyway**. Or right-click the `.exe` →
  **Properties** → tick **Unblock** → OK.
- **Fewer AV false positives:** switch from one-file to one-folder — in
  `QSYS-Plugin-Encryptor.spec` move `a.binaries, a.datas` out of `EXE(...)` into a
  `COLLECT(...)` (standard PyInstaller one-dir pattern). One-dir trips AV far less.
- **Permanent fix (optional):** code-sign the `.exe`
  (`signtool sign /fd SHA256 /a /tr http://timestamp.digicert.com /td SHA256 ...`).
  Since this is an internal tool you run yourself, Unblock is usually enough.

## Verification status (honest)

- **App logic — verified.** The app was run headless (offscreen) on Linux and the
  full path was exercised end-to-end against a stand-in tool: window construction,
  tool auto-detect + persistence, drag-routing, `.qplugx` auto-derivation, the
  QThread worker, the subprocess call, signal delivery, and the on-disk output. All
  green. The PyInstaller **spec was validated by a real freeze** (the bundled binary
  launches into its event loop).
- **NOT yet verified by me:** the actual Windows `.exe` (built by you via `BUILD.bat`),
  real OS drag-and-drop, and the real `plugin_tool_release.exe` output — those happen
  on your Windows machine. If anything misbehaves, copy the dark log box back to me.

## Layout

```
qplug-encryptor-pyside6/
├── BUILD.bat                     # one-click Windows build
├── QSYS-Plugin-Encryptor.spec    # PyInstaller spec (one-file, windowed, icon, utf8)
├── requirements.txt
├── assets/
│   └── icon.ico                  # app icon (padlock)
└── src/
    └── qplug_encryptor/
        ├── __init__.py           # __version__
        └── app.py                # the whole app (~1 file)
```

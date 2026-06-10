# Q-SYS Plugin Encryptor

Simple Windows GUIs around QSC's `plugin_tool_release.exe`. Drag a `.qplug` on,
hit **Encrypt**, get a `.qplugx`. Both versions only ever shell out to:

```
plugin_tool_release.exe encrypt  In.qplug  Out.qplugx
```

> This repo contains **only our GUI wrappers** (no QSC binaries committed).
> - The **PySide6 `.exe`** is **self-contained** — QSC's tool is fetched from
>   [`qsys-plugins/PluginEncryptionTool`](https://github.com/qsys-plugins/PluginEncryptionTool)
>   and bundled inside it at build time (MIT-licensed; notice shipped with it). Nothing to supply.
> - The **PowerShell** version is a thin wrapper: you point it at your own copy of
>   `plugin_tool_release.exe` (and keep its DLLs beside it).

## Two versions — pick one

| | `qplug-encryptor-gui/` (PowerShell) | `qplug-encryptor-pyside6/` (PySide6) |
|---|---|---|
| **Install needed** | **None** — built into Windows | A one-time build (or use the auto-built `.exe`) |
| **How to open** | Double-click `Encrypt-Plugin-GUI.bat` | Run the built `QSYS-Plugin-Encryptor.exe` |
| **Look & feel** | Plain WinForms | Polished native app, themed, app icon |
| **Best for** | "I just want it working now" | A nice clickable `.exe` to keep/share |

### A. PowerShell — zero install
Copy `qplug-encryptor-gui/` to Windows, double-click **`Encrypt-Plugin-GUI.bat`**. Done.

### B. PySide6 — automated Windows build (no local build needed)
The `.exe` is built for you in the cloud by GitHub Actions on a Windows runner, with
**QSC's encryption tool baked in** — download it, drag a `.qplug`, hit Encrypt. Nothing
to locate, no DLLs to place. CI verifies the tool is bundled (`--selftest`) on every build.

- **Every push** that touches `qplug-encryptor-pyside6/**`, or the **"Run workflow"**
  button (Actions tab → *Build Q-SYS Plugin Encryptor* → *Run workflow*), builds the
  `.exe`. Download it from the run's **Artifacts** → `QSYS-Plugin-Encryptor-windows-exe`.
- **For a clean single-file download**, push a tag and a GitHub **Release** is created
  with the `.exe` attached:
  ```bash
  git tag qplug-encryptor-v1.0.0
  git push origin qplug-encryptor-v1.0.0
  ```

You can still build locally if you prefer: see `qplug-encryptor-pyside6/README.md`
(`BUILD.bat`, needs Python 3.10+ on Windows). PyInstaller can't cross-compile, which
is exactly why the build is automated on a Windows runner.

## First run on Windows (SmartScreen)
A fresh unsigned `.exe` has no reputation yet. If SmartScreen warns:
right-click the `.exe` → **Properties** → tick **Unblock** → **OK**, or
**More info → Run anyway**.

## Layout
```
qsys-plugin-encryptor/
├── .github/workflows/build-qplug-encryptor.yml   # automated Windows .exe build
├── qplug-encryptor-gui/                           # PowerShell version (no install)
└── qplug-encryptor-pyside6/                        # PySide6 app (CI builds this)
```

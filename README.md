# Q-SYS Plugin Encryptor

A Windows GUI for QSC's plugin encryption tool. Drag a `.qplug` on, hit **Encrypt**,
get a `.qplugx`. It only ever runs:

```
plugin_tool_release.exe encrypt  In.qplug  Out.qplugx
```

## Download

Get the latest **`QSYS-Plugin-Encryptor.exe`** from
[**Releases**](https://github.com/NerdBase-by-Stark/qsys-plugin-encryptor/releases/latest).
It's self-contained — QSC's tool is bundled inside, nothing else to install. Run it,
drag a `.qplug`, hit Encrypt.

> First run: if SmartScreen blocks it, right-click the `.exe` → **Properties** →
> tick **Unblock** → **OK**.

## Two versions

| | PySide6 — recommended | PowerShell |
|---|---|---|
| Folder | [`qplug-encryptor-pyside6/`](qplug-encryptor-pyside6/) | [`qplug-encryptor-gui/`](qplug-encryptor-gui/) |
| Get it | download the `.exe` from Releases | copy the folder, double-click the `.bat` |
| QSC tool | bundled in the `.exe` | you supply your own copy |
| Install | none | none (uses built-in Windows PowerShell) |

Each folder's README has the details.

## Build automation

GitHub Actions builds the PySide6 `.exe` on a Windows runner — it fetches QSC's tool
from a pinned, checksum-verified fork, bundles it, and self-tests that it's embedded.
Push a tag (`qplug-encryptor-v*`) to publish a Release. No QSC binaries are committed
here (the tool is MIT-licensed; its notice ships in the build).

## Layout

```
.github/workflows/        automated Windows .exe build
qplug-encryptor-pyside6/  PySide6 app (the .exe)
qplug-encryptor-gui/      PowerShell version
```

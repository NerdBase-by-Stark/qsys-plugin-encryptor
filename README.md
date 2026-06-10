# Q-SYS Plugin Encryptor

A Windows app for QSC's plugin encryption tool. Drag a `.qplug` on, hit **Encrypt**,
get a `.qplugx`. It only ever runs:

```
plugin_tool_release.exe encrypt  In.qplug  Out.qplugx
```

## Download

Get **`QSYS-Plugin-Encryptor.exe`** from
[**Releases**](https://github.com/NerdBase-by-Stark/qsys-plugin-encryptor/releases/latest).
It's self-contained — QSC's tool is bundled inside, nothing else to install. Run it,
drag a `.qplug`, hit **Encrypt**.

> First run: if SmartScreen blocks it, right-click the `.exe` → **Properties** →
> tick **Unblock** → **OK**.

## How it's built

GitHub Actions builds the `.exe` on a Windows runner: it fetches QSC's tool from a
pinned, checksum-verified fork, bundles it, and self-tests that it's embedded. Push a
tag (`qplug-encryptor-v*`) to publish a Release. No QSC binaries are committed here
(the tool is MIT-licensed; its notice ships in the build).

App source and build details: [`qplug-encryptor-pyside6/`](qplug-encryptor-pyside6/).

## Layout

```
.github/workflows/        automated Windows .exe build
qplug-encryptor-pyside6/  the app (PySide6) + build
```

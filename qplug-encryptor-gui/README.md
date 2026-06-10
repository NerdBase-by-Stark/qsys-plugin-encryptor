# Q-SYS Plugin Encryptor (GUI)

A tiny, no-install Windows GUI around QSC's `plugin_tool_release.exe`.
Drag a `.qplug` on, hit **Encrypt**, get a `.qplugx`. That's it.

It wraps exactly this command:

```
plugin_tool_release.exe encrypt  In.qplug  Out.qplugx
```

## Install (none, really)

1. Copy this whole folder to your **Windows** machine.
2. Make sure you have QSC's encryption tool — the folder named `release` that
   contains `plugin_tool_release.exe` **and its DLLs** (`libssl-1_1-x64.dll`,
   `libcrypto-1_1-x64.dll`, etc. — the .exe won't run without them).
   - Easiest: drop this GUI folder **next to** that `release` folder, or drop
     these two files **inside** the `release` folder. It auto-detects either.

No Python, no .NET install, no admin rights. Uses the PowerShell + WinForms that
already ship with Windows 10/11.

## Use

1. Double-click **`Encrypt-Plugin-GUI.bat`**.
2. **Tool**: should show "✓ Tool found". If not, click **Auto-find** (scans
   Desktop / Downloads / Documents) or **Browse…** to point at
   `plugin_tool_release.exe`. It remembers your choice after the first time
   (saved to `qplug-encryptor.config` beside the script).
3. **Drag your `.qplug`** onto the window (or click *Browse for a .qplug*).
   The output `.qplugx` path is filled in automatically (same folder, same name).
4. Click **Encrypt → .qplugx**.
5. The status line turns green with the output path + size, or red with the
   tool's error output in the black log box.

Tip: you can also drag `plugin_tool_release.exe` itself onto the window to set
the tool.

## Notes / honesty

- This is just a front-end. All real work is done by QSC's `plugin_tool_release.exe`.
- The GUI reports success when the `.qplugx` file actually appears on disk, and
  always shows the tool's real exit code + output in the log.
- If Windows SmartScreen warns about the `.bat`, it's because it's unsigned —
  "More info" → "Run anyway". (It only launches the bundled `.ps1`.)

## Troubleshooting

| Symptom | Fix |
|---|---|
| "Tool not set" and Auto-find fails | Click **Browse…**, point at `plugin_tool_release.exe` inside its `release` folder. |
| Encrypt fails, log mentions a missing DLL | The `.exe` was moved away from its DLLs. Keep `plugin_tool_release.exe` together with the `libssl*/libcrypto*` DLLs from QSC's `release` folder. |
| `.bat` flashes and closes | Run it from PowerShell to see the error: `powershell -ExecutionPolicy Bypass -STA -File Q-SYS-Plugin-Encryptor.ps1` |
| Drag-and-drop does nothing | Launch via the `.bat` (it passes `-STA`, which drag-drop needs). Don't run the `.ps1` from an already-open non-STA shell. |

@echo off
rem  Double-click this to launch the Q-SYS Plugin Encryptor GUI.
rem  -STA is required for drag-and-drop; -ExecutionPolicy Bypass avoids the
rem  "scripts are disabled" error without changing any machine settings.
powershell.exe -NoProfile -ExecutionPolicy Bypass -STA -File "%~dp0Q-SYS-Plugin-Encryptor.ps1"
if errorlevel 1 (
    echo.
    echo The GUI exited with an error. Press any key to close.
    pause >nul
)

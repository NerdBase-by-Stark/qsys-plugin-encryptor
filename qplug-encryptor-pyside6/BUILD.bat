@echo off
rem ===========================================================================
rem  Build the Q-SYS Plugin Encryptor into a single Windows .exe.
rem  Run this ON WINDOWS (needs Python 3.10+ 64-bit installed).
rem  Output: dist\QSYS-Plugin-Encryptor.exe
rem ===========================================================================
setlocal
cd /d "%~dp0"

rem -- pick a python launcher
where py >nul 2>&1 && (set "PY=py -3") || (set "PY=python")

echo.
echo [1/4] Creating virtual environment (.venv) ...
if not exist ".venv\Scripts\python.exe" (
    %PY% -m venv .venv || goto :fail
)

echo [2/4] Installing dependencies ...
call ".venv\Scripts\activate.bat" || goto :fail
python -m pip install --upgrade pip || goto :fail
python -m pip install -r requirements.txt || goto :fail

echo [3/4] Running PyInstaller ...
pyinstaller --noconfirm --clean QSYS-Plugin-Encryptor.spec || goto :fail

echo [4/4] Done.
echo.
echo   EXE built:  "%cd%\dist\QSYS-Plugin-Encryptor.exe"
echo.
echo   Put it next to QSC's "release" folder (the one with plugin_tool_release.exe
echo   and its DLLs) so it auto-detects the tool, then just run it.
echo.
pause
exit /b 0

:fail
echo.
echo *** BUILD FAILED *** see the messages above.
pause
exit /b 1

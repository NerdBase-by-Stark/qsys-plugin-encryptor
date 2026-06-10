@echo off
rem ===========================================================================
rem  Build the Q-SYS Plugin Encryptor into a single, SELF-CONTAINED Windows .exe
rem  (QSC's encryption tool is fetched + bundled inside it).
rem  Run this ON WINDOWS (needs Python 3.10+ 64-bit and git installed).
rem  Output: dist\QSYS-Plugin-Encryptor.exe
rem ===========================================================================
setlocal
cd /d "%~dp0"

rem -- QSC tool pinned to a specific upstream commit (keep in sync with the workflow)
set "QSC_TOOL_REF=a3e0917ce61afb8d122bd17765027f712d514df7"

rem -- pick a python launcher
where py >nul 2>&1 && (set "PY=py -3") || (set "PY=python")

echo.
echo [1/5] Creating virtual environment (.venv) ...
if not exist ".venv\Scripts\python.exe" (
    %PY% -m venv .venv || goto :fail
)

echo [2/5] Installing dependencies ...
call ".venv\Scripts\activate.bat" || goto :fail
python -m pip install --upgrade pip || goto :fail
python -m pip install -r requirements.txt || goto :fail

echo [3/5] Fetching QSC encryption tool (pinned) ...
if not exist "vendor\plugin-tool\plugin_tool_release.exe" (
    where git >nul 2>&1 || (echo git is required to fetch the QSC tool & goto :fail)
    rmdir /s /q "%TEMP%\qsc-tool" 2>nul
    git clone --quiet https://github.com/qsys-plugins/PluginEncryptionTool.git "%TEMP%\qsc-tool" || goto :fail
    git -C "%TEMP%\qsc-tool" checkout --quiet %QSC_TOOL_REF% || goto :fail
    mkdir "vendor\plugin-tool" 2>nul
    copy /Y "%TEMP%\qsc-tool\release\*" "vendor\plugin-tool\" >nul || goto :fail
    copy /Y "%TEMP%\qsc-tool\license.txt" "vendor\plugin-tool\QSC-PluginEncryptionTool-LICENSE.txt" >nul
)

echo [4/5] Running PyInstaller ...
pyinstaller --noconfirm --clean QSYS-Plugin-Encryptor.spec || goto :fail

echo [5/5] Done.
echo.
echo   Self-contained EXE built:  "%cd%\dist\QSYS-Plugin-Encryptor.exe"
echo   QSC's tool is baked in - just run the .exe, drag a .qplug, hit Encrypt.
echo.
pause
exit /b 0

:fail
echo.
echo *** BUILD FAILED *** see the messages above.
pause
exit /b 1

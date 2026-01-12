@echo off
chcp 65001 >nul
echo ========================================
echo Node.js Environment Check
echo ========================================
echo.

echo [1] Checking Node.js installation...
where node >nul 2>&1
if %errorlevel% equ 0 (
    echo    [OK] Node.js is installed
    node --version
) else (
    echo    [FAIL] Node.js not found
)

echo.
echo [2] Checking npm availability...
where npm >nul 2>&1
if %errorlevel% equ 0 (
    echo    [OK] npm is installed
    npm --version
) else (
    echo    [FAIL] npm not found
)

echo.
echo [3] Checking common installation paths...
if exist "C:\Program Files\nodejs\node.exe" (
    echo    [FOUND] C:\Program Files\nodejs\node.exe
) else (
    echo    [NOT FOUND] C:\Program Files\nodejs\
)

if exist "%LOCALAPPDATA%\Programs\nodejs\node.exe" (
    echo    [FOUND] %LOCALAPPDATA%\Programs\nodejs\node.exe
) else (
    echo    [NOT FOUND] %LOCALAPPDATA%\Programs\nodejs\
)

echo.
echo [4] Checking PATH environment variable...
echo %PATH% | findstr /i "node" >nul
if %errorlevel% equ 0 (
    echo    [OK] PATH contains node-related paths
    for %%p in (%PATH%) do (
        echo %%p | findstr /i "node" >nul && echo       %%p
    )
) else (
    echo    [FAIL] No node-related paths found in PATH
)

echo.
echo ========================================
echo Diagnosis Complete
echo ========================================
echo.
echo If Node.js is not installed:
echo 1. Visit https://nodejs.org/ to download and install
echo 2. Or use nvm-windows: https://github.com/coreybutler/nvm-windows
echo.
echo After installation, restart your terminal/PowerShell
echo.
pause

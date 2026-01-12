@echo off
chcp 65001 >nul
echo ========================================
echo Node.js 环境检查
echo ========================================
echo.

echo [1] 检查 Node.js 是否安装...
where node >nul 2>&1
if %errorlevel% equ 0 (
    echo    [OK] Node.js 已安装
    node --version
) else (
    echo    [失败] Node.js 未找到
)

echo.
echo [2] 检查 npm 是否可用...
where npm >nul 2>&1
if %errorlevel% equ 0 (
    echo    [OK] npm 已安装
    npm --version
) else (
    echo    [失败] npm 未找到
)

echo.
echo [3] 检查常见安装路径...
if exist "C:\Program Files\nodejs\node.exe" (
    echo    [找到] C:\Program Files\nodejs\node.exe
) else (
    echo    [未找到] C:\Program Files\nodejs\
)

if exist "%LOCALAPPDATA%\Programs\nodejs\node.exe" (
    echo    [找到] %LOCALAPPDATA%\Programs\nodejs\node.exe
) else (
    echo    [未找到] %LOCALAPPDATA%\Programs\nodejs\
)

echo.
echo [4] 检查 PATH 环境变量...
echo %PATH% | findstr /i "node" >nul
if %errorlevel% equ 0 (
    echo    [OK] PATH 中包含 node 相关路径
    echo %PATH% | findstr /i "node"
) else (
    echo    [失败] PATH 中未找到 node 相关路径
)

echo.
echo ========================================
echo 诊断完成
echo ========================================
echo.
echo 如果 Node.js 未安装，请：
echo 1. 访问 https://nodejs.org/ 下载安装
echo 2. 或使用 nvm-windows: https://github.com/coreybutler/nvm-windows
echo.
pause

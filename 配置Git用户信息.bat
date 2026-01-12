@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ========================================
echo 配置Git用户信息
echo ========================================
echo.

echo 当前Git配置:
echo.
git config user.name >nul 2>&1
if %errorlevel% equ 0 (
    echo [已配置] 用户名称: 
    git config user.name
) else (
    echo [未配置] 用户名称
)
echo.

git config user.email >nul 2>&1
if %errorlevel% equ 0 (
    echo [已配置] 用户邮箱: 
    git config user.email
) else (
    echo [未配置] 用户邮箱
)
echo.

echo ========================================
echo 开始配置
echo ========================================
echo.

set /p user_name="请输入你的姓名: "
if "%user_name%"=="" (
    echo [错误] 姓名不能为空
    pause
    exit /b 1
)

set /p user_email="请输入你的邮箱: "
if "%user_email%"=="" (
    echo [错误] 邮箱不能为空
    pause
    exit /b 1
)

echo.
echo 正在配置...
git config user.name "%user_name%"
git config user.email "%user_email%"

echo.
echo ========================================
echo [成功] Git用户信息已配置
echo ========================================
echo.
echo 用户名称: %user_name%
echo 用户邮箱: %user_email%
echo.

echo 注意：
echo - 这是本地配置，只影响当前电脑
echo - 如果要在另一台电脑上使用，需要重新配置
echo - 或者使用全局配置（影响所有Git仓库）
echo.

set /p set_global="是否同时设置为全局配置？(Y/N，默认N): "
if /i "%set_global%"=="Y" (
    git config --global user.name "%user_name%"
    git config --global user.email "%user_email%"
    echo [成功] 已设置为全局配置
    echo.
)

pause

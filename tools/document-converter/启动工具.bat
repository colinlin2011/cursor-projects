@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ========================================
echo 文档转换工具
echo ========================================
echo.
echo 正在启动...
echo.

python launcher.py

pause

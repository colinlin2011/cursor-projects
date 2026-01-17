@echo off
chcp 65001 >nul
echo ========================================
echo 专利申请文档转Word工具
echo ========================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未检测到Python，请先安装Python
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM 检查pandoc是否安装
pandoc --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未检测到pandoc，请先安装pandoc
    echo 下载地址: https://pandoc.org/installing.html
    echo 或使用: choco install pandoc
    pause
    exit /b 1
)

REM 安装依赖
echo 正在检查并安装依赖...
python -m pip install -q pypandoc
if errorlevel 1 (
    echo 警告: 依赖安装可能失败，请手动运行: pip install pypandoc
)

REM 运行转换脚本
echo.
echo 开始转换...
echo.
python convert_to_word.py

pause

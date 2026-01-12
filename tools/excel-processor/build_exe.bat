@echo off
chcp 65001 >nul
echo ========================================
echo Excel 处理工具 - 打包脚本
echo ========================================
echo.

REM 检查 Python 是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Python，请先安装 Python 3.8 或更高版本
    pause
    exit /b 1
)

echo [1/4] 检查依赖包...
python -m pip install --upgrade pip >nul 2>&1
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo [错误] 依赖包安装失败
    pause
    exit /b 1
)

echo.
echo [2/4] 安装 PyInstaller...
python -m pip install pyinstaller
if errorlevel 1 (
    echo [错误] PyInstaller 安装失败
    pause
    exit /b 1
)

echo.
echo [3/4] 清理旧的打包文件...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "__pycache__" rmdir /s /q "__pycache__"

echo.
echo [4/4] 开始打包...
echo 这可能需要几分钟时间，请耐心等待...
echo.
python -m PyInstaller build_exe.spec --clean --noconfirm

if errorlevel 1 (
    echo.
    echo [错误] 打包失败，请检查错误信息
    pause
    exit /b 1
)

echo.
echo ========================================
echo 打包完成！
echo ========================================
echo.
echo 可执行文件位置: dist\Excel处理工具.exe
echo.
echo 提示：
echo 1. 首次运行可能需要几秒钟启动时间
echo 2. 如果杀毒软件报警，请添加信任（这是正常现象）
echo 3. 可以将 dist 文件夹中的 exe 文件复制到任何位置使用
echo.
pause

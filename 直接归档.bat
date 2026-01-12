@echo off
chcp 65001 >nul
echo ========================================
echo Excel 处理工具 - 直接归档
echo ========================================
echo.

REM 切换到项目目录
cd /d "%~dp0"

REM 检查并创建目标目录
if not exist "tools\excel-processor" (
    echo 创建目录结构...
    mkdir "tools\excel-processor"
    mkdir "tools\excel-processor\utils"
) else (
    echo [警告] tools\excel-processor 已存在
    echo 是否覆盖？(Y/N)
    set /p overwrite=
    if /i not "%overwrite%"=="Y" (
        echo 归档已取消
        pause
        exit /b 0
    )
    echo 正在删除旧目录...
    rmdir /s /q "tools\excel-processor"
    mkdir "tools\excel-processor"
    mkdir "tools\excel-processor\utils"
)

echo.
echo 正在移动文件...
echo.

REM 移动主要文件
if exist "main.py" (
    move /Y "main.py" "tools\excel-processor\" && echo [OK] main.py || echo [失败] main.py
)
if exist "launcher.py" (
    move /Y "launcher.py" "tools\excel-processor\" && echo [OK] launcher.py || echo [失败] launcher.py
)
if exist "config.py" (
    move /Y "config.py" "tools\excel-processor\" && echo [OK] config.py || echo [失败] config.py
)
if exist "requirements.txt" (
    move /Y "requirements.txt" "tools\excel-processor\" && echo [OK] requirements.txt || echo [失败] requirements.txt
)

REM 移动打包相关文件
if exist "build_exe.bat" (
    move /Y "build_exe.bat" "tools\excel-processor\" && echo [OK] build_exe.bat || echo [失败] build_exe.bat
)
if exist "build_exe.sh" (
    move /Y "build_exe.sh" "tools\excel-processor\" && echo [OK] build_exe.sh || echo [失败] build_exe.sh
)
if exist "build_exe.spec" (
    move /Y "build_exe.spec" "tools\excel-processor\" && echo [OK] build_exe.spec || echo [失败] build_exe.spec
)

REM 移动工具模块
if exist "utils\excel_handler.py" (
    move /Y "utils\excel_handler.py" "tools\excel-processor\utils\" && echo [OK] excel_handler.py || echo [失败] excel_handler.py
)
if exist "utils\__init__.py" (
    move /Y "utils\__init__.py" "tools\excel-processor\utils\" && echo [OK] __init__.py || echo [失败] __init__.py
)

REM 移动文档文件
if exist "README.md" (
    move /Y "README.md" "tools\excel-processor\" && echo [OK] README.md || echo [失败] README.md
)
if exist "快速开始.md" (
    move /Y "快速开始.md" "tools\excel-processor\" && echo [OK] 快速开始.md || echo [失败] 快速开始.md
)
if exist "打包说明.md" (
    move /Y "打包说明.md" "tools\excel-processor\" && echo [OK] 打包说明.md || echo [失败] 打包说明.md
)
if exist "修复说明.md" (
    move /Y "修复说明.md" "tools\excel-processor\" && echo [OK] 修复说明.md || echo [失败] 修复说明.md
)

REM 处理打包文件
echo.
if exist "dist\Excel处理工具.exe" (
    echo 检测到已打包的 exe 文件
    echo 是否保留打包文件？(Y/N)
    set /p keep_build=
    if /i "%keep_build%"=="Y" (
        if not exist "tools\excel-processor\dist" mkdir "tools\excel-processor\dist"
        if not exist "tools\excel-processor\build" mkdir "tools\excel-processor\build"
        xcopy /Y /E /I "dist\*" "tools\excel-processor\dist\" >nul 2>&1 && echo [OK] dist 目录已复制 || echo [失败] dist 目录
        xcopy /Y /E /I "build\*" "tools\excel-processor\build\" >nul 2>&1 && echo [OK] build 目录已复制 || echo [失败] build 目录
    ) else (
        echo 清理打包文件...
        rmdir /s /q build 2>nul
        rmdir /s /q dist 2>nul
    )
) else (
    echo 清理临时文件...
    rmdir /s /q build 2>nul
    rmdir /s /q dist 2>nul
)

REM 清理空目录
if exist "utils" (
    dir /b "utils" 2>nul | findstr /v "^$" >nul || rmdir "utils" 2>nul
)

echo.
echo ========================================
echo 归档完成！
echo ========================================
echo.
echo 项目已移动到: tools\excel-processor\
echo.
dir /b "tools\excel-processor" 2>nul
echo.
pause

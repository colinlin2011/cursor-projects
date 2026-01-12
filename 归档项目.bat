@echo off
chcp 65001 >nul
echo ========================================
echo Excel 处理工具 - 项目归档脚本
echo ========================================
echo.

REM 检查是否已经归档过
if exist "tools\excel-processor" (
    echo [警告] 检测到 tools\excel-processor 目录已存在
    echo 是否要覆盖？(Y/N)
    set /p overwrite=
    if /i not "%overwrite%"=="Y" (
        echo 归档已取消
        pause
        exit /b 0
    )
    echo 正在删除旧目录...
    rmdir /s /q "tools\excel-processor"
)

echo [1/5] 创建目录结构...
if not exist "tools" mkdir tools
if not exist "tools\excel-processor" mkdir tools\excel-processor
if not exist "tools\excel-processor\utils" mkdir tools\excel-processor\utils

echo [2/5] 移动源代码文件...
if exist "main.py" (
    move /Y main.py tools\excel-processor\ && echo    - main.py 已移动 || echo    [错误] main.py 移动失败
) else (
    echo    [警告] main.py 不存在
)
if exist "launcher.py" (
    move /Y launcher.py tools\excel-processor\ && echo    - launcher.py 已移动 || echo    [错误] launcher.py 移动失败
) else (
    echo    [警告] launcher.py 不存在
)
if exist "config.py" (
    move /Y config.py tools\excel-processor\ && echo    - config.py 已移动 || echo    [错误] config.py 移动失败
) else (
    echo    [警告] config.py 不存在
)
if exist "requirements.txt" (
    move /Y requirements.txt tools\excel-processor\ && echo    - requirements.txt 已移动 || echo    [错误] requirements.txt 移动失败
) else (
    echo    [警告] requirements.txt 不存在
)

echo [3/5] 移动工具模块...
if exist "utils" (
    if exist "utils\excel_handler.py" (
        move /Y utils\excel_handler.py tools\excel-processor\utils\ && echo    - excel_handler.py 已移动 || echo    [错误] excel_handler.py 移动失败
    )
    if exist "utils\__init__.py" (
        move /Y utils\__init__.py tools\excel-processor\utils\ && echo    - __init__.py 已移动 || echo    [错误] __init__.py 移动失败
    )
    REM 尝试删除空目录
    rmdir utils 2>nul
) else (
    echo    [警告] utils 目录不存在
)

echo [4/5] 移动配置和文档文件...
if exist "build_exe.bat" (
    move /Y build_exe.bat tools\excel-processor\ && echo    - build_exe.bat 已移动 || echo    [错误] build_exe.bat 移动失败
)
if exist "build_exe.sh" (
    move /Y build_exe.sh tools\excel-processor\ && echo    - build_exe.sh 已移动 || echo    [错误] build_exe.sh 移动失败
)
if exist "build_exe.spec" (
    move /Y build_exe.spec tools\excel-processor\ && echo    - build_exe.spec 已移动 || echo    [错误] build_exe.spec 移动失败
)
if exist "README.md" (
    move /Y README.md tools\excel-processor\ && echo    - README.md 已移动 || echo    [错误] README.md 移动失败
)
if exist "快速开始.md" (
    move /Y 快速开始.md tools\excel-processor\ && echo    - 快速开始.md 已移动 || echo    [错误] 快速开始.md 移动失败
)
if exist "打包说明.md" (
    move /Y 打包说明.md tools\excel-processor\ && echo    - 打包说明.md 已移动 || echo    [错误] 打包说明.md 移动失败
)
if exist "修复说明.md" (
    move /Y 修复说明.md tools\excel-processor\ && echo    - 修复说明.md 已移动 || echo    [错误] 修复说明.md 移动失败
)

echo [5/5] 处理打包文件...
if exist "dist\Excel处理工具.exe" (
    echo 检测到已打包的 exe 文件
    echo 是否保留打包文件？(Y/N，建议保留以便后续使用)
    set /p keep_build=
    if /i "%keep_build%"=="Y" (
        if not exist "tools\excel-processor\dist" mkdir tools\excel-processor\dist
        if not exist "tools\excel-processor\build" mkdir tools\excel-processor\build
        move /Y dist\* tools\excel-processor\dist\ >nul 2>&1
        move /Y build\* tools\excel-processor\build\ >nul 2>&1
        echo 已保留打包文件
    ) else (
        echo 正在清理打包文件...
        rmdir /s /q build >nul 2>&1
        rmdir /s /q dist >nul 2>&1
    )
) else (
    echo 未找到打包文件，清理临时文件...
    rmdir /s /q build >nul 2>&1
    rmdir /s /q dist >nul 2>&1
)

REM 清理空目录
if exist "utils" rmdir utils >nul 2>&1

echo.
echo ========================================
echo 归档完成！
echo ========================================
echo.
echo 项目已移动到: tools\excel-processor\
echo.
echo 后续操作：
echo 1. 进入工具目录: cd tools\excel-processor
echo 2. 运行工具: streamlit run main.py
echo 3. 打包工具: build_exe.bat
echo.
echo 现在可以在 Cursor Project 根目录开始新的工具项目了！
echo.
pause

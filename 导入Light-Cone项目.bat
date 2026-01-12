@echo off
chcp 65001 >nul
echo ========================================
echo 导入 Light-Cone-2025 项目
echo ========================================
echo.

REM 切换到项目目录
cd /d "%~dp0"

REM 检查 git 是否安装
where git >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到 Git，请先安装 Git
    echo 下载地址: https://git-scm.com/download/win
    pause
    exit /b 1
)

REM 创建网页应用目录
if not exist "web-apps" (
    echo 创建网页应用目录...
    mkdir "web-apps"
)

REM 检查目标目录
if exist "web-apps\Light-Cone-2025" (
    echo [警告] 目标目录已存在: web-apps\Light-Cone-2025
    echo 是否覆盖？(Y/N)
    set /p overwrite=
    if /i not "%overwrite%"=="Y" (
        echo 导入已取消
        pause
        exit /b 0
    )
    echo 正在删除旧目录...
    rmdir /s /q "web-apps\Light-Cone-2025"
)

echo.
echo 正在从 GitHub 克隆 Light-Cone-2025 项目...
echo.

echo 请输入 GitHub 仓库地址：
echo 格式示例：
echo   1. 完整地址: https://github.com/username/Light-Cone-2025.git
echo   2. 简短格式: username/Light-Cone-2025
echo   3. 仅用户名（将自动拼接）: username
echo.
set /p repo_input="请输入: "

REM 处理输入
if "%repo_input:https://github.com/%"=="%repo_input%" (
    if "%repo_input:http://github.com/%"=="%repo_input%" (
        REM 不是完整 URL，可能是简短格式或用户名
        if not "%repo_input:/=%"=="%repo_input%" (
            REM 包含斜杠，是 username/repo 格式
            set "repo_url=https://github.com/%repo_input%.git"
        ) else (
            REM 只有用户名
            set "repo_url=https://github.com/%repo_input%/Light-Cone-2025.git"
        )
    ) else (
        REM HTTP URL
        set "repo_url=%repo_input:.git=%"
        set "repo_url=%repo_url%.git"
    )
) else (
    REM HTTPS URL
    set "repo_url=%repo_input:.git=%"
    set "repo_url=%repo_url%.git"
)

echo 仓库地址: %repo_url%
echo.

git clone "%repo_url%" "web-apps\Light-Cone-2025"

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo 导入成功！
    echo ========================================
    echo.
    echo 项目已克隆到: web-apps\Light-Cone-2025
    echo.
    echo 后续操作：
    echo 1. 进入项目目录: cd web-apps\Light-Cone-2025
    echo 2. 查看项目说明: type README.md
    echo 3. 安装依赖（根据项目类型）:
    echo    - Node.js 项目: npm install
    echo    - Python 项目: pip install -r requirements.txt
    echo.
) else (
    echo.
    echo [错误] 克隆失败
    echo.
    echo 可能的原因：
    echo 1. 仓库地址不正确
    echo 2. 仓库不存在或为私有仓库
    echo 3. 网络连接问题
    echo.
    echo 请手动运行以下命令：
    echo git clone https://github.com/您的用户名/Light-Cone-2025.git web-apps\Light-Cone-2025
    echo.
)

pause

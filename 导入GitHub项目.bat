@echo off
chcp 65001 >nul
echo ========================================
echo 从 GitHub 导入项目
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

echo 请输入项目类型：
echo 1. 网页应用 (web-apps)
echo 2. Python 工具 (tools)
echo 3. 其他 (other)
echo.
set /p project_type="请选择 (1/2/3): "

if "%project_type%"=="1" (
    set category_dir=web-apps
    set category_name=网页应用
) else if "%project_type%"=="2" (
    set category_dir=tools
    set category_name=Python工具
) else if "%project_type%"=="3" (
    set category_dir=other
    set category_name=其他项目
) else (
    echo [错误] 无效的选择
    pause
    exit /b 1
)

echo.
echo 请输入 GitHub 仓库信息：
echo 格式示例: username/repository 或 https://github.com/username/repository.git
echo.
set /p repo_input="仓库地址或名称: "

REM 处理输入
set "repo_url=%repo_input%"
if not "%repo_input:https://github.com/%"=="%repo_input%" (
    REM 已经是完整 URL
    set "repo_name=%repo_input:https://github.com/=%"
    set "repo_name=%repo_name:.git=%"
    set "repo_name=%repo_name:/=%"
) else if not "%repo_input:http://github.com/%"=="%repo_input%" (
    REM HTTP URL
    set "repo_name=%repo_input:http://github.com/=%"
    set "repo_name=%repo_name:.git=%"
    set "repo_name=%repo_name:/=%"
) else if not "%repo_input:/=%"=="%repo_input%" (
    REM username/repo 格式
    set "repo_name=%repo_input%"
    set "repo_url=https://github.com/%repo_input%.git"
) else (
    REM 只有仓库名，需要用户名
    echo 请输入 GitHub 用户名：
    set /p github_user=
    set "repo_name=%github_user%/%repo_input%"
    set "repo_url=https://github.com/%github_user%/%repo_input%.git"
)

REM 提取项目名称（最后一个斜杠后的部分）
for /f "tokens=* delims=" %%a in ("%repo_name%") do set "project_name=%%~nxa"
for /f "tokens=2 delims=/" %%a in ("%repo_name%") do set "project_name=%%a"

echo.
echo 项目信息：
echo   类型: %category_name%
echo   仓库: %repo_name%
echo   项目名: %project_name%
echo   目标目录: %category_dir%\%project_name%
echo.

REM 检查目标目录
if exist "%category_dir%\%project_name%" (
    echo [警告] 目标目录已存在: %category_dir%\%project_name%
    echo 是否覆盖？(Y/N)
    set /p overwrite=
    if /i not "%overwrite%"=="Y" (
        echo 导入已取消
        pause
        exit /b 0
    )
    echo 正在删除旧目录...
    rmdir /s /q "%category_dir%\%project_name%"
)

REM 创建分类目录
if not exist "%category_dir%" (
    echo 创建分类目录: %category_dir%
    mkdir "%category_dir%"
)

echo.
echo 正在从 GitHub 克隆项目...
echo 仓库地址: %repo_url%
echo.

git clone "%repo_url%" "%category_dir%\%project_name%"

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo 导入成功！
    echo ========================================
    echo.
    echo 项目已克隆到: %category_dir%\%project_name%
    echo.
    echo 后续操作：
    echo 1. 进入项目目录: cd %category_dir%\%project_name%
    echo 2. 查看项目说明: type README.md
    echo 3. 安装依赖（如需要）: npm install 或 pip install -r requirements.txt
    echo.
) else (
    echo.
    echo [错误] 克隆失败
    echo 请检查：
    echo 1. 仓库地址是否正确
    echo 2. 是否有访问权限
    echo 3. 网络连接是否正常
    echo.
)

pause

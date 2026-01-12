@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ========================================
echo Git仓库一键初始化并推送
echo ========================================
echo.

REM 步骤1: 检查并初始化Git仓库
if not exist .git (
    echo [步骤1] 正在初始化Git仓库...
    git init
    if %errorlevel% neq 0 (
        echo [错误] Git未安装或初始化失败
        echo 请安装Git: https://git-scm.com/download/win
        pause
        exit /b 1
    )
    echo [成功] Git仓库已初始化
    echo.
) else (
    echo [提示] Git仓库已存在
    echo.
)

REM 步骤2: 检查Git用户配置
git config user.name >nul 2>&1
if %errorlevel% neq 0 (
    echo [步骤2] 需要配置Git用户信息
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
    git config user.name "%user_name%"
    git config user.email "%user_email%"
    echo [成功] Git用户信息已配置
    echo.
) else (
    echo [步骤2] Git用户信息已配置
    git config user.name
    git config user.email
    echo.
)

REM 步骤3: 检查远程仓库
git remote get-url origin >nul 2>&1
if %errorlevel% neq 0 (
    echo [步骤3] 需要配置远程仓库
    echo.
    echo 请先创建远程仓库:
    echo 1. 访问 https://github.com 或 https://gitee.com
    echo 2. 创建新仓库
    echo 3. 复制仓库地址
    echo.
    set /p repo_url="请输入仓库地址（直接回车跳过）: "
    if not "%repo_url%"=="" (
        git remote add origin "%repo_url%"
        if %errorlevel% equ 0 (
            echo [成功] 远程仓库已配置
            echo.
        ) else (
            echo [错误] 配置远程仓库失败
            echo.
        )
    ) else (
        echo [提示] 已跳过远程仓库配置
        echo 可以稍后运行: 配置远程仓库.bat
        echo.
    )
) else (
    echo [步骤3] 远程仓库已配置
    git remote -v
    echo.
)

REM 步骤4: 添加并提交文件
echo [步骤4] 正在添加文件...
git add .
echo.

echo [步骤4] 正在提交文件...
set /p commit_msg="请输入提交信息（直接回车使用默认）: "
if "%commit_msg%"=="" set commit_msg=初始提交：创建学习系统和工具

git commit -m "%commit_msg%"
if %errorlevel% neq 0 (
    echo [警告] 提交失败，可能没有需要提交的文件
    echo.
) else (
    echo [成功] 文件已提交
    echo.
)

REM 步骤5: 推送到远程仓库
git remote get-url origin >nul 2>&1
if %errorlevel% equ 0 (
    echo [步骤5] 正在推送到远程仓库...
    echo.
    
    REM 检查分支名称
    git branch --show-current >nul 2>&1
    if %errorlevel% equ 0 (
        git branch --show-current | findstr /C:"main" >nul
        if %errorlevel% neq 0 (
            echo [提示] 当前分支不是main，正在重命名...
            git branch -M main
        )
    ) else (
        echo [提示] 创建main分支...
        git branch -M main
    )
    
    git push -u origin main
    
    if %errorlevel% equ 0 (
        echo.
        echo ========================================
        echo [成功] 已推送到远程仓库
        echo ========================================
    ) else (
        echo.
        echo ========================================
        echo [警告] 推送可能失败，可能的原因:
        echo 1. 需要身份验证（GitHub需要Token）
        echo 2. 网络连接问题
        echo 3. 远程仓库地址错误
        echo.
        echo 解决方法:
        echo - GitHub: 需要创建Personal Access Token
        echo - Gitee: 可以直接使用账号密码
        echo ========================================
    )
) else (
    echo [步骤5] 跳过推送（未配置远程仓库）
    echo.
    echo 配置远程仓库后，可以运行: 同步到远程.bat
    echo.
)

echo.
echo ========================================
echo 完成
echo ========================================
echo.
pause

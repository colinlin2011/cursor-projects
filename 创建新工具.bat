@echo off
chcp 65001 >nul
echo ========================================
echo 创建新工具项目
echo ========================================
echo.

if not exist "tools" mkdir tools

echo 请输入新工具的名称（例如: pdf-processor, image-tool）:
set /p tool_name=

if "%tool_name%"=="" (
    echo 错误：工具名称不能为空
    pause
    exit /b 1
)

set tool_path=tools\%tool_name%

if exist "%tool_path%" (
    echo [错误] 工具目录已存在: %tool_path%
    pause
    exit /b 1
)

echo.
echo 正在创建工具项目: %tool_name%
echo 项目路径: %tool_path%
echo.

echo [1/4] 创建目录结构...
mkdir "%tool_path%"
mkdir "%tool_path%\utils"

echo [2/4] 复制模板文件...
if exist "项目模板\main.py" copy /Y "项目模板\main.py" "%tool_path%\" >nul
if exist "项目模板\config.py" copy /Y "项目模板\config.py" "%tool_path%\" >nul
if exist "项目模板\requirements.txt" copy /Y "项目模板\requirements.txt" "%tool_path%\" >nul
if exist "项目模板\README.md" copy /Y "项目模板\README.md" "%tool_path%\" >nul
if exist "项目模板\utils\__init__.py" (
    copy /Y "项目模板\utils\__init__.py" "%tool_path%\utils\" >nul 2>&1
)

echo [3/4] 更新配置文件...
cd "%tool_path%"
(
echo # %tool_name%
echo.
echo 这是一个新工具项目，请根据需要进行开发。
) > README.md

echo [4/4] 完成！
echo.
echo ========================================
echo 新工具项目已创建！
echo ========================================
echo.
echo 项目路径: %tool_path%
echo.
echo 下一步：
echo 1. 进入项目目录: cd %tool_path%
echo 2. 安装依赖: pip install -r requirements.txt
echo 3. 开始开发: streamlit run main.py
echo.
cd ..
pause

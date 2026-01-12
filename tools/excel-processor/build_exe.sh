#!/bin/bash
# Linux/Mac 打包脚本（如果需要）

echo "========================================"
echo "Excel 处理工具 - 打包脚本"
echo "========================================"
echo ""

echo "[1/4] 检查依赖包..."
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt

echo ""
echo "[2/4] 安装 PyInstaller..."
python3 -m pip install pyinstaller

echo ""
echo "[3/4] 清理旧的打包文件..."
rm -rf build dist __pycache__

echo ""
echo "[4/4] 开始打包..."
python3 -m PyInstaller build_exe.spec --clean --noconfirm

echo ""
echo "========================================"
echo "打包完成！"
echo "========================================"
echo ""
echo "可执行文件位置: dist/Excel处理工具"
echo ""

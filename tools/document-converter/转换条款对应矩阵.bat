@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ========================================
echo 条款对应矩阵转换工具
echo ========================================
echo.

python convert_clause_matrix.py

pause

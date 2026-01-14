#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
将课题申报书Markdown文件转换为HTML和PDF
"""

import os
import subprocess
import sys
from pathlib import Path

def convert_to_html(md_file, html_file):
    """将Markdown转换为HTML"""
    try:
        cmd = [
            'pandoc',
            md_file,
            '-o', html_file,
            '-f', 'markdown',
            '-t', 'html',
            '--standalone',
            '--css=https://cdn.jsdelivr.net/npm/github-markdown-css@5/github-markdown.min.css',
            '--metadata', 'title=基于多层次记忆架构的AI赋能教师工作空间构建及其教学改革实践研究'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode == 0:
            print(f"[成功] HTML转换成功: {html_file}")
            return True
        else:
            print(f"[失败] HTML转换失败: {result.stderr}")
            return False
    except Exception as e:
        print(f"[错误] 转换过程出错: {e}")
        return False

def convert_to_pdf(md_file, pdf_file):
    """将Markdown转换为PDF"""
    try:
        cmd = [
            'pandoc',
            md_file,
            '-o', pdf_file,
            '-f', 'markdown',
            '-t', 'pdf',
            '--pdf-engine=xelatex',
            '-V', 'mainfont=Microsoft YaHei',
            '-V', 'geometry:margin=2cm'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode == 0:
            print(f"[成功] PDF转换成功: {pdf_file}")
            return True
        else:
            print(f"[失败] PDF转换失败（可能需要安装LaTeX包）")
            return False
    except Exception as e:
        print(f"[错误] PDF转换过程出错: {e}")
        return False

def main():
    # 获取当前目录
    current_dir = Path(__file__).parent
    
    # 查找课题申报书文件
    md_files = list(current_dir.glob("*课题申报书*.md"))
    
    if not md_files:
        print("未找到课题申报书文件！")
        sys.exit(1)
    
    md_file = md_files[0]
    print(f"找到文件: {md_file.name}")
    
    # 输出文件路径
    html_file = current_dir / "课题申报书.html"
    pdf_file = current_dir / "课题申报书.pdf"
    
    # 转换为HTML
    print("\n正在转换为HTML...")
    html_success = convert_to_html(str(md_file), str(html_file))
    
    if html_success:
        # 尝试转换为PDF
        print("\n正在尝试转换为PDF...")
        pdf_success = convert_to_pdf(str(md_file), str(pdf_file))
        
        if not pdf_success:
            print("\n建议使用以下方法生成PDF：")
            print(f"1. 在浏览器中打开: {html_file}")
            print("2. 按 Ctrl+P 打开打印对话框")
            print("3. 选择'另存为PDF'或'Microsoft Print to PDF'")
            print("4. 保存为PDF文件")
        
        # 询问是否打开HTML文件
        try:
            response = input("\n是否现在打开HTML文件？(Y/N): ")
            if response.upper() == 'Y':
                if sys.platform == 'win32':
                    os.startfile(str(html_file))
                elif sys.platform == 'darwin':
                    subprocess.run(['open', str(html_file)])
                else:
                    subprocess.run(['xdg-open', str(html_file)])
        except:
            pass

if __name__ == '__main__':
    main()

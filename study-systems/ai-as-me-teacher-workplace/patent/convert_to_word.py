#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
专利申请文档转Word脚本
将Markdown格式的专利申请文档转换为Word格式
"""

import os
import sys
from pathlib import Path
import subprocess

def check_pypandoc():
    """检查pypandoc是否已安装"""
    try:
        import pypandoc
        return True, pypandoc
    except ImportError:
        return False, None

def install_pypandoc():
    """安装pypandoc"""
    print("正在安装pypandoc...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pypandoc"])
        import pypandoc
        return True, pypandoc
    except Exception as e:
        print(f"安装失败: {e}")
        return False, None

def convert_md_to_docx(source_path, output_path, title=None):
    """将Markdown文件转换为Word文档"""
    try:
        import pypandoc
        
        # 准备转换参数
        extra_args = [
            '-V', 'mainfont=Microsoft YaHei',  # 中文字体
            '-V', 'fontsize=12pt',              # 字体大小
            '--toc-depth=3',                     # 目录深度
        ]
        
        # 如果有参考文档，使用参考文档
        reference_doc = Path(__file__).parent / "reference.docx"
        if reference_doc.exists():
            extra_args.extend(['--reference-doc', str(reference_doc)])
        
        # 执行转换
        pypandoc.convert_file(
            str(source_path),
            'docx',
            outputfile=str(output_path),
            extra_args=extra_args
        )
        return True
    except Exception as e:
        print(f"转换失败: {e}")
        return False

def main():
    """主函数"""
    # 设置路径
    script_dir = Path(__file__).parent
    patent_dir = script_dir
    output_dir = patent_dir / "word-output"
    
    # 创建输出目录
    output_dir.mkdir(exist_ok=True)
    
    # 检查并安装pypandoc
    has_pypandoc, pypandoc = check_pypandoc()
    if not has_pypandoc:
        print("pypandoc未安装，正在安装...")
        has_pypandoc, pypandoc = install_pypandoc()
        if not has_pypandoc:
            print("错误: 无法安装pypandoc，请手动安装: pip install pypandoc")
            return 1
    
    # 检查pandoc是否安装
    try:
        subprocess.run(['pandoc', '--version'], 
                      capture_output=True, 
                      check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("错误: pandoc未安装")
        print("请访问 https://pandoc.org/installing.html 安装pandoc")
        return 1
    
    # 文件映射（核心申请文件）
    files = [
        {
            "source": "03-权利要求书.md",
            "output": "权利要求书.docx",
            "title": "权利要求书"
        },
        {
            "source": "04-说明书.md",
            "output": "说明书.docx",
            "title": "说明书"
        },
        {
            "source": "05-说明书摘要.md",
            "output": "说明书摘要.docx",
            "title": "说明书摘要"
        },
        {
            "source": "06-附图说明.md",
            "output": "附图说明.docx",
            "title": "附图说明"
        }
    ]
    
    # 可选：转换其他文件
    optional_files = [
        {
            "source": "01-技术方案分析.md",
            "output": "技术方案分析.docx",
            "title": "技术方案分析"
        },
        {
            "source": "02-专利申请文档结构.md",
            "output": "专利申请文档结构.docx",
            "title": "专利申请文档结构"
        },
        {
            "source": "08-现有技术检索.md",
            "output": "现有技术检索.docx",
            "title": "现有技术检索"
        }
    ]
    
    print("=" * 60)
    print("专利申请文档转Word工具")
    print("=" * 60)
    print()
    
    # 转换核心文件
    success_count = 0
    fail_count = 0
    
    print("正在转换核心申请文件...")
    print("-" * 60)
    
    for file_info in files:
        source_path = patent_dir / file_info["source"]
        output_path = output_dir / file_info["output"]
        
        if source_path.exists():
            print(f"正在转换: {file_info['source']} -> {file_info['output']}")
            
            if convert_md_to_docx(source_path, output_path, file_info["title"]):
                print(f"✓ 完成: {file_info['output']}")
                success_count += 1
            else:
                print(f"✗ 失败: {file_info['source']}")
                fail_count += 1
        else:
            print(f"✗ 文件不存在: {file_info['source']}")
            fail_count += 1
    
    # 询问是否转换其他文件
    print()
    response = input("是否转换其他文件（技术方案分析、文档结构、现有技术检索）？(Y/N): ")
    if response.upper() == 'Y':
        print()
        print("正在转换其他文件...")
        print("-" * 60)
        
        for file_info in optional_files:
            source_path = patent_dir / file_info["source"]
            output_path = output_dir / file_info["output"]
            
            if source_path.exists():
                print(f"正在转换: {file_info['source']} -> {file_info['output']}")
                
                if convert_md_to_docx(source_path, output_path, file_info["title"]):
                    print(f"✓ 完成: {file_info['output']}")
                    success_count += 1
                else:
                    print(f"✗ 失败: {file_info['source']}")
                    fail_count += 1
            else:
                print(f"✗ 文件不存在: {file_info['source']}")
                fail_count += 1
    
    # 输出结果
    print()
    print("=" * 60)
    print(f"转换完成！成功: {success_count} 个，失败: {fail_count} 个")
    print(f"输出目录: {output_dir.absolute()}")
    print("=" * 60)
    
    # 打开输出目录
    if sys.platform == "win32":
        os.startfile(output_dir)
    elif sys.platform == "darwin":
        subprocess.run(["open", output_dir])
    else:
        subprocess.run(["xdg-open", output_dir])
    
    return 0 if fail_count == 0 else 1

if __name__ == "__main__":
    sys.exit(main())

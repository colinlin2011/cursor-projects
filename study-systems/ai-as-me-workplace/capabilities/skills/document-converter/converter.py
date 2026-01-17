#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
文档转换核心模块
提供Markdown到Word的转换功能
"""

import os
import sys
from pathlib import Path
import subprocess
from typing import Dict, List, Optional, Tuple

def check_pypandoc() -> Tuple[bool, Optional[object]]:
    """检查pypandoc是否已安装"""
    try:
        import pypandoc
        return True, pypandoc
    except ImportError:
        return False, None

def check_pandoc() -> bool:
    """检查pandoc是否已安装"""
    try:
        result = subprocess.run(
            ['pandoc', '--version'],
            capture_output=True,
            check=True
        )
        return result.returncode == 0
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def install_pypandoc() -> Tuple[bool, Optional[object]]:
    """安装pypandoc"""
    print("正在安装pypandoc...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pypandoc"])
        import pypandoc
        return True, pypandoc
    except Exception as e:
        print(f"安装失败: {e}")
        return False, None

def check_dependencies() -> Dict[str, bool]:
    """检查所有依赖是否已安装"""
    return {
        "pypandoc": check_pypandoc()[0],
        "pandoc": check_pandoc()
    }

def install_dependencies() -> Dict[str, bool]:
    """安装所有依赖"""
    results = {}
    
    # 安装pypandoc
    if not check_pypandoc()[0]:
        results["pypandoc"] = install_pypandoc()[0]
    else:
        results["pypandoc"] = True
    
    # Pandoc需要手动安装
    results["pandoc"] = check_pandoc()
    if not results["pandoc"]:
        print("警告: Pandoc未安装，请手动安装:")
        print("  Windows: winget install --id JohnMacFarlane.Pandoc")
        print("  或访问: https://pandoc.org/installing.html")
    
    return results

def convert_markdown_to_word(
    source_file: str,
    output_file: Optional[str] = None,
    template_file: Optional[str] = None,
    output_dir: str = "word-output"
) -> Dict[str, any]:
    """
    将Markdown文件转换为Word文档
    
    Args:
        source_file: 源Markdown文件路径
        output_file: 输出Word文件路径（可选，默认自动生成）
        template_file: Word模板文件路径（可选）
        output_dir: 输出目录（当output_file为None时使用）
    
    Returns:
        包含转换结果的字典
    """
    # 检查依赖
    deps = check_dependencies()
    if not deps["pypandoc"]:
        has_pypandoc, pypandoc = install_pypandoc()
        if not has_pypandoc:
            return {
                "success": False,
                "error_code": "DEPENDENCY_MISSING",
                "message": "无法安装pypandoc，请手动安装: pip install pypandoc"
            }
    else:
        _, pypandoc = check_pypandoc()
    
    if not deps["pandoc"]:
        return {
            "success": False,
            "error_code": "PANDOC_NOT_FOUND",
            "message": "Pandoc未安装，请安装Pandoc或使用Docker版本"
        }
    
    # 检查源文件
    source_path = Path(source_file)
    if not source_path.exists():
        return {
            "success": False,
            "error_code": "FILE_NOT_FOUND",
            "message": f"源文件不存在: {source_file}"
        }
    
    # 确定输出文件路径
    if output_file is None:
        output_dir_path = Path(output_dir)
        output_dir_path.mkdir(exist_ok=True)
        output_file = str(output_dir_path / f"{source_path.stem}.docx")
    
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 准备转换参数
    extra_args = [
        '-V', 'mainfont=Microsoft YaHei',  # 中文字体
        '-V', 'fontsize=12pt',              # 字体大小
        '--toc-depth=3',                     # 目录深度
    ]
    
    # 检查模板文件
    if template_file:
        template_path = Path(template_file)
        if template_path.exists():
            extra_args.extend(['--reference-doc', str(template_path)])
    else:
        # 尝试查找默认模板
        default_template = source_path.parent / "reference.docx"
        if default_template.exists():
            extra_args.extend(['--reference-doc', str(default_template)])
    
    # 执行转换
    try:
        pypandoc.convert_file(
            str(source_path),
            'docx',
            outputfile=str(output_path),
            extra_args=extra_args
        )
        return {
            "success": True,
            "output_file": str(output_path),
            "message": "转换成功"
        }
    except Exception as e:
        return {
            "success": False,
            "error_code": "CONVERSION_FAILED",
            "message": f"转换失败: {str(e)}"
        }

def batch_convert_to_word(
    files: List[Dict[str, str]],
    output_dir: str = "word-output",
    template_file: Optional[str] = None
) -> List[Dict[str, any]]:
    """
    批量转换Markdown文件为Word文档
    
    Args:
        files: 文件列表，每个元素包含source和output键
        output_dir: 输出目录
        template_file: 模板文件路径（可选）
    
    Returns:
        转换结果列表
    """
    results = []
    output_dir_path = Path(output_dir)
    output_dir_path.mkdir(exist_ok=True)
    
    for file_info in files:
        source = file_info.get("source")
        output = file_info.get("output")
        
        if not source:
            results.append({
                "file": source or "unknown",
                "status": "failed",
                "message": "缺少source参数"
            })
            continue
        
        # 确定输出文件路径
        if not output:
            source_path = Path(source)
            output = str(output_dir_path / f"{source_path.stem}.docx")
        else:
            output = str(output_dir_path / output)
        
        # 执行转换
        result = convert_markdown_to_word(
            source_file=source,
            output_file=output,
            template_file=template_file,
            output_dir=output_dir
        )
        
        results.append({
            "file": source,
            "output": output,
            "status": "success" if result["success"] else "failed",
            "message": result.get("message", ""),
            "result": result
        })
    
    return results

def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Markdown转Word文档转换工具")
    parser.add_argument("--source", "-s", required=True, help="源Markdown文件路径")
    parser.add_argument("--output", "-o", help="输出Word文件路径")
    parser.add_argument("--template", "-t", help="Word模板文件路径")
    parser.add_argument("--output-dir", "-d", default="word-output", help="输出目录")
    parser.add_argument("--batch", action="store_true", help="批量转换模式")
    parser.add_argument("--source-dir", help="批量转换时的源目录")
    
    args = parser.parse_args()
    
    if args.batch:
        if args.source_dir:
            source_dir = Path(args.source_dir)
            files = [
                {"source": str(f), "output": f"{f.stem}.docx"}
                for f in source_dir.glob("*.md")
            ]
        else:
            print("错误: 批量转换模式需要指定--source-dir")
            return 1
        
        results = batch_convert_to_word(files, args.output_dir, args.template)
        success_count = sum(1 for r in results if r["status"] == "success")
        print(f"\n转换完成: 成功 {success_count}/{len(results)}")
        return 0 if success_count == len(results) else 1
    else:
        result = convert_markdown_to_word(
            source_file=args.source,
            output_file=args.output,
            template_file=args.template,
            output_dir=args.output_dir
        )
        
        if result["success"]:
            print(f"转换成功: {result['output_file']}")
            return 0
        else:
            print(f"转换失败: {result['message']}")
            return 1

if __name__ == "__main__":
    sys.exit(main())

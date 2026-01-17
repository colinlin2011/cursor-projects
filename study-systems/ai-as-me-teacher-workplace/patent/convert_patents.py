#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
专利文档转Word脚本
"""

import os
import sys
from pathlib import Path
import subprocess

# 设置输出编码
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def check_pypandoc():
    try:
        import pypandoc
        return True, pypandoc
    except ImportError:
        return False, None

def check_pandoc():
    try:
        subprocess.run(['pandoc', '--version'], capture_output=True, check=True)
        return True
    except:
        return False

def convert_file(source, output):
    try:
        import pypandoc
        pypandoc.convert_file(
            str(source),
            'docx',
            outputfile=str(output),
            extra_args=['-V', 'mainfont=Microsoft YaHei', '-V', 'fontsize=12pt', '--toc-depth=3']
        )
        return True
    except Exception as e:
        print(f"错误: {e}")
        return False

def main():
    # 检查依赖
    has_pypandoc, pypandoc = check_pypandoc()
    if not has_pypandoc:
        print("正在安装pypandoc...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pypandoc"])
        import pypandoc
    
    if not check_pandoc():
        print("错误: Pandoc未安装")
        return 1
    
    patent_dir = Path(__file__).parent
    
    patents = [
        {
            "name": "专利2-物流数字孪生教学平台",
            "dir": patent_dir / "专利2-物流数字孪生教学平台",
        },
        {
            "name": "专利3-物流实践课程智能设计系统",
            "dir": patent_dir / "专利3-物流实践课程智能设计系统",
        }
    ]
    
    files_to_convert = [
        "00-专利申请文件索引.md",
        "01-技术方案分析.md",
        "02-权利要求书.md",
        "03-说明书.md",
        "04-说明书摘要.md",
        "05-附图说明.md",
        "06-附图（Mermaid图表）.md",
    ]
    
    print("=" * 60)
    print("专利文档转Word工具")
    print("=" * 60)
    
    total_success = 0
    total_fail = 0
    
    for patent in patents:
        print(f"\n正在转换: {patent['name']}")
        print("-" * 60)
        
        output_dir = patent["dir"] / "word-output"
        output_dir.mkdir(exist_ok=True)
        
        for filename in files_to_convert:
            source = patent["dir"] / filename
            output = output_dir / filename.replace(".md", ".docx")
            
            if source.exists():
                print(f"转换: {filename}")
                if convert_file(source, output):
                    print(f"  [OK] 完成")
                    total_success += 1
                else:
                    print(f"  [FAIL] 失败")
                    total_fail += 1
            else:
                print(f"  [SKIP] 文件不存在: {filename}")
                total_fail += 1
    
    print()
    print("=" * 60)
    print(f"转换完成！成功: {total_success} 个，失败: {total_fail} 个")
    print("=" * 60)
    print()
    print("注意：Mermaid图表代码块已保留在Word中，需要手动转换为图片：")
    print("1. 使用在线工具 https://mermaid.live/ 将代码转换为图片")
    print("2. 或使用 mermaid-cli: npm install -g @mermaid-js/mermaid-cli")
    print("3. 然后将图片插入Word文档")
    
    return 0 if total_fail == 0 else 1

if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
专利文档转Word脚本
将专利2和专利3的Markdown文档转换为Word格式
"""

import os
import sys
from pathlib import Path
import subprocess

# 导入转换模块
converter_path = Path(__file__).parent.parent / "capabilities" / "skills" / "document-converter"
if converter_path.exists():
    sys.path.insert(0, str(converter_path))
    from converter import convert_markdown_to_word, check_dependencies, install_dependencies
else:
    # 如果找不到模块，直接使用pypandoc
    import pypandoc
    def convert_markdown_to_word(source_file, output_file, output_dir="word-output"):
        try:
            pypandoc.convert_file(
                source_file,
                'docx',
                outputfile=output_file,
                extra_args=['-V', 'mainfont=Microsoft YaHei', '-V', 'fontsize=12pt', '--toc-depth=3']
            )
            return {"success": True, "output_file": output_file, "message": "转换成功"}
        except Exception as e:
            return {"success": False, "message": f"转换失败: {str(e)}"}
    
    def check_dependencies():
        try:
            import pypandoc
            import subprocess
            subprocess.run(['pandoc', '--version'], capture_output=True, check=True)
            return {"pypandoc": True, "pandoc": True}
        except:
            return {"pypandoc": False, "pandoc": False}
    
    def install_dependencies():
        return check_dependencies()

def main():
    """主函数"""
    # 检查依赖
    deps = check_dependencies()
    if not deps["pypandoc"]:
        print("正在安装pypandoc...")
        install_dependencies()
    
    if not deps["pandoc"]:
        print("错误: Pandoc未安装，请先安装Pandoc")
        print("Windows: winget install --id JohnMacFarlane.Pandoc")
        return 1
    
    # 设置路径
    patent_dir = Path(__file__).parent
    
    # 定义要转换的专利文档
    patents = [
        {
            "name": "专利2-物流数字孪生教学平台",
            "dir": patent_dir / "专利2-物流数字孪生教学平台",
            "files": [
                {"source": "00-专利申请文件索引.md", "output": "00-专利申请文件索引.docx"},
                {"source": "01-技术方案分析.md", "output": "01-技术方案分析.docx"},
                {"source": "02-权利要求书.md", "output": "02-权利要求书.docx"},
                {"source": "03-说明书.md", "output": "03-说明书.docx"},
                {"source": "04-说明书摘要.md", "output": "04-说明书摘要.docx"},
                {"source": "05-附图说明.md", "output": "05-附图说明.docx"},
                {"source": "06-附图（Mermaid图表）.md", "output": "06-附图（Mermaid图表）.docx"},
            ]
        },
        {
            "name": "专利3-物流实践课程智能设计系统",
            "dir": patent_dir / "专利3-物流实践课程智能设计系统",
            "files": [
                {"source": "00-专利申请文件索引.md", "output": "00-专利申请文件索引.docx"},
                {"source": "01-技术方案分析.md", "output": "01-技术方案分析.docx"},
                {"source": "02-权利要求书.md", "output": "02-权利要求书.docx"},
                {"source": "03-说明书.md", "output": "03-说明书.docx"},
                {"source": "04-说明书摘要.md", "output": "04-说明书摘要.docx"},
                {"source": "05-附图说明.md", "output": "05-附图说明.docx"},
                {"source": "06-附图（Mermaid图表）.md", "output": "06-附图（Mermaid图表）.docx"},
            ]
        }
    ]
    
    print("=" * 60)
    print("专利文档转Word工具")
    print("=" * 60)
    print()
    
    total_success = 0
    total_fail = 0
    
    # 转换每个专利的文档
    for patent in patents:
        print(f"\n正在转换: {patent['name']}")
        print("-" * 60)
        
        # 创建输出目录
        output_dir = patent["dir"] / "word-output"
        output_dir.mkdir(exist_ok=True)
        
        for file_info in patent["files"]:
            source_path = patent["dir"] / file_info["source"]
            output_path = output_dir / file_info["output"]
            
            if source_path.exists():
                print(f"正在转换: {file_info['source']} -> {file_info['output']}")
                
                result = convert_markdown_to_word(
                    source_file=str(source_path),
                    output_file=str(output_path),
                    output_dir=str(output_dir)
                )
                
                if result["success"]:
                    print(f"✓ 完成: {file_info['output']}")
                    total_success += 1
                else:
                    print(f"✗ 失败: {result.get('message', '未知错误')}")
                    total_fail += 1
            else:
                print(f"✗ 文件不存在: {file_info['source']}")
                total_fail += 1
    
    # 输出结果
    print()
    print("=" * 60)
    print(f"转换完成！成功: {total_success} 个，失败: {total_fail} 个")
    print("=" * 60)
    
    # 关于Mermaid图表的说明
    print()
    print("注意：Mermaid图表已转换为Word，但图表代码块需要手动处理：")
    print("1. 可以使用在线工具（如 https://mermaid.live/）将Mermaid代码转换为图片")
    print("2. 或者使用mermaid-cli工具：npm install -g @mermaid-js/mermaid-cli")
    print("3. 然后将生成的图片插入到Word文档中")
    
    # 打开输出目录
    if sys.platform == "win32":
        for patent in patents:
            output_dir = patent["dir"] / "word-output"
            if output_dir.exists():
                os.startfile(output_dir)
    
    return 0 if total_fail == 0 else 1

if __name__ == "__main__":
    sys.exit(main())

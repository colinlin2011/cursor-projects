#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
批量转换所有论文为Word文档
"""
import sys
import os
from pathlib import Path

# 设置UTF-8编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 添加转换器路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'capabilities' / 'skills' / 'document-converter'))

from converter import batch_convert_to_word

def main():
    """主函数"""
    papers_dir = Path(__file__).parent / 'papers'
    output_dir = Path(__file__).parent / 'word-output'
    
    # 获取所有论文文件
    paper_files = list(papers_dir.glob('论文*.md'))
    
    if not paper_files:
        print("未找到论文文件！")
        return 1
    
    print("=" * 60)
    print("批量转换论文为Word文档".center(56))
    print("=" * 60)
    print(f"\n找到 {len(paper_files)} 篇论文")
    print(f"输出目录: {output_dir}")
    print("\n开始转换...\n")
    
    # 准备批量转换文件列表
    files = []
    for paper_file in paper_files:
        files.append({
            "source": str(paper_file),
            "output": f"{paper_file.stem}.docx"
        })
        print(f"  - {paper_file.name}")
    
    # 执行批量转换
    results = batch_convert_to_word(
        files=files,
        output_dir=str(output_dir)
    )
    
    # 输出结果
    print("\n" + "=" * 60)
    success_count = sum(1 for r in results if r["status"] == "success")
    print(f"转换完成: 成功 {success_count}/{len(results)} 篇论文")
    print("=" * 60)
    
    # 详细结果
    print("\n详细结果:")
    for result in results:
        status_icon = "✓" if result["status"] == "success" else "✗"
        print(f"  {status_icon} {Path(result['file']).name}: {result['message']}")
        if result["status"] == "success":
            print(f"    输出: {result['output']}")
    
    return 0 if success_count == len(results) else 1

if __name__ == "__main__":
    sys.exit(main())

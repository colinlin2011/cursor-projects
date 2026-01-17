#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
转换课题申报书为Word文档
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

from converter import convert_markdown_to_word

def main():
    """主函数"""
    # 源文件路径
    source_file = Path(__file__).parent / '课题申报书-基于多层次记忆架构的AI赋能教师工作空间构建及其教学改革实践研究.md'
    output_dir = Path(__file__).parent / 'word-output'
    
    print("=" * 60)
    print("课题申报书转Word工具".center(56))
    print("=" * 60)
    print(f"\n源文件: {source_file}")
    print(f"输出目录: {output_dir}")
    print("\n开始转换...")
    
    # 执行转换
    result = convert_markdown_to_word(
        source_file=str(source_file),
        output_dir=str(output_dir)
    )
    
    # 输出结果
    print("\n" + "=" * 60)
    if result.get("success"):
        print(f"✓ 转换成功！")
        print(f"输出文件: {result.get('output_file')}")
    else:
        print(f"✗ 转换失败！")
        print(f"错误代码: {result.get('error_code')}")
        print(f"错误信息: {result.get('message')}")
    print("=" * 60)
    
    return 0 if result.get("success") else 1

if __name__ == "__main__":
    sys.exit(main())

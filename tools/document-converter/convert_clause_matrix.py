"""
条款对应矩阵转换工具
将Markdown格式的条款对应矩阵转换为Excel或Word格式
"""

import sys
import os
from pathlib import Path

# 添加utils目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from utils.markdown_to_excel import MarkdownToExcel
from utils.markdown_to_word import MarkdownToWord


def main():
    """主函数"""
    print("=" * 60)
    print("条款对应矩阵转换工具")
    print("=" * 60)
    print()
    
    # 文件路径
    matrix_file = r"p:\Cursor Project\study-systems\autonomous-safety-study\materials\04_工作文档\条款对应矩阵.md"
    
    if not os.path.exists(matrix_file):
        print(f"❌ 文件不存在: {matrix_file}")
        return
    
    print(f"源文件: {matrix_file}")
    print()
    print("请选择转换格式:")
    print("1. Excel (.xlsx)")
    print("2. Word (.docx)")
    print("3. 两者都转换")
    print()
    
    choice = input("请输入选择 (1/2/3): ").strip()
    
    excel_converter = MarkdownToExcel()
    word_converter = MarkdownToWord()
    
    success_count = 0
    
    if choice in ['1', '3']:
        print()
        print("正在转换为Excel...")
        try:
            excel_file = matrix_file.replace('.md', '.xlsx')
            result = excel_converter.convert_to_excel(matrix_file, excel_file)
            print(f"✅ Excel转换成功: {result}")
            success_count += 1
        except Exception as e:
            print(f"❌ Excel转换失败: {e}")
            import traceback
            traceback.print_exc()
    
    if choice in ['2', '3']:
        print()
        print("正在转换为Word...")
        try:
            word_file = matrix_file.replace('.md', '.docx')
            result = word_converter.convert_to_word(matrix_file, word_file)
            print(f"✅ Word转换成功: {result}")
            success_count += 1
        except Exception as e:
            print(f"❌ Word转换失败: {e}")
            import traceback
            traceback.print_exc()
    
    print()
    print("=" * 60)
    if success_count > 0:
        print(f"✅ 转换完成！成功转换 {success_count} 个文件")
    else:
        print("❌ 转换失败")
    print("=" * 60)


if __name__ == "__main__":
    main()

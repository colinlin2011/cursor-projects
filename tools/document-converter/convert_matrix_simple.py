"""
条款对应矩阵转换工具 - 简化版
直接转换条款对应矩阵为Excel
"""

import sys
import io

# 修复Windows控制台编码问题
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import pandas as pd
from pathlib import Path
import re

def convert_markdown_table_to_excel(markdown_file, output_file):
    """将Markdown表格转换为Excel"""
    
    # 读取Markdown文件
    with open(markdown_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找所有表格
    table_pattern = r'\|[^\n]+\n\|[\s\-\|:]+\n(?:\|[^\n]+\n?)+'
    tables = re.findall(table_pattern, content, re.MULTILINE)
    
    if not tables:
        print("[错误] 未找到表格数据")
        return False
    
    print(f"找到 {len(tables)} 个表格")
    
    # 创建Excel写入器
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        for i, table_text in enumerate(tables):
            # 解析表格
            lines = table_text.strip().split('\n')
            table_data = []
            
            for line in lines:
                line = line.strip()
                if not line or not line.startswith('|'):
                    continue
                
                # 跳过分隔行
                if re.match(r'^\|[\s\-\|:]+\|$', line):
                    continue
                
                # 解析表格行
                cells = [cell.strip() for cell in line.split('|')[1:-1]]
                if cells:
                    table_data.append(cells)
            
            if table_data and len(table_data) > 1:
                # 第一行作为表头
                headers = table_data[0]
                data = table_data[1:]
                
                # 创建DataFrame
                df = pd.DataFrame(data, columns=headers)
                
                # 工作表名称
                sheet_name = f'表格{i+1}' if i < 10 else f'表{i+1}'
                
                # 写入工作表
                df.to_excel(writer, index=False, sheet_name=sheet_name)
                print(f"  已处理表格 {i+1}: {len(data)} 行数据")
    
    print(f"\n[成功] Excel文件已保存到: {output_file}")
    return True


def main():
    """主函数"""
    print("=" * 60)
    print("条款对应矩阵转换工具")
    print("=" * 60)
    print()
    
    # 文件路径
    matrix_file = Path(r"p:\Cursor Project\study-systems\autonomous-safety-study\materials\04_工作文档\条款对应矩阵.md")
    excel_file = matrix_file.parent / "条款对应矩阵.xlsx"
    
    if not matrix_file.exists():
        print(f"[错误] 文件不存在: {matrix_file}")
        return
    
    print(f"源文件: {matrix_file}")
    print(f"目标文件: {excel_file}")
    print()
    print("正在转换...")
    
    try:
        success = convert_markdown_table_to_excel(str(matrix_file), str(excel_file))
        if success:
            print()
            print("=" * 60)
            print("[成功] 转换完成！")
            print("=" * 60)
            print()
            print("提示：")
            print("1. 可以在Excel中编辑表格")
            print("2. 编辑完成后，可以使用Excel的'另存为'功能保存")
            print("3. 或者告诉我，我可以帮你将Excel转换回Markdown格式")
        else:
            print()
            print("=" * 60)
            print("[失败] 转换失败")
            print("=" * 60)
    except Exception as e:
        print(f"\n[错误] 转换失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

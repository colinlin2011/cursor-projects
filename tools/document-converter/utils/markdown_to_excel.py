"""
Markdown表格转Excel工具
将条款对应矩阵等Markdown表格转换为Excel格式
"""

import re
import pandas as pd
from pathlib import Path
from typing import List, Dict, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MarkdownToExcel:
    """Markdown表格转Excel转换器"""
    
    def __init__(self):
        pass
    
    def parse_markdown_table(self, markdown_text: str) -> List[List[str]]:
        """
        解析Markdown表格
        
        Args:
            markdown_text: Markdown表格文本
        
        Returns:
            表格数据（二维列表）
        """
        lines = markdown_text.strip().split('\n')
        table_data = []
        
        for line in lines:
            line = line.strip()
            if not line or not line.startswith('|'):
                continue
            
            # 跳过分隔行（如 |---|---|）
            if re.match(r'^\|[\s\-\|:]+\|$', line):
                continue
            
            # 解析表格行
            cells = [cell.strip() for cell in line.split('|')[1:-1]]
            if cells:
                table_data.append(cells)
        
        return table_data
    
    def extract_tables_from_markdown(self, markdown_file: str) -> Dict[str, List[List[str]]]:
        """
        从Markdown文件中提取所有表格
        
        Args:
            markdown_file: Markdown文件路径
        
        Returns:
            字典，键为表格标题，值为表格数据
        """
        with open(markdown_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tables = {}
        current_section = None
        current_table = []
        in_table = False
        
        lines = content.split('\n')
        
        for line in lines:
            # 检测表格开始（包含 | 的行）
            if '|' in line and not line.strip().startswith('#'):
                if not in_table:
                    in_table = True
                    # 尝试获取上一个标题作为表格标题
                    if current_section:
                        current_table = []
                if in_table:
                    # 跳过分隔行
                    if not re.match(r'^\|[\s\-\|:]+\|$', line.strip()):
                        cells = [cell.strip() for cell in line.split('|')[1:-1]]
                        if cells:
                            current_table.append(cells)
            else:
                if in_table and current_table:
                    # 表格结束
                    if current_section:
                        tables[current_section] = current_table
                    current_table = []
                    in_table = False
                
                # 检测标题
                if line.strip().startswith('#'):
                    # 提取标题文本
                    title = line.strip().lstrip('#').strip()
                    if title and not title.startswith('统计') and not title.startswith('重要提示'):
                        current_section = title
        
        # 处理最后一个表格
        if in_table and current_table and current_section:
            tables[current_section] = current_table
        
        return tables
    
    def convert_to_excel(self, markdown_file: str, output_file: Optional[str] = None) -> str:
        """
        将Markdown文件中的表格转换为Excel
        
        Args:
            markdown_file: Markdown文件路径
            output_file: 输出Excel文件路径（可选）
        
        Returns:
            输出文件路径
        """
        markdown_path = Path(markdown_file)
        
        if output_file is None:
            output_file = markdown_path.parent / f"{markdown_path.stem}.xlsx"
        else:
            output_file = Path(output_file)
        
        # 提取所有表格
        tables = self.extract_tables_from_markdown(markdown_file)
        
        if not tables:
            logger.warning("未找到表格，尝试直接解析整个文件")
            # 尝试直接解析整个文件作为单个表格
            with open(markdown_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 查找所有表格块
            table_blocks = re.findall(r'\|[^\n]+\n\|[\s\-\|:]+\n(?:\|[^\n]+\n?)+', content)
            
            if table_blocks:
                # 使用第一个表格块
                table_data = self.parse_markdown_table(table_blocks[0])
                if table_data:
                    df = pd.DataFrame(table_data[1:], columns=table_data[0] if table_data else None)
                    df.to_excel(output_file, index=False, sheet_name='条款对应矩阵')
                    logger.info(f"已创建Excel文件: {output_file}")
                    return str(output_file)
            else:
                raise ValueError("未找到任何表格数据")
        
        # 创建Excel写入器
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            sheet_count = 0
            
            for section, table_data in tables.items():
                if not table_data:
                    continue
                
                # 确保有表头
                if len(table_data) < 2:
                    continue
                
                # 第一行作为表头
                headers = table_data[0]
                data = table_data[1:]
                
                # 创建DataFrame
                df = pd.DataFrame(data, columns=headers)
                
                # 限制工作表名称长度（Excel限制31字符）
                sheet_name = section[:31] if len(section) > 31 else section
                if not sheet_name:
                    sheet_name = f"表格{sheet_count + 1}"
                
                # 写入工作表
                df.to_excel(writer, index=False, sheet_name=sheet_name)
                sheet_count += 1
            
            # 如果没有提取到表格，尝试整体转换
            if sheet_count == 0:
                logger.warning("未能提取表格，尝试整体转换")
                with open(markdown_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 查找所有表格
                table_pattern = r'\|[^\n]+\n\|[\s\-\|:]+\n(?:\|[^\n]+\n?)+'
                matches = re.finditer(table_pattern, content, re.MULTILINE)
                
                for i, match in enumerate(matches):
                    table_text = match.group()
                    table_data = self.parse_markdown_table(table_text)
                    if table_data and len(table_data) > 1:
                        df = pd.DataFrame(table_data[1:], columns=table_data[0])
                        df.to_excel(writer, index=False, sheet_name=f'表格{i+1}')
                        sheet_count += 1
        
        if sheet_count == 0:
            raise ValueError("未能提取任何表格数据")
        
        logger.info(f"已创建Excel文件: {output_file}，包含{sheet_count}个工作表")
        return str(output_file)


def convert_clause_matrix_to_excel():
    """转换条款对应矩阵为Excel"""
    matrix_file = r"p:\Cursor Project\study-systems\autonomous-safety-study\materials\04_工作文档\条款对应矩阵.md"
    output_file = r"p:\Cursor Project\study-systems\autonomous-safety-study\materials\04_工作文档\条款对应矩阵.xlsx"
    
    converter = MarkdownToExcel()
    
    try:
        result = converter.convert_to_excel(matrix_file, output_file)
        print(f"✅ 转换成功！")
        print(f"Excel文件已保存到: {result}")
        return True
    except Exception as e:
        print(f"❌ 转换失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    convert_clause_matrix_to_excel()

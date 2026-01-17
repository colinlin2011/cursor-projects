# -*- coding: utf-8 -*-
"""
FMEA数据读取器

从缓存文件中读取FMEA在线表格数据，识别主工作表并解析数据
"""

import sys
import os
import json
from typing import Dict, List, Any, Optional
from pathlib import Path

# 修复Windows控制台编码问题
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 缓存目录
SPREADSHEET_CACHE_DIR = Path("work/spreadsheet_cache")


class FMEADataReader:
    """FMEA数据读取器"""
    
    # 主工作表关键词（用于识别失效模式影响分析相关的工作表）
    MAIN_SHEET_KEYWORDS = [
        "失效模式",
        "FMEA",
        "Failure Mode",
        "失效模式影响分析",
        "失效模式与影响分析"
    ]
    
    def __init__(self, cache_dir: Path = None):
        """
        初始化FMEA数据读取器
        
        Args:
            cache_dir: 缓存目录路径，默认为 work/spreadsheet_cache
        """
        self.cache_dir = cache_dir or SPREADSHEET_CACHE_DIR
    
    def find_fmea_cache_file(self, fmea_name: str) -> Optional[Path]:
        """
        查找FMEA缓存文件
        
        Args:
            fmea_name: FMEA表格名称（如 "10_Planning_System_SW_FMEA" 或 "Planning"）
            
        Returns:
            缓存文件路径，如果未找到则返回None
        """
        if not self.cache_dir.exists():
            return None
        
        # 构建可能的文件名模式
        patterns = [
            f"wiki_MdbRwDYNyiv8E8kjWOQcuBvXnef_*{fmea_name}*.json",
            f"*{fmea_name}*.json"
        ]
        
        for pattern in patterns:
            for cache_file in self.cache_dir.glob(pattern):
                return cache_file
        
        # 如果精确匹配失败，尝试模糊匹配
        fmea_name_lower = fmea_name.lower()
        for cache_file in self.cache_dir.glob("wiki_MdbRwDYNyiv8E8kjWOQcuBvXnef_*.json"):
            if fmea_name_lower in cache_file.name.lower():
                return cache_file
        
        return None
    
    def load_cache_file(self, cache_file: Path) -> Optional[Dict[str, Any]]:
        """
        加载缓存文件
        
        Args:
            cache_file: 缓存文件路径
            
        Returns:
            缓存数据字典，如果加载失败则返回None
        """
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"[X] 加载缓存文件失败: {e}")
            return None
    
    def identify_main_sheet(self, cache_data: Dict[str, Any]) -> Optional[str]:
        """
        识别主工作表（失效模式影响分析相关的工作表）
        
        Args:
            cache_data: 缓存数据字典
            
        Returns:
            主工作表名称，如果未找到则返回None
        """
        sheets = cache_data.get('sheets', {})
        
        if not sheets:
            return None
        
        # 优先匹配包含关键词的工作表
        for sheet_name, sheet_data in sheets.items():
            sheet_name_lower = sheet_name.lower()
            for keyword in self.MAIN_SHEET_KEYWORDS:
                if keyword.lower() in sheet_name_lower:
                    # 检查是否有数据
                    rows = sheet_data.get('rows', [])
                    if rows:
                        return sheet_name
        
        # 如果没有找到匹配的工作表，返回第一个有数据的工作表
        for sheet_name, sheet_data in sheets.items():
            rows = sheet_data.get('rows', [])
            if rows:
                return sheet_name
        
        return None
    
    def get_sheet_data(self, cache_data: Dict[str, Any], sheet_name: str = None) -> Optional[Dict[str, Any]]:
        """
        获取工作表数据
        
        Args:
            cache_data: 缓存数据字典
            sheet_name: 工作表名称，如果为None则自动识别主工作表
            
        Returns:
            工作表数据字典，包含：
            - sheet_name: 工作表名称
            - headers: 表头列表
            - rows: 行数据列表（每行是一个字典，key为表头）
        """
        sheets = cache_data.get('sheets', {})
        
        if not sheet_name:
            sheet_name = self.identify_main_sheet(cache_data)
            if not sheet_name:
                return None
        
        sheet_data = sheets.get(sheet_name)
        if not sheet_data:
            return None
        
        headers = sheet_data.get('headers', [])
        rows = sheet_data.get('rows', [])
        
        # 将行数据转换为字典格式（key为表头）
        formatted_rows = []
        for row in rows:
            row_dict = {}
            for i, header in enumerate(headers):
                if i < len(row):
                    value = row[i]
                    # 处理富文本格式（列表格式）：提取纯文本
                    if isinstance(value, list):
                        text_parts = []
                        has_strikethrough = False
                        for item in value:
                            if isinstance(item, dict) and 'text' in item:
                                # 检查是否有删除线
                                segment_style = item.get('segmentStyle', {})
                                if segment_style.get('strikeThrough', False):
                                    has_strikethrough = True
                                text_parts.append(item['text'])
                        # 如果所有文本都有删除线，标记为None（表示应跳过）
                        if has_strikethrough and text_parts:
                            value = None  # 标记为None，后续会跳过
                        else:
                            value = ''.join(text_parts) if text_parts else ''
                    row_dict[header] = value
                else:
                    row_dict[header] = ""
            formatted_rows.append(row_dict)
        
        return {
            'sheet_name': sheet_name,
            'headers': headers,
            'rows': formatted_rows,
            'row_count': len(formatted_rows)
        }
    
    def read_fmea_data(self, fmea_name: str, sheet_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        读取FMEA数据（完整流程）
        
        Args:
            fmea_name: FMEA表格名称
            sheet_name: 工作表名称，如果为None则自动识别主工作表
            
        Returns:
            FMEA数据字典，包含：
            - cache_file: 缓存文件路径
            - fmea_name: FMEA表格名称
            - sheet_name: 主工作表名称
            - headers: 表头列表
            - rows: 行数据列表
            - row_count: 行数
        """
        # 查找缓存文件
        cache_file = self.find_fmea_cache_file(fmea_name)
        if not cache_file:
            print(f"[X] 未找到FMEA缓存文件: {fmea_name}")
            return None
        
        print(f"[OK] 找到缓存文件: {cache_file.name}")
        
        # 加载缓存文件
        cache_data = self.load_cache_file(cache_file)
        if not cache_data:
            return None
        
        # 获取工作表数据
        sheet_data = self.get_sheet_data(cache_data, sheet_name=sheet_name)
        if not sheet_data:
            if sheet_name:
                print(f"[X] 未找到指定工作表: {sheet_name}")
            else:
                print(f"[X] 未找到主工作表或工作表为空")
            return None
        
        print(f"[OK] 识别主工作表: {sheet_data['sheet_name']}")
        print(f"[OK] 数据行数: {sheet_data['row_count']}")
        
        return {
            'cache_file': str(cache_file),
            'fmea_name': fmea_name,
            **sheet_data
        }
    
    def validate_data(self, fmea_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证和清洗数据
        
        Args:
            fmea_data: FMEA数据字典
            
        Returns:
            验证结果字典，包含：
            - valid: 是否有效
            - issues: 问题列表
            - cleaned_rows: 清洗后的行数据
        """
        issues = []
        cleaned_rows = []
        
        headers = fmea_data.get('headers', [])
        rows = fmea_data.get('rows', [])
        
        if not headers:
            issues.append("缺少表头")
            return {
                'valid': False,
                'issues': issues,
                'cleaned_rows': []
            }
        
        if not rows:
            issues.append("没有数据行")
            return {
                'valid': False,
                'issues': issues,
                'cleaned_rows': []
            }
        
        # 检查必需字段（根据实际FMEA表格结构调整）
        required_fields = []  # 暂时不设置必需字段，因为不同FMEA表格结构可能不同
        
        # 清洗数据
        for i, row in enumerate(rows, 1):
            # 检查是否所有字段都为空
            if all(not str(value).strip() for value in row.values()):
                issues.append(f"第{i}行：所有字段都为空，跳过")
                continue
            
            # 清理空白字符
            cleaned_row = {}
            for header, value in row.items():
                if isinstance(value, str):
                    cleaned_row[header] = value.strip()
                else:
                    cleaned_row[header] = value
            
            cleaned_rows.append(cleaned_row)
        
        return {
            'valid': len(cleaned_rows) > 0,
            'issues': issues,
            'cleaned_rows': cleaned_rows
        }


def main():
    """测试函数"""
    reader = FMEADataReader()
    
    # 测试读取Planning FMEA
    fmea_name = "10_Planning_System_SW_FMEA"
    print(f"测试读取: {fmea_name}")
    print("=" * 80)
    
    fmea_data = reader.read_fmea_data(fmea_name)
    if fmea_data:
        print(f"\n表头（前10个）: {fmea_data['headers'][:10]}")
        print(f"\n第一行数据示例:")
        if fmea_data['rows']:
            first_row = fmea_data['rows'][0]
            for i, (header, value) in enumerate(list(first_row.items())[:5]):
                print(f"  {header}: {value}")
        
        # 验证数据
        validation = reader.validate_data(fmea_data)
        print(f"\n验证结果:")
        print(f"  有效: {validation['valid']}")
        if validation['issues']:
            print(f"  问题: {validation['issues'][:5]}")
        print(f"  清洗后行数: {len(validation['cleaned_rows'])}")


if __name__ == "__main__":
    main()

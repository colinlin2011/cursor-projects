# -*- coding: utf-8 -*-
"""
在线表格自然语言查询接口

基于缓存数据，提供自然语言查询能力
"""

import sys
import os
import json
from typing import Optional, Dict, List, Any
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from spreadsheet_cache_manager import SpreadsheetCacheManager, SPREADSHEET_CONFIGS, CACHE_DIR

# 配置信息
APP_ID = "cli_a9c92ca516f99bd9"
APP_SECRET = "zlOKnyZkSuSUSr0WlAl6qbh5Qw4eM6wC"
USER_ACCESS_TOKEN = os.getenv("FEISHU_USER_ACCESS_TOKEN", "u-fjEA3Zj5J4eGr.QY6KVnXg14hgJ04kgVOOwaFMy024ps")
SPACE_ID = "7353073903872868356"

# 修复Windows控制台编码问题
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass


class SpreadsheetQueryInterface:
    """在线表格查询接口"""
    
    def __init__(self):
        """初始化查询接口"""
        self.manager = SpreadsheetCacheManager(
            app_id=APP_ID,
            app_secret=APP_SECRET,
            user_access_token=USER_ACCESS_TOKEN,
            space_id=SPACE_ID
        )
        self._cache_data = {}  # 内存缓存
    
    def _load_cache_data(self, cache_file: str) -> Optional[Dict]:
        """加载缓存数据（带内存缓存）"""
        if cache_file in self._cache_data:
            return self._cache_data[cache_file]
        
        data = self.manager.get_cached_data(cache_file)
        if data:
            self._cache_data[cache_file] = data
        return data
    
    def get_sheet_data(self, sheet_name: str, cache_file: str = None) -> Optional[Dict]:
        """
        获取工作表数据
        
        Args:
            sheet_name: 工作表名称
            cache_file: 缓存文件名（可选，如果为None会在所有缓存中搜索）
            
        Returns:
            工作表数据字典，包含：
            - sheet_id: 工作表ID
            - title: 工作表名称
            - headers: 表头（第一行）
            - rows: 数据行
            - row_count: 行数
            - column_count: 列数
        """
        if cache_file:
            data = self._load_cache_data(cache_file)
            if data:
                return data.get('sheets', {}).get(sheet_name)
        else:
            # 从所有缓存中搜索
            for config in SPREADSHEET_CONFIGS:
                data = self._load_cache_data(config['cache_file'])
                if data:
                    sheet = data.get('sheets', {}).get(sheet_name)
                    if sheet:
                        return sheet
        return None
    
    def search_in_sheet(
        self,
        sheet_name: str,
        search_text: str,
        cache_file: str = None
    ) -> List[Dict]:
        """
        在工作表中搜索包含指定文本的行
        
        Args:
            sheet_name: 工作表名称
            search_text: 搜索文本
            cache_file: 缓存文件名（可选）
            
        Returns:
            匹配的行列表（每行是一个字典，key为列名，value为单元格值）
        """
        sheet_data = self.get_sheet_data(sheet_name, cache_file)
        if not sheet_data:
            return []
        
        headers = sheet_data.get('headers', [])
        rows = sheet_data.get('rows', [])
        matching_rows = []
        
        for row in rows:
            # 检查行中是否包含搜索文本
            row_text = ' '.join([str(cell) if cell is not None else '' for cell in row])
            if search_text.lower() in row_text.lower():
                # 转换为字典格式
                row_dict = {}
                for i, header in enumerate(headers):
                    if i < len(row):
                        row_dict[header] = row[i]
                matching_rows.append(row_dict)
        
        return matching_rows
    
    def get_row_by_index(
        self,
        sheet_name: str,
        row_index: int,
        cache_file: str = None
    ) -> Optional[Dict]:
        """
        根据行索引获取行数据
        
        Args:
            sheet_name: 工作表名称
            row_index: 行索引（0-based，不包括表头）
            cache_file: 缓存文件名（可选）
            
        Returns:
            行数据字典
        """
        sheet_data = self.get_sheet_data(sheet_name, cache_file)
        if not sheet_data:
            return None
        
        headers = sheet_data.get('headers', [])
        rows = sheet_data.get('rows', [])
        
        if row_index < 0 or row_index >= len(rows):
            return None
        
        row = rows[row_index]
        row_dict = {}
        for i, header in enumerate(headers):
            if i < len(row):
                row_dict[header] = row[i]
        
        return row_dict
    
    def get_all_sheets(self, cache_file: str = None) -> List[str]:
        """
        获取所有工作表名称列表
        
        Args:
            cache_file: 缓存文件名（可选）
            
        Returns:
            工作表名称列表
        """
        sheets = []
        
        if cache_file:
            data = self._load_cache_data(cache_file)
            if data:
                sheets = list(data.get('sheets', {}).keys())
        else:
            # 从所有缓存中收集
            seen = set()
            for config in SPREADSHEET_CONFIGS:
                data = self._load_cache_data(config['cache_file'])
                if data:
                    for name in data.get('sheets', {}).keys():
                        if name not in seen:
                            sheets.append(name)
                            seen.add(name)
        
        return sorted(sheets)
    
    def get_cache_summary(self) -> Dict[str, Any]:
        """
        获取缓存数据摘要
        
        Returns:
            缓存摘要信息
        """
        summary = {}
        
        for config in SPREADSHEET_CONFIGS:
            name = config['name']
            cache_file = config['cache_file']
            data = self._load_cache_data(cache_file)
            
            if data:
                summary[name] = {
                    'cache_file': cache_file,
                    'node_token': config['node_token'],
                    'cache_time': data.get('cache_time', 0),
                    'sheets': {
                        sheet_name: {
                            'row_count': sheet_data.get('row_count', 0),
                            'column_count': sheet_data.get('column_count', 0)
                        }
                        for sheet_name, sheet_data in data.get('sheets', {}).items()
                    }
                }
        
        return summary


# 全局查询接口实例
_query_interface = None

def get_query_interface() -> SpreadsheetQueryInterface:
    """获取全局查询接口实例"""
    global _query_interface
    if _query_interface is None:
        _query_interface = SpreadsheetQueryInterface()
    return _query_interface


# 便捷函数
def get_sheet(sheet_name: str) -> Optional[Dict]:
    """获取工作表数据（便捷函数）"""
    return get_query_interface().get_sheet_data(sheet_name)


def search_sheet(sheet_name: str, search_text: str) -> List[Dict]:
    """在工作表中搜索（便捷函数）"""
    return get_query_interface().search_in_sheet(sheet_name, search_text)


def get_all_sheets() -> List[str]:
    """获取所有工作表列表（便捷函数）"""
    return get_query_interface().get_all_sheets()


if __name__ == "__main__":
    # 测试查询接口
    interface = SpreadsheetQueryInterface()
    
    print("=" * 80)
    print("在线表格查询接口测试")
    print("=" * 80)
    print()
    
    # 获取缓存摘要
    summary = interface.get_cache_summary()
    print("缓存数据摘要:")
    for name, info in summary.items():
        print(f"\n## {name}")
        print(f"  工作表数: {len(info['sheets'])}")
        total_rows = sum(s.get('row_count', 0) for s in info['sheets'].values())
        print(f"  总行数: {total_rows}")
        for sheet_name, sheet_info in info['sheets'].items():
            print(f"  - {sheet_name}: {sheet_info['row_count']} 行, {sheet_info['column_count']} 列")
    
    print()
    print("=" * 80)
    print("测试查询: System SW FMEA工作表")
    print("=" * 80)
    print()
    
    sheet = interface.get_sheet_data("System SW FMEA")
    if sheet:
        print(f"工作表: {sheet.get('title', '')}")
        print(f"行数: {sheet.get('row_count', 0)}")
        print(f"列数: {sheet.get('column_count', 0)}")
        headers = [str(h) if h is not None else '' for h in sheet.get('headers', [])]
        print(f"表头: {', '.join(headers)}")
        
        # 显示前3行数据
        rows = sheet.get('rows', [])
        if rows:
            print()
            print("前3行数据:")
            for i, row in enumerate(rows[:3], 1):
                print(f"  行{i}: {row}")
    else:
        print("未找到该工作表")

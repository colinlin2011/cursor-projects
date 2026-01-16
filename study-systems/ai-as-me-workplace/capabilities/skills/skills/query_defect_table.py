# -*- coding: utf-8 -*-
"""
查询缺陷问题闭环表的记录数
"""

import sys
import os
import json
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bitable_query_interface import get_query_interface

# 修复Windows控制台编码问题
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

def main():
    interface = get_query_interface()
    
    # 从新多维表格缓存中查询
    cache_file = "new_bitable.json"
    
    # 获取"10. 缺陷问题闭环表"的数据
    table_name = "10. 缺陷问题闭环表"
    table_data = interface.get_table_data(table_name, cache_file)
    
    if table_data:
        record_count = table_data.get('record_count', 0)
        print("=" * 80)
        print(f"功能安全业务数据 - {table_name}")
        print("=" * 80)
        print()
        print(f"缺陷问题记录数: {record_count} 个")
        print()
        
        # 显示表结构信息
        fields = table_data.get('fields', [])
        if fields:
            print(f"字段数: {len(fields)} 个")
            print()
            print("主要字段:")
            for i, field in enumerate(fields[:10], 1):
                print(f"  {i}. {field.get('field_name', '')} ({field.get('field_type', '')})")
            if len(fields) > 10:
                print(f"  ... (共 {len(fields)} 个字段)")
    else:
        print(f"[!] 未找到数据表: {table_name}")
        print()
        print("可用的数据表:")
        # 列出所有数据表
        from bitable_cache_manager import CACHE_DIR
        cache_path = CACHE_DIR / cache_file
        if cache_path.exists():
            with open(cache_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for name in data.get('tables', {}).keys():
                    print(f"  - {name}")

if __name__ == "__main__":
    main()

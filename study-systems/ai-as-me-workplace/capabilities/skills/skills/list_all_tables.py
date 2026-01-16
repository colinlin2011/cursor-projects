# -*- coding: utf-8 -*-
"""
列出所有数据表及其记录数
"""

import sys
import os
import json
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bitable_cache_manager import CACHE_DIR

# 修复Windows控制台编码问题
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

def main():
    cache_file = "new_bitable.json"
    cache_path = CACHE_DIR / cache_file
    
    if not cache_path.exists():
        print(f"[X] 缓存文件不存在: {cache_path}")
        return
    
    print("=" * 80)
    print("功能安全业务数据 - 所有数据表")
    print("=" * 80)
    print()
    
    with open(cache_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        tables = data.get('tables', {})
        
        print(f"数据表总数: {len(tables)}")
        print()
        
        # 查找缺陷问题相关的表
        defect_tables = []
        for name, info in sorted(tables.items()):
            record_count = info.get('record_count', 0)
            if '缺陷' in name or '问题' in name or '闭环' in name:
                defect_tables.append((name, record_count))
            print(f"  {name}: {record_count} 条记录")
        
        print()
        print("=" * 80)
        print("缺陷问题相关表:")
        print("=" * 80)
        print()
        
        if defect_tables:
            for name, count in defect_tables:
                print(f"  {name}: {count} 条记录")
        else:
            print("  未找到缺陷问题相关的表")

if __name__ == "__main__":
    main()

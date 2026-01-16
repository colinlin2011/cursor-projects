# -*- coding: utf-8 -*-
"""
检查缓存中"缺陷问题闭环表"的记录数
"""

import sys
import os
import json
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bitable_cache_manager import CACHE_DIR, BITABLE_CONFIGS

# 修复Windows控制台编码问题
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

def check_cache_records():
    """检查缓存中的记录数"""
    
    # 找到"功能安全业务数据"的配置
    config = None
    for cfg in BITABLE_CONFIGS:
        if "功能安全业务数据" in cfg.get("name", "") or cfg.get("name") == "新多维表格":
            config = cfg
            break
    
    if not config:
        print("[X] 未找到配置")
        return
    
    cache_file = config['cache_file']
    cache_path = CACHE_DIR / cache_file
    
    print("=" * 80)
    print("检查缓存中的记录数")
    print("=" * 80)
    print()
    print(f"多维表格: {config['name']}")
    print(f"缓存文件: {cache_path}")
    print()
    
    if not cache_path.exists():
        print("[!] 缓存文件不存在")
        return
    
    try:
        with open(cache_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        tables = data.get('tables', {})
        
        print(f"数据表总数: {len(tables)}")
        print()
        
        # 查找缺陷问题闭环表
        defect_table = None
        defect_table_name = None
        
        for table_name, table_data in tables.items():
            if '缺陷问题闭环' in table_name or ('缺陷' in table_name and '闭环' in table_name):
                defect_table = table_data
                defect_table_name = table_name
                break
        
        if not defect_table:
            print("[!] 未找到'缺陷问题闭环表'")
            print()
            print("所有数据表:")
            for table_name, table_data in tables.items():
                record_count = table_data.get('record_count', 0)
                print(f"  - {table_name}: {record_count} 条记录")
            return
        
        record_count = defect_table.get('record_count', 0)
        
        print(f"找到数据表: {defect_table_name}")
        print(f"记录数: {record_count} 条")
        print()
        
        if record_count == 253:
            print("[✓] 记录数正确：253 条")
        else:
            print(f"[!] 记录数不匹配：期望 253 条，实际 {record_count} 条")
            print()
            print("需要同步缓存以更新数据")
        
    except Exception as e:
        print(f"[X] 读取缓存失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_cache_records()

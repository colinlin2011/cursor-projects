# -*- coding: utf-8 -*-
"""
检查多维表格缓存

验证"功能安全业务数据"多维表格的所有14个表是否都已缓存
"""

import sys
import os
import json
from pathlib import Path

# 修复Windows控制台编码问题
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 缓存文件路径
cache_file = Path("work/bitable_cache/new_bitable.json")

if not cache_file.exists():
    print(f"[!] 缓存文件不存在: {cache_file}")
    print("请先运行同步脚本：python auto_sync_all.py --once --force")
    sys.exit(1)

print("=" * 80)
print("检查'功能安全业务数据'多维表格缓存")
print("=" * 80)
print()

# 加载缓存数据
with open(cache_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

tables = data.get('tables', {})
cache_time = data.get('cache_time', 0)

print(f"缓存文件: {cache_file}")
print(f"缓存时间: {data.get('cache_time', 0)}")
print(f"表数量: {len(tables)}")
print()

if len(tables) == 0:
    print("[!] 缓存中没有表数据")
    sys.exit(1)

print("所有表及其记录数:")
print("-" * 80)
total_records = 0
for i, (name, table_info) in enumerate(tables.items(), 1):
    record_count = table_info.get('record_count', 0)
    table_id = table_info.get('table_id', 'N/A')
    total_records += record_count
    print(f"{i:2d}. {name}")
    print(f"     表ID: {table_id}")
    print(f"     记录数: {record_count}")
    print()

print("-" * 80)
print(f"总计: {len(tables)} 个表，{total_records} 条记录")
print()

# 检查是否包含"06. 安全需求总表"
safety_table_found = False
for name in tables.keys():
    if "06. 安全需求总表" in name or "安全需求总表" in name:
        safety_table_found = True
        print(f"[OK] 找到安全需求总表: {name}")
        break

if not safety_table_found:
    print("[!] 未找到'06. 安全需求总表'")

print()
print("=" * 80)
print("缓存验证完成")
print("=" * 80)

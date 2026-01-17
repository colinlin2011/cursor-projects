# -*- coding: utf-8 -*-
"""
检查Wiki节点下的在线表格缓存

验证所有在线表格是否已成功缓存
"""

import sys
import json
from pathlib import Path

# 修复Windows控制台编码问题
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

# 配置文件
config_file = Path("work/spreadsheet_cache/wiki_MdbRwDYNyiv8E8kjWOQcuBvXnef_config.json")

if not config_file.exists():
    print(f"[!] 配置文件不存在: {config_file}")
    print("请先运行缓存脚本：python cache_wiki_spreadsheets.py")
    sys.exit(1)

print("=" * 80)
print("检查Wiki节点下的在线表格缓存")
print("=" * 80)
print()

# 加载配置
with open(config_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

node_token = data.get('node_token', '')
node_url = data.get('node_url', '')
cached_spreadsheets = data.get('cached_spreadsheets', [])

print(f"节点URL: {node_url}")
print(f"Node Token: {node_token}")
print(f"已缓存的在线表格数: {len(cached_spreadsheets)}")
print()

if len(cached_spreadsheets) == 0:
    print("[!] 没有缓存的在线表格")
    sys.exit(1)

print("所有已缓存的在线表格:")
print("-" * 80)

total_sheets = 0
total_rows = 0

for i, spreadsheet in enumerate(cached_spreadsheets, 1):
    title = spreadsheet.get('title', '未知')
    sheets_count = spreadsheet.get('sheets_count', 0)
    total_rows_count = spreadsheet.get('total_rows', 0)
    cache_file = spreadsheet.get('cache_file', '')
    
    total_sheets += sheets_count
    total_rows += total_rows_count
    
    print(f"{i:2d}. {title}")
    print(f"     工作表数: {sheets_count}")
    print(f"     总行数: {total_rows_count}")
    print(f"     缓存文件: {cache_file}")
    print()

print("-" * 80)
print(f"总计: {len(cached_spreadsheets)} 个在线表格")
print(f"      {total_sheets} 个工作表")
print(f"      {total_rows} 行数据")
print()

# 验证缓存文件是否存在
print("验证缓存文件...")
missing_files = []
for spreadsheet in cached_spreadsheets:
    cache_file = spreadsheet.get('cache_file', '')
    if cache_file:
        file_path = Path("work/spreadsheet_cache") / cache_file
        if not file_path.exists():
            missing_files.append((spreadsheet.get('title', '未知'), cache_file))

if missing_files:
    print(f"[!] 发现 {len(missing_files)} 个缺失的缓存文件:")
    for title, cache_file in missing_files:
        print(f"  - {title}: {cache_file}")
else:
    print("[OK] 所有缓存文件都存在")

print()
print("=" * 80)
print("验证完成")
print("=" * 80)

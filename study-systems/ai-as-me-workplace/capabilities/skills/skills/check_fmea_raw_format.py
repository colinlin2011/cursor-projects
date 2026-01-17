# -*- coding: utf-8 -*-
"""检查FMEA原始数据中Function Description的格式"""

import json
from pathlib import Path

cache_file = Path("work/spreadsheet_cache/wiki_MdbRwDYNyiv8E8kjWOQcuBvXnef_14_11_Control_System_SW_FMEA.json")

with open(cache_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

sheet = data['sheets']['System SW FMEA']
headers = sheet['headers']
rows = sheet['rows']

func_idx = 2  # Function Description列索引

print("检查Function Description的格式:")
print("=" * 80)

# 查找包含富文本格式的行
for i, row in enumerate(rows):
    if len(row) > func_idx:
        func = row[func_idx]
        if func:
            func_type = type(func).__name__
            if isinstance(func, list):
                print(f"\n第{i+1}行 - Function Description是列表格式（富文本）:")
                print(json.dumps(func, ensure_ascii=False, indent=2)[:800])
                # 提取纯文本
                text_parts = []
                for item in func:
                    if isinstance(item, dict) and 'text' in item:
                        text_parts.append(item['text'])
                print(f"\n提取的纯文本: {''.join(text_parts)}")
                print()
                if i > 10:  # 只显示前几个
                    break

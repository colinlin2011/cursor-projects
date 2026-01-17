# -*- coding: utf-8 -*-
"""检查Function Description的格式"""

from fmea_data_reader import FMEADataReader
import json

reader = FMEADataReader()
data = reader.read_fmea_data('Control')
validation = reader.validate_data(data)
rows = validation['cleaned_rows']

print("检查Function Description的格式:")
print("=" * 80)

# 查找包含富文本格式的行
for i, row in enumerate(rows[:50]):
    func = row.get('Function Description', '')
    if func:
        func_type = type(func).__name__
        if isinstance(func, list):
            print(f"\n第{i+1}行 - Function Description是列表格式:")
            print(json.dumps(func, ensure_ascii=False, indent=2)[:500])
            # 提取纯文本
            text_parts = []
            for item in func:
                if isinstance(item, dict) and 'text' in item:
                    text_parts.append(item['text'])
            print(f"\n提取的纯文本: {''.join(text_parts)}")
            break
        elif isinstance(func, str):
            if i < 5:
                print(f"第{i+1}行 - Function Description是字符串: {func[:50]}")

# -*- coding: utf-8 -*-
"""检查子功能清单表中是否有富文本格式的功能描述"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from feishu_bitable_collaborator import create_bitable_collaborator
from token_manager import TokenManager
from bitable_cache_manager import APP_ID, APP_SECRET
import json
from pathlib import Path
from bitable_cache_manager import CACHE_DIR

token = TokenManager().get_valid_user_access_token()
collaborator = create_bitable_collaborator(APP_ID, APP_SECRET, token)

# 从缓存获取app_token和table_id
cache_file = CACHE_DIR / "new_bitable.json"
with open(cache_file, 'r', encoding='utf-8') as f:
    cache_data = json.load(f)

app_token = cache_data.get('app_token')
tables = cache_data.get('tables', {})
for name, data in tables.items():
    if '子功能清单表' in name:
        table_id = data.get('table_id')
        break

# 获取所有记录
records = collaborator.get_all_records(app_token, table_id)
print(f"记录数: {len(records)}")

# 查找包含富文本格式的记录
print("\n查找富文本格式的功能描述:")
print("=" * 80)

richtext_count = 0
for i, record in enumerate(records):
    record_fields = record.get('fields', {})
    function_description = record_fields.get('功能描述', '')
    
    if isinstance(function_description, list):
        richtext_count += 1
        if richtext_count <= 5:
            print(f"\n记录{i+1} (record_id: {record.get('record_id')}) - 功能描述是列表格式（富文本）:")
            print(json.dumps(function_description, ensure_ascii=False, indent=2)[:500])
            # 提取纯文本
            text_parts = []
            for item in function_description:
                if isinstance(item, dict) and 'text' in item:
                    text_parts.append(item['text'])
            print(f"\n提取的纯文本: {''.join(text_parts)}")

print(f"\n总计: {richtext_count} 条记录包含富文本格式的功能描述")

# -*- coding: utf-8 -*-
"""检查已导入的失效模式记录"""

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
    if '失效模式影响分析表_SW' in name:
        table_id = data.get('table_id')
        print(f"表名: {name}")
        print(f"table_id: {table_id}")
        break

# 获取表格结构
structure = collaborator.get_table_structure(app_token, table_id)
fields = structure.get('fields', [])

print("\n查找'关联功能'字段:")
for field in fields:
    if '关联功能' in field.get('field_name', ''):
        print(f"  字段名: {field.get('field_name')}")
        print(f"  字段ID: {field.get('field_id')}")
        print(f"  字段类型: {field.get('type')}")
        function_field_id = field.get('field_id')
        break

# 获取前10条记录
records = collaborator.get_all_records(app_token, table_id)
print(f"\n记录数: {len(records)}")

print("\n前5条记录的'关联功能'字段值:")
for i, record in enumerate(records[:5], 1):
    record_fields = record.get('fields', {})
    function_relation = record_fields.get('关联功能', [])
    
    print(f"\n记录{i}:")
    print(f"  关联功能类型: {type(function_relation).__name__}")
    if isinstance(function_relation, list):
        print(f"  关联功能数量: {len(function_relation)}")
        for j, item in enumerate(function_relation[:3], 1):
            if isinstance(item, dict):
                print(f"    {j}. {json.dumps(item, ensure_ascii=False, indent=2)[:200]}")
            else:
                print(f"    {j}. {item}")
    else:
        print(f"  关联功能: {function_relation}")

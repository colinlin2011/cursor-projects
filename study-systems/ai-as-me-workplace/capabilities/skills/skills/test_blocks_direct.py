# -*- coding: utf-8 -*-
"""
直接测试blocks获取
"""

import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

sys.stdout.reconfigure(encoding='utf-8')

from feishu_doc_collaborator import FeishuDocCollaborator
from fault_diagnosis_config import APP_ID, APP_SECRET, SPACE_ID, get_dynamic_user_access_token

print("=" * 80)
print("直接测试blocks获取")
print("=" * 80)
print()

token = get_dynamic_user_access_token()
print(f"Token: {token[:30]}...")
print()

collaborator = FeishuDocCollaborator(
    app_id=APP_ID,
    app_secret=APP_SECRET,
    user_access_token=token,
    space_id=SPACE_ID
)

node_token = "UBS2wO9aai7jB7kaw4QcQGNbngc"
document_id = "SLPQdlAV4owz2BxkC1ic1QdWnrB"

print(f"Node Token: {node_token}")
print(f"Document ID: {document_id}")
print()

# 直接调用API获取blocks
print("直接调用API获取blocks")
print("-" * 80)

blocks = collaborator.api.get_document_blocks(
    document_id=document_id,
    page_size=500,
    use_user_token=True
)

print(f"返回类型: {type(blocks)}")
print(f"Code: {blocks.get('code') if isinstance(blocks, dict) else 'N/A'}")
print(f"是否有data: {'data' in blocks if isinstance(blocks, dict) else False}")

if isinstance(blocks, dict) and blocks.get('code') == 0:
    data = blocks.get('data', {})
    items = data.get('items', [])
    print(f"Items数量: {len(items)}")
    print(f"Has more: {data.get('has_more', False)}")
    print(f"Page token: {data.get('page_token', 'N/A')[:50] if data.get('page_token') else 'N/A'}")
    
    if items:
        print(f"\n第一个block类型: {items[0].get('block_type')}")
        print(f"第一个block ID: {items[0].get('block_id')}")
else:
    print(f"返回结果: {json.dumps(blocks, ensure_ascii=False, indent=2)[:500] if isinstance(blocks, dict) else str(blocks)[:500]}")

print()

# 使用_get_all_blocks方法
print("使用_get_all_blocks方法")
print("-" * 80)

all_blocks = collaborator._get_all_blocks(document_id)
print(f"获取到的blocks数量: {len(all_blocks)}")

if all_blocks:
    print(f"第一个block类型: {all_blocks[0].get('block_type')}")
    print(f"第一个block ID: {all_blocks[0].get('block_id')}")

print()
print("=" * 80)
print("测试完成")
print("=" * 80)

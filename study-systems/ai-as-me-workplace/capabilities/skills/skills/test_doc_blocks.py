# -*- coding: utf-8 -*-
"""
测试文档blocks获取
"""

import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

sys.stdout.reconfigure(encoding='utf-8')

from feishu_api_wrapper import FeishuAPI
from fault_diagnosis_config import APP_ID, APP_SECRET, get_dynamic_user_access_token

print("=" * 80)
print("测试文档blocks获取")
print("=" * 80)
print()

token = get_dynamic_user_access_token()
print(f"Token: {token[:30]}...")
print()

api = FeishuAPI(
    plugin_id="",
    plugin_secret="",
    app_id=APP_ID,
    app_secret=APP_SECRET
)
api.set_user_access_token(token)

document_id = "SLPQdlAV4owz2BxkC1ic1QdWnrB"

print(f"Document ID: {document_id}")
print()

# 测试获取blocks
print("测试获取文档blocks")
print("-" * 80)

blocks = api.get_document_blocks(
    document_id=document_id,
    page_size=500,
    use_user_token=True
)

print(f"返回结果类型: {type(blocks)}")
print(f"返回结果: {json.dumps(blocks, ensure_ascii=False, indent=2) if isinstance(blocks, dict) else str(blocks)[:200]}")

if blocks:
    if isinstance(blocks, dict):
        code = blocks.get('code')
        print(f"Code: {code}")
        
        if code == 0:
            data = blocks.get('data', {})
            items = data.get('items', [])
            print(f"Items数量: {len(items)}")
            if items:
                print(f"第一个block: {json.dumps(items[0], ensure_ascii=False, indent=2)[:500]}")
        else:
            print(f"错误信息: {blocks.get('msg')}")
            print(f"完整响应: {json.dumps(blocks, ensure_ascii=False, indent=2)}")

print()
print("=" * 80)
print("测试完成")
print("=" * 80)

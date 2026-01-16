# -*- coding: utf-8 -*-
"""
测试文档访问
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

sys.stdout.reconfigure(encoding='utf-8')

from feishu_doc_collaborator import FeishuDocCollaborator
from fault_diagnosis_config import APP_ID, APP_SECRET, SPACE_ID, get_dynamic_user_access_token

print("=" * 80)
print("测试文档访问")
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

print(f"测试节点: {node_token}")
print()

# 测试获取document_id
print("步骤1: 获取document_id")
print("-" * 80)
document_id = collaborator._get_document_id_from_node(node_token)
print(f"Document ID: {document_id}")
print()

if document_id:
    print("步骤2: 获取文档内容")
    print("-" * 80)
    blocks = collaborator._get_all_blocks(document_id)
    print(f"Blocks数量: {len(blocks) if blocks else 0}")
    
    if blocks:
        print("[OK] 成功获取文档内容")
        # 转换为Markdown
        md_content = collaborator._blocks_to_markdown(blocks)
        print(f"Markdown内容长度: {len(md_content)}")
        print(f"前200字符: {md_content[:200]}")
    else:
        print("[X] 无法获取文档内容")
else:
    print("[X] 无法获取document_id")

print()
print("=" * 80)
print("测试完成")
print("=" * 80)

# -*- coding: utf-8 -*-
"""
测试Wiki文档访问权限
"""

import sys
import os
import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

sys.stdout.reconfigure(encoding='utf-8')

from token_manager import get_token_manager
from fault_diagnosis_config import SPACE_ID

print("=" * 80)
print("测试Wiki文档访问权限")
print("=" * 80)
print()

# 获取token
manager = get_token_manager()
token = manager.get_valid_user_access_token()

if not token:
    print("[X] 无法获取有效token")
    sys.exit(1)

print(f"[OK] 获取到token: {token[:30]}...")
print()

# 测试1: 获取Wiki节点信息
print("测试1: 获取Wiki节点信息")
print("-" * 80)

node_token = "UBS2wO9aai7jB7kaw4QcQGNbngc"
url = f"https://open.feishu.cn/open-apis/wiki/v2/spaces/{SPACE_ID}/nodes/{node_token}"
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

try:
    response = requests.get(url, headers=headers)
    print(f"状态码: {response.status_code}")
    result = response.json()
    
    if response.status_code == 200:
        print("[OK] 成功获取Wiki节点信息")
        print(f"节点信息: {result}")
    else:
        print(f"[X] 获取Wiki节点信息失败")
        print(f"错误信息: {result}")
        if result.get('code') == 99991677:
            print("错误原因: Token已过期或无效")
        elif result.get('code') == 99991663:
            print("错误原因: 权限不足，需要wiki:wiki和wiki:node:read权限")
except Exception as e:
    print(f"[X] 请求异常: {e}")

print()

# 测试2: 获取文档内容
print("测试2: 获取文档内容")
print("-" * 80)

# 先从节点获取document_id
try:
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        node_info = response.json()
        obj_token = node_info.get('data', {}).get('node', {}).get('obj_token')
        obj_type = node_info.get('data', {}).get('node', {}).get('obj_type')
        
        print(f"Object Token: {obj_token}")
        print(f"Object Type: {obj_type}")
        
        if obj_type == 'docx' and obj_token:
            # 获取文档内容
            doc_url = f"https://open.feishu.cn/open-apis/docx/v1/documents/{obj_token}/content"
            doc_response = requests.get(doc_url, headers=headers)
            print(f"文档内容请求状态码: {doc_response.status_code}")
            
            if doc_response.status_code == 200:
                print("[OK] 成功获取文档内容")
            else:
                doc_result = doc_response.json()
                print(f"[X] 获取文档内容失败: {doc_result}")
        else:
            print(f"[!] 节点类型不是docx: {obj_type}")
    else:
        print("[X] 无法获取节点信息，跳过文档内容测试")
except Exception as e:
    print(f"[X] 测试异常: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 80)
print("测试完成")
print("=" * 80)

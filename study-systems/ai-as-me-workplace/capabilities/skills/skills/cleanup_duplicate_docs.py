# -*- coding: utf-8 -*-
"""
清理重复的FSC文档

删除指定节点下的重复文档，只保留一个有内容的文档
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from feishu_api_wrapper import FeishuAPI

# 配置信息
APP_ID = "cli_a9c92ca516f99bd9"
APP_SECRET = "zlOKnyZkSuSUSr0WlAl6qbh5Qw4eM6wC"
SPACE_ID = "7353073903872868356"
PARENT_NODE_TOKEN = "V7FXwKKdLiEus3kU9oMcgLwGnpe"
DOC_TITLE = "舱驾一体域控的FSC文档"

# 要删除的文档节点token列表（空文档）
DUPLICATE_NODE_TOKENS = [
    "BLQiwhityiwSFvk5LmYcc3yNn1f",
    "S7ATwMd91iyXpFkVf56czOFAnNe",
    "AMyKw02UniKxqSkayaCcLdVRneh"
]

USER_ACCESS_TOKEN = os.getenv("FEISHU_USER_ACCESS_TOKEN", "u-4tBMNLQZ15Oqb0cGVm.7W.k1n31w4koprGGymw282HUW")

def delete_wiki_node(api: FeishuAPI, space_id: str, node_token: str) -> bool:
    """
    删除Wiki节点
    
    参考文档：飞书开放平台 - Wiki v2 API - 删除节点
    """
    endpoint = f"open-apis/wiki/v2/spaces/{space_id}/nodes/{node_token}"
    result = api._open_platform_request('DELETE', endpoint, use_user_token=True)
    
    if result and result.get('code') == 0:
        return True
    else:
        print(f"  删除失败: {result}")
        return False

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    
    print("=" * 60)
    print("清理重复的FSC文档")
    print("=" * 60)
    print()
    
    if not USER_ACCESS_TOKEN:
        print("[X] 错误：未设置USER_ACCESS_TOKEN")
        return
    
    # 初始化API
    api = FeishuAPI(
        plugin_id="",
        plugin_secret="",
        app_id=APP_ID,
        app_secret=APP_SECRET
    )
    api.set_user_access_token(USER_ACCESS_TOKEN)
    
    print(f"将删除以下文档节点：")
    for token in DUPLICATE_NODE_TOKENS:
        print(f"  - {token}")
    print()
    
    confirm = input("确认删除？(yes/no): ").strip().lower()
    if confirm != 'yes':
        print("已取消")
        return
    
    print()
    print("开始删除...")
    
    success_count = 0
    for token in DUPLICATE_NODE_TOKENS:
        print(f"删除节点: {token}")
        if delete_wiki_node(api, SPACE_ID, token):
            print(f"  [OK] 删除成功")
            success_count += 1
        else:
            print(f"  [X] 删除失败")
        print()
    
    print("=" * 60)
    print(f"删除完成：成功 {success_count}/{len(DUPLICATE_NODE_TOKENS)}")
    print("=" * 60)

if __name__ == "__main__":
    main()

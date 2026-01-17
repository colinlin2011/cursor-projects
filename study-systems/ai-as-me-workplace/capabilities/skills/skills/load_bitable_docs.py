# -*- coding: utf-8 -*-
"""
从多维表格中加载文档内容并缓存

多维表格内部可以包含云文档，需要通过多维表格API获取
"""

import sys
import os
import json
from datetime import datetime
from typing import Optional, Dict, Any
from pathlib import Path

# 修复Windows控制台编码问题
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from token_manager import TokenManager
from feishu_api_wrapper import FeishuAPI
from feishu_doc_collaborator import FeishuDocCollaborator

# 配置信息
APP_ID = "cli_a9c92ca516f99bd9"
APP_SECRET = "zlOKnyZkSuSUSr0WlAl6qbh5Qw4eM6wC"
SPACE_ID = "7353073903872868356"

# 历史工作平台多维表格
LEGACY_APP_TOKEN = "YWDGbSZZKalcnQskTThcSUSXnub"

# 文档node_token（从URL的table参数中提取）
DOC_NODE_TOKENS = [
    "ldxmuDnzIjTSlyRW",
    "ldxHfyQ1eqCXMji4"
]

# 缓存目录
CACHE_DIR = Path(__file__).parent.parent.parent.parent / "work" / "fault_diagnosis_cache" / "guides"
CACHE_DIR.mkdir(parents=True, exist_ok=True)


def get_user_access_token() -> Optional[str]:
    """获取有效的user_access_token（自动刷新）"""
    token_manager = TokenManager()
    token = token_manager.get_valid_user_access_token()
    if not token:
        print("[!] 无法获取有效token，尝试使用环境变量...")
        token = os.getenv("FEISHU_USER_ACCESS_TOKEN")
    return token


def load_doc_from_bitable(
    api: FeishuAPI,
    doc_collaborator: FeishuDocCollaborator,
    node_token: str,
    doc_name: str
) -> bool:
    """
    从多维表格中加载文档
    
    尝试多种方式：
    1. 直接使用node_token作为Wiki节点获取
    2. 通过多维表格API获取文档块
    """
    print(f"  处理文档: {doc_name}")
    print(f"    Node Token: {node_token}")
    
    cache_file = CACHE_DIR / f"guide_{node_token}.json"
    
    # 检查缓存
    if cache_file.exists():
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            cache_time = cache_data.get('cache_time', 0)
            # 缓存有效期24小时
            if datetime.now().timestamp() - cache_time < 24 * 3600:
                print(f"    [OK] 使用缓存（缓存时间: {datetime.fromtimestamp(cache_time).strftime('%Y-%m-%d %H:%M:%S')}）")
                return True
        except Exception as e:
            print(f"    [!] 读取缓存失败: {e}")
    
    # 方法1：尝试直接使用node_token作为Wiki节点
    print(f"    尝试方法1：作为Wiki节点获取...")
    try:
        document_id = doc_collaborator._get_document_id_from_node(node_token)
        if document_id:
            print(f"    [OK] 获取到document_id: {document_id}")
            # 获取文档内容
            blocks = doc_collaborator._get_all_blocks(document_id)
            if blocks:
                doc_content = doc_collaborator._blocks_to_markdown(blocks)
                if doc_content:
                    # 保存缓存
                    cache_data = {
                        'cache_time': datetime.now().timestamp(),
                        'node_token': node_token,
                        'document_id': document_id,
                        'content': doc_content
                    }
                    cache_file.write_text(
                        json.dumps(cache_data, indent=2, ensure_ascii=False),
                        encoding='utf-8'
                    )
                    print(f"    [OK] 文档加载成功并已缓存")
                    return True
    except Exception as e:
        print(f"    [!] 方法1失败: {e}")
    
    # 方法2：尝试通过多维表格获取文档块
    print(f"    尝试方法2：通过多维表格API获取...")
    try:
        # 获取多维表格信息
        bitable_info = api.get_bitable(LEGACY_APP_TOKEN, use_user_token=True)
        if bitable_info:
            print(f"    [OK] 获取到多维表格信息")
            # 注意：多维表格API可能不直接支持获取内部文档
            # 这里可能需要其他方法
    except Exception as e:
        print(f"    [!] 方法2失败: {e}")
    
    # 方法3：尝试直接使用node_token作为document_id（不使用space_id）
    print(f"    尝试方法3：直接使用node_token作为document_id...")
    try:
        # 直接调用文档API，不使用Wiki节点API
        blocks_result = api.get_document_blocks(
            document_id=node_token,
            page_size=500,
            use_user_token=True
        )
        
        if blocks_result:
            # 处理不同的返回格式
            if 'code' in blocks_result:
                if blocks_result.get('code') == 0:
                    items = blocks_result.get('data', {}).get('items', [])
                else:
                    raise Exception(f"API返回错误: {blocks_result.get('msg')}")
            elif 'items' in blocks_result:
                items = blocks_result.get('items', [])
            else:
                items = []
            
            if items:
                # 转换为Markdown
                doc_content = doc_collaborator._blocks_to_markdown(items)
                if doc_content:
                    # 保存缓存
                    cache_data = {
                        'cache_time': datetime.now().timestamp(),
                        'node_token': node_token,
                        'document_id': node_token,
                        'content': doc_content
                    }
                    cache_file.write_text(
                        json.dumps(cache_data, indent=2, ensure_ascii=False),
                        encoding='utf-8'
                    )
                    print(f"    [OK] 文档加载成功并已缓存")
                    return True
    except Exception as e:
        print(f"    [!] 方法3失败: {e}")
    
    print(f"    [X] 所有方法均失败，无法加载文档")
    return False


def main():
    """主函数"""
    print("=" * 80)
    print("从多维表格加载文档内容")
    print("=" * 80)
    print()
    
    # 获取有效的user_access_token
    print("步骤1：获取有效的user_access_token...")
    user_access_token = get_user_access_token()
    if not user_access_token:
        print("[X] 无法获取user_access_token")
        return
    
    print(f"[OK] 已获取user_access_token: {user_access_token[:20]}...")
    print()
    
    # 创建API和协作器
    print("步骤2：初始化API和协作器...")
    api = FeishuAPI(
        plugin_id="",
        plugin_secret="",
        app_id=APP_ID,
        app_secret=APP_SECRET
    )
    api.set_user_access_token(user_access_token)
    
    doc_collaborator = FeishuDocCollaborator(
        app_id=APP_ID,
        app_secret=APP_SECRET,
        user_access_token=user_access_token,
        space_id=SPACE_ID
    )
    
    print("[OK] 初始化完成")
    print()
    
    # 加载文档
    print("步骤3：加载文档...")
    print()
    
    success_count = 0
    for i, node_token in enumerate(DOC_NODE_TOKENS, 1):
        doc_name = f"历史工作平台文档{i}"
        print(f"[{i}/{len(DOC_NODE_TOKENS)}] {doc_name}")
        
        if load_doc_from_bitable(api, doc_collaborator, node_token, doc_name):
            success_count += 1
        
        print()
    
    print("=" * 80)
    print("文档加载完成")
    print(f"成功: {success_count}/{len(DOC_NODE_TOKENS)}")
    print("=" * 80)


if __name__ == "__main__":
    main()

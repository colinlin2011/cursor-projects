# -*- coding: utf-8 -*-
"""
缓存Wiki节点下的所有在线表格文档

从指定的Wiki节点中查找所有在线表格子节点，并缓存它们
"""

import sys
import os
import json
from pathlib import Path
from typing import List, Dict, Any, Optional

# 修复Windows控制台编码问题
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from feishu_api_wrapper import FeishuAPI
from spreadsheet_cache_manager import SpreadsheetCacheManager, CACHE_DIR
from token_manager import get_user_access_token

# 配置信息
APP_ID = "cli_a9c92ca516f99bd9"
APP_SECRET = "zlOKnyZkSuSUSr0WlAl6qbh5Qw4eM6wC"
SPACE_ID = "7353073903872868356"

# 目标节点
TARGET_NODE_TOKEN = "MdbRwDYNyiv8E8kjWOQcuBvXnef"
TARGET_NODE_URL = "https://zyt.feishu.cn/wiki/MdbRwDYNyiv8E8kjWOQcuBvXnef"


def list_all_spreadsheet_nodes(api: FeishuAPI, space_id: str, parent_node_token: str) -> List[Dict[str, Any]]:
    """
    递归列出所有在线表格节点
    
    Args:
        api: FeishuAPI实例
        space_id: 知识库ID
        parent_node_token: 父节点token
        
    Returns:
        在线表格节点列表
    """
    spreadsheet_nodes = []
    page_token = None
    
    print(f"列出节点下的所有子节点: {parent_node_token}...")
    
    while True:
        # 列出子节点
        result = api.list_wiki_nodes(
            space_id=space_id,
            parent_node_token=parent_node_token,
            page_size=50,
            page_token=page_token,
            use_user_token=True
        )
        
        if not result:
            break
        
        items = result.get('items', [])
        if not items:
            break
        
        print(f"  找到 {len(items)} 个子节点")
        
        for item in items:
            node_token = item.get('node_token', '')
            obj_type = item.get('obj_type', '')
            node_type = item.get('node_type', '')
            title = item.get('title', '未知')
            
            print(f"    - {title} (类型: {obj_type}, 节点类型: {node_type})")
            
            # 如果是在线表格
            if obj_type in ['sheet', 'spreadsheet']:
                spreadsheet_nodes.append({
                    'node_token': node_token,
                    'title': title,
                    'obj_type': obj_type,
                    'obj_token': item.get('obj_token', '')
                })
                print(f"      [✓] 在线表格")
            # 如果是文件夹或文档，递归查找（文档节点也可能包含子节点）
            elif node_type == 'folder' or obj_type == 'folder' or obj_type == 'docx':
                print(f"      [→] {node_type}/{obj_type}，递归查找子节点...")
                sub_nodes = list_all_spreadsheet_nodes(api, space_id, node_token)
                spreadsheet_nodes.extend(sub_nodes)
        
        # 检查是否有下一页
        page_token = result.get('page_token')
        if not page_token:
            break
    
    return spreadsheet_nodes


def cache_spreadsheet_node(
    manager: SpreadsheetCacheManager,
    node_token: str,
    title: str,
    cache_file: str
) -> Dict[str, Any]:
    """
    缓存单个在线表格节点
    
    Args:
        manager: SpreadsheetCacheManager实例
        node_token: 节点token
        title: 表格标题
        cache_file: 缓存文件名
        
    Returns:
        缓存结果
    """
    print(f"\n缓存在线表格: {title}")
    print(f"  Node Token: {node_token}")
    print(f"  缓存文件: {cache_file}")
    
    try:
        data = manager.load_spreadsheet_data(
            node_token=node_token,
            cache_file=cache_file,
            force_refresh=True
        )
        
        sheets_count = len(data.get('sheets', {}))
        total_rows = sum(s.get('row_count', 0) for s in data.get('sheets', {}).values())
        
        return {
            'success': True,
            'title': title,
            'node_token': node_token,
            'cache_file': cache_file,
            'sheets_count': sheets_count,
            'total_rows': total_rows
        }
    except Exception as e:
        print(f"  [X] 缓存失败: {e}")
        import traceback
        traceback.print_exc()
        return {
            'success': False,
            'title': title,
            'node_token': node_token,
            'error': str(e)
        }


def main():
    """主函数"""
    print("=" * 80)
    print("缓存Wiki节点下的所有在线表格文档")
    print("=" * 80)
    print()
    print(f"目标节点: {TARGET_NODE_URL}")
    print(f"Node Token: {TARGET_NODE_TOKEN}")
    print()
    
    # 获取有效的访问令牌
    user_access_token = get_user_access_token()
    if not user_access_token:
        print("[X] 无法获取有效的访问令牌")
        return
    
    # 创建API和缓存管理器
    api = FeishuAPI(
        plugin_id="",
        plugin_secret="",
        app_id=APP_ID,
        app_secret=APP_SECRET
    )
    api.set_user_access_token(user_access_token)
    
    manager = SpreadsheetCacheManager(
        app_id=APP_ID,
        app_secret=APP_SECRET,
        user_access_token=user_access_token,
        space_id=SPACE_ID
    )
    
    # 1. 列出所有在线表格节点
    print("步骤1: 查找所有在线表格节点...")
    print("-" * 80)
    spreadsheet_nodes = list_all_spreadsheet_nodes(api, SPACE_ID, TARGET_NODE_TOKEN)
    
    if not spreadsheet_nodes:
        print("[!] 未找到任何在线表格节点")
        return
    
    print()
    print(f"[OK] 找到 {len(spreadsheet_nodes)} 个在线表格节点")
    print()
    
    # 2. 缓存所有在线表格
    print("步骤2: 缓存所有在线表格...")
    print("=" * 80)
    print()
    
    results = []
    for i, node in enumerate(spreadsheet_nodes, 1):
        title = node['title']
        node_token = node['node_token']
        
        # 生成缓存文件名（使用安全的文件名）
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_title = safe_title.replace(' ', '_')
        cache_file = f"wiki_{TARGET_NODE_TOKEN}_{i:02d}_{safe_title}.json"
        
        result = cache_spreadsheet_node(manager, node_token, title, cache_file)
        results.append(result)
        print()
    
    # 3. 汇总结果
    print("=" * 80)
    print("缓存完成")
    print("=" * 80)
    print()
    
    success_count = sum(1 for r in results if r.get('success'))
    total_count = len(results)
    
    print(f"总计: {success_count}/{total_count} 成功")
    print()
    
    for result in results:
        if result.get('success'):
            print(f"✓ {result['title']}")
            print(f"  工作表数: {result['sheets_count']}")
            print(f"  总行数: {result['total_rows']}")
            print(f"  缓存文件: {result['cache_file']}")
        else:
            print(f"✗ {result['title']}: {result.get('error', '未知错误')}")
        print()
    
    # 保存配置
    config_file = CACHE_DIR / f"wiki_{TARGET_NODE_TOKEN}_config.json"
    config_data = {
        'node_token': TARGET_NODE_TOKEN,
        'node_url': TARGET_NODE_URL,
        'cached_spreadsheets': [
            {
                'title': r['title'],
                'node_token': r['node_token'],
                'cache_file': r.get('cache_file', ''),
                'sheets_count': r.get('sheets_count', 0),
                'total_rows': r.get('total_rows', 0)
            }
            for r in results if r.get('success')
        ],
        'cache_time': json.dumps(datetime.now().isoformat())
    }
    
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config_data, f, ensure_ascii=False, indent=2)
    
    print(f"[OK] 配置已保存到: {config_file}")


if __name__ == "__main__":
    from datetime import datetime
    main()

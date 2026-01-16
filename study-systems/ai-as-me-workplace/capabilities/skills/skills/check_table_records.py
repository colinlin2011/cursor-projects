# -*- coding: utf-8 -*-
"""
检查数据表的实际记录数
"""

import sys
import os
import json
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bitable_cache_manager import BitableCacheManager, CACHE_DIR, BITABLE_CONFIGS
from feishu_api_wrapper import FeishuAPI

# 配置信息
APP_ID = "cli_a9c92ca516f99bd9"
APP_SECRET = "zlOKnyZkSuSUSr0WlAl6qbh5Qw4eM6wC"
USER_ACCESS_TOKEN = os.getenv("FEISHU_USER_ACCESS_TOKEN", "u-fjEA3Zj5J4eGr.QY6KVnXg14hgJ04kgVOOwaFMy024ps")
SPACE_ID = "7353073903872868356"

# 修复Windows控制台编码问题
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

def check_table_records():
    """检查缺陷问题闭环表的实际记录数"""
    
    # 找到"功能安全业务数据"的配置
    config = None
    for cfg in BITABLE_CONFIGS:
        if "功能安全业务数据" in cfg.get("name", "") or cfg.get("name") == "新多维表格":
            config = cfg
            break
    
    if not config:
        print("[X] 未找到配置")
        return
    
    print("=" * 80)
    print("检查缺陷问题闭环表记录数")
    print("=" * 80)
    print()
    print(f"多维表格: {config['name']}")
    print(f"Node Token: {config['node_token']}")
    print()
    
    # 创建API和协作器
    api = FeishuAPI(
        plugin_id="",
        plugin_secret="",
        app_id=APP_ID,
        app_secret=APP_SECRET
    )
    api.set_user_access_token(USER_ACCESS_TOKEN)
    
    from feishu_bitable_collaborator import create_bitable_collaborator
    collaborator = create_bitable_collaborator(
        app_id=APP_ID,
        app_secret=APP_SECRET,
        user_access_token=USER_ACCESS_TOKEN
    )
    
    # 获取app_token
    manager = BitableCacheManager(APP_ID, APP_SECRET, USER_ACCESS_TOKEN, SPACE_ID)
    app_token = manager.get_app_token_from_wiki(config['node_token'])
    
    if not app_token:
        print("[X] 无法获取app_token")
        return
    
    print(f"[OK] app_token: {app_token}")
    print()
    
    # 列出所有数据表
    tables_result = api.list_bitable_tables(app_token, use_user_token=True)
    if not tables_result:
        print("[X] 无法列出数据表")
        return
    
    tables = tables_result.get('items', []) if 'items' in tables_result else []
    
    # 找到"10. 缺陷问题闭环表"
    target_table = None
    for table in tables:
        table_name = table.get('name', '')
        if '缺陷问题闭环' in table_name:
            target_table = table
            break
    
    if not target_table:
        print("[X] 未找到缺陷问题闭环表")
        print()
        print("可用的数据表:")
        for table in tables:
            print(f"  - {table.get('name', '')}")
        return
    
    table_id = target_table.get('table_id')
    table_name = target_table.get('name', '')
    
    print(f"[OK] 找到数据表: {table_name}")
    print(f"Table ID: {table_id}")
    print()
    
    # 获取记录数
    print("正在获取记录...")
    try:
        records = collaborator.get_all_records(app_token, table_id)
        record_count = len(records)
        
        print()
        print("=" * 80)
        print(f"结果: {table_name}")
        print("=" * 80)
        print()
        print(f"缺陷问题记录数: {record_count} 个")
        print()
        
        if record_count > 0:
            print("前3条记录的示例:")
            for i, record in enumerate(records[:3], 1):
                fields = record.get('fields', {})
                print(f"\n记录 {i}:")
                # 显示关键字段
                key_fields = ['工作项id', 'Ticket ID', '名称', '状态', '当前负责人']
                for field_name in key_fields:
                    value = fields.get(field_name, '')
                    if value:
                        print(f"  {field_name}: {value}")
        
    except Exception as e:
        print(f"[X] 获取记录失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_table_records()

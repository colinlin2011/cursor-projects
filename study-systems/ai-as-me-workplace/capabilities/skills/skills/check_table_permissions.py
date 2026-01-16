# -*- coding: utf-8 -*-
"""
检查多维表格中特定数据表的访问权限
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bitable_cache_manager import BitableCacheManager, APP_ID, APP_SECRET, SPACE_ID, BITABLE_CONFIGS
from feishu_api_wrapper import FeishuAPI

# 修复Windows控制台编码问题
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

# 配置信息
USER_ACCESS_TOKEN = os.getenv("FEISHU_USER_ACCESS_TOKEN", "u-eIUWr84upbgokMMGU78cvQk1npEg4kOXryayFxa020ku")

def check_table_permissions():
    """检查数据表的访问权限"""
    
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
    print("检查数据表访问权限")
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
    print("正在列出所有数据表...")
    tables = collaborator.list_tables(app_token)
    
    if not tables:
        print("[X] 无法列出数据表")
        return
    
    print(f"[OK] 找到 {len(tables)} 个数据表")
    print()
    
    # 检查每个表的访问权限
    target_tables = ["09. 故障上报明细表（同步Fault ID上报BI面板）", "10. 缺陷问题闭环表"]
    
    print("=" * 80)
    print("检查目标数据表的访问权限")
    print("=" * 80)
    print()
    
    for table in tables:
        table_name = table.get('name', '')
        table_id = table.get('table_id', '')
        
        if any(target in table_name for target in ["故障上报", "缺陷问题闭环"]):
            print(f"数据表: {table_name}")
            print(f"Table ID: {table_id}")
            print()
            
            # 尝试获取表结构
            print("  尝试获取表结构...")
            try:
                structure = collaborator.get_table_structure(app_token, table_id)
                if structure:
                    print(f"  [OK] 可以访问表结构")
                    fields = structure.get('fields', [])
                    print(f"  字段数: {len(fields)}")
                else:
                    print(f"  [X] 无法获取表结构")
            except Exception as e:
                print(f"  [X] 获取表结构失败: {e}")
            
            print()
            
            # 尝试获取记录数
            print("  尝试获取记录...")
            try:
                records = collaborator.get_all_records(app_token, table_id)
                if records is not None:
                    record_count = len(records) if isinstance(records, list) else 0
                    print(f"  [OK] 可以访问记录")
                    print(f"  记录数: {record_count}")
                else:
                    print(f"  [X] 无法获取记录（返回None）")
            except Exception as e:
                error_msg = str(e)
                if "RolePermNotAllow" in error_msg or "1254302" in error_msg:
                    print(f"  [X] 权限不足: RolePermNotAllow")
                    print(f"  错误信息: {e}")
                    print()
                    print("  可能的原因：")
                    print("  1. 当前用户账号没有访问此表的权限")
                    print("  2. 表可能被设置为私有或需要特定角色权限")
                    print("  3. 需要在多维表格中为当前用户账号授权")
                else:
                    print(f"  [X] 获取记录失败: {e}")
            
            print()
            print("-" * 80)
            print()

if __name__ == "__main__":
    check_table_permissions()

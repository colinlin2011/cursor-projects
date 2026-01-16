# -*- coding: utf-8 -*-
"""
同步"功能安全业务数据"多维表格的缓冲，确保"缺陷问题闭环表"有253条记录
"""

import sys
import os
import json
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bitable_cache_manager import BitableCacheManager, APP_ID, APP_SECRET, SPACE_ID, BITABLE_CONFIGS

# 修复Windows控制台编码问题
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

def sync_functional_safety_bitable():
    """同步功能安全业务数据多维表格"""
    
    print("=" * 80)
    print("同步功能安全业务数据多维表格")
    print("=" * 80)
    print()
    
    # 优先使用环境变量中的访问令牌
    user_access_token = os.getenv("FEISHU_USER_ACCESS_TOKEN")
    if not user_access_token:
        # 如果没有环境变量，使用默认值（可能已过期）
        from bitable_cache_manager import USER_ACCESS_TOKEN as DEFAULT_TOKEN
        user_access_token = DEFAULT_TOKEN
        print("[!] 警告：未设置环境变量 FEISHU_USER_ACCESS_TOKEN")
        print("    使用默认访问令牌（可能已过期）")
        print()
    
    # 找到"功能安全业务数据"的配置（对应"新多维表格"）
    config = None
    for cfg in BITABLE_CONFIGS:
        if "功能安全业务数据" in cfg.get("name", "") or cfg.get("name") == "新多维表格":
            config = cfg
            break
    
    if not config:
        print("[X] 未找到'功能安全业务数据'多维表格配置")
        return False
    
    print(f"多维表格: {config['name']}")
    print(f"Node Token: {config['node_token']}")
    print(f"缓存文件: {config['cache_file']}")
    print()
    
    # 创建缓存管理器
    manager = BitableCacheManager(
        app_id=APP_ID,
        app_secret=APP_SECRET,
        user_access_token=user_access_token,
        space_id=SPACE_ID
    )
    
    # 强制刷新缓存
    print("正在同步数据（强制刷新）...")
    print()
    
    try:
        data = manager.load_bitable_data(
            node_token=config['node_token'],
            cache_file=config['cache_file'],
            force_refresh=True
        )
        
        if not data:
            print("[X] 同步失败：无法获取数据")
            return False
        
        print()
        print("=" * 80)
        print("同步完成")
        print("=" * 80)
        print()
        
        # 检查"缺陷问题闭环表"的记录数
        tables = data.get('tables', {})
        
        # 查找缺陷问题闭环表（可能是"10. 缺陷问题闭环表"或其他名称）
        defect_table = None
        defect_table_name = None
        
        for table_name, table_data in tables.items():
            if '缺陷问题闭环' in table_name or '缺陷' in table_name:
                defect_table = table_data
                defect_table_name = table_name
                break
        
        if not defect_table:
            print("[!] 未找到'缺陷问题闭环表'")
            print()
            print("可用的数据表:")
            for table_name in tables.keys():
                print(f"  - {table_name}")
            return False
        
        record_count = defect_table.get('record_count', 0)
        
        print(f"数据表: {defect_table_name}")
        print(f"记录数: {record_count} 条")
        print()
        
        if record_count == 253:
            print("[✓] 记录数正确：253 条")
            return True
        else:
            print(f"[!] 记录数不匹配：期望 253 条，实际 {record_count} 条")
            print()
            print("提示：如果记录数不正确，可能是：")
            print("  1. 多维表格中的数据已更新")
            print("  2. 需要重新同步缓存")
            return False
        
    except Exception as e:
        error_msg = str(e)
        print(f"[X] 同步失败: {error_msg}")
        print()
        
        # 检查是否是访问令牌过期
        if "401" in error_msg or "expired" in error_msg.lower() or "Authentication token" in error_msg:
            print("=" * 80)
            print("访问令牌已过期，需要更新")
            print("=" * 80)
            print()
            print("解决方法：")
            print("1. 获取新的访问令牌（参考 get_user_token_for_bitable.py）")
            print("2. 设置环境变量：")
            print('   PowerShell: $env:FEISHU_USER_ACCESS_TOKEN="your_new_token"')
            print('   CMD: set FEISHU_USER_ACCESS_TOKEN=your_new_token')
            print("3. 重新运行此脚本")
            print()
        
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = sync_functional_safety_bitable()
    sys.exit(0 if success else 1)

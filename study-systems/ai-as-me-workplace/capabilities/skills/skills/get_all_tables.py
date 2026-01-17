# -*- coding: utf-8 -*-
"""
获取多维表格的所有数据表列表
用于确认正确的table_id
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from feishu_bitable_collaborator import create_bitable_collaborator

# 配置信息
APP_TOKEN = "YWDGbSZZKalcnQskTThcSUSXnub"

def get_credentials():
    """获取API凭证"""
    app_id = os.getenv('FEISHU_APP_ID')
    app_secret = os.getenv('FEISHU_APP_SECRET')
    user_access_token = os.getenv('FEISHU_USER_ACCESS_TOKEN')
    
    # 如果没有环境变量，尝试从bitable_cache_manager导入
    if not app_id or not app_secret:
        try:
            from bitable_cache_manager import APP_ID, APP_SECRET
            app_id = app_id or APP_ID
            app_secret = app_secret or APP_SECRET
        except ImportError:
            pass
    
    if not user_access_token:
        try:
            from bitable_cache_manager import USER_ACCESS_TOKEN
            user_access_token = USER_ACCESS_TOKEN
        except ImportError:
            pass
    
    # 如果还是没有，使用默认值
    if not app_id:
        app_id = "cli_a9c92ca516f99bd9"
    if not app_secret:
        app_secret = "zlOKnyZkSuSUSr0WlAl6qbh5Qw4eM6wC"
    
    return app_id, app_secret, user_access_token

def main():
    print("=" * 60)
    print("获取多维表格数据表列表")
    print("=" * 60)
    print()
    
    # 获取凭证
    app_id, app_secret, user_access_token = get_credentials()
    
    print(f"app_token: {APP_TOKEN}")
    print(f"使用应用ID: {app_id[:10]}...")
    if user_access_token:
        print(f"使用user_access_token: {user_access_token[:20]}...")
    else:
        print("警告: 未设置user_access_token，可能无法获取数据表列表")
    print()
    
    # 创建协作器
    print("正在初始化飞书API连接...")
    collaborator = create_bitable_collaborator(
        app_id=app_id,
        app_secret=app_secret,
        user_access_token=user_access_token
    )
    
    # 获取多维表格信息
    print("正在获取多维表格信息...")
    app_info = collaborator.get_app_info(APP_TOKEN)
    app_name = "Colin个人工作平台"
    
    if app_info:
        if 'code' in app_info and app_info.get('code') == 0:
            app_data = app_info.get('data', {})
            app_name = app_data.get('app', {}).get('name', app_name)
        elif 'app' in app_info:
            app_name = app_info.get('app', {}).get('name', app_name)
    
    print(f"多维表格名称: {app_name}")
    print()
    
    # 获取所有数据表
    print("正在获取数据表列表...")
    tables = collaborator.list_tables(APP_TOKEN)
    
    if not tables:
        print("未找到数据表")
        print()
        print("可能的原因：")
        print("1. user_access_token已过期，需要重新获取")
        print("2. 应用权限不足，需要 'bitable:app:readonly' 或 'bitable:app' 权限")
        print("3. 该多维表格确实没有数据表")
        return
    
    print(f"找到 {len(tables)} 个数据表：")
    print()
    print("| 序号 | 数据表名称 | 数据表ID |")
    print("|------|-----------|----------|")
    
    for i, table in enumerate(tables, 1):
        table_name = table.get('name', '未知')
        table_id = table.get('table_id', '未知')
        print(f"| {i} | {table_name} | `{table_id}` |")
    
    print()
    print("=" * 60)
    print("完成！")
    print("=" * 60)
    print()
    print("提示：可以使用这些table_id来更新导入脚本中的TABLE_IDS列表")

if __name__ == "__main__":
    main()

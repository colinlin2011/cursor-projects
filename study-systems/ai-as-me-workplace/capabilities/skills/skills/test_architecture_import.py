# -*- coding: utf-8 -*-
"""
测试架构元素导入功能
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fmea_data_reader import FMEADataReader
from import_architecture_elements import ArchitectureElementImporter
from token_manager import TokenManager
from bitable_cache_manager import (
    BitableCacheManager,
    BITABLE_CONFIGS,
    APP_ID,
    APP_SECRET,
    SPACE_ID,
    CACHE_DIR
)
import json

# 目标多维表格配置
TARGET_NODE_TOKEN = "BPddwBxoRiPFSsk8jZJctCMmndg"
TARGET_TABLE_NAME = "架构元素表"


def get_app_token_and_table_id(user_access_token: str):
    """获取app_token和table_id"""
    manager = BitableCacheManager(
        app_id=APP_ID,
        app_secret=APP_SECRET,
        user_access_token=user_access_token,
        space_id=SPACE_ID
    )
    
    app_token = manager.get_app_token_from_wiki(TARGET_NODE_TOKEN, SPACE_ID)
    if not app_token:
        return None, None
    
    cache_file = None
    for config in BITABLE_CONFIGS:
        if config['node_token'] == TARGET_NODE_TOKEN:
            cache_file = config['cache_file']
            break
    
    if not cache_file:
        return None, None
    
    cache_path = CACHE_DIR / cache_file
    if not cache_path.exists():
        manager.load_bitable_data(TARGET_NODE_TOKEN, cache_file, force_refresh=True)
    
    with open(cache_path, 'r', encoding='utf-8') as f:
        cache_data = json.load(f)
    
    tables = cache_data.get('tables', {})
    table_data = None
    
    if TARGET_TABLE_NAME in tables:
        table_data = tables[TARGET_TABLE_NAME]
    else:
        for name, data in tables.items():
            if TARGET_TABLE_NAME in name or name in TARGET_TABLE_NAME:
                table_data = data
                break
    
    if not table_data:
        return None, None
    
    table_id = table_data.get('table_id')
    return app_token, table_id


def main():
    print("=" * 80)
    print("测试架构元素导入功能")
    print("=" * 80)
    print()
    
    # 1. 获取token
    token_manager = TokenManager()
    user_access_token = token_manager.get_valid_user_access_token()
    if not user_access_token:
        print("[X] 无法获取用户访问令牌")
        return
    
    # 2. 读取FMEA数据
    print("步骤1: 读取FMEA数据...")
    reader = FMEADataReader()
    fmea_data = reader.read_fmea_data('Control')
    if not fmea_data:
        print("[X] 无法读取FMEA数据")
        return
    
    validation = reader.validate_data(fmea_data)
    cleaned_rows = validation['cleaned_rows']
    print(f"[OK] 已读取 {len(cleaned_rows)} 行有效数据")
    print()
    
    # 3. 获取app_token和table_id
    print("步骤2: 获取多维表格信息...")
    app_token, table_id = get_app_token_and_table_id(user_access_token)
    if not app_token or not table_id:
        print("[X] 无法获取多维表格信息")
        return
    
    print(f"[OK] app_token: {app_token[:20]}...")
    print(f"[OK] table_id: {table_id}")
    print()
    
    # 4. 测试导入（试运行）
    print("步骤3: 试运行导入...")
    importer = ArchitectureElementImporter(app_token, table_id, user_access_token)
    result = importer.import_elements(cleaned_rows, dry_run=True)
    
    print()
    print("=" * 80)
    print("试运行结果")
    print("=" * 80)
    print(f"总计: {result['stats']['total']}")
    print()
    
    # 询问是否继续实际导入
    response = input("\n是否继续实际导入？(y/n): ")
    if response.lower() == 'y':
        print("\n开始实际导入...")
        result = importer.import_elements(cleaned_rows, dry_run=False)
        print()
        print("=" * 80)
        print("导入结果")
        print("=" * 80)
        print(f"总计: {result['stats']['total']}")
        print(f"新建: {result['stats']['created']}")
        print(f"已存在: {result['stats']['existing']}")
        print(f"失败: {result['stats']['failed']}")
        print(f"\nElement Name到Record ID的映射（前10个）:")
        for name, record_id in list(result['element_name_to_record_id'].items())[:10]:
            print(f"  {name}: {record_id}")


if __name__ == "__main__":
    main()

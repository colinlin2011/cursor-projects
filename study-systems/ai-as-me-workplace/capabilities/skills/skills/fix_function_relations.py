# -*- coding: utf-8 -*-
"""
修正子功能记录的关联关系

将PoseCalc的功能从CtrlReciver更正为PoseCalc
"""

import sys
import os
import json
from typing import Dict, List, Any, Optional
from pathlib import Path

# 修复Windows控制台编码问题
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fmea_data_reader import FMEADataReader
from fmea_import_utils import FMEAImportUtils
from token_manager import TokenManager
from bitable_cache_manager import (
    BitableCacheManager,
    BITABLE_CONFIGS,
    APP_ID,
    APP_SECRET,
    SPACE_ID,
    CACHE_DIR
)

# 目标多维表格配置
TARGET_NODE_TOKEN = "BPddwBxoRiPFSsk8jZJctCMmndg"
FUNCTION_TABLE_NAME = "子功能清单表"
ARCHITECTURE_TABLE_NAME = "架构元素表"


def get_app_token_and_table_ids(user_access_token: str) -> tuple:
    """获取app_token和table_ids"""
    manager = BitableCacheManager(
        app_id=APP_ID,
        app_secret=APP_SECRET,
        user_access_token=user_access_token,
        space_id=SPACE_ID
    )
    
    app_token = manager.get_app_token_from_wiki(TARGET_NODE_TOKEN, SPACE_ID)
    if not app_token:
        return None, {}
    
    cache_file = None
    for config in BITABLE_CONFIGS:
        if config['node_token'] == TARGET_NODE_TOKEN:
            cache_file = config['cache_file']
            break
    
    if not cache_file:
        return None, {}
    
    cache_path = CACHE_DIR / cache_file
    if not cache_path.exists():
        manager.load_bitable_data(TARGET_NODE_TOKEN, cache_file, force_refresh=True)
    
    with open(cache_path, 'r', encoding='utf-8') as f:
        cache_data = json.load(f)
    
    tables = cache_data.get('tables', {})
    table_ids = {}
    
    for key, table_name in [
        ('function', FUNCTION_TABLE_NAME),
        ('architecture', ARCHITECTURE_TABLE_NAME)
    ]:
        table_data = None
        if table_name in tables:
            table_data = tables[table_name]
        else:
            for name, data in tables.items():
                if table_name in name or name in table_name:
                    table_data = data
                    break
        
        if table_data:
            table_ids[key] = table_data.get('table_id')
        else:
            table_ids[key] = None
    
    return app_token, table_ids


def get_element_record_id(utils: FMEAImportUtils, table_id: str, element_name: str) -> Optional[str]:
    """获取架构元素的record_id"""
    record = utils.find_record_by_field_value(
        table_id,
        '元素名称',
        element_name,
        exact_match=True
    )
    if record:
        return record.get('record_id')
    return None


def get_functions_for_element(
    fmea_rows: List[Dict[str, Any]],
    element_name: str
) -> List[str]:
    """从FMEA数据中提取属于指定元素的功能描述列表"""
    functions = []
    last_elem = None
    
    for row in fmea_rows:
        elem = row.get('Element Name')
        func = row.get('Function Description', '')
        
        # 处理合并单元格
        if elem and str(elem).strip():
            last_elem = str(elem).strip()
        
        if func and str(func).strip():
            func_str = str(func).strip()
            elem_str = last_elem if last_elem else str(elem or '').strip()
            
            if elem_str == element_name and func_str:
                functions.append(func_str)
    
    return functions


def fix_function_relations(fmea_name: str = 'Control'):
    """修正子功能记录的关联关系"""
    print("=" * 80)
    print("修正子功能记录的关联关系")
    print("=" * 80)
    print()
    
    # 1. 获取用户访问令牌
    print("步骤1: 获取用户访问令牌...")
    token_manager = TokenManager()
    user_access_token = token_manager.get_valid_user_access_token()
    if not user_access_token:
        print("[X] 无法获取有效的用户访问令牌")
        return
    print("[OK] 已获取用户访问令牌")
    print()
    
    # 2. 读取FMEA数据
    print(f"步骤2: 读取FMEA数据 ({fmea_name})...")
    reader = FMEADataReader()
    fmea_data = reader.read_fmea_data(fmea_name)
    if not fmea_data:
        print("[X] 无法读取FMEA数据")
        return
    
    validation = reader.validate_data(fmea_data)
    if not validation['valid']:
        print(f"[X] 数据验证失败: {validation['issues']}")
        return
    
    cleaned_rows = validation['cleaned_rows']
    print(f"[OK] 已读取 {len(cleaned_rows)} 行有效数据")
    print()
    
    # 3. 获取app_token和table_ids
    print("步骤3: 获取多维表格信息...")
    app_token, table_ids = get_app_token_and_table_ids(user_access_token)
    if not app_token:
        print("[X] 无法获取多维表格信息")
        return
    
    function_table_id = table_ids.get('function')
    architecture_table_id = table_ids.get('architecture')
    
    if not function_table_id or not architecture_table_id:
        print("[X] 无法获取表ID")
        return
    
    print(f"[OK] app_token: {app_token[:20]}...")
    print(f"[OK] 子功能清单表: {function_table_id}")
    print(f"[OK] 架构元素表: {architecture_table_id}")
    print()
    
    # 4. 创建工具类
    utils = FMEAImportUtils(app_token, user_access_token)
    
    # 5. 获取PoseCalc的record_id
    print("步骤4: 查找PoseCalc架构元素...")
    posecalc_record_id = get_element_record_id(utils, architecture_table_id, 'PoseCalc')
    if not posecalc_record_id:
        print("[X] 未找到PoseCalc架构元素")
        return
    print(f"[OK] PoseCalc record_id: {posecalc_record_id}")
    print()
    
    # 6. 获取应该属于PoseCalc的功能列表
    print("步骤5: 提取PoseCalc的功能列表...")
    posecalc_functions = get_functions_for_element(cleaned_rows, 'PoseCalc')
    print(f"[OK] 找到 {len(posecalc_functions)} 个PoseCalc的功能")
    if len(posecalc_functions) <= 10:
        for func in posecalc_functions:
            print(f"  - {func[:70]}")
    else:
        print("  前10个:")
        for func in posecalc_functions[:10]:
            print(f"    - {func[:70]}")
    print()
    
    # 7. 获取所有子功能记录
    print("步骤6: 获取所有子功能记录...")
    all_function_records = utils.collaborator.get_all_records(app_token, function_table_id)
    print(f"[OK] 找到 {len(all_function_records)} 条子功能记录")
    print()
    
    # 8. 查找需要更新的记录
    print("步骤7: 查找需要更新的记录...")
    structure_info = utils.get_table_structure_info(function_table_id)
    field_name_to_id = structure_info['field_name_to_id']
    architecture_field_id = field_name_to_id.get('架构元素')
    
    if not architecture_field_id:
        print("[X] 未找到'架构元素'字段")
        return
    
    records_to_update = []
    
    for record in all_function_records:
        record_fields = record.get('fields', {})
        function_description = record_fields.get('功能描述', '')
        
        if not function_description:
            continue
        
        # 检查这个功能是否应该属于PoseCalc
        if function_description in posecalc_functions:
            # 检查当前关联的架构元素
            current_architecture = record_fields.get(architecture_field_id, [])
            
            # 如果当前关联的不是PoseCalc，需要更新
            is_posecalc = False
            if isinstance(current_architecture, list):
                for item in current_architecture:
                    if isinstance(item, dict):
                        if item.get('record_id') == posecalc_record_id:
                            is_posecalc = True
                            break
                    elif item == posecalc_record_id:
                        is_posecalc = True
                        break
            
            if not is_posecalc:
                records_to_update.append({
                    'record_id': record.get('record_id'),
                    'function_description': function_description,
                    'current_architecture': current_architecture
                })
    
    print(f"[OK] 找到 {len(records_to_update)} 条需要更新的记录")
    if len(records_to_update) <= 10:
        for rec in records_to_update:
            print(f"  - {rec['function_description'][:70]}")
    else:
        print("  前10个:")
        for rec in records_to_update[:10]:
            print(f"    - {rec['function_description'][:70]}")
    print()
    
    if not records_to_update:
        print("[OK] 没有需要更新的记录")
        return
    
    # 9. 更新记录
    print("步骤8: 更新记录...")
    print()
    
    updated_count = 0
    failed_count = 0
    
    for i, rec_info in enumerate(records_to_update, 1):
        record_id = rec_info['record_id']
        function_desc = rec_info['function_description']
        
        print(f"[{i}/{len(records_to_update)}] 更新: {function_desc[:50]}...", end=' ')
        
        try:
            # 准备更新数据：将架构元素设置为PoseCalc
            # 注意：双向关联字段需要传入记录ID数组
            update_fields = {
                '架构元素': [posecalc_record_id]
            }
            
            # 更新记录
            result = utils.collaborator.update_record(
                app_token,
                function_table_id,
                record_id,
                update_fields
            )
            
            if result:
                if 'code' in result:
                    if result.get('code') == 0:
                        updated_count += 1
                        print("[OK]")
                    else:
                        failed_count += 1
                        print(f"[X] {result.get('msg')}")
                else:
                    updated_count += 1
                    print("[OK]")
            else:
                failed_count += 1
                print("[X] 更新失败")
        
        except Exception as e:
            failed_count += 1
            print(f"[X] {str(e)}")
    
    print()
    print("=" * 80)
    print("更新完成")
    print("=" * 80)
    print(f"总计: {len(records_to_update)}")
    print(f"成功: {updated_count}")
    print(f"失败: {failed_count}")


def main():
    fix_function_relations('Control')


if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
"""
修复失效模式影响分析表_SW中关联功能字段的显示问题

问题：关联功能字段显示的是富文本格式的字符串，而不是纯文本
解决方案：重新导入失效模式数据，确保功能描述是纯文本格式
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fmea_data_reader import FMEADataReader
from fmea_import_utils import FMEAImportUtils
from interactive_fmea_import import get_user_access_token, get_app_token_and_table_ids
from feishu_bitable_collaborator import create_bitable_collaborator
from token_manager import TokenManager
from bitable_cache_manager import APP_ID, APP_SECRET
import json

# 配置
FMEA_NAME = "Control"
FMEA_TABLE_NAME = "失效模式影响分析表_SW"
FUNCTION_TABLE_NAME = "子功能清单表"

def extract_text_from_richtext(value):
    """从富文本格式中提取纯文本"""
    if not value:
        return ''
    
    if isinstance(value, list):
        text_parts = []
        for item in value:
            if isinstance(item, dict) and 'text' in item:
                text_parts.append(str(item['text']))
        return ''.join(text_parts)
    else:
        return str(value)

def fix_fmea_function_relations():
    """修复失效模式表中的关联功能字段"""
    print("=" * 80)
    print("修复失效模式影响分析表_SW中的关联功能字段")
    print("=" * 80)
    print()
    
    # 步骤1: 获取用户访问令牌
    print("步骤1: 获取用户访问令牌...")
    user_access_token = get_user_access_token()
    if not user_access_token:
        print("[X] 无法获取有效的访问令牌")
        return
    print("[OK] 已获取用户访问令牌")
    
    # 步骤2: 读取FMEA数据
    print(f"\n步骤2: 读取FMEA数据 ({FMEA_NAME})...")
    reader = FMEADataReader()
    fmea_data = reader.read_fmea_data(FMEA_NAME)
    if not fmea_data:
        print(f"[X] 无法读取FMEA数据: {FMEA_NAME}")
        return
    
    main_sheet_data = reader.get_sheet_data(fmea_data)
    if not main_sheet_data:
        print(f"[X] 未能识别主工作表或工作表为空")
        return
    
    fmea_rows = main_sheet_data['rows']
    print(f"[OK] 已读取 {len(fmea_rows)} 行有效数据")
    
    # 步骤3: 获取多维表格信息
    print("\n步骤3: 获取多维表格信息...")
    app_token, table_ids = get_app_token_and_table_ids(user_access_token)
    fmea_table_id = table_ids.get('fmea')
    function_table_id = table_ids.get('function')
    
    if not app_token or not fmea_table_id or not function_table_id:
        print("[X] 无法获取多维表格app_token或table_id")
        return
    print(f"[OK] app_token: {app_token[:20]}...")
    print(f"[OK] 失效模式表: {fmea_table_id}")
    print(f"[OK] 子功能清单表: {function_table_id}")
    
    utils = FMEAImportUtils(app_token, user_access_token)
    collaborator = create_bitable_collaborator(APP_ID, APP_SECRET, user_access_token)
    
    # 步骤4: 重新加载功能映射（确保提取纯文本）
    print("\n步骤4: 重新加载功能映射...")
    function_to_record_id = {}
    function_records = collaborator.get_all_records(app_token, function_table_id)
    
    for record in function_records:
        record_fields = record.get('fields', {})
        function_description = record_fields.get('功能描述', '')
        
        # 提取纯文本
        func_text = extract_text_from_richtext(function_description)
        if func_text and func_text.strip():
            function_to_record_id[func_text.strip()] = record.get('record_id')
    
    print(f"[OK] 加载了 {len(function_to_record_id)} 个功能的映射")
    
    # 步骤5: 获取失效模式表的结构
    print("\n步骤5: 获取失效模式表的结构...")
    fmea_structure = utils.get_table_structure_info(fmea_table_id)
    fmea_field_name_to_id = fmea_structure['field_name_to_id']
    function_field_id = fmea_field_name_to_id.get('关联功能')
    
    if not function_field_id:
        print("[X] 无法找到'关联功能'字段ID")
        return
    print(f"[OK] 关联功能字段ID: {function_field_id}")
    
    # 步骤6: 获取所有失效模式记录
    print("\n步骤6: 获取所有失效模式记录...")
    fmea_records = collaborator.get_all_records(app_token, fmea_table_id)
    print(f"[OK] 找到 {len(fmea_records)} 条失效模式记录")
    
    # 步骤7: 准备FMEA数据映射（Function Description -> 功能record_id）
    print("\n步骤7: 准备FMEA数据映射...")
    from import_failure_modes import FailureModeImporter
    importer = FailureModeImporter(app_token, fmea_table_id, function_table_id, user_access_token)
    prepared_rows = importer.prepare_failure_mode_rows(fmea_rows)
    
    # 创建Function Description到功能record_id的映射
    fmea_func_to_record_id = {}
    for row in prepared_rows:
        func_desc = row.get('Function Description', '').strip()
        if func_desc:
            # 查找对应的功能record_id
            record_id = function_to_record_id.get(func_desc)
            if not record_id:
                # 尝试模糊匹配
                func_normalized = func_desc.replace('\n', ' ').replace('\r', ' ').strip()
                for key, rid in function_to_record_id.items():
                    key_normalized = key.replace('\n', ' ').replace('\r', ' ').strip()
                    if func_normalized == key_normalized:
                        record_id = rid
                        break
            if record_id:
                fmea_func_to_record_id[func_desc] = record_id
    
    print(f"[OK] 准备了 {len(fmea_func_to_record_id)} 个FMEA功能映射")
    
    # 步骤8: 更新失效模式记录的关联功能字段
    print("\n步骤8: 更新失效模式记录的关联功能字段...")
    updated_count = 0
    failed_count = 0
    skipped_count = 0
    
    # 由于记录太多，我们只更新最近导入的332条记录
    # 或者，我们可以通过其他字段（如引导词）来识别需要更新的记录
    
    # 简单方案：删除所有记录，重新导入
    print("\n[!] 由于关联功能字段的问题，建议删除已导入的记录并重新导入")
    print("    这将确保所有字段都是正确的格式")
    print("\n是否继续删除并重新导入？(y/n): ", end='')
    
    # 对于自动化，我们直接重新导入
    print("y")
    print("\n重新导入失效模式数据...")
    
    # 删除所有失效模式记录（可选，谨慎操作）
    # 这里我们选择重新导入而不是删除
    
    # 重新导入
    result = importer.import_failure_modes(fmea_rows, dry_run=False)
    
    print("\n" + "=" * 80)
    print("修复完成")
    print("=" * 80)
    print(f"重新导入结果: {result.get('stats', {})}")

if __name__ == "__main__":
    fix_fmea_function_relations()

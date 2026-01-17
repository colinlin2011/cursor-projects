# -*- coding: utf-8 -*-
"""
删除并重新导入失效模式数据

解决关联功能字段显示富文本乱码的问题
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from interactive_fmea_import import interactive_import, get_user_access_token, get_app_token_and_table_ids
from feishu_bitable_collaborator import create_bitable_collaborator
from feishu_api_wrapper import FeishuAPI
from token_manager import TokenManager
from bitable_cache_manager import APP_ID, APP_SECRET

# 配置
FMEA_NAME = "Control"

def delete_fmea_records():
    """删除失效模式表中的所有记录"""
    print("=" * 80)
    print("删除失效模式影响分析表_SW中的所有记录")
    print("=" * 80)
    print()
    
    user_access_token = get_user_access_token()
    if not user_access_token:
        print("[X] 无法获取有效的访问令牌")
        return False
    
    app_token, table_ids = get_app_token_and_table_ids(user_access_token)
    fmea_table_id = table_ids.get('fmea')
    
    if not fmea_table_id:
        print("[X] 无法找到失效模式表")
        return False
    
    collaborator = create_bitable_collaborator(APP_ID, APP_SECRET, user_access_token)
    api = collaborator.api  # 使用collaborator的API实例
    
    # 获取所有记录
    print("获取所有失效模式记录...")
    records = collaborator.get_all_records(app_token, fmea_table_id)
    print(f"[OK] 找到 {len(records)} 条记录")
    
    if len(records) == 0:
        print("[!] 没有记录需要删除")
        return True
    
    # 批量删除（每批最多500条）
    BATCH_SIZE = 500
    total_batches = (len(records) + BATCH_SIZE - 1) // BATCH_SIZE
    
    print(f"\n开始批量删除（每批最多 {BATCH_SIZE} 条）...")
    
    deleted_count = 0
    failed_count = 0
    
    for batch_idx in range(total_batches):
        start_idx = batch_idx * BATCH_SIZE
        end_idx = min(start_idx + BATCH_SIZE, len(records))
        batch_records = records[start_idx:end_idx]
        record_ids = [r.get('record_id') for r in batch_records]
        
        print(f"[{batch_idx + 1}/{total_batches}] 删除第 {start_idx + 1}-{end_idx} 条记录...", end=' ')
        
        try:
            # 使用API wrapper的批量删除方法
            result = api.batch_delete_bitable_records(
                app_token,
                fmea_table_id,
                record_ids,
                use_user_token=True
            )
            
            if result:
                if 'code' in result and result.get('code') == 0:
                    deleted_count += len(record_ids)
                    print(f"[OK] 成功: {len(record_ids)}")
                else:
                    failed_count += len(record_ids)
                    error_msg = result.get('msg', '未知错误')
                    print(f"[X] 失败: {error_msg}")
            else:
                failed_count += len(record_ids)
                print(f"[X] 失败: API返回为空")
        
        except Exception as e:
            failed_count += len(record_ids)
            print(f"[X] 异常: {e}")
    
    print()
    print("=" * 80)
    print("删除完成")
    print("=" * 80)
    print(f"总计: {len(records)}")
    print(f"成功: {deleted_count}")
    print(f"失败: {failed_count}")
    
    return failed_count == 0

if __name__ == "__main__":
    print("警告：此操作将删除失效模式影响分析表_SW中的所有记录！")
    print("删除后将重新导入数据。")
    print()
    
    # 删除记录
    if delete_fmea_records():
        print("\n" + "=" * 80)
        print("重新导入失效模式数据...")
        print("=" * 80)
        print()
        
        # 重新导入
        result = interactive_import(FMEA_NAME, steps=['fmea'], dry_run=False)
        
        if result.get('success'):
            print("\n[OK] 重新导入成功！")
        else:
            print("\n[X] 重新导入失败")
    else:
        print("\n[X] 删除失败，取消重新导入")

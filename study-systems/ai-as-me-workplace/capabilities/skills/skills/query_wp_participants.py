# -*- coding: utf-8 -*-
"""
查询工作包的参与人员
"""

import sys
import os
from typing import List, Dict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bitable_query_interface import get_query_interface

# 修复Windows控制台编码问题
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

def query_work_package_participants(task_id: str) -> List[Dict]:
    """
    查询工作包的参与人员
    
    Args:
        task_id: 任务ID（如WP_001）
        
    Returns:
        参与人员列表
    """
    interface = get_query_interface()
    
    # 获取工作包信息
    wp_info = interface.get_work_package_info(task_id)
    
    if not wp_info:
        return []
    
    # 从"功能安全部人力盘点"缓存中查询
    cache_file = "hr_inventory.json"
    
    # 获取投入分配表
    allocation_table = interface.get_table_data("投入分配表_怎么分", cache_file)
    
    if not allocation_table:
        return []
    
    # 查找与该工作包相关的投入分配记录
    wp_record_id = wp_info.get('record_id')
    participants = []
    
    for record in allocation_table.get('records', []):
        fields = record.get('fields', {})
        
        # 检查投入任务字段
        task_field = fields.get('投入任务', [])
        if task_field and isinstance(task_field, list):
            for item in task_field:
                if isinstance(item, dict):
                    record_ids = item.get('record_ids', [])
                    if wp_record_id in record_ids:
                        # 找到相关分配，提取人员信息
                        person_field = fields.get('人员', [])
                        if person_field and isinstance(person_field, list):
                            for person_item in person_field:
                                if isinstance(person_item, dict):
                                    person_record_ids = person_item.get('record_ids', [])
                                    if person_record_ids:
                                        # 从资源池表中查找人员信息
                                        person_record_id = person_record_ids[0]
                                        resource_table = interface.get_table_data("资源池表_谁可用", cache_file)
                                        if resource_table:
                                            for person_record in resource_table.get('records', []):
                                                if person_record.get('record_id') == person_record_id:
                                                    person_fields = person_record.get('fields', {})
                                                    person_name = person_fields.get('姓名', '')
                                                    
                                                    # 获取投入信息
                                                    allocation_info = {
                                                        'person_name': person_name,
                                                        'person_record': person_record,
                                                        'allocation': record,
                                                        'h1_input': fields.get('H1总投入', 0),
                                                        'h2_input': fields.get('H2总投入', 0),
                                                        'year_input': fields.get('全年总投入', 0),
                                                        'work_package': fields.get('工作包', [])
                                                    }
                                                    participants.append(allocation_info)
                                                    break
                        break
    
    return participants

def main():
    task_id = "WP_001"
    
    print("=" * 80)
    print(f"查询工作包参与人员: {task_id}")
    print("=" * 80)
    print()
    
    interface = get_query_interface()
    
    # 获取工作包信息
    wp_info = interface.get_work_package_info(task_id)
    
    if not wp_info:
        print(f"[!] 未找到工作包: {task_id}")
        print()
        print("提示: 请确认任务ID是否正确")
        return
    
    wp_fields = wp_info.get('fields', {})
    
    print("工作包信息:")
    print(f"  任务ID: {task_id}")
    print(f"  工作包: {wp_fields.get('工作包', '')}")
    print(f"  目标: {wp_fields.get('目标Object', '')}")
    print(f"  关键结果: {wp_fields.get('关键结果KR', '')}")
    print(f"  业务方向: {wp_fields.get('业务方向', '')}")
    print(f"  主责小组: {', '.join(wp_fields.get('主责小组', [])) if isinstance(wp_fields.get('主责小组'), list) else wp_fields.get('主责小组', '')}")
    print(f"  人力总需求: {wp_fields.get('人力总需求', '')}")
    print(f"  已投入人力: {wp_fields.get('已投入人力', '')}")
    print(f"  人力缺口: {wp_fields.get('人力缺口', '')}")
    print()
    
    # 查询参与人员
    participants = query_work_package_participants(task_id)
    
    if not participants:
        print("[!] 未找到参与人员")
        print()
        print("可能的原因:")
        print("  1. 该工作包尚未分配人员")
        print("  2. 投入分配表中没有相关记录")
        return
    
    print("=" * 80)
    print(f"参与人员 ({len(participants)} 人)")
    print("=" * 80)
    print()
    
    total_h1 = 0
    total_h2 = 0
    total_year = 0
    
    for i, p in enumerate(participants, 1):
        person_name = p['person_name']
        person_fields = p['person_record'].get('fields', {})
        allocation_fields = p['allocation'].get('fields', {})
        
        print(f"{i}. {person_name}")
        print(f"   所属小组: {person_fields.get('所属小组', '')}")
        print(f"   人员属性: {person_fields.get('人员属性', '')}")
        
        # 投入信息
        h1 = float(p['h1_input'] or 0)
        h2 = float(p['h2_input'] or 0)
        year = float(p['year_input'] or 0)
        
        total_h1 += h1
        total_h2 += h2
        total_year += year
        
        print(f"   投入情况:")
        print(f"     - H1投入: {h1}")
        print(f"     - H2投入: {h2}")
        print(f"     - 全年投入: {year}")
        
        # 工作包名称
        work_pkg = allocation_fields.get('工作包', [])
        if work_pkg and isinstance(work_pkg, list) and len(work_pkg) > 0:
            wp_name = work_pkg[0].get('text', '') if isinstance(work_pkg[0], dict) else str(work_pkg[0])
            print(f"   工作包: {wp_name}")
        
        print()
    
    print("=" * 80)
    print("投入汇总")
    print("=" * 80)
    print()
    print(f"参与人数: {len(participants)} 人")
    print(f"H1总投入: {total_h1:.2f}")
    print(f"H2总投入: {total_h2:.2f}")
    print(f"全年总投入: {total_year:.2f}")
    print()
    
    # 与工作包需求对比
    wp_manpower_req = float(wp_fields.get('人力总需求', 0) or 0)
    wp_manpower_actual = float(wp_fields.get('已投入人力', 0) or 0)
    
    if wp_manpower_req > 0:
        print(f"工作包人力总需求: {wp_manpower_req}")
        print(f"工作包已投入人力: {wp_manpower_actual}")
        print(f"查询到的投入分配: {total_year:.2f}")
        if abs(total_year - wp_manpower_actual) > 0.01:
            print(f"[!] 注意: 投入分配总和({total_year:.2f})与工作包已投入人力({wp_manpower_actual})不一致")

if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
"""
查询特定人员的人力盘点情况

在多维表格中查找指定人员的投入情况
"""

import sys
import os
from typing import Optional, Dict, List, Any
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from feishu_bitable_collaborator import create_bitable_collaborator
from feishu_api_wrapper import FeishuAPI

# 配置信息
APP_ID = "cli_a9c92ca516f99bd9"
APP_SECRET = "zlOKnyZkSuSUSr0WlAl6qbh5Qw4eM6wC"
USER_ACCESS_TOKEN = os.getenv("FEISHU_USER_ACCESS_TOKEN", "u-fjEA3Zj5J4eGr.QY6KVnXg14hgJ04kgVOOwaFMy024ps")
SPACE_ID = "7353073903872868356"
NODE_TOKEN = "CGMnwhxzLixWhGk87jYcDRfonsh"

def get_app_token_from_wiki(api: FeishuAPI, space_id: str, node_token: str) -> Optional[str]:
    """通过Wiki节点获取app_token"""
    result = api.get_wiki_node(space_id, node_token, use_user_token=True)
    if result:
        node = result.get('node', result) if 'node' in result else result
        if node.get('obj_type') == 'bitable':
            return node.get('obj_token')
    return None

def search_person_in_records(records: List[Dict], fields: Dict, person_name: str) -> List[Dict]:
    """在记录中搜索包含指定人员的记录"""
    matching_records = []
    
    # 创建字段名到字段ID的映射
    field_name_to_id = {}
    field_id_to_name = {}
    for field_id, field_info in fields.items():
        field_name = field_info.get('field_name', '')
        field_name_to_id[field_name] = field_id
        field_id_to_name[field_id] = field_name
    
    for record in records:
        record_fields = record.get('fields', {})
        matched = False
        match_info = {}
        
        # 检查所有字段
        for field_id, value in record_fields.items():
            if not value:
                continue
            
            field_name = field_id_to_name.get(field_id, field_id)
            
            # 检查文本字段
            if isinstance(value, str) and person_name in value:
                matched = True
                match_info[field_name] = value
                break
            
            # 检查列表字段（人员、多选等）
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        # 检查name字段
                        if person_name in item.get('name', ''):
                            matched = True
                            match_info[field_name] = value
                            break
                        # 检查text字段
                        if person_name in item.get('text', ''):
                            matched = True
                            match_info[field_name] = value
                            break
                    elif isinstance(item, str) and person_name in item:
                        matched = True
                        match_info[field_name] = value
                        break
                if matched:
                    break
        
        if matched:
            matching_records.append({
                'record_id': record.get('record_id', ''),
                'fields': record_fields,
                'match_info': match_info
            })
    
    return matching_records

def format_field_value(value: Any, field_type: str) -> str:
    """格式化字段值"""
    if value is None or value == '':
        return ''
    
    field_type_str = str(field_type)
    
    if field_type_str in ['3', '4']:  # 单选或多选
        if isinstance(value, list):
            return ', '.join([item.get('text', item.get('name', '')) for item in value])
        elif isinstance(value, dict):
            return value.get('text', value.get('name', ''))
    elif field_type_str == '11':  # 人员
        if isinstance(value, list):
            return ', '.join([item.get('name', '') for item in value])
        elif isinstance(value, dict):
            return value.get('name', '')
    elif field_type_str == '5':  # 日期
        if isinstance(value, int):
            from datetime import datetime
            return datetime.fromtimestamp(value / 1000).strftime('%Y-%m-%d')
    elif field_type_str == '2':  # 数字
        return str(value)
    
    return str(value)

def analyze_person_bitable(person_name: str):
    """分析指定人员的人力盘点情况"""
    sys.stdout.reconfigure(encoding='utf-8')
    
    print("=" * 80)
    print(f"查询人员人力盘点情况: {person_name}")
    print("=" * 80)
    print()
    
    # 创建API和协作器
    api = FeishuAPI(
        plugin_id="",
        plugin_secret="",
        app_id=APP_ID,
        app_secret=APP_SECRET
    )
    api.set_user_access_token(USER_ACCESS_TOKEN)
    
    collaborator = create_bitable_collaborator(
        app_id=APP_ID,
        app_secret=APP_SECRET,
        user_access_token=USER_ACCESS_TOKEN
    )
    
    # 获取app_token
    print("步骤1：获取多维表格app_token...")
    app_token = get_app_token_from_wiki(api, SPACE_ID, NODE_TOKEN)
    if not app_token:
        print("[X] 无法获取app_token")
        return
    
    print(f"[OK] app_token: {app_token}")
    print()
    
    # 列出所有数据表
    print("步骤2：列出所有数据表...")
    tables_result = api.list_bitable_tables(app_token, use_user_token=True)
    if not tables_result:
        print("[X] 无法列出数据表")
        return
    
    tables = tables_result.get('items', []) if 'items' in tables_result else []
    print(f"[OK] 找到 {len(tables)} 个数据表")
    print()
    
    # 分析结果
    all_results = {}
    
    # 遍历每个数据表
    for table in tables:
        table_id = table.get('table_id')
        table_name = table.get('name', '未知')
        
        print(f"分析数据表: {table_name}")
        
        # 获取表格结构
        structure = collaborator.get_table_structure(app_token, table_id)
        fields_list = structure.get('fields', [])
        
        # 创建字段映射（field_id -> field_info）
        fields_map = {}
        for field in fields_list:
            field_id = field.get('field_id', '')
            fields_map[field_id] = {
                'field_name': field.get('field_name', ''),
                'field_type': field.get('type', ''),
                'field_id': field_id
            }
        
        # 获取所有记录
        records = collaborator.get_all_records(app_token, table_id)
        print(f"  记录数: {len(records)}")
        
        # 调试：查看API实际返回
        if len(records) == 0:
            # 直接调用API看看返回什么
            result = api.get_bitable_records(app_token, table_id, page_size=10)
            print(f"  [调试] API返回: {result}")
            if result:
                if 'code' in result:
                    print(f"  [调试] code: {result.get('code')}, msg: {result.get('msg')}")
                elif 'items' in result:
                    print(f"  [调试] items数量: {len(result.get('items', []))}")
        
        # 搜索包含该人员的记录
        # 对于资源池表，直接通过姓名字段搜索
        # 对于投入分配表，通过人员字段搜索
        # 对于业务规划表，可能通过主责小组或其他字段间接关联
        
        matching_records = search_person_in_records(records, fields_map, person_name)
        
        # 如果是投入分配表，还需要通过关联的资源池表查找
        if table_name == "投入分配表_怎么分" and not matching_records:
            # 先找到人员在资源池表中的record_id
            resource_pool_table = None
            for t in tables:
                if t.get('name') == "资源池表_谁可用":
                    resource_pool_table = t
                    break
            
            if resource_pool_table:
                resource_records = collaborator.get_all_records(app_token, resource_pool_table.get('table_id'))
                person_record_id = None
                for r in resource_records:
                    fields_data = r.get('fields', {})
                    # 查找姓名字段
                    for field_id, value in fields_data.items():
                        field_info = fields_map.get(field_id, {})
                        if field_info.get('field_name') == '姓名' and value == person_name:
                            person_record_id = r.get('record_id')
                            break
                    if person_record_id:
                        break
                
                # 在投入分配表中查找包含该record_id的记录
                if person_record_id:
                    for record in records:
                        record_fields = record.get('fields', {})
                        # 查找人员字段
                        for field_id, value in record_fields.items():
                            field_info = fields_map.get(field_id, {})
                            if field_info.get('field_name') == '人员' and value:
                                if isinstance(value, list):
                                    for item in value:
                                        if isinstance(item, dict):
                                            record_ids = item.get('record_ids', [])
                                            if person_record_id in record_ids:
                                                matching_records.append({
                                                    'record_id': record.get('record_id', ''),
                                                    'fields': record_fields,
                                                    'match_info': {field_info.get('field_name'): value}
                                                })
                                                break
        
        if matching_records:
            print(f"  [OK] 找到 {len(matching_records)} 条相关记录")
            all_results[table_name] = {
                'table_id': table_id,
                'fields': fields_map,
                'records': matching_records
            }
        else:
            print(f"  [!] 未找到相关记录")
        
        print()
    
    # 生成报告
    if not all_results:
        print("=" * 80)
        print(f"未找到 '{person_name}' 的相关记录")
        print("=" * 80)
        return
    
    print("=" * 80)
    print(f"{person_name} 的人力盘点情况")
    print("=" * 80)
    print()
    
    # 生成详细报告
    report_lines = []
    report_lines.append("=" * 80)
    report_lines.append(f"{person_name} 的人力盘点情况分析")
    report_lines.append("=" * 80)
    report_lines.append("")
    
    for table_name, table_data in all_results.items():
        report_lines.append(f"## {table_name}")
        report_lines.append("")
        
        fields_map = table_data['fields']
        records = table_data['records']
        
        report_lines.append(f"**相关记录数**: {len(records)}")
        report_lines.append("")
        
        # 分析记录
        for i, record_data in enumerate(records, 1):
            record_id = record_data.get('record_id', '')
            record_fields = record_data.get('fields', {})
            match_info = record_data.get('match_info', {})
            
            report_lines.append(f"### 记录 {i}")
            report_lines.append("")
            
            # 显示所有字段信息
            for field_id, value in record_fields.items():
                if value is not None and value != '':
                    field_info = fields_map.get(field_id, {})
                    field_name = field_info.get('field_name', field_id)
                    field_type = field_info.get('field_type', '')
                    
                    formatted_value = format_field_value(value, field_type)
                    if formatted_value:
                        # 标记匹配的字段
                        marker = " ⭐" if field_name in match_info else ""
                        report_lines.append(f"- **{field_name}**: {formatted_value}{marker}")
            
            report_lines.append("")
        
        # 统计分析
        if table_name == "资源池表_谁可用":
            report_lines.append("### 资源池信息分析")
            report_lines.append("")
            
            for record_data in records:
                record_fields = record_data.get('fields', {})
                
                # 提取关键信息
                name = record_fields.get('姓名', '')
                group = record_fields.get('所属小组', '')
                role = record_fields.get('人员属性', '')
                bandwidth = record_fields.get('可投带宽', '')
                actual_input = record_fields.get('实际投入', '')
                q1 = record_fields.get('Q1', '')
                q2 = record_fields.get('Q2', '')
                q3 = record_fields.get('Q3', '')
                q4 = record_fields.get('Q4', '')
                status = record_fields.get('当前状态', '')
                
                report_lines.append(f"**基本信息**:")
                report_lines.append(f"- 姓名: {name}")
                report_lines.append(f"- 所属小组: {group}")
                report_lines.append(f"- 人员属性: {role}")
                report_lines.append(f"- 当前状态: {status}")
                report_lines.append("")
                
                report_lines.append(f"**带宽情况**:")
                report_lines.append(f"- 可投带宽: {bandwidth}")
                report_lines.append(f"- 实际投入: {actual_input}")
                report_lines.append(f"- Q1投入: {q1}")
                report_lines.append(f"- Q2投入: {q2}")
                report_lines.append(f"- Q3投入: {q3}")
                report_lines.append(f"- Q4投入: {q4}")
                report_lines.append("")
                
                # 分析投入分配
                allocation_field = record_fields.get('投入分配表_怎么分', [])
                if allocation_field:
                    if isinstance(allocation_field, list) and len(allocation_field) > 0:
                        allocation_info = allocation_field[0]
                        allocation_ids = allocation_info.get('text_arr', [])
                        report_lines.append(f"**投入分配数**: {len(allocation_ids)}个")
                        report_lines.append(f"**分配ID**: {', '.join(allocation_ids[:10])}")
                        if len(allocation_ids) > 10:
                            report_lines.append(f"  (共{len(allocation_ids)}个)")
                        report_lines.append("")
        
        elif table_name == "投入分配表_怎么分":
            report_lines.append("### 投入分配分析")
            report_lines.append("")
            
            # 统计投入情况
            total_h1 = 0
            total_h2 = 0
            total_year = 0
            work_packages = []
            
            for record_data in records:
                record_fields = record_data.get('fields', {})
                h1 = record_fields.get('H1总投入', 0)
                h2 = record_fields.get('H2总投入', 0)
                year = record_fields.get('全年总投入', 0)
                work_pkg = record_fields.get('工作包', [])
                task = record_fields.get('投入任务', [])
                allocation_id = record_fields.get('分配ID', '')
                remark = record_fields.get('备注说明', '')
                
                if isinstance(h1, (int, float)):
                    total_h1 += float(h1)
                if isinstance(h2, (int, float)):
                    total_h2 += float(h2)
                if isinstance(year, (int, float)):
                    total_year += float(year)
                
                if work_pkg:
                    if isinstance(work_pkg, list) and len(work_pkg) > 0:
                        wp_name = work_pkg[0].get('text', '') if isinstance(work_pkg[0], dict) else str(work_pkg[0])
                        work_packages.append({
                            'name': wp_name,
                            'h1': h1,
                            'h2': h2,
                            'year': year,
                            'allocation_id': allocation_id,
                            'remark': remark,
                            'task': task
                        })
            
            report_lines.append(f"**投入统计**:")
            report_lines.append(f"- H1总投入: {total_h1:.2f}")
            report_lines.append(f"- H2总投入: {total_h2:.2f}")
            report_lines.append(f"- 全年总投入: {total_year:.2f}")
            report_lines.append("")
            
            if work_packages:
                report_lines.append(f"**参与工作包** (共{len(work_packages)}个):")
                report_lines.append("")
                for i, wp in enumerate(work_packages, 1):
                    report_lines.append(f"{i}. **{wp['name']}**")
                    report_lines.append(f"   - 分配ID: {wp['allocation_id']}")
                    report_lines.append(f"   - H1投入: {wp['h1']}")
                    report_lines.append(f"   - H2投入: {wp['h2']}")
                    report_lines.append(f"   - 全年投入: {wp['year']}")
                    if wp.get('remark'):
                        report_lines.append(f"   - 备注: {wp['remark']}")
                    report_lines.append("")
        
        elif table_name == "业务规划表_做什么":
            report_lines.append("### 参与工作包分析")
            report_lines.append("")
            
            # 分析参与的工作包
            objectives = []
            krs = []
            work_packages = []
            
            for record_data in records:
                record_fields = record_data.get('fields', {})
                obj = record_fields.get('目标Object', '')
                kr = record_fields.get('关键结果KR', '')
                wp = record_fields.get('工作包', '')
                direction = record_fields.get('业务方向', '')
                group = record_fields.get('主责小组', [])
                
                if obj:
                    objectives.append(obj)
                if kr:
                    krs.append(kr)
                if wp:
                    work_packages.append({
                        'name': wp,
                        'objective': obj,
                        'kr': kr,
                        'direction': direction,
                        'group': group
                    })
            
            if objectives:
                unique_objs = list(set(objectives))
                report_lines.append(f"**参与目标** (共{len(unique_objs)}个):")
                for obj in unique_objs:
                    report_lines.append(f"- {obj}")
                report_lines.append("")
            
            if krs:
                unique_krs = list(set(krs))
                report_lines.append(f"**参与关键结果** (共{len(unique_krs)}个):")
                for kr in unique_krs[:5]:  # 只显示前5个
                    report_lines.append(f"- {kr}")
                if len(unique_krs) > 5:
                    report_lines.append(f"  ... (共{len(unique_krs)}个)")
                report_lines.append("")
            
            if work_packages:
                report_lines.append(f"**参与工作包** (共{len(work_packages)}个):")
                for i, wp in enumerate(work_packages[:10], 1):  # 只显示前10个
                    report_lines.append(f"{i}. {wp['name']}")
                    if wp.get('direction'):
                        report_lines.append(f"   - 业务方向: {wp['direction']}")
                    if wp.get('group'):
                        report_lines.append(f"   - 主责小组: {', '.join(wp['group']) if isinstance(wp['group'], list) else wp['group']}")
                if len(work_packages) > 10:
                    report_lines.append(f"  ... (共{len(work_packages)}个)")
                report_lines.append("")
    
    # 通过投入分配表关联到业务规划表，获取详细工作包信息
    if "投入分配表_怎么分" in all_results:
        allocation_records = all_results["投入分配表_怎么分"]['records']
        business_plan_table = None
        for t in tables:
            if t.get('name') == "业务规划表_做什么":
                business_plan_table = t
                break
        
        if business_plan_table:
            business_plan_records = collaborator.get_all_records(app_token, business_plan_table.get('table_id'))
            # 创建record_id到记录的映射
            business_plan_map = {r.get('record_id'): r for r in business_plan_records}
            
            report_lines.append("")
            report_lines.append("=" * 80)
            report_lines.append("## 详细工作包信息")
            report_lines.append("=" * 80)
            report_lines.append("")
            
            for i, allocation_record in enumerate(allocation_records, 1):
                allocation_fields = allocation_record.get('fields', {})
                task_field = allocation_fields.get('投入任务', [])
                work_pkg_name = allocation_fields.get('工作包', [])
                
                if task_field and isinstance(task_field, list) and len(task_field) > 0:
                    task_info = task_field[0]
                    task_record_ids = task_info.get('record_ids', [])
                    
                    if task_record_ids:
                        task_record_id = task_record_ids[0]
                        task_record = business_plan_map.get(task_record_id)
                        
                        if task_record:
                            task_fields = task_record.get('fields', {})
                            
                            report_lines.append(f"### 工作包 {i}: {work_pkg_name[0].get('text', '') if isinstance(work_pkg_name, list) and len(work_pkg_name) > 0 else ''}")
                            report_lines.append("")
                            
                            # 显示关键信息
                            task_id = task_fields.get('任务ID', '')
                            objective = task_fields.get('目标Object', '')
                            kr = task_fields.get('关键结果KR', '')
                            direction = task_fields.get('业务方向', '')
                            group = task_fields.get('主责小组', [])
                            manpower_req = task_fields.get('人力总需求', '')
                            manpower_actual = task_fields.get('已投入人力', '')
                            manpower_gap = task_fields.get('人力缺口', '')
                            start_time = task_fields.get('开始时间', '')
                            end_time = task_fields.get('结束时间', '')
                            year = task_fields.get('归属年份', [])
                            
                            if task_id:
                                report_lines.append(f"- **任务ID**: {task_id}")
                            if objective:
                                report_lines.append(f"- **目标**: {objective}")
                            if kr:
                                report_lines.append(f"- **关键结果**: {kr}")
                            if direction:
                                report_lines.append(f"- **业务方向**: {direction}")
                            if group:
                                report_lines.append(f"- **主责小组**: {', '.join(group) if isinstance(group, list) else group}")
                            if manpower_req:
                                report_lines.append(f"- **人力总需求**: {manpower_req}")
                            if manpower_actual:
                                report_lines.append(f"- **已投入人力**: {manpower_actual}")
                            if manpower_gap:
                                report_lines.append(f"- **人力缺口**: {manpower_gap}")
                            if year:
                                report_lines.append(f"- **归属年份**: {', '.join(year) if isinstance(year, list) else year}")
                            
                            allocation_h1 = allocation_fields.get('H1总投入', '')
                            allocation_h2 = allocation_fields.get('H2总投入', '')
                            allocation_year = allocation_fields.get('全年总投入', '')
                            
                            report_lines.append(f"- **林广义投入**: H1={allocation_h1}, H2={allocation_h2}, 全年={allocation_year}")
                            
                            report_lines.append("")
    
    # 总结
    report_lines.append("")
    report_lines.append("=" * 80)
    report_lines.append("## 总结")
    report_lines.append("=" * 80)
    report_lines.append("")
    
    total_records = sum(len(data['records']) for data in all_results.values())
    report_lines.append(f"- **总记录数**: {total_records}条")
    report_lines.append(f"- **涉及数据表**: {len(all_results)}个")
    report_lines.append("")
    
    # 生成定性总结
    if "资源池表_谁可用" in all_results and "投入分配表_怎么分" in all_results:
        resource_record = all_results["资源池表_谁可用"]['records'][0]
        resource_fields = resource_record.get('fields', {})
        allocation_records = all_results["投入分配表_怎么分"]['records']
        
        actual_input = resource_fields.get('实际投入', 0)
        bandwidth = resource_fields.get('可投带宽', 0)
        role = resource_fields.get('人员属性', '')
        group = resource_fields.get('所属小组', '')
        
        total_h1 = sum(float(r.get('fields', {}).get('H1总投入', 0) or 0) for r in allocation_records)
        total_h2 = sum(float(r.get('fields', {}).get('H2总投入', 0) or 0) for r in allocation_records)
        total_year = sum(float(r.get('fields', {}).get('全年总投入', 0) or 0) for r in allocation_records)
        
        report_lines.append("### 人力盘点情况总结")
        report_lines.append("")
        report_lines.append(f"**基本信息**:")
        report_lines.append(f"- 角色: {role}")
        report_lines.append(f"- 所属小组: {group}")
        report_lines.append(f"- 可投带宽: {bandwidth}")
        report_lines.append(f"- 实际投入: {actual_input} (超出可投带宽{float(actual_input) - float(bandwidth):.1f})")
        report_lines.append("")
        
        report_lines.append(f"**投入分布**:")
        report_lines.append(f"- H1总投入: {total_h1:.2f}")
        report_lines.append(f"- H2总投入: {total_h2:.2f}")
        report_lines.append(f"- 全年总投入: {total_year:.2f}")
        report_lines.append(f"- 参与工作包数: {len(allocation_records)}个")
        report_lines.append("")
        
        report_lines.append(f"**投入特点**:")
        if total_year > 1.0:
            report_lines.append(f"- 投入超负荷: 全年投入{total_year:.2f}，超过可投带宽{bandwidth}，存在超负荷工作")
        elif total_year == 1.0:
            report_lines.append(f"- 投入饱和: 全年投入{total_year:.2f}，达到可投带宽上限")
        else:
            report_lines.append(f"- 投入合理: 全年投入{total_year:.2f}，在可投带宽范围内")
        
        # 分析工作包类型
        work_pkg_types = {}
        for r in allocation_records:
            wp = r.get('fields', {}).get('工作包', [])
            if wp and isinstance(wp, list) and len(wp) > 0:
                wp_name = wp[0].get('text', '') if isinstance(wp[0], dict) else str(wp[0])
                if '管理' in wp_name:
                    work_pkg_types['管理类'] = work_pkg_types.get('管理类', 0) + 1
                elif '结构化管理' in wp_name or '数据' in wp_name:
                    work_pkg_types['数据/结构化管理'] = work_pkg_types.get('数据/结构化管理', 0) + 1
                elif '合规' in wp_name:
                    work_pkg_types['合规类'] = work_pkg_types.get('合规类', 0) + 1
                else:
                    work_pkg_types['其他'] = work_pkg_types.get('其他', 0) + 1
        
        if work_pkg_types:
            report_lines.append(f"- 工作包类型分布:")
            for wp_type, count in work_pkg_types.items():
                report_lines.append(f"  - {wp_type}: {count}个")
        
        report_lines.append("")
    
    # 打印报告
    report = '\n'.join(report_lines)
    print(report)
    
    # 保存报告
    output_file = f"work/person_bitable_{person_name}.md"
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print()
    print(f"[OK] 报告已保存到: {output_file}")

if __name__ == "__main__":
    person_name = "林广义"
    analyze_person_bitable(person_name)

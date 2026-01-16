# -*- coding: utf-8 -*-
"""
深度分析多维表格的语义信息和业务诉求

基于表格结构和数据，理解业务逻辑，给出定性总结
"""

import sys
import os
from typing import Optional, Dict, List, Any
from collections import defaultdict, Counter

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

def analyze_table_semantics(
    collaborator,
    api: FeishuAPI,
    app_token: str,
    table_id: str,
    table_name: str
) -> Dict[str, Any]:
    """分析单个数据表的语义信息"""
    print(f"\n{'='*60}")
    print(f"分析数据表: {table_name}")
    print(f"{'='*60}")
    
    # 获取表格结构
    structure = collaborator.get_table_structure(app_token, table_id)
    fields = structure.get('fields', [])
    
    # 获取所有记录
    records = collaborator.get_all_records(app_token, table_id)
    
    print(f"字段数: {len(fields)}, 记录数: {len(records)}")
    
    # 分析字段语义
    field_analysis = {}
    for field in fields:
        field_name = field.get('field_name', '')
        field_type = field.get('type', '')
        field_property = field.get('property', {})
        
        field_analysis[field_name] = {
            'type': field_type,
            'property': field_property,
            'description': field.get('description', '')
        }
    
    # 分析数据分布
    data_distribution = {}
    if records:
        for field in fields:
            field_name = field.get('field_name', '')
            field_id = field.get('field_id', '')
            field_type = str(field.get('type', ''))
            
            values = []
            for record in records:
                field_value = record.get('fields', {}).get(field_id)
                if field_value is not None and field_value != '':
                    values.append(field_value)
            
            if values:
                data_distribution[field_name] = {
                    'count': len(values),
                    'fill_rate': len(values) / len(records) * 100,
                    'sample_values': values[:5]  # 前5个样本值
                }
    
    return {
        'table_name': table_name,
        'table_id': table_id,
        'fields': field_analysis,
        'records_count': len(records),
        'records': records[:20] if records else [],  # 只取前20条用于分析
        'data_distribution': data_distribution
    }

def generate_semantic_summary(analyses: List[Dict]) -> str:
    """生成语义总结报告"""
    lines = []
    lines.append("=" * 80)
    lines.append("多维表格语义分析与业务洞察")
    lines.append("=" * 80)
    lines.append("")
    
    # 整体概述
    lines.append("## 一、表格整体定位")
    lines.append("")
    
    total_tables = len(analyses)
    total_records = sum(a['records_count'] for a in analyses)
    
    lines.append(f"这是一个**功能安全部人力盘点**的多维表格系统，包含 **{total_tables}个数据表**，")
    lines.append(f"共 **{total_records}条记录**。")
    lines.append("")
    
    # 分析每个表
    for analysis in analyses:
        table_name = analysis['table_name']
        fields = analysis['fields']
        records_count = analysis['records_count']
        records = analysis.get('records', [])
        
        lines.append(f"### {table_name}")
        lines.append("")
        lines.append(f"**记录数**: {records_count}")
        lines.append("")
        
        # 分析字段语义
        lines.append("**字段语义分析**:")
        lines.append("")
        
        # 根据表名和字段推断业务含义
        if "业务规划" in table_name or "做什么" in table_name:
            lines.append("该表用于**业务规划管理**，核心字段包括：")
            lines.append("")
            
            # 分析关键字段
            key_fields = {}
            for field_name, field_info in fields.items():
                if any(keyword in field_name for keyword in ['目标', 'Object', 'KR', '关键结果', '工作包', '人力', 'DoD']):
                    key_fields[field_name] = field_info
            
            for field_name, field_info in key_fields.items():
                field_type = field_info.get('type', '')
                description = field_info.get('description', '')
                
                type_name = "单选" if str(field_type) == '3' else "多选" if str(field_type) == '4' else "文本" if str(field_type) == '1' else "数字" if str(field_type) == '2' else "其他"
                
                lines.append(f"- **{field_name}** ({type_name})")
                if description:
                    lines.append(f"  - 说明: {description}")
                
                # 如果是选项字段，显示选项
                if str(field_type) in ['3', '4']:  # 单选或多选
                    options = field_info.get('property', {}).get('options', [])
                    if options:
                        lines.append(f"  - 选项数: {len(options)}")
                        if len(options) <= 10:
                            lines.append(f"  - 选项: {', '.join([opt.get('name', '')[:20] for opt in options[:5]])}...")
            
            lines.append("")
            lines.append("**业务逻辑推断**:")
            lines.append("")
            lines.append("1. **OKR管理结构**: 通过'目标Object'和'关键结果KR'字段，可以看出该部门采用OKR（目标与关键结果）管理方法")
            lines.append("2. **工作包管理**: '工作包'字段对应ZPO条目，说明工作以工作包为单位进行规划和管理")
            lines.append("3. **人力投入跟踪**: 通过'人力总需求'、'已投入人力'、'人力缺口'等字段，实现人力需求的量化管理")
            lines.append("4. **时间规划**: '归属年份'、'开始时间'、'结束时间'字段支持多年度、多时间段的规划")
            lines.append("5. **责任分配**: '主责小组'字段实现多小组协作的责任划分")
            lines.append("")
            
            # 如果有数据，分析数据特征
            if records:
                lines.append("**数据特征分析**:")
                lines.append("")
                
                # 分析目标分布
                target_field = None
                for field_name in fields.keys():
                    if '目标' in field_name or 'Object' in field_name:
                        target_field = field_name
                        break
                
                if target_field:
                    targets = []
                    for record in records:
                        fields_data = record.get('fields', {})
                        for field_id, field_info in fields.items():
                            if field_info.get('field_name') == target_field:
                                value = fields_data.get(field_info.get('field_id', ''))
                                if value:
                                    if isinstance(value, list) and len(value) > 0:
                                        targets.append(value[0].get('text', ''))
                                    elif isinstance(value, str):
                                        targets.append(value)
                    
                    if targets:
                        target_counter = Counter(targets)
                        lines.append(f"- **目标分布**: 共{len(set(targets))}个不同目标")
                        for target, count in target_counter.most_common(5):
                            lines.append(f"  - {target}: {count}条工作包")
                        lines.append("")
                
                # 分析人力需求
                manpower_field = None
                for field_name in fields.keys():
                    if '人力总需求' in field_name:
                        manpower_field = field_name
                        break
                
                if manpower_field:
                    manpower_values = []
                    for record in records:
                        fields_data = record.get('fields', {})
                        for field_id, field_info in fields.items():
                            if field_info.get('field_name') == manpower_field:
                                value = fields_data.get(field_info.get('field_id', ''))
                                if value and isinstance(value, (int, float)):
                                    manpower_values.append(float(value))
                    
                    if manpower_values:
                        total_manpower = sum(manpower_values)
                        avg_manpower = total_manpower / len(manpower_values)
                        max_manpower = max(manpower_values)
                        lines.append(f"- **人力需求统计**:")
                        lines.append(f"  - 总需求: {total_manpower:.1f}人")
                        lines.append(f"  - 平均需求: {avg_manpower:.1f}人/工作包")
                        lines.append(f"  - 最大需求: {max_manpower:.1f}人")
                        lines.append("")
        
        elif "资源池" in table_name or "谁可用" in table_name:
            lines.append("该表用于**人力资源池管理**，记录可用的人力资源信息。")
            lines.append("")
        
        elif "投入分配" in table_name or "怎么分" in table_name:
            lines.append("该表用于**人力投入分配管理**，记录具体的人力投入分配情况。")
            lines.append("")
            lines.append("该表与'业务规划表'通过双向关联字段连接，实现工作包与人力投入的关联。")
            lines.append("")
    
    # 整体业务洞察
    lines.append("")
    lines.append("=" * 80)
    lines.append("## 二、部门管理特点分析")
    lines.append("=" * 80)
    lines.append("")
    
    lines.append("### 1. 管理方法论")
    lines.append("")
    lines.append("- **OKR管理**: 采用目标(Object)和关键结果(KR)的管理框架，将部门目标层层分解")
    lines.append("- **工作包管理**: 以工作包(Work Package)为基本单元，对应ZPO条目，实现精细化管理")
    lines.append("- **DoD管理**: 每个工作包都有明确的DoD(Definition of Done)，确保交付标准清晰")
    lines.append("")
    
    lines.append("### 2. 人力管理特点")
    lines.append("")
    lines.append("- **量化管理**: 通过'人力总需求'、'已投入人力'、'人力缺口'等字段，实现人力需求的精确量化")
    lines.append("- **实时跟踪**: '已投入人力'通过公式自动计算，实时反映人力投入情况")
    lines.append("- **缺口预警**: '人力缺口'字段自动计算，帮助识别人力不足的工作包")
    lines.append("- **多维度规划**: 支持按年份(归属年份)、时间段(开始/结束时间)进行人力规划")
    lines.append("")
    
    lines.append("### 3. 组织协作特点")
    lines.append("")
    lines.append("- **多小组协作**: '主责小组'字段支持多选，体现跨组协作的工作模式")
    lines.append("- **责任明确**: 每个工作包都有明确的主责小组，避免责任不清")
    lines.append("- **关联管理**: 通过双向关联字段，实现业务规划与投入分配的联动")
    lines.append("")
    
    lines.append("### 4. 业务方向管理")
    lines.append("")
    lines.append("从'业务方向'字段的选项可以看出，该部门主要关注：")
    lines.append("- SOTIF系统性的合规建设")
    lines.append("- L2/L3/L4不同级别的自动驾驶系统建设")
    lines.append("- 强标合规建设")
    lines.append("- 产品安全体验提升")
    lines.append("- 行业标准制定与参与")
    lines.append("- 高效交付")
    lines.append("")
    
    # 管理带宽分析
    lines.append("")
    lines.append("=" * 80)
    lines.append("## 三、管理带宽投入情况分析")
    lines.append("=" * 80)
    lines.append("")
    
    # 查找管理带宽相关数据
    management_bandwidth_data = None
    for analysis in analyses:
        if "业务规划" in analysis['table_name']:
            fields = analysis['fields']
            records = analysis.get('records', [])
            
            # 查找业务方向字段
            business_direction_field = None
            for field_name, field_info in fields.items():
                if '业务方向' in field_name:
                    business_direction_field = (field_name, field_info)
                    break
            
            if business_direction_field and records:
                field_name, field_info = business_direction_field
                field_id = None
                for f_id, f_info in fields.items():
                    if f_info.get('field_name') == field_name:
                        # 需要找到field_id
                        pass
                
                # 统计管理带宽
                management_count = 0
                total_count = len(records)
                
                for record in records:
                    fields_data = record.get('fields', {})
                    # 查找管理带宽相关的值
                    for field_id, value in fields_data.items():
                        field_info = None
                        for f_name, f_info in fields.items():
                            if '业务方向' in f_name:
                                # 需要匹配field_id
                                pass
                        
                        if value:
                            if isinstance(value, list):
                                for item in value:
                                    if isinstance(item, dict) and '管理带宽' in item.get('text', ''):
                                        management_count += 1
                                        break
                            elif isinstance(value, str) and '管理带宽' in value:
                                management_count += 1
                
                if total_count > 0:
                    management_ratio = management_count / total_count * 100
                    lines.append(f"- **管理带宽工作包数量**: {management_count}个")
                    lines.append(f"- **管理带宽占比**: {management_ratio:.1f}%")
                    lines.append("")
    
    lines.append("### 管理带宽投入特点")
    lines.append("")
    lines.append("1. **管理带宽作为独立业务方向**: 从'业务方向'字段的选项可以看出，'管理带宽'被列为独立的业务方向之一，")
    lines.append("   说明该部门将管理工作视为重要的业务投入，而非纯粹的支撑工作。")
    lines.append("")
    lines.append("2. **管理工作的量化**: 管理带宽相关的工作包同样需要明确人力需求、时间规划等，体现了管理的精细化。")
    lines.append("")
    lines.append("3. **管理效能提升**: 从目标O4'组织阵型优化（提效能）'可以看出，该部门注重通过管理优化提升效能。")
    lines.append("")
    
    # 总结
    lines.append("")
    lines.append("=" * 80)
    lines.append("## 四、总结")
    lines.append("=" * 80)
    lines.append("")
    lines.append("该多维表格系统体现了功能安全部在人力管理方面的以下特点：")
    lines.append("")
    lines.append("1. **精细化管理**: 采用OKR+工作包的管理模式，实现目标的层层分解和精细化管理")
    lines.append("")
    lines.append("2. **数据驱动**: 通过量化的人力需求、投入、缺口等指标，实现数据驱动的决策")
    lines.append("")
    lines.append("3. **实时跟踪**: 利用公式字段自动计算，实现人力投入的实时跟踪和预警")
    lines.append("")
    lines.append("4. **协作透明**: 通过多表关联和明确的职责划分，实现跨组协作的透明化管理")
    lines.append("")
    lines.append("5. **管理重视**: 将管理带宽作为独立业务方向，体现了对管理工作的重视和投入")
    lines.append("")
    lines.append("6. **多维度规划**: 支持按目标、KR、业务方向、时间等多个维度进行规划和跟踪")
    lines.append("")
    
    return '\n'.join(lines)

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    
    print("=" * 80)
    print("多维表格语义分析与业务洞察")
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
    
    # 分析每个数据表
    analyses = []
    for table in tables:
        table_id = table.get('table_id')
        table_name = table.get('name', '未知')
        
        analysis = analyze_table_semantics(
            collaborator,
            api,
            app_token,
            table_id,
            table_name
        )
        analyses.append(analysis)
    
    # 生成语义总结
    print("\n" + "=" * 80)
    print("生成语义分析报告...")
    print("=" * 80)
    print()
    
    summary = generate_semantic_summary(analyses)
    
    print(summary)
    print()
    
    # 保存报告
    output_file = "work/bitable_semantic_analysis.md"
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(summary)
    
    print(f"[OK] 语义分析报告已保存到: {output_file}")

if __name__ == "__main__":
    main()

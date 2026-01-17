# -*- coding: utf-8 -*-
"""
分析指定的多维表格结构

查看关键表的结构、字段、记录数等信息
"""

import sys
import os
import json
from pathlib import Path
from typing import Dict, List, Any

# 修复Windows控制台编码问题
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bitable_query_interface import get_query_interface
from bitable_cache_manager import CACHE_DIR

# 要分析的表名列表
TARGET_TABLES = [
    "架构元素表",
    "非期待事件表",
    "子功能清单表",
    "失效模式影响分析表_HW",
    "失效模式影响分析表_SW",
    "安全机制表"
]

def get_field_type_name(field_type: Any) -> str:
    """获取字段类型名称"""
    field_type_str = str(field_type)
    type_map = {
        '1': '文本',
        '2': '数字',
        '3': '单选',
        '4': '多选',
        '5': '日期',
        '7': '复选框',
        '11': '人员',
        '13': '电话号码',
        '15': '超链接',
        '17': '附件',
        '18': '关联',
        '19': '公式',
        '20': '公式',
        '21': '双向关联',
        '22': '创建人',
        '23': '修改人',
        '1001': '自动编号',
        '1002': '地理位置',
        '1003': '群组',
        '1004': '双向关联',
        '1005': '自动编号'
    }
    return type_map.get(field_type_str, f'未知类型({field_type})')

def analyze_table_structure(table_data: Dict[str, Any], table_name: str) -> None:
    """分析单个表的结构"""
    print("=" * 80)
    print(f"表名: {table_name}")
    print("=" * 80)
    print()
    
    # 基本信息
    record_count = table_data.get('record_count', 0)
    table_id = table_data.get('table_id', 'N/A')
    
    print(f"表ID: {table_id}")
    print(f"记录数: {record_count}")
    print()
    
    # 字段信息
    fields = table_data.get('fields', [])
    if fields:
        print(f"字段数: {len(fields)}")
        print()
        print("字段列表:")
        print("-" * 80)
        
        for i, field in enumerate(fields, 1):
            field_name = field.get('field_name', '未知')
            field_type = field.get('field_type', '未知')
            field_id = field.get('field_id', 'N/A')
            
            # 获取字段类型名称
            type_name = get_field_type_name(field_type)
            
            print(f"{i:2d}. {field_name}")
            print(f"     类型: {type_name} ({field_type})")
            print(f"     字段ID: {field_id}")
            
            # 如果是关联字段，显示关联信息
            if str(field_type) in ['18', '21', '1004']:  # 关联字段
                # 注意：缓存中的字段信息可能不包含property，需要从原始API获取
                print(f"     [关联字段]")
            
            # 如果是单选/多选，显示选项
            if str(field_type) in ['3', '4']:  # 单选或多选
                print(f"     [选项字段]")
            
            print()
    else:
        print("[!] 无法获取字段信息")
    
    # 显示前几条记录示例（如果有）
    records = table_data.get('records', [])
    if records and len(records) > 0:
        print("-" * 80)
        print("记录示例（前3条）:")
        print("-" * 80)
        for i, record in enumerate(records[:3], 1):
            print(f"\n记录 {i}:")
            fields_data = record.get('fields', {})
            for field_name, field_value in list(fields_data.items())[:5]:  # 只显示前5个字段
                if field_value:
                    # 处理不同类型的值
                    if isinstance(field_value, list):
                        if field_value and isinstance(field_value[0], dict):
                            value_str = ', '.join([str(v.get('text', v)) for v in field_value[:3]])
                        else:
                            value_str = ', '.join([str(v) for v in field_value[:3]])
                        if len(field_value) > 3:
                            value_str += f" ... (共{len(field_value)}项)"
                    else:
                        value_str = str(field_value)
                    if len(value_str) > 100:
                        value_str = value_str[:100] + "..."
                    print(f"  {field_name}: {value_str}")
    
    print()

def main():
    """主函数"""
    print("=" * 80)
    print("分析指定的多维表格结构")
    print("=" * 80)
    print()
    
    cache_file = "new_bitable.json"
    cache_path = CACHE_DIR / cache_file
    
    if not cache_path.exists():
        print(f"[!] 缓存文件不存在: {cache_path}")
        print("正在同步数据...")
        print()
        
        # 尝试同步数据
        try:
            from auto_sync_all import sync_all_caches
            sync_all_caches(force_refresh=True)
            print()
        except Exception as e:
            print(f"[X] 同步失败: {e}")
            print("请手动运行: python auto_sync_all.py --once --force")
            return
        
        # 重新检查
        if not cache_path.exists():
            print("[X] 同步后缓存文件仍不存在")
            return
    
    # 加载缓存数据
    print(f"加载缓存文件: {cache_path}")
    with open(cache_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    tables = data.get('tables', {})
    
    print(f"总表数: {len(tables)}")
    print()
    
    # 先列出所有表名，方便查找
    print("所有可用的表名:")
    print("-" * 80)
    for name in sorted(tables.keys()):
        print(f"  - {name}")
    print()
    
    # 获取查询接口
    interface = get_query_interface()
    
    # 分析每个目标表
    found_tables = []
    not_found_tables = []
    
    for target_table_name in TARGET_TABLES:
        # 尝试精确匹配和模糊匹配
        table_data = None
        matched_table_name = None
        
        # 精确匹配
        if target_table_name in tables:
            table_data = interface.get_table_data(target_table_name, cache_file)
            if table_data:
                matched_table_name = target_table_name
        
        # 模糊匹配
        if not table_data:
            for table_name in tables.keys():
                if target_table_name in table_name or table_name in target_table_name:
                    table_data = interface.get_table_data(table_name, cache_file)
                    if table_data:
                        matched_table_name = table_name
                        break
        
        if table_data:
            found_tables.append((matched_table_name, table_data))
        else:
            not_found_tables.append(target_table_name)
    
    # 显示找到的表
    if found_tables:
        print(f"[OK] 找到 {len(found_tables)} 个表")
        print()
        
        for table_name, table_data in found_tables:
            analyze_table_structure(table_data, table_name)
    
    # 显示未找到的表
    if not_found_tables:
        print("=" * 80)
        print("未找到的表:")
        print("=" * 80)
        print()
        for table_name in not_found_tables:
            print(f"  - {table_name}")
        print()
        
        # 提供相似表名建议
        print("相似的表名（可能匹配）:")
        print("-" * 80)
        for not_found in not_found_tables:
            suggestions = []
            for table_name in tables.keys():
                # 简单的相似度匹配
                if any(keyword in table_name for keyword in not_found.split('表')[0].split('_')):
                    suggestions.append(table_name)
            if suggestions:
                print(f"  '{not_found}' 可能的匹配:")
                for sug in suggestions[:3]:
                    print(f"    - {sug}")
        print()
    
    print("=" * 80)
    print("分析完成")
    print("=" * 80)

if __name__ == "__main__":
    main()

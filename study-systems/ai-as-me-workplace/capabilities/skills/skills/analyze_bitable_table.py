# -*- coding: utf-8 -*-
"""
分析并总结多维表格内容

使用多维表格协作器访问表格并生成总结报告
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from feishu_bitable_collaborator import create_bitable_collaborator

# 配置信息
APP_ID = "cli_a9c92ca516f99bd9"
APP_SECRET = "zlOKnyZkSuSUSr0WlAl6qbh5Qw4eM6wC"
USER_ACCESS_TOKEN = os.getenv("FEISHU_USER_ACCESS_TOKEN", "u-euA79EeIpex9kiDRX3ONqS0hgoJw4kiXVyGy3wM00KTo")

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    
    # 多维表格信息
    app_token = "CGMnwhxzLixWhGk87jYcDRfonsh"
    table_id = "ldxHpfvt2RgjapGD"
    
    print("=" * 60)
    print("多维表格分析和总结")
    print("=" * 60)
    print()
    print(f"App Token: {app_token}")
    print(f"Table ID: {table_id}")
    print()
    
    # 创建协作器
    print("步骤1：创建协作器...")
    collaborator = create_bitable_collaborator(
        app_id=APP_ID,
        app_secret=APP_SECRET,
        user_access_token=USER_ACCESS_TOKEN
    )
    print("[OK] 协作器创建成功")
    print()
    
    # 获取表格信息
    print("步骤2：获取多维表格信息...")
    app_info = collaborator.get_app_info(app_token)
    if app_info and app_info.get('code') == 0:
        app_data = app_info.get('data', {}).get('app', {})
        app_name = app_data.get('name', '未知')
        print(f"[OK] 多维表格名称: {app_name}")
    else:
        print("[!] 无法获取表格信息，继续执行...")
    print()
    
    # 获取表格结构
    print("步骤3：获取表格结构...")
    structure = collaborator.get_table_structure(app_token, table_id)
    print(f"[OK] 字段数量: {len(structure['fields'])}")
    print(f"[OK] 视图数量: {len(structure['views'])}")
    print()
    
    # 显示字段信息
    if structure['fields']:
        print("字段列表:")
        for i, field in enumerate(structure['fields'], 1):
            field_name = field.get('field_name', '未知')
            field_type = field.get('type', '未知')
            field_type_name = collaborator._get_field_type_name(field_type)
            print(f"  {i}. {field_name} ({field_type_name})")
        print()
    
    # 获取所有记录
    print("步骤4：获取所有记录...")
    records = collaborator.get_all_records(app_token, table_id)
    print(f"[OK] 总记录数: {len(records)}")
    print()
    
    # 分析数据表
    print("步骤5：分析数据表...")
    analysis = collaborator.analyze_table(app_token, table_id)
    print("[OK] 分析完成")
    print()
    
    # 显示统计信息
    stats = analysis['statistics']
    print("统计信息:")
    print(f"  - 总记录数: {stats['total_records']}")
    print(f"  - 总字段数: {stats['total_fields']}")
    print(f"  - 总视图数: {stats['total_views']}")
    print()
    
    # 显示字段类型分布
    if stats['field_types']:
        print("字段类型分布:")
        for field_type, count in stats['field_types'].items():
            type_name = collaborator._get_field_type_name(field_type)
            print(f"  - {type_name}: {count}个")
        print()
    
    # 生成完整总结
    print("步骤6：生成数据表总结报告...")
    print()
    summary = collaborator.summarize_table(
        app_token,
        table_id,
        include_structure=True,
        include_statistics=True,
        include_insights=True
    )
    
    print(summary)
    print()
    
    # 保存到文件
    output_file = "work/bitable_summary.md"
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(summary)
    
    print(f"[OK] 总结报告已保存到: {output_file}")
    print()
    
    # 显示部分数据示例（前5条记录）
    if records:
        print("=" * 60)
        print("数据示例（前5条记录）")
        print("=" * 60)
        print()
        
        field_map = {f.get('field_id'): f for f in structure['fields']}
        
        for i, record in enumerate(records[:5], 1):
            print(f"记录 {i}:")
            fields_data = record.get('fields', {})
            for field_id, value in list(fields_data.items())[:5]:  # 只显示前5个字段
                field_info = field_map.get(field_id, {})
                field_name = field_info.get('field_name', field_id)
                formatted_value = collaborator._format_field_value(value, field_info.get('type', ''))
                if formatted_value:
                    print(f"  - {field_name}: {formatted_value}")
            print()

if __name__ == "__main__":
    main()

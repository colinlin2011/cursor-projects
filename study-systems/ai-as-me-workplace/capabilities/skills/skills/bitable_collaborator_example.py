# -*- coding: utf-8 -*-
"""
多维表格协作器使用示例

展示如何使用FeishuBitableCollaborator进行多维表格协作
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from feishu_bitable_collaborator import create_bitable_collaborator

# 配置信息
APP_ID = "cli_a9c92ca516f99bd9"
APP_SECRET = "zlOKnyZkSuSUSr0WlAl6qbh5Qw4eM6wC"
USER_ACCESS_TOKEN = os.getenv("FEISHU_USER_ACCESS_TOKEN", "u-4tBMNLQZ15Oqb0cGVm.7W.k1n31w4koprGGymw282HUW")

def example_1_get_table_structure():
    """示例1：获取表格结构"""
    print("=" * 60)
    print("示例1：获取表格结构")
    print("=" * 60)
    print()
    
    # 创建协作器
    collaborator = create_bitable_collaborator(
        app_id=APP_ID,
        app_secret=APP_SECRET,
        user_access_token=USER_ACCESS_TOKEN
    )
    
    # 从URL中提取app_token和table_id
    # 例如：https://bitable.feishu.cn/app/xxxxxxxxxx/table/xxxxxxxxxx
    app_token = "your_app_token"
    table_id = "your_table_id"
    
    # 获取表格结构
    structure = collaborator.get_table_structure(app_token, table_id)
    
    print(f"字段数量: {len(structure['fields'])}")
    print(f"视图数量: {len(structure['views'])}")
    print()
    print("字段列表:")
    for field in structure['fields']:
        print(f"  - {field.get('field_name')} ({field.get('type')})")

def example_2_analyze_table():
    """示例2：分析数据表"""
    print("=" * 60)
    print("示例2：分析数据表")
    print("=" * 60)
    print()
    
    collaborator = create_bitable_collaborator(
        app_id=APP_ID,
        app_secret=APP_SECRET,
        user_access_token=USER_ACCESS_TOKEN
    )
    
    app_token = "your_app_token"
    table_id = "your_table_id"
    
    # 分析数据表
    analysis = collaborator.analyze_table(app_token, table_id)
    
    print("统计信息:")
    print(f"  总记录数: {analysis['statistics']['total_records']}")
    print(f"  总字段数: {analysis['statistics']['total_fields']}")
    print()
    
    print("数据洞察:")
    for insight in analysis['insights']:
        print(f"  - {insight['title']}: {insight['content']}")

def example_3_summarize_table():
    """示例3：生成数据表总结"""
    print("=" * 60)
    print("示例3：生成数据表总结")
    print("=" * 60)
    print()
    
    collaborator = create_bitable_collaborator(
        app_id=APP_ID,
        app_secret=APP_SECRET,
        user_access_token=USER_ACCESS_TOKEN
    )
    
    app_token = "your_app_token"
    table_id = "your_table_id"
    
    # 生成总结
    summary = collaborator.summarize_table(
        app_token,
        table_id,
        include_structure=True,
        include_statistics=True,
        include_insights=True
    )
    
    print(summary)

def example_4_crud_operations():
    """示例4：CRUD操作"""
    print("=" * 60)
    print("示例4：CRUD操作")
    print("=" * 60)
    print()
    
    collaborator = create_bitable_collaborator(
        app_id=APP_ID,
        app_secret=APP_SECRET,
        user_access_token=USER_ACCESS_TOKEN
    )
    
    app_token = "your_app_token"
    table_id = "your_table_id"
    
    # 创建记录
    new_record = collaborator.create_record(
        app_token,
        table_id,
        fields={
            "字段名1": "值1",
            "字段名2": "值2"
        }
    )
    
    if new_record:
        record_id = new_record.get('data', {}).get('record', {}).get('record_id')
        print(f"[OK] 记录已创建: {record_id}")
        
        # 更新记录
        updated = collaborator.update_record(
            app_token,
            table_id,
            record_id,
            fields={
                "字段名1": "新值1"
            }
        )
        
        if updated:
            print(f"[OK] 记录已更新: {record_id}")
        
        # 删除记录
        if collaborator.delete_record(app_token, table_id, record_id):
            print(f"[OK] 记录已删除: {record_id}")

def example_5_export_to_markdown():
    """示例5：导出为Markdown"""
    print("=" * 60)
    print("示例5：导出为Markdown")
    print("=" * 60)
    print()
    
    collaborator = create_bitable_collaborator(
        app_id=APP_ID,
        app_secret=APP_SECRET,
        user_access_token=USER_ACCESS_TOKEN
    )
    
    app_token = "your_app_token"
    table_id = "your_table_id"
    
    # 导出为Markdown
    md_content = collaborator.export_to_markdown(
        app_token,
        table_id,
        output_file="work/bitable_export.md"
    )
    
    print("[OK] 已导出到 work/bitable_export.md")
    print(f"内容长度: {len(md_content)} 字符")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        example_num = sys.argv[1]
        if example_num == "1":
            example_1_get_table_structure()
        elif example_num == "2":
            example_2_analyze_table()
        elif example_num == "3":
            example_3_summarize_table()
        elif example_num == "4":
            example_4_crud_operations()
        elif example_num == "5":
            example_5_export_to_markdown()
        else:
            print("用法: python bitable_collaborator_example.py [1|2|3|4|5]")
    else:
        print("多维表格协作器使用示例")
        print()
        print("运行示例：")
        print("  python bitable_collaborator_example.py 1  # 获取表格结构")
        print("  python bitable_collaborator_example.py 2  # 分析数据表")
        print("  python bitable_collaborator_example.py 3  # 生成数据表总结")
        print("  python bitable_collaborator_example.py 4  # CRUD操作")
        print("  python bitable_collaborator_example.py 5  # 导出为Markdown")

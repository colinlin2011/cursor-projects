# -*- coding: utf-8 -*-
"""
分析Wiki中的多维表格

对于Wiki中的多维表格，需要先通过Wiki API获取节点信息，得到app_token
"""

import sys
import os
import re
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from feishu_bitable_collaborator import create_bitable_collaborator
from feishu_api_wrapper import FeishuAPI

# 配置信息
APP_ID = "cli_a9c92ca516f99bd9"
APP_SECRET = "zlOKnyZkSuSUSr0WlAl6qbh5Qw4eM6wC"
USER_ACCESS_TOKEN = os.getenv("FEISHU_USER_ACCESS_TOKEN", "u-fjEA3Zj5J4eGr.QY6KVnXg14hgJ04kgVOOwaFMy024ps")

def extract_from_wiki_url(url: str) -> tuple:
    """
    从Wiki URL中提取space_id和node_token
    
    格式：https://zyt.feishu.cn/wiki/{node_token}?table={table_id}
    """
    # 提取node_token（在/wiki/之后，?之前）
    match = re.search(r'/wiki/([^?]+)', url)
    if match:
        node_token = match.group(1)
    else:
        return None, None, None
    
    # 提取table_id（在?table=之后）
    match = re.search(r'[?&]table=([^&]+)', url)
    if table_id := match.group(1) if match else None:
        pass
    else:
        table_id = None
    
    # 尝试从URL中提取space_id（通常在域名后的路径中，但这里没有）
    # 需要从Wiki API获取
    space_id = None
    
    return space_id, node_token, table_id

def get_app_token_from_wiki_node(api: FeishuAPI, space_id: str, node_token: str) -> Optional[str]:
    """
    通过Wiki节点获取多维表格的app_token
    
    对于Wiki中的多维表格，obj_type应该是'bitable'，obj_token就是app_token
    """
    result = api.get_wiki_node(space_id, node_token, use_user_token=True)
    
    if result and result.get('code') == 0:
        node = result.get('node', {})
        obj_type = node.get('obj_type', '')
        obj_token = node.get('obj_token', '')
        
        if obj_type == 'bitable':
            return obj_token
    
    return None

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    
    # Wiki中的多维表格URL
    wiki_url = "https://zyt.feishu.cn/wiki/CGMnwhxzLixWhGk87jYcDRfonsh?table=ldxHpfvt2RgjapGD"
    
    print("=" * 60)
    print("分析Wiki中的多维表格")
    print("=" * 60)
    print()
    print(f"Wiki URL: {wiki_url}")
    print()
    
    # 从URL提取信息
    space_id, node_token, table_id = extract_from_wiki_url(wiki_url)
    
    if not node_token:
        print("[X] 无法从URL中提取node_token")
        return
    
    print(f"提取的信息:")
    print(f"  - Node Token: {node_token}")
    print(f"  - Table ID: {table_id}")
    print()
    
    # 创建API实例
    api = FeishuAPI(
        plugin_id="",
        plugin_secret="",
        app_id=APP_ID,
        app_secret=APP_SECRET
    )
    api.set_user_access_token(USER_ACCESS_TOKEN)
    
    # 对于Wiki中的多维表格，node_token可能就是app_token
    # 但根据飞书API文档，Wiki中的多维表格需要通过节点信息获取app_token
    # 我们需要space_id才能调用get_wiki_node
    
    # 尝试方法1：直接使用node_token作为app_token（某些情况下可能有效）
    print("步骤1：尝试直接使用node_token作为app_token...")
    app_token = node_token
    
    # 如果用户知道space_id，可以尝试通过Wiki API获取
    # 这里我们先尝试直接访问，如果失败再提示用户提供space_id
    
    print()
    
    # 创建多维表格协作器
    print("步骤2：创建多维表格协作器...")
    collaborator = create_bitable_collaborator(
        app_id=APP_ID,
        app_secret=APP_SECRET,
        user_access_token=USER_ACCESS_TOKEN
    )
    print("[OK] 协作器创建成功")
    print()
    
    # 尝试获取表格结构
    print("步骤3：获取表格结构...")
    print(f"  使用 app_token: {app_token}")
    print(f"  使用 table_id: {table_id}")
    print()
    
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
    else:
        print("[!] 无法获取字段信息")
        print("  可能的原因：")
        print("  1. app_token不正确（Wiki中的多维表格需要特殊处理）")
        print("  2. table_id不正确")
        print("  3. 没有访问权限")
        print()
        return
    
    # 获取所有记录
    print("步骤4：获取所有记录...")
    records = collaborator.get_all_records(app_token, table_id)
    print(f"[OK] 总记录数: {len(records)}")
    print()
    
    if not records:
        print("[!] 数据表为空或无法获取记录")
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
            for field_id, value in list(fields_data.items())[:10]:  # 显示前10个字段
                field_info = field_map.get(field_id, {})
                field_name = field_info.get('field_name', field_id)
                formatted_value = collaborator._format_field_value(value, field_info.get('type', ''))
                if formatted_value:
                    print(f"  - {field_name}: {formatted_value}")
            print()

if __name__ == "__main__":
    main()

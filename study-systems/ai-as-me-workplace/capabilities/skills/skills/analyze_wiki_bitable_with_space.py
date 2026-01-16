# -*- coding: utf-8 -*-
"""
分析Wiki中的多维表格（需要space_id）

对于Wiki中的多维表格，需要通过Wiki API获取节点信息，得到app_token
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
    从Wiki URL中提取node_token和table_id
    
    格式：https://zyt.feishu.cn/wiki/{node_token}?table={table_id}
    """
    # 提取node_token（在/wiki/之后，?之前）
    match = re.search(r'/wiki/([^?]+)', url)
    node_token = match.group(1) if match else None
    
    # 提取table_id（在?table=之后）
    match = re.search(r'[?&]table=([^&]+)', url)
    table_id = match.group(1) if match else None
    
    return node_token, table_id

def get_app_token_from_wiki_node(api: FeishuAPI, space_id: str, node_token: str) -> Optional[str]:
    """
    通过Wiki节点获取多维表格的app_token
    
    对于Wiki中的多维表格，obj_type应该是'bitable'，obj_token就是app_token
    """
    result = api.get_wiki_node(space_id, node_token, use_user_token=True)
    
    if not result:
        print("  [!] API调用返回None")
        return None
    
    # 检查是否有错误码
    if result.get('code') is not None and result.get('code') != 0:
        print(f"  [!] API调用失败: code={result.get('code')}, msg={result.get('msg')}")
        print(f"  完整响应: {result}")
        return None
    
    # 获取节点信息（可能在result.node中，也可能直接在result中）
    node = result.get('node', result) if 'node' in result else result
    obj_type = node.get('obj_type', '')
    obj_token = node.get('obj_token', '')
    
    print(f"  节点信息: obj_type={obj_type}, obj_token={obj_token}")
    
    if obj_type == 'bitable':
        return obj_token
    else:
        print(f"  [!] 节点类型不是bitable，而是: {obj_type}")
    
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
    node_token, table_id = extract_from_wiki_url(wiki_url)
    
    if not node_token:
        print("[X] 无法从URL中提取node_token")
        return
    
    if not table_id:
        print("[X] 无法从URL中提取table_id")
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
    
    # 默认space_id（除非特别说明）
    space_id = os.getenv("FEISHU_SPACE_ID", "7353073903872868356")
    
    print(f"使用 space_id: {space_id}")
    print()
    
    # 通过Wiki节点获取app_token
    print("步骤1：通过Wiki节点获取app_token...")
    app_token = get_app_token_from_wiki_node(api, space_id, node_token)
    
    if not app_token:
        print("[X] 无法从Wiki节点获取app_token")
        print("  可能的原因：")
        print("  1. space_id不正确")
        print("  2. node_token不正确")
        print("  3. 节点类型不是bitable")
        print("  4. 没有访问权限")
        return
    
    print(f"[OK] 获取到app_token: {app_token}")
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
    
    # 先列出所有数据表，确认table_id
    print("步骤2.5：列出所有数据表...")
    tables_result = api.list_bitable_tables(app_token, use_user_token=True)
    
    if tables_result:
        # 处理不同的返回格式
        if 'code' in tables_result:
            # 标准格式：有code字段
            if tables_result.get('code') == 0:
                tables = tables_result.get('data', {}).get('items', [])
            else:
                print(f"  [!] 列出数据表失败: code={tables_result.get('code')}, msg={tables_result.get('msg')}")
                tables = []
        else:
            # 直接返回data格式
            if 'items' in tables_result:
                tables = tables_result.get('items', [])
            else:
                tables = []
    else:
        tables = []
    
    if tables:
        print(f"[OK] 找到 {len(tables)} 个数据表:")
        for i, table in enumerate(tables, 1):
            table_name = table.get('name', '未知')
            table_id_found = table.get('table_id', '未知')
            print(f"  {i}. {table_name} (ID: {table_id_found})")
        
        # 如果URL中的table_id不在列表中，使用第一个表
        table_ids = [t.get('table_id') for t in tables]
        if table_id not in table_ids:
            print()
            print(f"[!] URL中的table_id ({table_id}) 不在数据表列表中")
            print(f"[!] 将使用第一个数据表: {tables[0].get('name')} (ID: {tables[0].get('table_id')})")
            table_id = tables[0].get('table_id')
        else:
            print(f"[OK] 使用URL中的table_id: {table_id}")
        print()
    else:
        print("[!] 无法列出数据表，继续使用URL中的table_id")
        print()
    
    # 获取表格结构
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
        return
    
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
            for field_id, value in list(fields_data.items())[:10]:  # 显示前10个字段
                field_info = field_map.get(field_id, {})
                field_name = field_info.get('field_name', field_id)
                formatted_value = collaborator._format_field_value(value, field_info.get('type', ''))
                if formatted_value:
                    print(f"  - {field_name}: {formatted_value}")
            print()

if __name__ == "__main__":
    main()

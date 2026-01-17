# -*- coding: utf-8 -*-
"""
飞书资源配置查看工具

快速查看统一配置文件中的所有资源
"""

import sys
import os
from pathlib import Path

# 修复Windows控制台编码问题
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from feishu_config_loader import FeishuConfigLoader


def print_detailed_info(loader: FeishuConfigLoader):
    """打印详细信息"""
    print("=" * 80)
    print("飞书资源配置详细信息")
    print("=" * 80)
    print()
    
    # 云文档
    documents = loader.get_documents()
    print(f"📄 云文档 ({len(documents)} 个)")
    print("-" * 80)
    for doc in documents:
        print(f"  ID: {doc.get('id', 'N/A')}")
        print(f"  名称: {doc.get('name', 'N/A')}")
        print(f"  Node Token: {doc.get('node_token', 'N/A')}")
        print(f"  URL: {doc.get('url', 'N/A')}")
        print(f"  分类: {doc.get('category', '未分类')}")
        print(f"  缓存文件: {doc.get('cache_file', 'N/A')}")
        print(f"  同步间隔: {doc.get('sync_interval_hours', 24)} 小时")
        print(f"  状态: {'启用' if doc.get('enabled', True) else '禁用'}")
        print(f"  描述: {doc.get('description', '无')}")
        print()
    
    # 多维表格
    bitables = loader.get_bitables()
    print(f"📊 多维表格 ({len(bitables)} 个)")
    print("-" * 80)
    for bitable in bitables:
        print(f"  ID: {bitable.get('id', 'N/A')}")
        print(f"  名称: {bitable.get('name', 'N/A')}")
        if bitable.get('node_token'):
            print(f"  Node Token: {bitable.get('node_token', 'N/A')}")
        if bitable.get('app_token'):
            print(f"  App Token: {bitable.get('app_token', 'N/A')}")
        print(f"  URL: {bitable.get('url', 'N/A')}")
        print(f"  分类: {bitable.get('category', '未分类')}")
        print(f"  缓存文件: {bitable.get('cache_file', 'N/A')}")
        print(f"  同步间隔: {bitable.get('sync_interval_hours', 24)} 小时")
        print(f"  状态: {'启用' if bitable.get('enabled', True) else '禁用'}")
        print(f"  描述: {bitable.get('description', '无')}")
        if bitable.get('note'):
            print(f"  备注: {bitable.get('note')}")
        print()
    
    # 在线表格
    spreadsheets = loader.get_spreadsheets()
    print(f"📈 在线表格 ({len(spreadsheets)} 个)")
    print("-" * 80)
    for spreadsheet in spreadsheets:
        print(f"  ID: {spreadsheet.get('id', 'N/A')}")
        print(f"  名称: {spreadsheet.get('name', 'N/A')}")
        print(f"  Node Token: {spreadsheet.get('node_token', 'N/A')}")
        print(f"  URL: {spreadsheet.get('url', 'N/A')}")
        print(f"  分类: {spreadsheet.get('category', '未分类')}")
        print(f"  缓存文件: {spreadsheet.get('cache_file', 'N/A')}")
        print(f"  同步间隔: {spreadsheet.get('sync_interval_hours', 24)} 小时")
        print(f"  状态: {'启用' if spreadsheet.get('enabled', True) else '禁用'}")
        print(f"  描述: {spreadsheet.get('description', '无')}")
        print()
    
    print("=" * 80)


def print_by_category(loader: FeishuConfigLoader):
    """按分类打印资源"""
    print("=" * 80)
    print("按分类查看资源")
    print("=" * 80)
    print()
    
    all_resources = loader.list_all_resources()
    categories = set()
    
    # 收集所有分类
    for resource_type, items in all_resources.items():
        for item in items:
            category = item.get('category', '未分类')
            categories.add(category)
    
    # 按分类打印
    for category in sorted(categories):
        print(f"📁 {category}")
        print("-" * 80)
        
        for resource_type, items in all_resources.items():
            type_name = {
                'documents': '📄 云文档',
                'bitables': '📊 多维表格',
                'spreadsheets': '📈 在线表格'
            }.get(resource_type, resource_type)
            
            matching_items = [item for item in items if item.get('category') == category]
            if matching_items:
                print(f"  {type_name}:")
                for item in matching_items:
                    status = "✓" if item.get('enabled', True) else "✗"
                    print(f"    {status} [{item.get('id', 'N/A')}] {item.get('name', 'N/A')}")
        
        print()


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='查看飞书资源配置')
    parser.add_argument('--detailed', '-d', action='store_true', help='显示详细信息')
    parser.add_argument('--category', '-c', action='store_true', help='按分类显示')
    parser.add_argument('--id', type=str, help='查看指定ID的资源')
    
    args = parser.parse_args()
    
    loader = FeishuConfigLoader()
    
    if args.id:
        # 查看指定ID的资源
        resource = loader.get_resource_by_id(args.id)
        if resource:
            print("=" * 80)
            print(f"资源详情: {args.id}")
            print("=" * 80)
            print()
            for key, value in resource.items():
                print(f"  {key}: {value}")
            print()
            print("=" * 80)
        else:
            print(f"[!] 未找到ID为 '{args.id}' 的资源")
    elif args.detailed:
        # 显示详细信息
        print_detailed_info(loader)
    elif args.category:
        # 按分类显示
        print_by_category(loader)
    else:
        # 显示摘要
        loader.print_summary()


if __name__ == "__main__":
    main()

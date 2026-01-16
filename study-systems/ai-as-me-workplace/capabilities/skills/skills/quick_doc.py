# -*- coding: utf-8 -*-
"""
快速文档协作脚本

提供命令行接口，快速创建、更新文档
"""

import sys
import os
import argparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from feishu_doc_collaborator import create_doc_collaborator

# 默认配置
DEFAULT_APP_ID = "cli_a9c92ca516f99bd9"
DEFAULT_APP_SECRET = "zlOKnyZkSuSUSr0WlAl6qbh5Qw4eM6wC"
DEFAULT_SPACE_ID = "7353073903872868356"
DEFAULT_USER_TOKEN = os.getenv("FEISHU_USER_ACCESS_TOKEN", "u-4tBMNLQZ15Oqb0cGVm.7W.k1n31w4koprGGymw282HUW")

def cmd_create(args):
    """创建或查找文档"""
    collaborator = create_doc_collaborator(
        app_id=args.app_id,
        app_secret=args.app_secret,
        user_access_token=args.token,
        space_id=args.space_id
    )
    
    doc_info = collaborator.create_or_find_doc(
        doc_title=args.title,
        parent_node_token=args.parent,
        auto_create=not args.no_create
    )
    
    if doc_info:
        print(f"节点token: {doc_info['node_token']}")
        print(f"文档ID: {doc_info['document_id']}")
        print(f"文档链接: {doc_info['doc_url']}")
        print()
        print(f"本地Markdown文件: {collaborator.get_local_md_path(args.title)}")
    else:
        print("[X] 无法创建或查找文档")

def cmd_sync_to(args):
    """同步Markdown到飞书"""
    collaborator = create_doc_collaborator(
        app_id=args.app_id,
        app_secret=args.app_secret,
        user_access_token=args.token,
        space_id=args.space_id
    )
    
    success = collaborator.sync_to_feishu(
        node_token=args.node_token,
        md_file_path=args.md_file,
        doc_title=args.title,
        clear_first=not args.append
    )
    
    if success:
        print("[OK] 同步成功")
    else:
        print("[X] 同步失败")

def cmd_sync_from(args):
    """从飞书同步到Markdown"""
    collaborator = create_doc_collaborator(
        app_id=args.app_id,
        app_secret=args.app_secret,
        user_access_token=args.token,
        space_id=args.space_id
    )
    
    success = collaborator.sync_from_feishu(
        node_token=args.node_token,
        md_file_path=args.md_file,
        doc_title=args.title
    )
    
    if success:
        print("[OK] 同步成功")
    else:
        print("[X] 同步失败")

def main():
    parser = argparse.ArgumentParser(description='飞书文档协作工具')
    parser.add_argument('--app-id', default=DEFAULT_APP_ID, help='应用ID')
    parser.add_argument('--app-secret', default=DEFAULT_APP_SECRET, help='应用密钥')
    parser.add_argument('--token', default=DEFAULT_USER_TOKEN, help='用户身份凭证')
    parser.add_argument('--space-id', default=DEFAULT_SPACE_ID, help='知识库ID')
    
    subparsers = parser.add_subparsers(dest='command', help='命令')
    
    # 创建文档命令
    create_parser = subparsers.add_parser('create', help='创建或查找文档')
    create_parser.add_argument('title', help='文档标题')
    create_parser.add_argument('--parent', help='父节点token')
    create_parser.add_argument('--no-create', action='store_true', help='如果不存在，不自动创建')
    create_parser.set_defaults(func=cmd_create)
    
    # 同步到飞书命令
    sync_to_parser = subparsers.add_parser('sync-to', help='同步Markdown到飞书')
    sync_to_parser.add_argument('node_token', help='文档节点token')
    sync_to_parser.add_argument('--md-file', help='Markdown文件路径')
    sync_to_parser.add_argument('--title', help='文档标题（用于自动查找Markdown文件）')
    sync_to_parser.add_argument('--append', action='store_true', help='追加模式（不清空现有内容）')
    sync_to_parser.set_defaults(func=cmd_sync_to)
    
    # 从飞书同步命令
    sync_from_parser = subparsers.add_parser('sync-from', help='从飞书同步到Markdown')
    sync_from_parser.add_argument('node_token', help='文档节点token')
    sync_from_parser.add_argument('--md-file', help='Markdown文件保存路径')
    sync_from_parser.add_argument('--title', help='文档标题（用于自动确定Markdown文件路径）')
    sync_from_parser.set_defaults(func=cmd_sync_from)
    
    args = parser.parse_args()
    
    if args.command:
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()

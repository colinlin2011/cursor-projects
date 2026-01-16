# -*- coding: utf-8 -*-
"""
文档协作器使用示例

展示如何使用FeishuDocCollaborator进行文档协作
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from feishu_doc_collaborator import create_doc_collaborator

# 配置信息
APP_ID = "cli_a9c92ca516f99bd9"
APP_SECRET = "zlOKnyZkSuSUSr0WlAl6qbh5Qw4eM6wC"
USER_ACCESS_TOKEN = os.getenv("FEISHU_USER_ACCESS_TOKEN", "u-4tBMNLQZ15Oqb0cGVm.7W.k1n31w4koprGGymw282HUW")
SPACE_ID = "7353073903872868356"

def example_1_create_or_find_doc():
    """示例1：创建或查找文档"""
    print("=" * 60)
    print("示例1：创建或查找文档")
    print("=" * 60)
    print()
    
    # 创建协作器
    collaborator = create_doc_collaborator(
        app_id=APP_ID,
        app_secret=APP_SECRET,
        user_access_token=USER_ACCESS_TOKEN,
        space_id=SPACE_ID
    )
    
    # 创建或查找文档
    doc_info = collaborator.create_or_find_doc(
        doc_title="测试文档",
        parent_node_token="V7FXwKKdLiEus3kU9oMcgLwGnpe",  # 可选
        auto_create=True
    )
    
    if doc_info:
        print(f"文档节点token: {doc_info['node_token']}")
        print(f"文档ID: {doc_info['document_id']}")
        print(f"文档链接: {doc_info['doc_url']}")
        return doc_info
    
    return None

def example_2_sync_md_to_feishu():
    """示例2：同步本地Markdown到飞书"""
    print("=" * 60)
    print("示例2：同步本地Markdown到飞书")
    print("=" * 60)
    print()
    
    collaborator = create_doc_collaborator(
        app_id=APP_ID,
        app_secret=APP_SECRET,
        user_access_token=USER_ACCESS_TOKEN,
        space_id=SPACE_ID
    )
    
    # 方式1：指定节点token和Markdown文件路径
    success = collaborator.sync_to_feishu(
        node_token="DrFAwvNyAi21cJkQj11cUdRZnPh",
        md_file_path="work/fsc-doc/舱驾一体域控的FSC文档.md",
        clear_first=True
    )
    
    # 方式2：指定节点token和文档标题（自动查找Markdown文件）
    # success = collaborator.sync_to_feishu(
    #     node_token="DrFAwvNyAi21cJkQj11cUdRZnPh",
    #     doc_title="舱驾一体域控的FSC文档",
    #     clear_first=True
    # )
    
    if success:
        print("[OK] 同步成功")
    else:
        print("[X] 同步失败")

def example_3_sync_from_feishu():
    """示例3：从飞书同步到本地Markdown"""
    print("=" * 60)
    print("示例3：从飞书同步到本地Markdown")
    print("=" * 60)
    print()
    
    collaborator = create_doc_collaborator(
        app_id=APP_ID,
        app_secret=APP_SECRET,
        user_access_token=USER_ACCESS_TOKEN,
        space_id=SPACE_ID
    )
    
    # 从飞书读取内容并保存为本地Markdown
    success = collaborator.sync_from_feishu(
        node_token="DrFAwvNyAi21cJkQj11cUdRZnPh",
        doc_title="舱驾一体域控的FSC文档"
    )
    
    if success:
        print("[OK] 同步成功")
    else:
        print("[X] 同步失败")

def example_4_add_content():
    """示例4：直接添加内容到文档"""
    print("=" * 60)
    print("示例4：直接添加内容到文档")
    print("=" * 60)
    print()
    
    collaborator = create_doc_collaborator(
        app_id=APP_ID,
        app_secret=APP_SECRET,
        user_access_token=USER_ACCESS_TOKEN,
        space_id=SPACE_ID
    )
    
    # 添加标题
    collaborator.add_content(
        node_token="DrFAwvNyAi21cJkQj11cUdRZnPh",
        content="新增章节",
        content_type="heading2"
    )
    
    # 添加文本
    collaborator.add_content(
        node_token="DrFAwvNyAi21cJkQj11cUdRZnPh",
        content="这是新增的文本内容。",
        content_type="text"
    )
    
    # 添加列表项
    collaborator.add_content(
        node_token="DrFAwvNyAi21cJkQj11cUdRZnPh",
        content="列表项1",
        content_type="bullet"
    )

def example_5_complete_workflow():
    """示例5：完整工作流程"""
    print("=" * 60)
    print("示例5：完整工作流程")
    print("=" * 60)
    print()
    
    collaborator = create_doc_collaborator(
        app_id=APP_ID,
        app_secret=APP_SECRET,
        user_access_token=USER_ACCESS_TOKEN,
        space_id=SPACE_ID
    )
    
    # 步骤1：创建或查找文档
    doc_info = collaborator.create_or_find_doc(
        doc_title="新文档",
        parent_node_token="V7FXwKKdLiEus3kU9oMcgLwGnpe",
        auto_create=True
    )
    
    if not doc_info:
        print("[X] 无法创建或查找文档")
        return
    
    node_token = doc_info['node_token']
    doc_title = doc_info['title']
    
    # 步骤2：从飞书读取到本地（如果文档已有内容）
    collaborator.sync_from_feishu(
        node_token=node_token,
        doc_title=doc_title
    )
    
    # 步骤3：在本地Markdown文件中编辑（手动操作）
    md_path = collaborator.get_local_md_path(doc_title)
    print(f"请在本地编辑Markdown文件: {md_path}")
    print("编辑完成后，运行步骤4同步到飞书")
    
    # 步骤4：同步到飞书
    # collaborator.sync_to_feishu(
    #     node_token=node_token,
    #     doc_title=doc_title,
    #     clear_first=True
    # )

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        example_num = sys.argv[1]
        if example_num == "1":
            example_1_create_or_find_doc()
        elif example_num == "2":
            example_2_sync_md_to_feishu()
        elif example_num == "3":
            example_3_sync_from_feishu()
        elif example_num == "4":
            example_4_add_content()
        elif example_num == "5":
            example_5_complete_workflow()
        else:
            print("用法: python doc_collaborator_example.py [1|2|3|4|5]")
    else:
        print("文档协作器使用示例")
        print()
        print("运行示例：")
        print("  python doc_collaborator_example.py 1  # 创建或查找文档")
        print("  python doc_collaborator_example.py 2  # 同步Markdown到飞书")
        print("  python doc_collaborator_example.py 3  # 从飞书同步到Markdown")
        print("  python doc_collaborator_example.py 4  # 直接添加内容")
        print("  python doc_collaborator_example.py 5  # 完整工作流程")

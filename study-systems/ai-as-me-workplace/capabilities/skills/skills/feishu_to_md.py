# -*- coding: utf-8 -*-
"""
飞书文档到Markdown同步工具

支持从飞书文档读取内容并保存为本地Markdown文件
"""

import sys
import os
from typing import Optional, Dict, List
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from feishu_api_wrapper import FeishuAPI

# 配置信息
APP_ID = "cli_a9c92ca516f99bd9"
APP_SECRET = "zlOKnyZkSuSUSr0WlAl6qbh5Qw4eM6wC"
SPACE_ID = "7353073903872868356"
NODE_TOKEN = "DrFAwvNyAi21cJkQj11cUdRZnPh"

USER_ACCESS_TOKEN = os.getenv("FEISHU_USER_ACCESS_TOKEN", "u-4tBMNLQZ15Oqb0cGVm.7W.k1n31w4koprGGymw282HUW")
MD_FILE_PATH = "work/fsc-doc/舱驾一体域控的FSC文档.md"

def extract_text_from_block(block: Dict) -> str:
    """从块中提取文本内容"""
    block_type = block.get('block_type', 0)
    
    # 标题块
    if block_type in [3, 4, 5, 6, 7, 8, 9, 10, 11]:
        heading_fields = {
            3: "heading1",
            4: "heading2",
            5: "heading3",
            6: "heading4",
            7: "heading5",
            8: "heading6",
            9: "heading7",
            10: "heading8",
            11: "heading9"
        }
        field_name = heading_fields.get(block_type, "heading1")
        heading_data = block.get(field_name, {})
        elements = heading_data.get('elements', [])
        
        text_parts = []
        for element in elements:
            if 'text_run' in element:
                text_parts.append(element['text_run'].get('content', ''))
        
        return ''.join(text_parts)
    
    # 文本块
    elif block_type == 2:
        text_data = block.get('text', {})
        elements = text_data.get('elements', [])
        
        text_parts = []
        for element in elements:
            if 'text_run' in element:
                text_parts.append(element['text_run'].get('content', ''))
        
        return ''.join(text_parts)
    
    # 无序列表
    elif block_type == 12:
        bullet_data = block.get('bullet', {})
        elements = bullet_data.get('elements', [])
        
        text_parts = []
        for element in elements:
            if 'text_run' in element:
                text_parts.append(element['text_run'].get('content', ''))
        
        return '- ' + ''.join(text_parts)
    
    # 有序列表
    elif block_type == 13:
        ordered_data = block.get('ordered', {})
        elements = ordered_data.get('elements', [])
        
        text_parts = []
        for element in elements:
            if 'text_run' in element:
                text_parts.append(element['text_run'].get('content', ''))
        
        return '1. ' + ''.join(text_parts)
    
    return ""

def blocks_to_markdown(blocks: List[Dict]) -> str:
    """将块列表转换为Markdown格式"""
    md_lines = []
    
    for block in blocks:
        block_type = block.get('block_type', 0)
        text = extract_text_from_block(block)
        
        if not text:
            continue
        
        # 标题
        if block_type == 3:  # heading1
            md_lines.append(f"# {text}")
        elif block_type == 4:  # heading2
            md_lines.append(f"## {text}")
        elif block_type == 5:  # heading3
            md_lines.append(f"### {text}")
        elif block_type == 6:  # heading4
            md_lines.append(f"#### {text}")
        elif block_type == 7:  # heading5
            md_lines.append(f"##### {text}")
        # 列表（已经包含-或1.前缀）
        elif block_type in [12, 13]:
            md_lines.append(text)
        # 文本
        else:
            md_lines.append(text)
        
        md_lines.append("")  # 添加空行
    
    return '\n'.join(md_lines)

def get_document_id_from_node(api: FeishuAPI, space_id: str, node_token: str) -> Optional[str]:
    """从节点获取document_id"""
    result = api.get_wiki_node(space_id, node_token, use_user_token=True)
    
    if result:
        node = result.get('node', result) if 'node' in result else result
        obj_token = node.get('obj_token')
        obj_type = node.get('obj_type')
        
        if obj_type == 'docx' and obj_token:
            return obj_token
    
    return None

def fetch_feishu_to_md(api: FeishuAPI, document_id: str) -> str:
    """从飞书文档获取内容并转换为Markdown"""
    print("  获取文档所有块...")
    
    all_blocks = []
    page_token = None
    
    while True:
        blocks = api.get_document_blocks(
            document_id=document_id,
            page_size=500,
            page_token=page_token,
            use_user_token=True
        )
        
        if not blocks or blocks.get('code') != 0:
            break
        
        items = blocks.get('data', {}).get('items', [])
        all_blocks.extend(items)
        
        has_more = blocks.get('data', {}).get('has_more', False)
        if not has_more:
            break
        
        page_token = blocks.get('data', {}).get('page_token')
    
    print(f"  [OK] 获取到 {len(all_blocks)} 个块")
    
    # 跳过根节点（Page块）
    if all_blocks and all_blocks[0].get('block_type') == 1:
        all_blocks = all_blocks[1:]
    
    # 转换为Markdown
    print("  转换为Markdown格式...")
    md_content = blocks_to_markdown(all_blocks)
    
    return md_content

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    
    print("=" * 60)
    print("飞书文档到Markdown同步工具")
    print("=" * 60)
    print()
    
    if not USER_ACCESS_TOKEN:
        print("[X] 错误：未设置USER_ACCESS_TOKEN")
        return
    
    # 初始化API
    api = FeishuAPI(
        plugin_id="",
        plugin_secret="",
        app_id=APP_ID,
        app_secret=APP_SECRET
    )
    api.set_user_access_token(USER_ACCESS_TOKEN)
    
    # 获取项目根目录
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent.parent
    md_file_path = project_root / MD_FILE_PATH
    
    print(f"飞书文档节点: {NODE_TOKEN}")
    print(f"Markdown文件: {md_file_path}")
    print()
    
    # 获取document_id
    print("步骤1：获取文档ID...")
    document_id = get_document_id_from_node(api, SPACE_ID, NODE_TOKEN)
    
    if not document_id:
        print("[X] 无法获取document_id")
        return
    
    print(f"[OK] 文档ID: {document_id}")
    print()
    
    # 获取内容
    print("步骤2：从飞书文档获取内容...")
    md_content = fetch_feishu_to_md(api, document_id)
    
    if not md_content:
        print("[X] 无法获取文档内容")
        return
    
    print()
    
    # 保存到Markdown文件
    print("步骤3：保存到Markdown文件...")
    
    # 确保目录存在
    md_file_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(md_file_path, 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    print(f"[OK] 已保存到: {md_file_path}")
    print()
    print("=" * 60)
    print("[OK] 同步完成！")
    print("=" * 60)
    print()
    print("提示：")
    print("1. 可以在本地Markdown文件中编辑内容")
    print("2. 编辑完成后，运行 sync_md_to_feishu.py 同步回飞书")

if __name__ == "__main__":
    main()

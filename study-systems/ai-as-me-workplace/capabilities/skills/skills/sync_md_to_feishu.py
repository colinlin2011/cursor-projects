# -*- coding: utf-8 -*-
"""
Markdown到飞书文档同步工具

支持将本地Markdown文件同步到飞书文档，实现本地编辑、云端同步的工作流程
"""

import sys
import os
import re
from typing import Optional, Dict, List
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from feishu_api_wrapper import FeishuAPI

# 配置信息
APP_ID = "cli_a9c92ca516f99bd9"
APP_SECRET = "zlOKnyZkSuSUSr0WlAl6qbh5Qw4eM6wC"
SPACE_ID = "7353073903872868356"
NODE_TOKEN = "DrFAwvNyAi21cJkQj11cUdRZnPh"  # 飞书文档节点token

USER_ACCESS_TOKEN = os.getenv("FEISHU_USER_ACCESS_TOKEN", "u-4tBMNLQZ15Oqb0cGVm.7W.k1n31w4koprGGymw282HUW")

# Markdown文件路径（相对于项目根目录）
MD_FILE_PATH = "work/fsc-doc/舱驾一体域控的FSC文档.md"

def parse_markdown_to_blocks(md_content: str) -> List[Dict]:
    """
    将Markdown内容解析为飞书文档块
    
    支持的Markdown元素：
    - # 标题1 -> heading1 (block_type=3)
    - ## 标题2 -> heading2 (block_type=4)
    - ### 标题3 -> heading3 (block_type=5)
    - #### 标题4 -> heading4 (block_type=6)
    - 普通文本 -> text (block_type=2)
    - - 列表项 -> bullet (block_type=12)
    - **粗体** -> text with bold
    """
    blocks = []
    lines = md_content.split('\n')
    
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        
        # 跳过空行
        if not line:
            i += 1
            continue
        
        # 标题
        if line.startswith('#'):
            level = len(line) - len(line.lstrip('#'))
            title = line.lstrip('#').strip()
            
            # 标题级别映射：1->3, 2->4, 3->5, 4->6
            block_type = level + 2
            heading_fields = {
                3: "heading1",
                4: "heading2",
                5: "heading3",
                6: "heading4",
                7: "heading5"
            }
            field_name = heading_fields.get(block_type, "heading2")
            
            blocks.append({
                "block_type": block_type,
                field_name: {
                    "elements": [
                        {
                            "text_run": {
                                "content": title
                            }
                        }
                    ]
                }
            })
        
        # 无序列表
        elif line.startswith('- ') or line.startswith('* '):
            content = line[2:].strip()
            blocks.append({
                "block_type": 12,
                "bullet": {
                    "elements": [
                        {
                            "text_run": {
                                "content": content
                            }
                        }
                    ]
                }
            })
        
        # 有序列表（暂时按文本处理）
        elif re.match(r'^\d+\.\s', line):
            content = re.sub(r'^\d+\.\s', '', line)
            blocks.append({
                "block_type": 2,
                "text": {
                    "elements": [
                        {
                            "text_run": {
                                "content": content
                            }
                        }
                    ]
                }
            })
        
        # 普通文本
        else:
            # 处理粗体等格式（简化处理，只提取文本）
            content = re.sub(r'\*\*(.*?)\*\*', r'\1', line)  # 移除粗体标记
            content = re.sub(r'_(.*?)_', r'\1', content)  # 移除斜体标记
            
            if content.strip():
                blocks.append({
                    "block_type": 2,
                    "text": {
                        "elements": [
                            {
                                "text_run": {
                                    "content": content
                                }
                            }
                        ]
                    }
                })
        
        i += 1
    
    return blocks

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

def clear_document_content(api: FeishuAPI, document_id: str):
    """清空文档内容（保留根节点）"""
    print("  清空现有内容...")
    
    # 获取所有块
    blocks = api.get_document_blocks(
        document_id=document_id,
        page_size=500,
        use_user_token=True
    )
    
    if blocks and blocks.get('code') == 0:
        items = blocks.get('data', {}).get('items', [])
        
        # 删除除根节点外的所有块
        if len(items) > 1:
            # 获取根节点ID（第一个块）
            root_block_id = items[0].get('block_id')
            
            # 删除所有子块
            # 注意：需要从后往前删除，避免索引变化
            child_count = len(items) - 1
            if child_count > 0:
                result = api.delete_blocks(
                    document_id=document_id,
                    block_id=root_block_id,
                    start_index=0,
                    end_index=child_count,
                    use_user_token=True
                )
                
                if result:
                    print(f"    [OK] 已删除 {child_count} 个块")
                else:
                    print(f"    [X] 删除失败")

def sync_md_to_feishu(md_file_path: str, api: FeishuAPI, document_id: str, clear_first: bool = True):
    """将Markdown文件同步到飞书文档"""
    import time
    
    # 读取Markdown文件
    print(f"步骤1：读取Markdown文件...")
    md_path = Path(md_file_path)
    
    if not md_path.exists():
        print(f"[X] 文件不存在: {md_file_path}")
        return False
    
    with open(md_path, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    print(f"[OK] 文件读取成功: {md_path.name}")
    print()
    
    # 解析Markdown为块
    print("步骤2：解析Markdown内容...")
    blocks = parse_markdown_to_blocks(md_content)
    print(f"[OK] 解析完成，共 {len(blocks)} 个块")
    print()
    
    # 清空现有内容（可选）
    if clear_first:
        print("步骤3：清空现有内容...")
        clear_document_content(api, document_id)
        print()
    
    # 添加新内容
    print("步骤4：添加内容到飞书文档...")
    
    # 分批添加（每次最多50个块，避免单次请求过大）
    batch_size = 50
    total_batches = (len(blocks) + batch_size - 1) // batch_size
    
    for i in range(0, len(blocks), batch_size):
        batch = blocks[i:i+batch_size]
        batch_num = i // batch_size + 1
        
        print(f"  添加批次 {batch_num}/{total_batches} ({len(batch)} 个块)...")
        
        result = api.create_block(
            document_id=document_id,
            block_id=document_id,
            children=batch,
            document_revision_id=-1,
            use_user_token=True
        )
        
        if result:
            print(f"    [OK] 批次 {batch_num} 添加成功")
        else:
            print(f"    [X] 批次 {batch_num} 添加失败")
        
        time.sleep(0.5)  # 避免频率限制
    
    print()
    print("[OK] 同步完成！")
    return True

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    
    print("=" * 60)
    print("Markdown到飞书文档同步工具")
    print("=" * 60)
    print()
    
    if not USER_ACCESS_TOKEN:
        print("[X] 错误：未设置USER_ACCESS_TOKEN")
        print()
        print("请设置环境变量：")
        print('  $env:FEISHU_USER_ACCESS_TOKEN="your_token"')
        return
    
    # 初始化API
    api = FeishuAPI(
        plugin_id="",
        plugin_secret="",
        app_id=APP_ID,
        app_secret=APP_SECRET
    )
    api.set_user_access_token(USER_ACCESS_TOKEN)
    
    # 获取项目根目录（从capabilities/skills/skills/向上3级到项目根）
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent.parent  # capabilities/skills/skills -> capabilities/skills -> capabilities -> project_root
    md_file_path = project_root / MD_FILE_PATH
    
    print(f"Markdown文件: {md_file_path}")
    print(f"飞书文档节点: {NODE_TOKEN}")
    print()
    
    # 获取document_id
    print("步骤1：获取文档ID...")
    document_id = get_document_id_from_node(api, SPACE_ID, NODE_TOKEN)
    
    if not document_id:
        print("[X] 无法获取document_id")
        return
    
    print(f"[OK] 文档ID: {document_id}")
    print()
    
    # 询问是否清空现有内容
    clear_first = True
    if clear_first:
        print("注意：将清空文档现有内容，然后同步Markdown内容")
        print()
    
    # 同步
    success = sync_md_to_feishu(str(md_file_path), api, document_id, clear_first)
    
    if success:
        print()
        print("=" * 60)
        print("[OK] 同步完成！")
        print("=" * 60)
        print()
        print(f"文档链接: https://bytedance.larkoffice.com/wiki/{SPACE_ID}/{NODE_TOKEN}")
        print()
        print("提示：")
        print("1. 可以在本地Markdown文件中继续编辑")
        print("2. 编辑完成后，重新运行此脚本同步到飞书")
        print("3. 支持标题、文本、列表等基本Markdown元素")

if __name__ == "__main__":
    main()

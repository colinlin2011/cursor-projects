# -*- coding: utf-8 -*-
"""
飞书表格辅助工具

用于创建飞书原生表格
"""

import uuid
from typing import List, Dict, Any


def generate_table_block_id() -> str:
    """生成表格块ID"""
    return f"table_{uuid.uuid4().hex[:16]}"


def generate_table_cell_id() -> str:
    """生成表格单元格ID"""
    return f"cell_{uuid.uuid4().hex[:16]}"


def create_table_structure(
    headers: List[str],
    rows: List[List[str]],
    max_rows: int = 50
) -> Dict[str, Any]:
    """
    创建表格结构（用于create_descendant API）
    
    Args:
        headers: 表头列表
        rows: 数据行列表
        max_rows: 最大行数（限制表格大小）
        
    Returns:
        表格结构字典，包含children_id和descendants
    """
    if not headers or not rows:
        return None
    
    # 限制行数
    rows = rows[:max_rows]
    
    # 表格尺寸
    row_size = len(rows) + 1  # 表头 + 数据行
    column_size = len(headers)
    
    # 生成表格块ID
    table_id = generate_table_block_id()
    
    # 生成所有单元格ID（按行x列顺序）
    all_cell_ids = []
    for i in range(row_size):
        for j in range(column_size):
            all_cell_ids.append(generate_table_cell_id())
    
    # 构建descendants结构
    descendants = []
    
    # 1. 创建表格块
    descendants.append({
        "block_id": table_id,
        "block_type": 31,  # 表格块
        "table": {
            "property": {
                "row_size": row_size,
                "column_size": column_size,
                "header_row": True  # 第一行为表头
            }
        },
        "children": all_cell_ids
    })
    
    # 2. 创建单元格块和内容
    # 所有数据（表头 + 数据行）
    all_data = [headers] + rows
    
    for idx, cell_id in enumerate(all_cell_ids):
        row_idx = idx // column_size
        col_idx = idx % column_size
        
        # 获取单元格内容
        if row_idx < len(all_data) and col_idx < len(all_data[row_idx]):
            cell_content = str(all_data[row_idx][col_idx])
            # 清理内容
            cell_content = cell_content.replace("\n", " ").replace("\r", " ").strip()
            if len(cell_content) > 500:
                cell_content = cell_content[:500] + "..."
        else:
            cell_content = ""
        
        # 创建单元格内容块ID
        cell_child_id = f"{cell_id}_child"
        
        # 创建单元格块
        descendants.append({
            "block_id": cell_id,
            "block_type": 32,  # 表格单元格
            "table_cell": {},
            "children": [cell_child_id]
        })
        
        # 创建单元格内容（文本块）
        descendants.append({
            "block_id": cell_child_id,
            "block_type": 2,  # 文本块
            "text": {
                "elements": [{
                    "text_run": {
                        "content": cell_content
                    }
                }]
            },
            "children": []
        })
    
    return {
        "children_id": [table_id],
        "descendants": descendants
    }

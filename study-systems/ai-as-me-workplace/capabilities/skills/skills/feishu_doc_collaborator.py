# -*- coding: utf-8 -*-
"""
飞书文档协作器 - 通用文档协作能力

提供简洁的API，支持：
- 创建/查找文档
- 本地Markdown编辑
- Markdown与飞书文档双向同步
- 内容更新和管理
"""

import sys
import os
import re
import time
from typing import Optional, Dict, List
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from feishu_api_wrapper import FeishuAPI


class FeishuDocCollaborator:
    """
    飞书文档协作器
    
    提供统一的接口进行文档协作，支持本地Markdown编辑和飞书文档同步
    """
    
    def __init__(
        self,
        app_id: str,
        app_secret: str,
        user_access_token: str,
        space_id: str,
        work_dir: Optional[str] = None
    ):
        """
        初始化文档协作器
        
        Args:
            app_id: 飞书应用ID
            app_secret: 飞书应用密钥
            user_access_token: 用户身份凭证
            space_id: 知识库ID
            work_dir: 工作目录（用于存储本地Markdown文件），默认为项目根目录下的work目录
        """
        self.app_id = app_id
        self.app_secret = app_secret
        self.user_access_token = user_access_token
        self.space_id = space_id
        
        # 初始化API
        self.api = FeishuAPI(
            plugin_id="",
            plugin_secret="",
            app_id=app_id,
            app_secret=app_secret
        )
        self.api.set_user_access_token(user_access_token)
        
        # 设置工作目录
        if work_dir:
            self.work_dir = Path(work_dir)
        else:
            # 默认工作目录：项目根目录下的work目录
            script_dir = Path(__file__).parent
            project_root = script_dir.parent.parent.parent
            self.work_dir = project_root / "work"
        
        self.work_dir.mkdir(parents=True, exist_ok=True)
    
    def create_or_find_doc(
        self,
        doc_title: str,
        parent_node_token: Optional[str] = None,
        auto_create: bool = True
    ) -> Optional[Dict]:
        """
        创建或查找文档
        
        Args:
            doc_title: 文档标题
            parent_node_token: 父节点token（None表示根目录）
            auto_create: 如果文档不存在，是否自动创建
            
        Returns:
            文档信息字典，包含：
            - node_token: 节点token
            - document_id: 文档ID
            - title: 文档标题
            - doc_url: 文档链接
        """
        # 查找已存在的文档
        existing_doc = self._find_existing_doc(doc_title, parent_node_token)
        
        if existing_doc:
            print(f"[OK] 找到已存在的文档: {doc_title}")
            # 标记为已存在的文档
            existing_doc['is_existing'] = True
            return existing_doc
        
        # 如果不存在且允许自动创建
        if auto_create:
            print(f"[OK] 文档不存在，创建新文档: {doc_title}")
            return self._create_doc(doc_title, parent_node_token)
        else:
            print(f"[!] 文档不存在，且auto_create=False，未创建")
            return None
    
    def _find_existing_doc(
        self,
        doc_title: str,
        parent_node_token: Optional[str]
    ) -> Optional[Dict]:
        """查找已存在的文档"""
        result = self.api.list_wiki_nodes(
            space_id=self.space_id,
            parent_node_token=parent_node_token,
            page_size=50,
            use_user_token=True
        )
        
        if result:
            items = result.get('items', [])
            
            for item in items:
                title = item.get('title', '')
                obj_type = item.get('obj_type', '')
                
                if title == doc_title and obj_type == 'docx':
                    node_token = item.get('node_token')
                    obj_token = item.get('obj_token')
                    
                    return {
                        'node_token': node_token,
                        'document_id': obj_token,
                        'title': title,
                        'doc_url': f"https://zyt.feishu.cn/wiki/{node_token}"
                    }
        
        return None
    
    def _create_doc(
        self,
        doc_title: str,
        parent_node_token: Optional[str]
    ) -> Optional[Dict]:
        """创建新文档"""
        doc = self.api.create_wiki_doc(
            space_id=self.space_id,
            parent_node_token=parent_node_token,
            title=doc_title,
            use_user_token=True
        )
        
        if doc:
            node = doc.get('node', {})
            node_token = node.get('node_token')
            obj_token = node.get('obj_token')
            
            return {
                'node_token': node_token,
                'document_id': obj_token,
                'title': doc_title,
                'doc_url': f"https://zyt.feishu.cn/wiki/{node_token}"
            }
        
        return None
    
    def get_local_md_path(self, doc_title: str) -> Path:
        """获取本地Markdown文件路径"""
        # 创建doc子目录
        doc_dir = self.work_dir / "docs"
        doc_dir.mkdir(parents=True, exist_ok=True)
        
        # 文件名：文档标题.md
        safe_filename = re.sub(r'[<>:"/\\|?*]', '_', doc_title)  # 移除非法字符
        return doc_dir / f"{safe_filename}.md"
    
    def sync_to_feishu(
        self,
        node_token: str,
        md_file_path: Optional[str] = None,
        doc_title: Optional[str] = None,
        clear_first: bool = True
    ) -> bool:
        """
        将本地Markdown同步到飞书文档
        
        Args:
            node_token: 飞书文档节点token
            md_file_path: Markdown文件路径（如果为None，则根据doc_title自动查找）
            doc_title: 文档标题（用于自动查找Markdown文件）
            clear_first: 是否先清空飞书文档现有内容
            
        Returns:
            是否成功
        """
        # 确定Markdown文件路径
        if md_file_path:
            md_path = Path(md_file_path)
        elif doc_title:
            md_path = self.get_local_md_path(doc_title)
        else:
            print("[X] 错误：必须提供md_file_path或doc_title")
            return False
        
        if not md_path.exists():
            print(f"[X] 错误：Markdown文件不存在: {md_path}")
            return False
        
        # 获取document_id
        document_id = self._get_document_id_from_node(node_token)
        if not document_id:
            print("[X] 错误：无法获取document_id")
            return False
        
        # 读取Markdown
        with open(md_path, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        # 解析为块
        blocks = self._parse_markdown_to_blocks(md_content)
        
        # 清空现有内容（可选）
        if clear_first:
            self._clear_document_content(document_id)
        
        # 添加内容
        return self._add_blocks_to_document(document_id, blocks)
    
    def sync_from_feishu(
        self,
        node_token: str,
        md_file_path: Optional[str] = None,
        doc_title: Optional[str] = None
    ) -> bool:
        """
        从飞书文档读取内容并保存为本地Markdown
        
        Args:
            node_token: 飞书文档节点token
            md_file_path: Markdown文件保存路径（如果为None，则根据doc_title自动确定）
            doc_title: 文档标题（用于自动确定Markdown文件路径）
            
        Returns:
            是否成功
        """
        # 获取document_id
        document_id = self._get_document_id_from_node(node_token)
        if not document_id:
            print("[X] 错误：无法获取document_id")
            return False
        
        # 获取文档内容
        blocks = self._get_all_blocks(document_id)
        if not blocks:
            print("[X] 错误：无法获取文档内容")
            return False
        
        # 转换为Markdown
        md_content = self._blocks_to_markdown(blocks)
        
        # 确定保存路径
        if md_file_path:
            md_path = Path(md_file_path)
        elif doc_title:
            md_path = self.get_local_md_path(doc_title)
        else:
            print("[X] 错误：必须提供md_file_path或doc_title")
            return False
        
        # 确保目录存在
        md_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 保存
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        print(f"[OK] 已保存到: {md_path}")
        return True
    
    def _get_document_id_from_node(self, node_token: str) -> Optional[str]:
        """从节点获取document_id"""
        result = self.api.get_wiki_node(
            self.space_id,
            node_token,
            use_user_token=True
        )
        
        if result:
            # 处理不同的返回格式
            if 'code' in result and result.get('code') == 0:
                # 标准格式：有code字段且为0
                data = result.get('data', {})
                node = data.get('node', {})
            elif 'node' in result:
                # 直接包含node字段
                node = result.get('node', {})
            else:
                # 直接就是node数据
                node = result
            
            obj_token = node.get('obj_token')
            obj_type = node.get('obj_type')
            
            if obj_type == 'docx' and obj_token:
                return obj_token
        
        return None
    
    def _parse_markdown_to_blocks(self, md_content: str) -> List[Dict]:
        """将Markdown内容解析为飞书文档块"""
        blocks = []
        lines = md_content.split('\n')
        
        i = 0
        while i < len(lines):
            line = lines[i].rstrip()
            
            if not line:
                i += 1
                continue
            
            # 标题
            if line.startswith('#'):
                level = len(line) - len(line.lstrip('#'))
                title = line.lstrip('#').strip()
                block_type = level + 2
                heading_fields = {
                    3: "heading1", 4: "heading2", 5: "heading3",
                    6: "heading4", 7: "heading5"
                }
                field_name = heading_fields.get(block_type, "heading2")
                
                blocks.append({
                    "block_type": block_type,
                    field_name: {
                        "elements": [{"text_run": {"content": title}}]
                    }
                })
            
            # 无序列表
            elif line.startswith('- ') or line.startswith('* '):
                content = line[2:].strip()
                blocks.append({
                    "block_type": 12,
                    "bullet": {
                        "elements": [{"text_run": {"content": content}}]
                    }
                })
            
            # 有序列表
            elif re.match(r'^\d+\.\s', line):
                content = re.sub(r'^\d+\.\s', '', line)
                blocks.append({
                    "block_type": 2,
                    "text": {
                        "elements": [{"text_run": {"content": content}}]
                    }
                })
            
            # 普通文本
            else:
                content = re.sub(r'\*\*(.*?)\*\*', r'\1', line)
                content = re.sub(r'_(.*?)_', r'\1', content)
                
                if content.strip():
                    blocks.append({
                        "block_type": 2,
                        "text": {
                            "elements": [{"text_run": {"content": content}}]
                        }
                    })
            
            i += 1
        
        return blocks
    
    def _blocks_to_markdown(self, blocks: List[Dict]) -> str:
        """将块列表转换为Markdown格式"""
        md_lines = []
        
        for block in blocks:
            block_type = block.get('block_type', 0)
            text = self._extract_text_from_block(block)
            
            if not text:
                continue
            
            if block_type == 3:
                md_lines.append(f"# {text}")
            elif block_type == 4:
                md_lines.append(f"## {text}")
            elif block_type == 5:
                md_lines.append(f"### {text}")
            elif block_type == 6:
                md_lines.append(f"#### {text}")
            elif block_type == 7:
                md_lines.append(f"##### {text}")
            elif block_type in [12, 13]:
                md_lines.append(text)
            else:
                md_lines.append(text)
            
            md_lines.append("")
        
        return '\n'.join(md_lines)
    
    def _extract_text_from_block(self, block: Dict) -> str:
        """从块中提取文本内容"""
        block_type = block.get('block_type', 0)
        
        # 标题块
        if block_type in [3, 4, 5, 6, 7, 8, 9, 10, 11]:
            heading_fields = {
                3: "heading1", 4: "heading2", 5: "heading3",
                6: "heading4", 7: "heading5", 8: "heading6",
                9: "heading7", 10: "heading8", 11: "heading9"
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
    
    def _get_all_blocks(self, document_id: str) -> List[Dict]:
        """获取文档所有块"""
        all_blocks = []
        page_token = None
        
        while True:
            blocks = self.api.get_document_blocks(
                document_id=document_id,
                page_size=500,
                page_token=page_token,
                use_user_token=True
            )
            
            if not blocks:
                break
            
            # 处理不同的返回格式
            if isinstance(blocks, dict):
                # 检查是否有code字段（标准格式）
                if 'code' in blocks:
                    if blocks.get('code') != 0:
                        # 如果有错误码，输出错误信息
                        print(f"[!] 获取blocks失败: code={blocks.get('code')}, msg={blocks.get('msg')}")
                        break
                    # 标准格式：有code字段，数据在data中
                    data = blocks.get('data', {})
                    items = data.get('items', [])
                    has_more = data.get('has_more', False)
                    page_token = data.get('page_token')
                else:
                    # 直接返回data格式：没有code字段，直接包含items
                    items = blocks.get('items', [])
                    has_more = blocks.get('has_more', False)
                    page_token = blocks.get('page_token')
                
                all_blocks.extend(items)
                
                if not has_more:
                    break
            else:
                # 如果不是字典格式，直接使用
                break
        
        # 跳过根节点
        if all_blocks and all_blocks[0].get('block_type') == 1:
            all_blocks = all_blocks[1:]
        
        return all_blocks
    
    def _clear_document_content(self, document_id: str):
        """清空文档内容（保留根节点）"""
        blocks = self.api.get_document_blocks(
            document_id=document_id,
            page_size=500,
            use_user_token=True
        )
        
        if blocks and blocks.get('code') == 0:
            items = blocks.get('data', {}).get('items', [])
            
            if len(items) > 1:
                root_block_id = items[0].get('block_id')
                child_count = len(items) - 1
                
                if child_count > 0:
                    self.api.delete_blocks(
                        document_id=document_id,
                        block_id=root_block_id,
                        start_index=0,
                        end_index=child_count,
                        use_user_token=True
                    )
    
    def _add_blocks_to_document(self, document_id: str, blocks: List[Dict]) -> bool:
        """添加块到文档"""
        batch_size = 50
        total_batches = (len(blocks) + batch_size - 1) // batch_size
        
        for i in range(0, len(blocks), batch_size):
            batch = blocks[i:i+batch_size]
            batch_num = i // batch_size + 1
            
            result = self.api.create_block(
                document_id=document_id,
                block_id=document_id,
                children=batch,
                document_revision_id=-1,
                use_user_token=True
            )
            
            if not result:
                print(f"    [X] 批次 {batch_num} 添加失败")
                return False
            
            time.sleep(0.5)  # 避免频率限制
        
        return True
    
    def add_content(
        self,
        node_token: str,
        content: str,
        content_type: str = "text"
    ) -> bool:
        """
        向文档添加内容
        
        Args:
            node_token: 文档节点token
            content: 内容文本
            content_type: 内容类型（"text", "heading1", "heading2", "heading3", "bullet"）
            
        Returns:
            是否成功
        """
        document_id = self._get_document_id_from_node(node_token)
        if not document_id:
            return False
        
        # 根据类型创建块
        if content_type == "heading1":
            block = {
                "block_type": 3,
                "heading1": {"elements": [{"text_run": {"content": content}}]}
            }
        elif content_type == "heading2":
            block = {
                "block_type": 4,
                "heading2": {"elements": [{"text_run": {"content": content}}]}
            }
        elif content_type == "heading3":
            block = {
                "block_type": 5,
                "heading3": {"elements": [{"text_run": {"content": content}}]}
            }
        elif content_type == "bullet":
            block = {
                "block_type": 12,
                "bullet": {"elements": [{"text_run": {"content": content}}]}
            }
        else:  # text
            block = {
                "block_type": 2,
                "text": {"elements": [{"text_run": {"content": content}}]}
            }
        
        result = self.api.create_block(
            document_id=document_id,
            block_id=document_id,
            children=[block],
            document_revision_id=-1,
            use_user_token=True
        )
        
        return result is not None


# 便捷函数
def create_doc_collaborator(
    app_id: str,
    app_secret: str,
    user_access_token: str,
    space_id: str,
    work_dir: Optional[str] = None
) -> FeishuDocCollaborator:
    """
    创建文档协作器实例（便捷函数）
    
    Args:
        app_id: 飞书应用ID
        app_secret: 飞书应用密钥
        user_access_token: 用户身份凭证
        space_id: 知识库ID
        work_dir: 工作目录（可选）
        
    Returns:
        FeishuDocCollaborator实例
    """
    return FeishuDocCollaborator(
        app_id=app_id,
        app_secret=app_secret,
        user_access_token=user_access_token,
        space_id=space_id,
        work_dir=work_dir
    )

# -*- coding: utf-8 -*-
"""
故障定位指引读取模块

从飞书Wiki读取故障定位指引文档，解析结构化表格，建立Fault ID到指引信息的映射
"""

import sys
import os
import json
import re
from typing import Optional, Dict, List, Any
from pathlib import Path
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from feishu_api_wrapper import FeishuAPI
from feishu_doc_collaborator import FeishuDocCollaborator
from fault_diagnosis_config import (
    SPACE_ID, APP_ID, APP_SECRET,
    get_guide_docs, get_dynamic_user_access_token,
    GUIDE_CACHE_DIR
)

# 修复Windows控制台编码问题
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass


class FaultGuideReader:
    """故障定位指引读取器"""
    
    def __init__(self):
        """初始化读取器"""
        self.api = FeishuAPI(
            plugin_id="",
            plugin_secret="",
            app_id=APP_ID,
            app_secret=APP_SECRET
        )
        # 使用动态token（自动刷新）
        self.api.set_user_access_token(get_dynamic_user_access_token())
        
        self.doc_collaborator = FeishuDocCollaborator(
            app_id=APP_ID,
            app_secret=APP_SECRET,
            user_access_token=get_dynamic_user_access_token(),
            space_id=SPACE_ID
        )
        
        self.guide_cache = {}  # 内存缓存
        self.guide_mapping = {}  # Fault ID到指引的映射
    
    def _refresh_token_if_needed(self):
        """如果需要，刷新token"""
        new_token = get_dynamic_user_access_token()
        if new_token:
            self.api.set_user_access_token(new_token)
            # 更新doc_collaborator的token（如果支持）
            if hasattr(self.doc_collaborator, 'api') and hasattr(self.doc_collaborator.api, 'set_user_access_token'):
                self.doc_collaborator.api.set_user_access_token(new_token)
    
    def load_fault_guide(self, node_token: str, force_refresh: bool = False) -> Optional[Dict]:
        """
        加载故障定位指引文档
        
        Args:
            node_token: Wiki节点token
            force_refresh: 是否强制刷新
            
        Returns:
            指引文档内容
        """
        cache_file = GUIDE_CACHE_DIR / f"guide_{node_token}.json"
        
        # 检查缓存
        if not force_refresh and cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                    cache_time = cache_data.get('cache_time', 0)
                    # 缓存有效期24小时
                    if datetime.now().timestamp() - cache_time < 24 * 3600:
                        print(f"[OK] 从缓存加载指引文档: {node_token}")
                        return cache_data.get('content')
            except Exception as e:
                print(f"[!] 读取缓存失败: {e}")
        
        # 从Wiki读取文档
        print(f"从Wiki加载指引文档: {node_token}...")
        
        try:
            # 方法1：通过Wiki节点获取document_id
            document_id = self.doc_collaborator._get_document_id_from_node(node_token)
            
            # 方法2：如果方法1失败，尝试直接使用node_token作为document_id
            if not document_id:
                print(f"[!] 无法通过Wiki节点获取document_id，尝试直接使用node_token...")
                document_id = node_token
            
            # 获取文档内容
            blocks = self.doc_collaborator._get_all_blocks(document_id)
            if not blocks:
                print(f"[X] 无法获取文档内容")
                return None
            
            # 转换为Markdown
            doc_content = self.doc_collaborator._blocks_to_markdown(blocks)
            
            if doc_content:
                # 保存缓存
                cache_data = {
                    'cache_time': datetime.now().timestamp(),
                    'node_token': node_token,
                    'document_id': document_id,
                    'content': doc_content
                }
                with open(cache_file, 'w', encoding='utf-8') as f:
                    json.dump(cache_data, f, ensure_ascii=False, indent=2)
                
                print(f"[OK] 指引文档加载成功")
                return doc_content
            else:
                print(f"[X] 无法获取文档内容")
                return None
                
        except Exception as e:
            print(f"[X] 加载指引文档失败: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def parse_guide_structure(self, content: str) -> Dict[str, Any]:
        """
        解析指引文档结构，提取Fault ID映射
        
        Args:
            content: 文档内容（Markdown格式）
            
        Returns:
            解析后的指引结构
        """
        guide_structure = {
            'fault_id_mapping': {},  # Fault ID -> 指引信息
            'grep_patterns': {},  # Fault ID -> grep模式
            'analysis_points': {},  # Fault ID -> 分析要点
            'common_causes': {},  # Fault ID -> 常见原因
            'troubleshooting_steps': {},  # Fault ID -> 排查步骤
            'content': content  # 保存完整内容供AI分析使用
        }
        
        # 解析Markdown内容，查找表格
        lines = content.split('\n')
        current_table = []
        in_table = False
        
        for line in lines:
            # 检测表格开始（Markdown表格以|开头）
            if '|' in line and not in_table:
                in_table = True
                current_table = [line]
            elif in_table:
                if '|' in line:
                    current_table.append(line)
                else:
                    # 表格结束，解析表格
                    if len(current_table) > 2:  # 至少包含表头和分隔线
                        self._parse_table(current_table, guide_structure)
                    current_table = []
                    in_table = False
        
        # 处理最后一个表格
        if in_table and len(current_table) > 2:
            self._parse_table(current_table, guide_structure)
        
        # 如果没有找到表格，尝试从文本中提取Fault ID信息
        if not guide_structure['fault_id_mapping']:
            self._extract_from_text(content, guide_structure)
        
        return guide_structure
    
    def _parse_table(self, table_lines: List[str], guide_structure: Dict):
        """解析Markdown表格"""
        if len(table_lines) < 2:
            return
        
        # 解析表头
        header_line = table_lines[0]
        headers = [h.strip() for h in header_line.split('|')[1:-1]]  # 去掉首尾空元素
        
        # 查找Fault ID列索引
        fault_id_col = None
        for i, header in enumerate(headers):
            if 'fault' in header.lower() and 'id' in header.lower():
                fault_id_col = i
                break
        
        if fault_id_col is None:
            return
        
        # 解析数据行
        for line in table_lines[2:]:  # 跳过表头和分隔线
            cells = [c.strip() for c in line.split('|')[1:-1]]
            if len(cells) <= fault_id_col:
                continue
            
            fault_id = cells[fault_id_col]
            if not fault_id:
                continue
            
            # 规范化Fault ID格式
            fault_id = self._normalize_fault_id(fault_id)
            
            # 提取各列信息
            guide_info = {}
            for i, header in enumerate(headers):
                if i < len(cells):
                    guide_info[header] = cells[i]
            
            guide_structure['fault_id_mapping'][fault_id] = guide_info
            
            # 提取grep模式或命令
            if 'grep' in str(guide_info).lower() or '提取' in str(guide_info) or '命令' in str(guide_info):
                for key, value in guide_info.items():
                    if 'grep' in key.lower() or '提取' in key or '命令' in key:
                        guide_structure['grep_patterns'][fault_id] = value
                        # 同时解析grep命令语义
                        parsed_cmd = self._parse_grep_command(value)
                        if parsed_cmd:
                            guide_structure['grep_commands'] = guide_structure.get('grep_commands', {})
                            guide_structure['grep_commands'][fault_id] = parsed_cmd
                        break
    
    def _parse_grep_command(self, command: str) -> Optional[Dict[str, Any]]:
        """
        解析grep命令语义
        
        例如: v log.gz |grep SetFunc |grep -E "fu_st:0x3|fu_st:0x4"
        意味着: 先过滤包含SetFunc的行，再过滤包含fu_st:0x3或fu_st:0x4的行，然后提取fa_id
        
        Args:
            command: grep命令字符串
            
        Returns:
            解析后的命令结构或None
        """
        if not command or not isinstance(command, str):
            return None
        
        command = command.strip()
        
        # 解析管道命令
        parts = [p.strip() for p in command.split('|')]
        
        filters = []  # 过滤条件列表
        extract_pattern = None  # 提取模式（用于提取fa_id）
        
        for part in parts:
            # 解析grep命令
            if part.startswith('grep'):
                # 提取grep的参数和模式
                # 例如: grep SetFunc 或 grep -E "fu_st:0x3|fu_st:0x4"
                grep_match = re.match(r'grep(?:\s+-[Ee])?\s+(.+)', part)
                if grep_match:
                    pattern = grep_match.group(1).strip().strip('"\'')
                    filters.append(pattern)
            elif 'fa_id' in part.lower() or 'fault' in part.lower():
                # 如果命令中提到fa_id或fault，尝试提取提取模式
                extract_match = re.search(r'fa_id[:\s]+(0x[0-9A-Fa-f]+)', part, re.IGNORECASE)
                if extract_match:
                    extract_pattern = extract_match.group(1)
        
        if filters:
            return {
                'filters': filters,
                'extract_pattern': extract_pattern or r'fa_id[:\s]+(0x[0-9A-Fa-f]+)',
                'original_command': command
            }
        
        return None
    
    def _extract_from_text(self, content: str, guide_structure: Dict):
        """从文本中提取Fault ID信息"""
        # 查找Fault ID模式
        fault_id_patterns = [
            r'Fault\s*ID[:\s]+(0x[0-9A-Fa-f]+)',
            r'Fault\s*ID[:\s]+([0-9]+)',
            r'故障ID[:\s]+(0x[0-9A-Fa-f]+)',
            r'故障ID[:\s]+([0-9]+)',
        ]
        
        for pattern in fault_id_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                fault_id = self._normalize_fault_id(match.group(1))
                if fault_id not in guide_structure['fault_id_mapping']:
                    guide_structure['fault_id_mapping'][fault_id] = {
                        'fault_id': fault_id,
                        'content': content[max(0, match.start()-200):match.end()+200]  # 提取上下文
                    }
    
    def _normalize_fault_id(self, fault_id: str) -> str:
        """规范化Fault ID格式"""
        if not fault_id:
            return ""
        
        fault_id = fault_id.strip()
        
        # 转换为大写并规范化
        if fault_id.startswith('0x') or fault_id.startswith('0X'):
            # 移除0x前缀，转换为数字，再格式化为4位16进制
            hex_str = fault_id[2:].upper()
            try:
                num = int(hex_str, 16)
                fault_id = f"0x{num:04X}"  # 4位16进制，如0x0165
            except ValueError:
                # 如果转换失败，保持原样但转大写
                fault_id = '0x' + hex_str
        elif fault_id.isdigit():
            # 如果是纯数字，转换为0x格式（4位16进制）
            num = int(fault_id)
            fault_id = f"0x{num:04X}"
        
        return fault_id
    
    def get_guide_by_fault_id(self, fault_id: str) -> Optional[Dict[str, Any]]:
        """
        根据Fault ID获取指引信息
        
        Args:
            fault_id: Fault ID（支持多种格式）
            
        Returns:
            指引信息字典
        """
        # 规范化Fault ID
        normalized_id = self._normalize_fault_id(fault_id)
        
        # 从所有指引文档中查找
        for guide_doc in get_guide_docs():
            node_token = guide_doc['node_token']
            
            # 加载指引文档
            if node_token not in self.guide_cache:
                content = self.load_fault_guide(node_token)
                if content:
                    structure = self.parse_guide_structure(content)
                    self.guide_cache[node_token] = structure
                else:
                    self.guide_cache[node_token] = {}
            
            structure = self.guide_cache.get(node_token, {})
            mapping = structure.get('fault_id_mapping', {})
            
            # 查找匹配的Fault ID
            if normalized_id in mapping:
                guide_info = mapping[normalized_id].copy()
                guide_info['grep_pattern'] = structure.get('grep_patterns', {}).get(normalized_id)
                guide_info['grep_command'] = structure.get('grep_commands', {}).get(normalized_id)
                # 添加完整内容供AI分析使用
                guide_info['content'] = structure.get('content', '')
                guide_info['完整内容'] = structure.get('content', '')
                return guide_info
            
            # 尝试模糊匹配（如果精确匹配失败）
            for key, value in mapping.items():
                if normalized_id in key or key in normalized_id:
                    guide_info = value.copy()
                    guide_info['grep_pattern'] = structure.get('grep_patterns', {}).get(key)
                    guide_info['grep_command'] = structure.get('grep_commands', {}).get(key)
                    # 添加完整内容供AI分析使用
                    guide_info['content'] = structure.get('content', '')
                    guide_info['完整内容'] = structure.get('content', '')
                    return guide_info
        
        return None
    
    def get_grep_patterns(self, fault_id: str) -> Optional[str]:
        """
        获取Fault ID的grep提取模式
        
        Args:
            fault_id: Fault ID
            
        Returns:
            grep模式字符串
        """
        guide_info = self.get_guide_by_fault_id(fault_id)
        if guide_info:
            return guide_info.get('grep_pattern') or guide_info.get('grep模式') or guide_info.get('提取模式')
        return None
    
    def load_all_guides(self, force_refresh: bool = False):
        """加载所有指引文档"""
        print("=" * 80)
        print("加载所有故障定位指引文档")
        print("=" * 80)
        print()
        
        # 刷新token（如果需要）
        self._refresh_token_if_needed()
        
        for guide_doc in get_guide_docs():
            print(f"加载: {guide_doc['name']}")
            print(f"  Node Token: {guide_doc['node_token']}")
            
            content = self.load_fault_guide(guide_doc['node_token'], force_refresh)
            if content:
                structure = self.parse_guide_structure(content)
                self.guide_cache[guide_doc['node_token']] = structure
                mapping_count = len(structure.get('fault_id_mapping', {}))
                print(f"  [OK] 加载成功，包含 {mapping_count} 个Fault ID映射")
            else:
                print(f"  [X] 加载失败")
            print()
        
        print("=" * 80)
        print("指引文档加载完成")
        print("=" * 80)
    
    def refresh_all_guides_if_needed(self, max_cache_age_hours: int = 24):
        """
        如果缓存过期，刷新所有指引文档
        
        Args:
            max_cache_age_hours: 缓存最大有效期（小时）
        """
        # 刷新token（如果需要）
        self._refresh_token_if_needed()
        
        for guide_doc in get_guide_docs():
            node_token = guide_doc['node_token']
            cache_file = GUIDE_CACHE_DIR / f"guide_{node_token}.json"
            
            should_refresh = True
            if cache_file.exists():
                try:
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        cache_data = json.load(f)
                        cache_time = cache_data.get('cache_time', 0)
                        # 检查缓存是否过期
                        if datetime.now().timestamp() - cache_time < max_cache_age_hours * 3600:
                            should_refresh = False
                except:
                    pass
            
            if should_refresh:
                print(f"刷新指引文档缓存: {guide_doc['name']}")
                self.load_fault_guide(node_token, force_refresh=True)


def get_guide_reader() -> FaultGuideReader:
    """获取指引读取器实例（单例模式）"""
    if not hasattr(get_guide_reader, '_instance'):
        get_guide_reader._instance = FaultGuideReader()
    return get_guide_reader._instance

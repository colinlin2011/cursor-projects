# -*- coding: utf-8 -*-
"""
日志路径提取模块

从问题单的多个字段中提取日志路径
"""

import re
from typing import List, Optional, Dict, Any

from fault_diagnosis_config import LOG_PATH_KEYWORDS, get_field_name


class LogPathExtractor:
    """日志路径提取器"""
    
    def __init__(self):
        """初始化提取器"""
        self.keywords = LOG_PATH_KEYWORDS
        # 日志路径模式
        self.path_patterns = [
            r"/rawdata/[^\s\n]+",  # /rawdata/roadtestv3/...
            r"/bench-log/[^\s\n]+",  # /bench-log/...
            r"roadtest[^\s\n]*",  # roadtest相关路径
        ]
    
    def extract_from_ticket(self, ticket_data: Dict[str, Any]) -> List[str]:
        """
        从问题单中提取日志路径
        
        Args:
            ticket_data: 问题单数据字典
            
        Returns:
            日志路径列表
        """
        paths = []
        fields = ticket_data.get('fields', {})
        
        # 从关键字段中提取
        key_fields = [get_field_name("描述"), get_field_name("Ticket元信息")]
        
        for field_name in key_fields:
            if field_name in fields:
                value = fields[field_name]
                if value:
                    found_paths = self.find_log_path_in_text(str(value))
                    paths.extend(found_paths)
        
        # 从所有字段中查找包含关键字的路径
        for field_name, field_value in fields.items():
            if field_name not in key_fields and field_value:
                value_str = str(field_value)
                # 检查是否包含关键字
                if any(keyword in value_str for keyword in self.keywords):
                    found_paths = self.find_log_path_in_text(value_str)
                    paths.extend(found_paths)
        
        # 去重并验证
        unique_paths = []
        seen = set()
        for path in paths:
            normalized = self.normalize_path(path)
            if normalized and normalized not in seen:
                if self.validate_log_path(normalized):
                    unique_paths.append(normalized)
                    seen.add(normalized)
        
        return unique_paths
    
    def find_log_path_in_text(self, text: str) -> List[str]:
        """
        在文本中查找日志路径
        
        Args:
            text: 文本内容
            
        Returns:
            找到的路径列表
        """
        paths = []
        
        # 使用正则表达式匹配路径
        for pattern in self.path_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                path = match.group(0).strip()
                # 清理路径（移除末尾的标点符号）
                path = re.sub(r'[.,;:!?]+$', '', path)
                if path:
                    paths.append(path)
        
        # 如果没有匹配到，尝试查找包含关键字的行
        if not paths:
            lines = text.split('\n')
            for line in lines:
                for keyword in self.keywords:
                    if keyword in line:
                        # 尝试提取路径
                        parts = line.split(keyword)
                        if len(parts) > 1:
                            # 提取关键字后的路径部分
                            path_part = keyword + parts[1].split()[0] if parts[1].split() else ""
                            if path_part:
                                paths.append(path_part)
                        break
        
        return paths
    
    def normalize_path(self, path: str) -> Optional[str]:
        """
        规范化路径
        
        Args:
            path: 原始路径
            
        Returns:
            规范化后的路径
        """
        if not path:
            return None
        
        # 移除前后空白
        path = path.strip()
        
        # 移除常见的标点符号
        path = re.sub(r'^[.,;:!?]+|[.,;:!?]+$', '', path)
        
        # 如果路径包含 roadtest 但没有 /rawdata/ 前缀，添加前缀
        if 'roadtest' in path.lower() and '/rawdata/' not in path:
            if path.startswith('/'):
                # 如果以 / 开头，例如 /roadtestv3/... -> /rawdata/roadtestv3/...
                if path.startswith('/roadtest'):
                    path = '/rawdata' + path
            else:
                # 如果不以 / 开头，例如 roadtestv3/... -> /rawdata/roadtestv3/...
                path = '/rawdata/' + path.lstrip('/')
        # 确保路径以/开头（如果是绝对路径）
        elif path.startswith('rawdata') or path.startswith('bench-log'):
            path = '/' + path
        
        return path
    
    def validate_log_path(self, path: str) -> bool:
        """
        验证路径格式
        
        Args:
            path: 路径字符串
            
        Returns:
            是否为有效路径
        """
        if not path:
            return False
        
        # 检查是否包含关键字
        if not any(keyword in path for keyword in self.keywords):
            return False
        
        # 检查路径格式
        if path.startswith('/rawdata/') or path.startswith('/bench-log/'):
            return True
        
        if 'roadtest' in path.lower():
            return True
        
        return False
    
    def extract_from_text(self, text: str) -> List[str]:
        """
        从文本中提取日志路径（便捷方法）
        
        Args:
            text: 文本内容
            
        Returns:
            日志路径列表
        """
        paths = self.find_log_path_in_text(text)
        unique_paths = []
        seen = set()
        for path in paths:
            normalized = self.normalize_path(path)
            if normalized and normalized not in seen:
                if self.validate_log_path(normalized):
                    unique_paths.append(normalized)
                    seen.add(normalized)
        return unique_paths


def extract_log_paths_from_ticket(ticket_data: Dict[str, Any]) -> List[str]:
    """
    从问题单中提取日志路径（便捷函数）
    
    Args:
        ticket_data: 问题单数据字典
        
    Returns:
        日志路径列表
    """
    extractor = LogPathExtractor()
    return extractor.extract_from_ticket(ticket_data)

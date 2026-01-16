# -*- coding: utf-8 -*-
"""
能力匹配器

基于能力元数据自动匹配和组合能力
"""

import logging
from typing import Dict, Any, List, Optional, Set
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)


class CapabilityMatcher:
    """能力匹配器"""
    
    def __init__(self, capability_registry: Dict[str, Dict[str, Any]]):
        """
        初始化能力匹配器
        
        Args:
            capability_registry: 能力注册表（能力ID -> 能力元数据）
        """
        self.registry = capability_registry
        self._build_index()
    
    def _build_index(self):
        """构建索引"""
        self.name_index: Dict[str, List[str]] = {}  # 名称 -> 能力ID列表
        self.keyword_index: Dict[str, List[str]] = {}  # 关键词 -> 能力ID列表
        self.category_index: Dict[str, List[str]] = {}  # 类别 -> 能力ID列表
        
        for capability_id, metadata in self.registry.items():
            name = metadata.get('name', '')
            description = metadata.get('description', '')
            category = metadata.get('category', '')
            
            # 名称索引
            if name:
                name_lower = name.lower()
                if name_lower not in self.name_index:
                    self.name_index[name_lower] = []
                self.name_index[name_lower].append(capability_id)
            
            # 关键词索引（从名称和描述中提取）
            keywords = self._extract_keywords(name, description)
            for keyword in keywords:
                if keyword not in self.keyword_index:
                    self.keyword_index[keyword] = []
                self.keyword_index[keyword].append(capability_id)
            
            # 类别索引
            if category:
                if category not in self.category_index:
                    self.category_index[category] = []
                self.category_index[category].append(capability_id)
    
    def _extract_keywords(self, name: str, description: str) -> List[str]:
        """
        提取关键词
        
        Args:
            name: 能力名称
            description: 能力描述
            
        Returns:
            关键词列表
        """
        keywords = []
        text = f"{name} {description}".lower()
        
        # 常见关键词
        common_keywords = [
            '飞书', 'feishu', '文档', 'doc', '表格', 'table', 'bitable',
            '多维表格', 'spreadsheet', '查询', 'query', '分析', 'analyze',
            '故障', 'fault', '问题', 'ticket', '缓存', 'cache', '数据', 'data'
        ]
        
        for keyword in common_keywords:
            if keyword in text:
                keywords.append(keyword)
        
        # 提取中文词汇（简单实现）
        import re
        chinese_words = re.findall(r'[\u4e00-\u9fa5]{2,}', text)
        keywords.extend(chinese_words[:5])  # 限制数量
        
        return list(set(keywords))
    
    def match_by_name(self, name: str, threshold: float = 0.6) -> List[tuple[str, float]]:
        """
        按名称匹配能力
        
        Args:
            name: 查询名称
            threshold: 相似度阈值
            
        Returns:
            (能力ID, 相似度) 列表，按相似度降序排列
        """
        name_lower = name.lower()
        matches = []
        
        for capability_id, metadata in self.registry.items():
            capability_name = metadata.get('name', '').lower()
            
            # 计算相似度
            similarity = SequenceMatcher(None, name_lower, capability_name).ratio()
            
            if similarity >= threshold:
                matches.append((capability_id, similarity))
        
        # 按相似度降序排列
        matches.sort(key=lambda x: x[1], reverse=True)
        
        return matches
    
    def match_by_keywords(self, keywords: List[str]) -> List[tuple[str, int]]:
        """
        按关键词匹配能力
        
        Args:
            keywords: 关键词列表
            
        Returns:
            (能力ID, 匹配分数) 列表，按分数降序排列
        """
        scores: Dict[str, int] = {}
        
        for keyword in keywords:
            keyword_lower = keyword.lower()
            
            # 在关键词索引中查找
            if keyword_lower in self.keyword_index:
                for capability_id in self.keyword_index[keyword_lower]:
                    scores[capability_id] = scores.get(capability_id, 0) + 1
        
        # 转换为列表并排序
        matches = [(cap_id, score) for cap_id, score in scores.items()]
        matches.sort(key=lambda x: x[1], reverse=True)
        
        return matches
    
    def match_by_category(self, category: str) -> List[str]:
        """
        按类别匹配能力
        
        Args:
            category: 类别名称
            
        Returns:
            能力ID列表
        """
        return self.category_index.get(category, [])
    
    def match_by_description(self, description: str, threshold: float = 0.3) -> List[tuple[str, float]]:
        """
        按描述匹配能力
        
        Args:
            description: 查询描述
            threshold: 相似度阈值
            
        Returns:
            (能力ID, 相似度) 列表
        """
        description_lower = description.lower()
        matches = []
        
        for capability_id, metadata in self.registry.items():
            capability_desc = metadata.get('description', '').lower()
            
            # 计算相似度
            similarity = SequenceMatcher(None, description_lower, capability_desc).ratio()
            
            if similarity >= threshold:
                matches.append((capability_id, similarity))
        
        # 按相似度降序排列
        matches.sort(key=lambda x: x[1], reverse=True)
        
        return matches
    
    def match(
        self,
        query: str,
        category: Optional[str] = None,
        limit: int = 10
    ) -> List[tuple[str, float]]:
        """
        综合匹配能力
        
        Args:
            query: 查询字符串
            category: 类别过滤（可选）
            limit: 返回结果数量限制
            
        Returns:
            (能力ID, 匹配分数) 列表
        """
        # 提取关键词
        keywords = self._extract_keywords(query, '')
        
        # 综合匹配结果
        all_matches: Dict[str, float] = {}
        
        # 1. 名称匹配（权重：0.5）
        name_matches = self.match_by_name(query, threshold=0.5)
        for cap_id, score in name_matches:
            all_matches[cap_id] = all_matches.get(cap_id, 0) + score * 0.5
        
        # 2. 关键词匹配（权重：0.3）
        keyword_matches = self.match_by_keywords(keywords)
        for cap_id, score in keyword_matches:
            all_matches[cap_id] = all_matches.get(cap_id, 0) + score * 0.3
        
        # 3. 描述匹配（权重：0.2）
        desc_matches = self.match_by_description(query, threshold=0.2)
        for cap_id, score in desc_matches:
            all_matches[cap_id] = all_matches.get(cap_id, 0) + score * 0.2
        
        # 类别过滤
        if category:
            category_caps = set(self.match_by_category(category))
            all_matches = {cap_id: score for cap_id, score in all_matches.items()
                          if cap_id in category_caps}
        
        # 转换为列表并排序
        matches = [(cap_id, score) for cap_id, score in all_matches.items()]
        matches.sort(key=lambda x: x[1], reverse=True)
        
        return matches[:limit]

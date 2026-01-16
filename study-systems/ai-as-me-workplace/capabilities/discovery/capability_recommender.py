# -*- coding: utf-8 -*-
"""
能力推荐器

基于使用历史和能力关系推荐能力组合
"""

import logging
from typing import Dict, Any, List, Optional, Set
from collections import defaultdict

logger = logging.getLogger(__name__)


class CapabilityRecommender:
    """能力推荐器"""
    
    def __init__(
        self,
        capability_registry: Dict[str, Dict[str, Any]],
        usage_history: Optional[List[Dict[str, Any]]] = None
    ):
        """
        初始化能力推荐器
        
        Args:
            capability_registry: 能力注册表
            usage_history: 使用历史记录
        """
        self.registry = capability_registry
        self.usage_history = usage_history or []
        self._build_cooccurrence_matrix()
    
    def _build_cooccurrence_matrix(self):
        """构建共现矩阵（哪些能力经常一起使用）"""
        self.cooccurrence: Dict[tuple[str, str], int] = defaultdict(int)
        
        # 从使用历史中提取共现关系
        for record in self.usage_history:
            capabilities = record.get('capabilities', [])
            if len(capabilities) < 2:
                continue
            
            # 记录每对能力的共现
            for i, cap1 in enumerate(capabilities):
                for cap2 in capabilities[i+1:]:
                    pair = tuple(sorted([cap1, cap2]))
                    self.cooccurrence[pair] += 1
    
    def recommend_combinations(
        self,
        base_capability: str,
        limit: int = 5
    ) -> List[tuple[str, float]]:
        """
        推荐能力组合
        
        Args:
            base_capability: 基础能力ID
            limit: 返回结果数量限制
            
        Returns:
            (能力ID, 推荐分数) 列表
        """
        recommendations: Dict[str, float] = {}
        
        # 查找与基础能力共现的其他能力
        for (cap1, cap2), count in self.cooccurrence.items():
            if cap1 == base_capability:
                recommendations[cap2] = count
            elif cap2 == base_capability:
                recommendations[cap1] = count
        
        # 转换为列表并排序
        recs = [(cap_id, score) for cap_id, score in recommendations.items()]
        recs.sort(key=lambda x: x[1], reverse=True)
        
        return recs[:limit]
    
    def recommend_by_use_case(
        self,
        use_case: str,
        limit: int = 5
    ) -> List[tuple[str, float]]:
        """
        基于用例推荐能力
        
        Args:
            use_case: 用例描述
            limit: 返回结果数量限制
            
        Returns:
            (能力ID, 推荐分数) 列表
        """
        # 从使用历史中查找相似用例
        use_case_lower = use_case.lower()
        use_case_scores: Dict[str, float] = defaultdict(float)
        
        for record in self.usage_history:
            record_use_case = record.get('use_case', '').lower()
            if not record_use_case:
                continue
            
            # 计算用例相似度（简单实现）
            from difflib import SequenceMatcher
            similarity = SequenceMatcher(None, use_case_lower, record_use_case).ratio()
            
            if similarity > 0.3:
                # 记录该用例中使用的能力
                capabilities = record.get('capabilities', [])
                for cap_id in capabilities:
                    use_case_scores[cap_id] += similarity
        
        # 转换为列表并排序
        recs = [(cap_id, score) for cap_id, score in use_case_scores.items()]
        recs.sort(key=lambda x: x[1], reverse=True)
        
        return recs[:limit]
    
    def analyze_dependencies(self, capability_id: str) -> Dict[str, Any]:
        """
        分析能力依赖关系
        
        Args:
            capability_id: 能力ID
            
        Returns:
            依赖分析结果
        """
        metadata = self.registry.get(capability_id, {})
        dependencies = metadata.get('dependencies', [])
        
        # 分析直接依赖
        direct_deps = []
        for dep_id in dependencies:
            if dep_id in self.registry:
                direct_deps.append({
                    'capability_id': dep_id,
                    'name': self.registry[dep_id].get('name', ''),
                    'type': 'direct'
                })
        
        # 分析间接依赖（依赖的依赖）
        indirect_deps = []
        for dep in direct_deps:
            dep_id = dep['capability_id']
            dep_metadata = self.registry.get(dep_id, {})
            dep_deps = dep_metadata.get('dependencies', [])
            
            for indirect_dep_id in dep_deps:
                if indirect_dep_id not in [d['capability_id'] for d in direct_deps]:
                    if indirect_dep_id in self.registry:
                        indirect_deps.append({
                            'capability_id': indirect_dep_id,
                            'name': self.registry[indirect_dep_id].get('name', ''),
                            'type': 'indirect',
                            'via': dep_id
                        })
        
        return {
            'capability_id': capability_id,
            'direct_dependencies': direct_deps,
            'indirect_dependencies': indirect_deps,
            'total_dependencies': len(direct_deps) + len(indirect_deps)
        }
    
    def detect_conflicts(self, capabilities: List[str]) -> List[Dict[str, Any]]:
        """
        检测能力冲突
        
        Args:
            capabilities: 能力ID列表
            
        Returns:
            冲突列表
        """
        conflicts = []
        
        # 检查依赖冲突
        all_deps: Set[str] = set()
        for cap_id in capabilities:
            metadata = self.registry.get(cap_id, {})
            deps = metadata.get('dependencies', [])
            all_deps.update(deps)
        
        # 检查是否有能力在依赖列表中（循环依赖）
        for cap_id in capabilities:
            if cap_id in all_deps:
                conflicts.append({
                    'type': 'circular_dependency',
                    'capability': cap_id,
                    'message': f"能力 {cap_id} 存在循环依赖"
                })
        
        # 检查版本冲突（如果有版本信息）
        versions: Dict[str, Dict[str, Any]] = {}
        for cap_id in capabilities:
            metadata = self.registry.get(cap_id, {})
            version = metadata.get('version', '')
            if version:
                if cap_id not in versions:
                    versions[cap_id] = {'version': version, 'capabilities': []}
                versions[cap_id]['capabilities'].append(cap_id)
        
        return conflicts

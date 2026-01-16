# -*- coding: utf-8 -*-
"""
能力发现引擎

基于业务需求自动发现和组合原子能力
"""

import logging
from typing import Dict, Any, List, Optional
from pathlib import Path

from .capability_matcher import CapabilityMatcher
from .capability_recommender import CapabilityRecommender

logger = logging.getLogger(__name__)


class CapabilityDiscovery:
    """能力发现引擎"""
    
    def __init__(
        self,
        capability_registry: Dict[str, Dict[str, Any]],
        usage_history: Optional[List[Dict[str, Any]]] = None
    ):
        """
        初始化能力发现引擎
        
        Args:
            capability_registry: 能力注册表
            usage_history: 使用历史记录
        """
        self.registry = capability_registry
        self.matcher = CapabilityMatcher(capability_registry)
        self.recommender = CapabilityRecommender(capability_registry, usage_history)
    
    def discover(
        self,
        requirement: str,
        category: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        发现能力
        
        Args:
            requirement: 业务需求描述
            category: 类别过滤（可选）
            limit: 返回结果数量限制
            
        Returns:
            能力列表，包含匹配信息
        """
        # 使用匹配器查找能力
        matches = self.matcher.match(requirement, category, limit)
        
        # 构建结果
        results = []
        for cap_id, score in matches:
            metadata = self.registry.get(cap_id, {})
            results.append({
                'capability_id': cap_id,
                'name': metadata.get('name', ''),
                'description': metadata.get('description', ''),
                'match_score': score,
                'metadata': metadata
            })
        
        return results
    
    def discover_combination(
        self,
        requirement: str,
        base_capability: Optional[str] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        发现能力组合
        
        Args:
            requirement: 业务需求描述
            base_capability: 基础能力ID（可选）
            limit: 返回结果数量限制
            
        Returns:
            能力组合列表
        """
        # 如果指定了基础能力，基于它推荐组合
        if base_capability:
            recommendations = self.recommender.recommend_combinations(
                base_capability, limit
            )
        else:
            # 否则先发现基础能力，再推荐组合
            base_matches = self.discover(requirement, limit=1)
            if not base_matches:
                return []
            
            base_capability = base_matches[0]['capability_id']
            recommendations = self.recommender.recommend_combinations(
                base_capability, limit
            )
        
        # 构建组合结果
        combinations = []
        for cap_id, score in recommendations:
            metadata = self.registry.get(cap_id, {})
            combinations.append({
                'capability_id': cap_id,
                'name': metadata.get('name', ''),
                'description': metadata.get('description', ''),
                'recommendation_score': score,
                'base_capability': base_capability,
                'metadata': metadata
            })
        
        return combinations
    
    def suggest_workflow(
        self,
        requirement: str,
        max_steps: int = 5
    ) -> Dict[str, Any]:
        """
        建议工作流
        
        Args:
            requirement: 业务需求描述
            max_steps: 最大步骤数
            
        Returns:
            建议的工作流定义
        """
        # 发现相关能力
        capabilities = self.discover(requirement, limit=max_steps)
        
        if not capabilities:
            return {
                'success': False,
                'error': '未找到匹配的能力'
            }
        
        # 分析依赖关系
        workflow_steps = []
        used_capabilities = set()
        
        for cap_info in capabilities:
            cap_id = cap_info['capability_id']
            
            # 检查依赖
            dep_analysis = self.recommender.analyze_dependencies(cap_id)
            direct_deps = dep_analysis.get('direct_dependencies', [])
            
            # 先添加依赖
            for dep in direct_deps:
                dep_id = dep['capability_id']
                if dep_id not in used_capabilities:
                    workflow_steps.append({
                        'capability': dep_id,
                        'action': 'execute',
                        'input': {},
                        'output': f'{dep_id}_result'
                    })
                    used_capabilities.add(dep_id)
            
            # 再添加主能力
            if cap_id not in used_capabilities:
                workflow_steps.append({
                    'capability': cap_id,
                    'action': 'execute',
                    'input': {},
                    'output': f'{cap_id}_result'
                })
                used_capabilities.add(cap_id)
        
        return {
            'success': True,
            'workflow': {
                'name': f'建议工作流: {requirement[:50]}',
                'version': '1.0.0',
                'description': f'基于需求 "{requirement}" 自动生成的工作流',
                'steps': workflow_steps
            },
            'capabilities': [c['capability_id'] for c in capabilities]
        }
    
    def validate_combination(self, capabilities: List[str]) -> Dict[str, Any]:
        """
        验证能力组合
        
        Args:
            capabilities: 能力ID列表
            
        Returns:
            验证结果
        """
        # 检查能力是否存在
        missing = []
        for cap_id in capabilities:
            if cap_id not in self.registry:
                missing.append(cap_id)
        
        if missing:
            return {
                'valid': False,
                'errors': [f'能力不存在: {cap_id}' for cap_id in missing]
            }
        
        # 检测冲突
        conflicts = self.recommender.detect_conflicts(capabilities)
        
        # 分析依赖
        all_deps = []
        for cap_id in capabilities:
            dep_analysis = self.recommender.analyze_dependencies(cap_id)
            all_deps.extend(dep_analysis.get('direct_dependencies', []))
        
        return {
            'valid': len(conflicts) == 0,
            'conflicts': conflicts,
            'dependencies': all_deps,
            'total_capabilities': len(capabilities),
            'total_dependencies': len(set(d['capability_id'] for d in all_deps))
        }

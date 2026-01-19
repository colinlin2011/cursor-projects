#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
能力发现工具

用于搜索和发现团队共享能力库中的能力。

使用方法：
    python discover_capabilities.py --search "关键词"
    python discover_capabilities.py --scenario "场景名称"
    python discover_capabilities.py --stats
    python discover_capabilities.py --sort-by usage
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional

# 获取脚本所在目录
SCRIPT_DIR = Path(__file__).parent
TEAM_SHARED_DIR = SCRIPT_DIR.parent
REGISTRY_FILE = TEAM_SHARED_DIR / "capabilities" / "registry.md"
USAGE_FILE = TEAM_SHARED_DIR / "usage" / "usage-history.md"


class CapabilityDiscovery:
    """能力发现引擎"""
    
    def __init__(self):
        self.registry_file = REGISTRY_FILE
        self.usage_file = USAGE_FILE
        
    def parse_registry(self) -> List[Dict[str, any]]:
        """解析注册表，提取能力信息"""
        capabilities = []
        
        if not self.registry_file.exists():
            print(f"注册表文件不存在: {self.registry_file}")
            return capabilities
        
        with open(self.registry_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 解析Skill能力表格
        skill_pattern = r'\| (TEAM-SKILL-\d+) \| ([^|]+) \| ([^|]+) \| ([^|]+) \|'
        for match in re.finditer(skill_pattern, content):
            capabilities.append({
                'id': match.group(1),
                'name': match.group(2).strip(),
                'type': match.group(3).strip(),
                'description': match.group(4).strip(),
                'category': 'skill'
            })
        
        # 解析Agent能力表格
        agent_pattern = r'\| (TEAM-AGENT-\d+) \| ([^|]+) \| ([^|]+) \| ([^|]+) \|'
        for match in re.finditer(agent_pattern, content):
            capabilities.append({
                'id': match.group(1),
                'name': match.group(2).strip(),
                'type': match.group(3).strip(),
                'description': match.group(4).strip(),
                'category': 'agent'
            })
        
        # 解析本地工具表格
        tool_pattern = r'\| (TEAM-TOOL-\d+) \| ([^|]+) \| ([^|]+) \| ([^|]+) \|'
        for match in re.finditer(tool_pattern, content):
            capabilities.append({
                'id': match.group(1),
                'name': match.group(2).strip(),
                'type': match.group(3).strip(),
                'description': match.group(4).strip(),
                'category': 'local-tool'
            })
        
        # 解析MCP能力表格
        mcp_pattern = r'\| (TEAM-MCP-\d+) \| ([^|]+) \| ([^|]+) \| ([^|]+) \|'
        for match in re.finditer(mcp_pattern, content):
            capabilities.append({
                'id': match.group(1),
                'name': match.group(2).strip(),
                'type': match.group(3).strip(),
                'description': match.group(4).strip(),
                'category': 'mcp'
            })
        
        return capabilities
    
    def search_by_keyword(self, keyword: str) -> List[Dict[str, any]]:
        """按关键词搜索能力"""
        capabilities = self.parse_registry()
        keyword_lower = keyword.lower()
        
        results = []
        for cap in capabilities:
            # 搜索名称、描述、ID
            if (keyword_lower in cap['name'].lower() or 
                keyword_lower in cap['description'].lower() or
                keyword_lower in cap['id'].lower()):
                results.append(cap)
        
        return results
    
    def recommend_by_scenario(self, scenario: str) -> List[Dict[str, any]]:
        """按场景推荐能力"""
        # 场景映射（可以根据实际情况扩展）
        scenario_mapping = {
            '文档协作': ['文档', '协作', '编辑'],
            '数据分析': ['数据', '分析', '统计'],
            '飞书集成': ['飞书', 'API', '集成'],
            '自动化': ['自动', '流程', '任务'],
        }
        
        keywords = scenario_mapping.get(scenario, [scenario])
        results = []
        
        capabilities = self.parse_registry()
        for cap in capabilities:
            for keyword in keywords:
                if keyword.lower() in cap['description'].lower():
                    results.append(cap)
                    break
        
        return results
    
    def get_statistics(self) -> Dict[str, any]:
        """获取使用统计"""
        capabilities = self.parse_registry()
        
        stats = {
            'total': len(capabilities),
            'by_type': {},
            'by_category': {}
        }
        
        # 按类型统计
        for cap in capabilities:
            cap_type = cap['type']
            stats['by_type'][cap_type] = stats['by_type'].get(cap_type, 0) + 1
        
        # 按分类统计
        for cap in capabilities:
            category = cap.get('category', 'unknown')
            stats['by_category'][category] = stats['by_category'].get(category, 0) + 1
        
        return stats
    
    def sort_by_usage(self, capabilities: List[Dict[str, any]]) -> List[Dict[str, any]]:
        """按使用次数排序"""
        # 这里应该从使用记录文件中读取使用次数
        # 目前简化处理，返回原列表
        return sorted(capabilities, key=lambda x: x.get('usage_count', 0), reverse=True)
    
    def sort_by_rating(self, capabilities: List[Dict[str, any]]) -> List[Dict[str, any]]:
        """按评分排序"""
        # 这里应该从使用记录文件中读取评分
        # 目前简化处理，返回原列表
        return sorted(capabilities, key=lambda x: x.get('rating', 0), reverse=True)
    
    def display_results(self, results: List[Dict[str, any]], title: str = "搜索结果"):
        """显示搜索结果"""
        if not results:
            print(f"\n{title}: 未找到匹配的能力")
            return
        
        print(f"\n{title}: 找到 {len(results)} 个能力\n")
        print("-" * 100)
        
        for i, cap in enumerate(results, 1):
            print(f"\n{i}. {cap['id']} - {cap['name']}")
            print(f"   类型: {cap['type']}")
            print(f"   描述: {cap['description']}")
            print(f"   分类: {cap.get('category', '-')}")
            print("-" * 100)
    
    def display_statistics(self, stats: Dict[str, any]):
        """显示统计信息"""
        print("\n能力统计信息")
        print("=" * 50)
        print(f"总能力数: {stats['total']}")
        
        print("\n按类型统计:")
        for cap_type, count in stats['by_type'].items():
            print(f"  {cap_type}: {count}")
        
        print("\n按分类统计:")
        for category, count in stats['by_category'].items():
            print(f"  {category}: {count}")
        print("=" * 50)


def main():
    parser = argparse.ArgumentParser(description="发现团队共享能力")
    parser.add_argument("--search", help="按关键词搜索")
    parser.add_argument("--scenario", help="按场景推荐")
    parser.add_argument("--stats", action="store_true", help="显示统计信息")
    parser.add_argument("--sort-by", choices=["usage", "rating"], help="排序方式")
    
    args = parser.parse_args()
    
    discovery = CapabilityDiscovery()
    
    if args.stats:
        # 显示统计信息
        stats = discovery.get_statistics()
        discovery.display_statistics(stats)
    
    elif args.search:
        # 关键词搜索
        results = discovery.search_by_keyword(args.search)
        if args.sort_by == "usage":
            results = discovery.sort_by_usage(results)
        elif args.sort_by == "rating":
            results = discovery.sort_by_rating(results)
        discovery.display_results(results, f"搜索 '{args.search}'")
    
    elif args.scenario:
        # 场景推荐
        results = discovery.recommend_by_scenario(args.scenario)
        if args.sort_by == "usage":
            results = discovery.sort_by_usage(results)
        elif args.sort_by == "rating":
            results = discovery.sort_by_rating(results)
        discovery.display_results(results, f"场景 '{args.scenario}' 推荐")
    
    else:
        # 显示所有能力
        capabilities = discovery.parse_registry()
        if args.sort_by == "usage":
            capabilities = discovery.sort_by_usage(capabilities)
        elif args.sort_by == "rating":
            capabilities = discovery.sort_by_rating(capabilities)
        discovery.display_results(capabilities, "所有能力")
    
    sys.exit(0)


if __name__ == "__main__":
    main()

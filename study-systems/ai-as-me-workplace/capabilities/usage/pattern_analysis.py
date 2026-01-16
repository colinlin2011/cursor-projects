# -*- coding: utf-8 -*-
"""
能力使用模式分析

分析能力使用情况，识别使用模式
"""

import logging
from typing import Dict, Any, List, Optional
from collections import defaultdict, Counter
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class PatternAnalyzer:
    """模式分析器"""
    
    def __init__(self, usage_history: List[Dict[str, Any]]):
        """
        初始化模式分析器
        
        Args:
            usage_history: 使用历史记录列表
        """
        self.usage_history = usage_history
    
    def analyze_usage_frequency(self) -> Dict[str, Any]:
        """
        分析使用频率
        
        Returns:
            使用频率统计
        """
        capability_counts = Counter()
        total_usage = len(self.usage_history)
        
        for record in self.usage_history:
            capabilities = record.get('capabilities', [])
            for cap_id in capabilities:
                capability_counts[cap_id] += 1
        
        # 计算频率
        frequencies = {}
        for cap_id, count in capability_counts.items():
            frequencies[cap_id] = {
                'count': count,
                'frequency': count / total_usage if total_usage > 0 else 0,
                'percentage': (count / total_usage * 100) if total_usage > 0 else 0
            }
        
        return {
            'total_usage': total_usage,
            'capability_frequencies': frequencies,
            'most_used': capability_counts.most_common(10)
        }
    
    def analyze_usage_patterns(self) -> Dict[str, Any]:
        """
        分析使用模式
        
        Returns:
            使用模式统计
        """
        # 时间模式
        time_patterns = self._analyze_time_patterns()
        
        # 组合模式
        combination_patterns = self._analyze_combination_patterns()
        
        # 场景模式
        scenario_patterns = self._analyze_scenario_patterns()
        
        return {
            'time_patterns': time_patterns,
            'combination_patterns': combination_patterns,
            'scenario_patterns': scenario_patterns
        }
    
    def _analyze_time_patterns(self) -> Dict[str, Any]:
        """分析时间模式"""
        hour_counts = defaultdict(int)
        day_counts = defaultdict(int)
        
        for record in self.usage_history:
            timestamp = record.get('timestamp')
            if not timestamp:
                continue
            
            try:
                if isinstance(timestamp, str):
                    dt = datetime.fromisoformat(timestamp)
                else:
                    dt = timestamp
                
                hour_counts[dt.hour] += 1
                day_counts[dt.strftime('%A')] += 1
            except Exception:
                continue
        
        return {
            'hourly_distribution': dict(hour_counts),
            'daily_distribution': dict(day_counts),
            'peak_hour': max(hour_counts.items(), key=lambda x: x[1])[0] if hour_counts else None,
            'peak_day': max(day_counts.items(), key=lambda x: x[1])[0] if day_counts else None
        }
    
    def _analyze_combination_patterns(self) -> Dict[str, Any]:
        """分析组合模式"""
        combinations = defaultdict(int)
        
        for record in self.usage_history:
            capabilities = record.get('capabilities', [])
            if len(capabilities) < 2:
                continue
            
            # 记录能力组合
            combo_key = tuple(sorted(capabilities))
            combinations[combo_key] += 1
        
        # 找出最常见的组合
        most_common_combos = sorted(
            combinations.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        return {
            'total_combinations': len(combinations),
            'most_common_combinations': [
                {'capabilities': list(combo), 'count': count}
                for combo, count in most_common_combos
            ]
        }
    
    def _analyze_scenario_patterns(self) -> Dict[str, Any]:
        """分析场景模式"""
        scenario_counts = Counter()
        
        for record in self.usage_history:
            scenario = record.get('scenario', 'unknown')
            scenario_counts[scenario] += 1
        
        return {
            'scenario_distribution': dict(scenario_counts),
            'most_common_scenario': scenario_counts.most_common(1)[0] if scenario_counts else None
        }
    
    def analyze_effectiveness(self) -> Dict[str, Any]:
        """
        分析使用效果
        
        Returns:
            效果分析结果
        """
        success_counts = defaultdict(int)
        total_counts = defaultdict(int)
        
        for record in self.usage_history:
            capabilities = record.get('capabilities', [])
            success = record.get('success', False)
            
            for cap_id in capabilities:
                total_counts[cap_id] += 1
                if success:
                    success_counts[cap_id] += 1
        
        # 计算成功率
        success_rates = {}
        for cap_id, total in total_counts.items():
            success_count = success_counts.get(cap_id, 0)
            success_rates[cap_id] = {
                'total': total,
                'success': success_count,
                'failure': total - success_count,
                'success_rate': success_count / total if total > 0 else 0
            }
        
        return {
            'capability_effectiveness': success_rates,
            'overall_success_rate': sum(success_counts.values()) / sum(total_counts.values()) if total_counts else 0
        }
    
    def identify_trends(self, days: int = 30) -> Dict[str, Any]:
        """
        识别使用趋势
        
        Args:
            days: 分析天数
            
        Returns:
            趋势分析结果
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        
        recent_records = [
            r for r in self.usage_history
            if self._parse_timestamp(r.get('timestamp')) and
            self._parse_timestamp(r.get('timestamp')) >= cutoff_date
        ]
        
        old_records = [
            r for r in self.usage_history
            if self._parse_timestamp(r.get('timestamp')) and
            self._parse_timestamp(r.get('timestamp')) < cutoff_date
        ]
        
        # 比较近期和早期的使用情况
        recent_capabilities = Counter()
        old_capabilities = Counter()
        
        for record in recent_records:
            for cap_id in record.get('capabilities', []):
                recent_capabilities[cap_id] += 1
        
        for record in old_records:
            for cap_id in record.get('capabilities', []):
                old_capabilities[cap_id] += 1
        
        # 计算趋势
        trends = {}
        all_capabilities = set(recent_capabilities.keys()) | set(old_capabilities.keys())
        
        for cap_id in all_capabilities:
            recent_count = recent_capabilities.get(cap_id, 0)
            old_count = old_capabilities.get(cap_id, 0)
            
            if old_count == 0:
                trend = 'new'
            elif recent_count > old_count * 1.2:
                trend = 'increasing'
            elif recent_count < old_count * 0.8:
                trend = 'decreasing'
            else:
                trend = 'stable'
            
            trends[cap_id] = {
                'recent_count': recent_count,
                'old_count': old_count,
                'trend': trend,
                'change_rate': (recent_count - old_count) / old_count if old_count > 0 else float('inf')
            }
        
        return {
            'period_days': days,
            'recent_total': len(recent_records),
            'old_total': len(old_records),
            'trends': trends
        }
    
    def _parse_timestamp(self, timestamp: Any) -> Optional[datetime]:
        """解析时间戳"""
        if not timestamp:
            return None
        
        try:
            if isinstance(timestamp, str):
                return datetime.fromisoformat(timestamp)
            elif isinstance(timestamp, datetime):
                return timestamp
        except Exception:
            pass
        
        return None

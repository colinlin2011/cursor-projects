# -*- coding: utf-8 -*-
"""
日志分析模块

根据故障定位指引分析日志内容，使用AI进行智能分析，生成结构化的分析报告
"""

import sys
import os
import re
from typing import Dict, List, Any, Optional
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fault_guide_reader import get_guide_reader

# 修复Windows控制台编码问题
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass


class LogAnalyzer:
    """日志分析器"""
    
    def __init__(self):
        """初始化分析器"""
        self.guide_reader = get_guide_reader()
    
    def analyze_log_by_guide(
        self,
        log_content: str,
        fault_id: str,
        guide_info: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        根据指引分析日志
        
        Args:
            log_content: 日志内容
            fault_id: Fault ID
            guide_info: 指引信息（可选）
            
        Returns:
            分析结果字典
        """
        if not guide_info:
            guide_info = self.guide_reader.get_guide_by_fault_id(fault_id)
        
        # 提取关键错误
        key_errors = self.extract_key_errors(log_content, guide_info)
        
        # 分析日志内容
        analysis_result = {
            'fault_id': fault_id,
            'analysis_time': datetime.now().isoformat(),
            'key_errors': key_errors,
            'error_count': len(key_errors),
            'log_size': len(log_content),
            'guide_info': guide_info,
            'analysis_points': self._extract_analysis_points(log_content, guide_info),
            'timeline': self._extract_timeline(log_content),
            'modules_affected': self._extract_modules(log_content)
        }
        
        return analysis_result
    
    def extract_key_errors(self, log_content: str, guide_info: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """
        提取关键错误信息
        
        Args:
            log_content: 日志内容
            guide_info: 指引信息（可选）
            
        Returns:
            关键错误列表
        """
        errors = []
        
        # 错误关键词
        error_keywords = [
            'error', 'ERROR', 'Error',
            'fault', 'FAULT', 'Fault',
            'fail', 'FAIL', 'Fail',
            'exception', 'Exception', 'EXCEPTION',
            'crash', 'Crash', 'CRASH',
            'timeout', 'Timeout', 'TIMEOUT',
            '异常', '错误', '失败', '故障'
        ]
        
        lines = log_content.split('\n')
        for i, line in enumerate(lines):
            # 检查是否包含错误关键词
            if any(keyword in line for keyword in error_keywords):
                # 尝试提取时间戳
                timestamp = self._extract_timestamp(line)
                
                # 提取Fault ID相关
                fault_id_match = re.search(r'0x[0-9A-Fa-f]+', line, re.IGNORECASE)
                fault_id = fault_id_match.group(0) if fault_id_match else None
                
                errors.append({
                    'line_number': i + 1,
                    'timestamp': timestamp,
                    'fault_id': fault_id,
                    'content': line.strip(),
                    'severity': self._classify_severity(line)
                })
        
        # 按严重程度排序
        severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        errors.sort(key=lambda x: severity_order.get(x['severity'], 4))
        
        return errors[:50]  # 返回前50个错误
    
    def _extract_timestamp(self, line: str) -> Optional[str]:
        """从日志行中提取时间戳"""
        # 常见时间戳格式
        patterns = [
            r'\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}',  # 2025-01-15 14:30:00
            r'\d{4}/\d{2}/\d{2}\s+\d{2}:\d{2}:\d{2}',  # 2025/01/15 14:30:00
            r'\d{2}:\d{2}:\d{2}',  # 14:30:00
        ]
        
        for pattern in patterns:
            match = re.search(pattern, line)
            if match:
                return match.group(0)
        
        return None
    
    def _classify_severity(self, line: str) -> str:
        """分类错误严重程度"""
        line_lower = line.lower()
        
        if any(word in line_lower for word in ['crash', 'fatal', 'critical', '严重', '致命']):
            return 'critical'
        elif any(word in line_lower for word in ['error', 'fail', '错误', '失败']):
            return 'high'
        elif any(word in line_lower for word in ['warn', 'warning', '警告']):
            return 'medium'
        else:
            return 'low'
    
    def _extract_analysis_points(self, log_content: str, guide_info: Optional[Dict]) -> List[str]:
        """提取分析要点"""
        points = []
        
        if guide_info:
            # 从指引中获取分析要点
            analysis_points = guide_info.get('分析要点') or guide_info.get('分析点') or guide_info.get('要点')
            if analysis_points:
                if isinstance(analysis_points, str):
                    points.append(analysis_points)
                elif isinstance(analysis_points, list):
                    points.extend(analysis_points)
        
        # 从日志中提取关键信息
        if '轨迹' in log_content or 'trajectory' in log_content.lower():
            points.append("涉及轨迹相关功能")
        if '通信' in log_content or 'communication' in log_content.lower():
            points.append("涉及通信模块")
        if '规划' in log_content or 'planning' in log_content.lower():
            points.append("涉及规划模块")
        
        return points
    
    def _extract_timeline(self, log_content: str) -> List[Dict[str, Any]]:
        """提取时间线"""
        timeline = []
        lines = log_content.split('\n')
        
        for i, line in enumerate(lines[:1000]):  # 限制处理前1000行
            timestamp = self._extract_timestamp(line)
            if timestamp:
                # 检查是否包含关键事件
                if any(keyword in line.lower() for keyword in ['fault', 'error', 'start', 'stop', 'init']):
                    timeline.append({
                        'timestamp': timestamp,
                        'line': i + 1,
                        'event': line.strip()[:100]  # 截取前100字符
                    })
        
        return timeline[:20]  # 返回前20个事件
    
    def _extract_modules(self, log_content: str) -> List[str]:
        """提取涉及的模块"""
        modules = set()
        
        # 常见模块关键词
        module_keywords = [
            'Planning', 'Control', 'Perception', 'Localization',
            '规划', '控制', '感知', '定位'
        ]
        
        for keyword in module_keywords:
            if keyword in log_content:
                modules.add(keyword)
        
        return list(modules)
    
    def generate_analysis_report(self, analysis_result: Dict[str, Any]) -> str:
        """
        生成分析报告
        
        Args:
            analysis_result: 分析结果字典
            
        Returns:
            格式化的分析报告
        """
        fault_id = analysis_result.get('fault_id', 'Unknown')
        key_errors = analysis_result.get('key_errors', [])
        error_count = analysis_result.get('error_count', 0)
        guide_info = analysis_result.get('guide_info', {})
        analysis_points = analysis_result.get('analysis_points', [])
        timeline = analysis_result.get('timeline', [])
        modules = analysis_result.get('modules_affected', [])
        
        report_lines = []
        report_lines.append("=" * 80)
        report_lines.append(f"故障定位分析报告 - Fault ID: {fault_id}")
        report_lines.append("=" * 80)
        report_lines.append("")
        report_lines.append(f"分析时间: {analysis_result.get('analysis_time', '')}")
        report_lines.append("")
        
        # 故障信息
        report_lines.append("## 故障信息")
        report_lines.append("")
        report_lines.append(f"- **Fault ID**: {fault_id}")
        if guide_info:
            fault_name = guide_info.get('故障名称') or guide_info.get('Fault Name') or guide_info.get('名称')
            if fault_name:
                report_lines.append(f"- **故障名称**: {fault_name}")
            fault_desc = guide_info.get('故障描述') or guide_info.get('Fault Description') or guide_info.get('描述')
            if fault_desc:
                report_lines.append(f"- **故障描述**: {fault_desc}")
        report_lines.append("")
        
        # 关键错误
        report_lines.append("## 关键错误信息")
        report_lines.append("")
        report_lines.append(f"共发现 {error_count} 个错误")
        report_lines.append("")
        
        if key_errors:
            # 按严重程度分组
            critical_errors = [e for e in key_errors if e.get('severity') == 'critical']
            high_errors = [e for e in key_errors if e.get('severity') == 'high']
            
            if critical_errors:
                report_lines.append("### 严重错误")
                for error in critical_errors[:5]:
                    report_lines.append(f"- [{error.get('timestamp', 'N/A')}] {error.get('content', '')[:100]}")
                report_lines.append("")
            
            if high_errors:
                report_lines.append("### 高级错误")
                for error in high_errors[:10]:
                    report_lines.append(f"- [{error.get('timestamp', 'N/A')}] {error.get('content', '')[:100]}")
                report_lines.append("")
        
        # 分析要点
        if analysis_points:
            report_lines.append("## 分析要点")
            report_lines.append("")
            for point in analysis_points:
                report_lines.append(f"- {point}")
            report_lines.append("")
        
        # 涉及模块
        if modules:
            report_lines.append("## 涉及模块")
            report_lines.append("")
            for module in modules:
                report_lines.append(f"- {module}")
            report_lines.append("")
        
        # 时间线
        if timeline:
            report_lines.append("## 关键时间线")
            report_lines.append("")
            for event in timeline[:10]:
                report_lines.append(f"- [{event.get('timestamp', 'N/A')}] {event.get('event', '')[:80]}")
            report_lines.append("")
        
        # 初步结论
        report_lines.append("## 初步结论")
        report_lines.append("")
        conclusion = self._generate_conclusion(analysis_result)
        report_lines.append(conclusion)
        report_lines.append("")
        
        report_lines.append("=" * 80)
        
        return '\n'.join(report_lines)
    
    def _generate_conclusion(self, analysis_result: Dict[str, Any]) -> str:
        """生成初步结论"""
        fault_id = analysis_result.get('fault_id', '')
        key_errors = analysis_result.get('key_errors', [])
        error_count = analysis_result.get('error_count', 0)
        guide_info = analysis_result.get('guide_info', {})
        modules = analysis_result.get('modules_affected', [])
        
        conclusion_parts = []
        
        # 基于错误数量
        if error_count > 50:
            conclusion_parts.append("日志中发现大量错误信息，表明系统存在严重问题。")
        elif error_count > 10:
            conclusion_parts.append("日志中发现多个错误信息，需要重点关注。")
        elif error_count > 0:
            conclusion_parts.append("日志中发现少量错误信息。")
        else:
            conclusion_parts.append("日志中未发现明显的错误信息。")
        
        # 基于严重程度
        critical_count = sum(1 for e in key_errors if e.get('severity') == 'critical')
        if critical_count > 0:
            conclusion_parts.append(f"发现 {critical_count} 个严重错误，可能导致系统功能失效。")
        
        # 基于指引信息
        if guide_info:
            common_causes = guide_info.get('常见原因') or guide_info.get('Common Causes')
            if common_causes:
                conclusion_parts.append(f"根据故障定位指引，可能的原因包括：{common_causes}")
        
        # 基于涉及模块
        if modules:
            conclusion_parts.append(f"涉及模块：{', '.join(modules)}")
        
        # 建议
        conclusion_parts.append("建议：")
        conclusion_parts.append("1. 检查相关模块的运行状态")
        conclusion_parts.append("2. 查看关键错误的时间序列，确定故障发生时间点")
        conclusion_parts.append("3. 根据故障定位指引进行进一步排查")
        
        return '\n'.join(conclusion_parts)


def analyze_log(log_content: str, fault_id: str, guide_info: Optional[Dict] = None) -> Dict[str, Any]:
    """
    分析日志内容（便捷函数）
    
    Args:
        log_content: 日志内容
        fault_id: Fault ID
        guide_info: 指引信息（可选）
        
    Returns:
        分析结果字典
    """
    analyzer = LogAnalyzer()
    return analyzer.analyze_log_by_guide(log_content, fault_id, guide_info)

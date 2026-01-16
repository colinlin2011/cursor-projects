# -*- coding: utf-8 -*-
"""
通过单号查询故障信息

整合问题单监控、多维表格查询、故障分析等能力，提供统一的查询接口
"""

import sys
import os
from typing import Dict, Any, Optional, List
from pathlib import Path

# 修复Windows控制台编码问题
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fault_ticket_monitor import FaultTicketMonitor
from bitable_query_interface import get_query_interface
from fault_diagnosis_config import (
    DEFECT_TABLE_NAME, DEFECT_TABLE_CACHE_FILE, get_field_name
)


class FaultQueryByTicket:
    """通过单号查询故障信息"""
    
    def __init__(self):
        """初始化查询器"""
        self.ticket_monitor = FaultTicketMonitor()
        self.query_interface = get_query_interface()
    
    def normalize_ticket_id(self, ticket_id: str) -> str:
        """
        规范化单号格式
        
        支持多种格式：
        - 工作项ID：6683487902
        - 记录ID：recv8hWWsiysEn
        - 问题单号：其他格式
        
        Args:
            ticket_id: 原始单号
            
        Returns:
            规范化后的单号
        """
        # 去除空格
        ticket_id = ticket_id.strip()
        
        # 如果包含URL，提取ID
        if 'rec' in ticket_id.lower():
            # 记录ID格式
            if '/' in ticket_id:
                ticket_id = ticket_id.split('/')[-1]
        elif ticket_id.isdigit():
            # 工作项ID格式
            pass
        else:
            # 其他格式，尝试提取数字或ID
            import re
            match = re.search(r'(rec\w+|[\d]+)', ticket_id)
            if match:
                ticket_id = match.group(1)
        
        return ticket_id
    
    def query_by_ticket_id(
        self,
        ticket_id: str,
        include_analysis: bool = False
    ) -> Dict[str, Any]:
        """
        通过单号查询故障信息
        
        Args:
            ticket_id: 问题单ID（支持工作项ID、记录ID、问题单号）
            include_analysis: 是否包含故障分析
            
        Returns:
            故障信息字典，包含：
            - ticket_info: 问题单基本信息
            - defect_data: 缺陷数据
            - fault_analysis: 故障分析（如果include_analysis=True）
        """
        # 规范化单号
        normalized_id = self.normalize_ticket_id(ticket_id)
        
        result = {
            'ticket_id': ticket_id,
            'normalized_id': normalized_id,
            'success': False,
            'data': {},
            'error': None
        }
        
        try:
            # 步骤1: 获取问题单信息
            print(f"步骤1: 获取问题单信息 (ID: {normalized_id})...")
            ticket_info = self.ticket_monitor.get_ticket_info(normalized_id)
            
            if not ticket_info:
                result['error'] = f"未找到问题单信息: {normalized_id}"
                print(f"[X] {result['error']}")
                return result
            
            print(f"[OK] 问题单信息获取成功")
            print(f"  记录ID: {ticket_info.get('record_id')}")
            print(f"  工作项ID: {ticket_info.get('work_item_id')}")
            
            result['data']['ticket_info'] = ticket_info
            
            # 步骤2: 从多维表格获取详细数据
            print("\n步骤2: 从多维表格获取详细数据...")
            table_data = self.query_interface.get_table_data(
                DEFECT_TABLE_NAME,
                DEFECT_TABLE_CACHE_FILE
            )
            
            if not table_data:
                result['error'] = f"无法获取表数据: {DEFECT_TABLE_NAME}"
                print(f"[X] {result['error']}")
                return result
            
            # 查找匹配的记录
            records = table_data.get('records', [])
            defect_record = None
            
            for record in records:
                record_id = record.get('record_id', '')
                fields = record.get('fields', {})
                work_item_id = fields.get(get_field_name("工作项id"), "")
                
                if record_id == ticket_info.get('record_id') or \
                   work_item_id == ticket_info.get('work_item_id'):
                    defect_record = record
                    break
            
            if defect_record:
                print(f"[OK] 找到缺陷记录")
                result['data']['defect_data'] = defect_record
            else:
                print(f"[!] 未找到匹配的缺陷记录")
                result['data']['defect_data'] = None
            
            # 步骤3: 提取关键信息
            print("\n步骤3: 提取关键信息...")
            key_info = self._extract_key_info(ticket_info, defect_record)
            result['data']['key_info'] = key_info
            print(f"[OK] 关键信息提取完成")
            
            # 步骤4: 故障分析（如果需要）
            if include_analysis and defect_record:
                print("\n步骤4: 进行故障分析...")
                analysis = self._analyze_fault(ticket_info, defect_record)
                result['data']['fault_analysis'] = analysis
                print(f"[OK] 故障分析完成")
            
            result['success'] = True
            print(f"\n[OK] 查询完成")
            
        except Exception as e:
            result['error'] = f"查询异常: {str(e)}"
            print(f"[X] {result['error']}")
            import traceback
            traceback.print_exc()
        
        return result
    
    def _extract_key_info(
        self,
        ticket_info: Dict[str, Any],
        defect_record: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        提取关键信息
        
        Args:
            ticket_info: 问题单信息
            defect_record: 缺陷记录
            
        Returns:
            关键信息字典
        """
        key_info = {
            'record_id': ticket_info.get('record_id'),
            'work_item_id': ticket_info.get('work_item_id'),
            'fields': {}
        }
        
        if defect_record:
            fields = defect_record.get('fields', {})
            
            # 提取常用字段
            common_fields = [
                "工作项id", "问题描述", "问题状态", "优先级",
                "创建时间", "更新时间", "负责人", "工具回传"
            ]
            
            for field_name in common_fields:
                field_key = get_field_name(field_name)
                if field_key in fields:
                    key_info['fields'][field_name] = fields[field_key]
        
        return key_info
    
    def _analyze_fault(
        self,
        ticket_info: Dict[str, Any],
        defect_record: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        分析故障信息
        
        Args:
            ticket_info: 问题单信息
            defect_record: 缺陷记录
            
        Returns:
            分析结果字典
        """
        analysis = {
            'summary': '',
            'status': '',
            'priority': '',
            'recommendations': []
        }
        
        fields = defect_record.get('fields', {})
        
        # 提取状态和优先级
        status_field = get_field_name("问题状态")
        priority_field = get_field_name("优先级")
        
        analysis['status'] = fields.get(status_field, '未知')
        analysis['priority'] = fields.get(priority_field, '未知')
        
        # 生成摘要
        description_field = get_field_name("问题描述")
        description = fields.get(description_field, '')
        
        if description:
            analysis['summary'] = f"问题描述: {description[:200]}..." if len(description) > 200 else description
        else:
            analysis['summary'] = "暂无问题描述"
        
        # 生成建议
        if analysis['status'] == '待处理':
            analysis['recommendations'].append("建议尽快处理此问题")
        elif analysis['priority'] == '高':
            analysis['recommendations'].append("高优先级问题，需要重点关注")
        
        return analysis
    
    def format_result(self, result: Dict[str, Any]) -> str:
        """
        格式化查询结果
        
        Args:
            result: 查询结果字典
            
        Returns:
            格式化的字符串
        """
        if not result.get('success'):
            return f"查询失败: {result.get('error')}"
        
        data = result.get('data', {})
        ticket_info = data.get('ticket_info', {})
        key_info = data.get('key_info', {})
        analysis = data.get('fault_analysis')
        
        output = []
        output.append("=" * 60)
        output.append("故障信息查询结果")
        output.append("=" * 60)
        output.append(f"\n单号: {result.get('ticket_id')}")
        output.append(f"规范化ID: {result.get('normalized_id')}")
        
        if ticket_info:
            output.append(f"\n问题单信息:")
            output.append(f"  记录ID: {ticket_info.get('record_id')}")
            output.append(f"  工作项ID: {ticket_info.get('work_item_id')}")
        
        if key_info and key_info.get('fields'):
            output.append(f"\n关键信息:")
            for field_name, field_value in key_info['fields'].items():
                output.append(f"  {field_name}: {field_value}")
        
        if analysis:
            output.append(f"\n故障分析:")
            output.append(f"  摘要: {analysis.get('summary')}")
            output.append(f"  状态: {analysis.get('status')}")
            output.append(f"  优先级: {analysis.get('priority')}")
            
            if analysis.get('recommendations'):
                output.append(f"  建议:")
                for rec in analysis['recommendations']:
                    output.append(f"    - {rec}")
        
        output.append("\n" + "=" * 60)
        
        return "\n".join(output)


def query_fault_by_ticket(
    ticket_id: str,
    include_analysis: bool = False
) -> Dict[str, Any]:
    """
    便捷函数：通过单号查询故障信息
    
    Args:
        ticket_id: 问题单ID
        include_analysis: 是否包含故障分析
        
    Returns:
        查询结果字典
    """
    query = FaultQueryByTicket()
    return query.query_by_ticket_id(ticket_id, include_analysis)


if __name__ == "__main__":
    # 测试示例
    import sys
    
    if len(sys.argv) < 2:
        print("用法: python fault_query_by_ticket.py <ticket_id> [--analysis]")
        print("示例: python fault_query_by_ticket.py 6683487902 --analysis")
        sys.exit(1)
    
    ticket_id = sys.argv[1]
    include_analysis = '--analysis' in sys.argv
    
    query = FaultQueryByTicket()
    result = query.query_by_ticket_id(ticket_id, include_analysis)
    
    # 格式化输出
    formatted = query.format_result(result)
    print(formatted)

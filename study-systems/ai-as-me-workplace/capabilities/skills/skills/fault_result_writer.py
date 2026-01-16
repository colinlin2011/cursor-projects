# -*- coding: utf-8 -*-
"""
结果回填模块

将分析结果回填到"缺陷问题闭环表"的特定字段
"""

import sys
import os
from typing import Dict, Any, Optional
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from feishu_bitable_collaborator import create_bitable_collaborator
from bitable_cache_manager import BitableCacheManager, BITABLE_CONFIGS, APP_ID, APP_SECRET, SPACE_ID
from fault_diagnosis_config import (
    DEFECT_TABLE_NAME, DEFECT_TABLE_CACHE_FILE,
    get_field_name, get_dynamic_user_access_token
)

# 修复Windows控制台编码问题
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass


class FaultResultWriter:
    """结果回填器"""
    
    def __init__(self):
        """初始化回填器"""
        # 使用动态token（自动刷新）
        user_token = get_dynamic_user_access_token()
        self.collaborator = create_bitable_collaborator(
            app_id=APP_ID,
            app_secret=APP_SECRET,
            user_access_token=user_token
        )
        
        # 获取app_token
        self.manager = BitableCacheManager(APP_ID, APP_SECRET, user_token, SPACE_ID)
        config = None
        for cfg in BITABLE_CONFIGS:
            if cfg.get('cache_file') == DEFECT_TABLE_CACHE_FILE:
                config = cfg
                break
        
        if config:
            self.app_token = self.manager.get_app_token_from_wiki(config['node_token'])
            self.table_id = self._get_table_id()
        else:
            self.app_token = None
            self.table_id = None
    
    def _get_table_id(self) -> Optional[str]:
        """获取缺陷问题闭环表的table_id"""
        if not self.app_token:
            return None
        
        tables = self.collaborator.list_tables(self.app_token)
        for table in tables:
            if table.get('name') == DEFECT_TABLE_NAME:
                return table.get('table_id')
        return None
    
    def _get_field_id_by_name(self, field_name: str) -> Optional[str]:
        """根据字段名获取字段ID"""
        if not self.app_token or not self.table_id:
            return None
        
        try:
            structure = self.collaborator.get_table_structure(self.app_token, self.table_id)
            fields = structure.get('fields', [])
            
            for field in fields:
                if field.get('field_name') == field_name:
                    return field.get('field_id')
        except Exception as e:
            print(f"[!] 获取字段ID失败: {e}")
        
        return None
    
    def format_report_for_bitable(self, report: str) -> str:
        """
        格式化报告为表格格式
        
        Args:
            report: 分析报告文本
            
        Returns:
            格式化后的报告（适合多维表格显示）
        """
        # 限制报告长度（多维表格字段可能有长度限制）
        max_length = 10000
        
        if len(report) > max_length:
            report = report[:max_length] + "\n\n... (报告过长，已截断)"
        
        return report
    
    def update_ticket_field(self, ticket_id: str, field_name: str, value: Any) -> bool:
        """
        更新问题单字段（通过字段名）
        
        Args:
            ticket_id: 问题单记录ID
            field_name: 字段名称
            value: 字段值
            
        Returns:
            是否更新成功
        """
        field_id = self._get_field_id_by_name(field_name)
        if not field_id:
            print(f"[X] 无法获取字段ID: {field_name}")
            return False
        
        return self.update_ticket_field_by_id(ticket_id, field_id, value)
    
    def update_ticket_field_by_id(self, ticket_id: str, field_id: str, value: Any) -> bool:
        """
        更新问题单字段（通过字段ID）
        
        Args:
            ticket_id: 问题单记录ID
            field_id: 字段ID
            value: 字段值
            
        Returns:
            是否更新成功
        """
        if not self.app_token or not self.table_id:
            print("[X] 无法获取app_token或table_id")
            return False
        
        try:
            # 构建更新字段（使用字段ID）
            fields = {
                field_id: value
            }
            
            # 更新记录
            result = self.collaborator.update_record(
                self.app_token,
                self.table_id,
                ticket_id,
                fields
            )
            
            if result:
                print(f"[OK] 字段更新成功")
                return True
            else:
                print(f"[X] 字段更新失败")
                return False
                
        except Exception as e:
            print(f"[X] 更新字段失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def write_analysis_result(
        self,
        ticket_id: str,
        analysis_report: Dict[str, Any],
        ticket_info: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        写入分析结果到问题单（生成飞书文档报告并回填链接）
        
        Args:
            ticket_id: 问题单记录ID
            analysis_report: 分析报告字典
            ticket_info: 问题单信息（可选）
            
        Returns:
            是否写入成功
        """
        print("=" * 80)
        print("回填分析结果到缺陷问题闭环表")
        print("=" * 80)
        print()
        print(f"问题单ID: {ticket_id}")
        print()
        
        # 创建飞书文档报告
        doc_info = None
        from fault_report_generator import FaultReportGenerator
        
        try:
            report_generator = FaultReportGenerator()
            
            # 从analysis_report中提取分析结果列表
            analysis_results = analysis_report.get('analysis_results', [])
            
            if not analysis_results:
                # 如果没有analysis_results，尝试从其他字段构建
                print("[!] 警告: analysis_report中没有analysis_results字段，尝试从其他字段构建")
                analysis_results = []
                for key, value in analysis_report.items():
                    if isinstance(value, dict) and 'fault_id' in value:
                        analysis_results.append(value)
                
                # 如果还是没有，尝试从fault_ids构建
                if not analysis_results and 'fault_ids' in analysis_report:
                    print("[!] 警告: 从fault_ids字段构建analysis_results")
                    fault_ids = analysis_report.get('fault_ids', [])
                    for fault_id in fault_ids:
                        analysis_results.append({
                            'fault_id': fault_id,
                            'guide_info': {},
                            'analysis': {}
                        })
            
            # 获取执行步骤（从analysis_report中提取）
            execution_steps = analysis_report.get('steps', [])
            
            # 获取日志内容（用于提取统计信息）
            log_content = analysis_report.get('log_content', '')
            
            # 创建报告文档
            doc_info = report_generator.create_report_document(
                ticket_id=ticket_id,
                ticket_info=ticket_info or {},
                analysis_results=analysis_results,
                execution_steps=execution_steps,
                log_content=log_content
            )
            
            if doc_info:
                doc_url = doc_info.get('doc_url', '')
                doc_title = doc_info.get('title', '故障分析报告')
                
                # 构建回填内容（包含文档链接）
                result_content = f"""分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

故障分析报告已生成，请查看：
{doc_url}

报告标题: {doc_title}
"""
            else:
                # 如果创建文档失败，回退到文本报告
                print("[!] 警告: 创建飞书文档失败，使用文本报告")
                from log_analyzer import LogAnalyzer
                analyzer = LogAnalyzer()
                report_text = analyzer.generate_analysis_report(analysis_report)
                formatted_report = self.format_report_for_bitable(report_text)
                result_content = f"""
分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

{formatted_report}
"""
        except Exception as e:
            print(f"[!] 警告: 生成飞书文档报告失败: {e}")
            print("    回退到文本报告")
            import traceback
            traceback.print_exc()
            
            # 回退到文本报告
            from log_analyzer import LogAnalyzer
            analyzer = LogAnalyzer()
            report_text = analyzer.generate_analysis_report(analysis_report)
            formatted_report = self.format_report_for_bitable(report_text)
            result_content = f"""
分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

{formatted_report}
"""
        
        # 获取回填字段名和字段ID
        result_field_name = get_field_name("工具回传")
        result_field_id = self._get_field_id_by_name(result_field_name)
        
        if not result_field_id:
            print(f"[!] 警告: 无法获取字段ID，尝试使用字段名: {result_field_name}")
            result_field_id = result_field_name
        
        # 更新字段（使用字段ID）
        success = self.update_ticket_field_by_id(ticket_id, result_field_id, result_content.strip())
        
        if success:
            print()
            print("[OK] 分析结果已成功回填到问题单")
            print(f"字段: {result_field_name}")
            if doc_info:
                print(f"报告文档: {doc_info.get('doc_url', '')}")
        else:
            print()
            print("[X] 分析结果回填失败")
        
        return success


def write_result_to_ticket(ticket_id: str, analysis_report: Dict[str, Any]) -> bool:
    """
    将分析结果写入问题单（便捷函数）
    
    Args:
        ticket_id: 问题单记录ID
        analysis_report: 分析报告字典
        
    Returns:
        是否写入成功
    """
    writer = FaultResultWriter()
    return writer.write_analysis_result(ticket_id, analysis_report)

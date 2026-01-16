# -*- coding: utf-8 -*-
"""
故障分析报告生成器

生成结构化的飞书文档报告，展示故障相关信息
"""

import sys
import os
import re
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from feishu_api_wrapper import FeishuAPI
from feishu_doc_collaborator import FeishuDocCollaborator
from fault_diagnosis_config import (
    SPACE_ID, APP_ID, APP_SECRET,
    get_dynamic_user_access_token,
    REPORT_PARENT_NODE_TOKEN
)
from fault_statistics_extractor import FaultStatisticsExtractor
from fault_summary_grep import FaultSummaryGrep

# 修复Windows控制台编码问题
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass


class FaultReportGenerator:
    """故障分析报告生成器"""
    
    def __init__(self, parent_node_token: Optional[str] = None):
        """
        初始化报告生成器
        
        Args:
            parent_node_token: 父节点token（可选，用于指定报告存放位置，默认使用配置中的节点）
        """
        self.api = FeishuAPI(
            plugin_id="",
            plugin_secret="",
            app_id=APP_ID,
            app_secret=APP_SECRET
        )
        self.api.set_user_access_token(get_dynamic_user_access_token())
        
        self.doc_collaborator = FeishuDocCollaborator(
            app_id=APP_ID,
            app_secret=APP_SECRET,
            user_access_token=get_dynamic_user_access_token(),
            space_id=SPACE_ID
        )
        
        self.space_id = SPACE_ID
        # 使用配置中的父节点，如果没有指定则使用默认值
        self.parent_node_token = parent_node_token or REPORT_PARENT_NODE_TOKEN
        self.statistics_extractor = FaultStatisticsExtractor()
        self.summary_grep = FaultSummaryGrep()
    
    def create_report_document(
        self,
        ticket_id: str,
        ticket_info: Dict[str, Any],
        analysis_results: List[Dict[str, Any]],
        execution_steps: Optional[List[Dict[str, Any]]] = None,
        log_content: str = ""
    ) -> Optional[Dict[str, Any]]:
        """
        创建故障分析报告文档
        
        Args:
            ticket_id: 问题单ID
            ticket_info: 问题单信息
            analysis_results: 分析结果列表
            execution_steps: 执行步骤列表（可选）
            log_content: 日志内容（用于提取统计信息）
            
        Returns:
            文档信息字典（包含node_token, document_id, doc_url）或None
        """
        # 生成文档标题（格式：分析时间_工作项id_提出时间）
        work_item_id = ticket_info.get('工作项ID', ticket_id)
        
        # 提取提出时间（从ticket_info的fields中提取"创建时间"）
        submit_date = datetime.now().strftime('%Y/%m/%d')  # 默认值
        
        # 从ticket_info的fields中提取创建时间
        fields = ticket_info.get('fields', {})
        create_time = fields.get('创建时间', '')
        
        if create_time:
            try:
                # 如果是时间戳（毫秒）
                if isinstance(create_time, (int, float)):
                    # 转换为秒（如果是毫秒）
                    if create_time > 1e12:  # 毫秒时间戳
                        create_time = create_time / 1000
                    dt = datetime.fromtimestamp(create_time)
                    submit_date = dt.strftime('%Y/%m/%d')
                elif isinstance(create_time, str):
                    # 尝试解析字符串格式
                    # 如果是时间戳字符串
                    try:
                        ts = int(create_time)
                        if ts > 1e12:  # 毫秒时间戳
                            ts = ts / 1000
                        dt = datetime.fromtimestamp(ts)
                        submit_date = dt.strftime('%Y/%m/%d')
                    except:
                        # 尝试解析日期字符串
                        for fmt in ['%Y-%m-%d %H:%M:%S', '%Y/%m/%d %H:%M:%S', '%Y-%m-%d', '%Y/%m/%d']:
                            try:
                                dt = datetime.strptime(create_time.split()[0], fmt.split()[0])
                                submit_date = dt.strftime('%Y/%m/%d')
                                break
                            except:
                                continue
            except Exception as e:
                print(f"[!] 解析创建时间失败: {e}")
        
        analysis_time = datetime.now().strftime('%Y%m%d')
        submit_date_formatted = submit_date.replace('/', '')
        doc_title = f"{analysis_time}_{work_item_id}_{submit_date_formatted}"
        
        print(f"创建报告文档: {doc_title}")
        
        # 检查是否已存在相同标题的文档
        doc_info = self.doc_collaborator.create_or_find_doc(
            doc_title=doc_title,
            parent_node_token=self.parent_node_token,
            auto_create=True
        )
        
        if not doc_info:
            print("[X] 创建/查找文档失败")
            return None
        
        document_id = doc_info['document_id']
        node_token = doc_info['node_token']
        doc_url = doc_info['doc_url']
        
        # 检查文档是否已存在（通过检查doc_info中是否有'is_existing'标记）
        is_existing = doc_info.get('is_existing', False)
        
        if is_existing:
            print(f"[OK] 找到已存在的文档: {doc_url}")
            print("[!] 清空旧内容...")
            # 清空旧内容
            self.doc_collaborator._clear_document_content(document_id)
        else:
            print(f"[OK] 文档创建成功: {doc_url}")
        
        # 生成报告内容
        report_content = self._generate_report_content(
            ticket_id, ticket_info, analysis_results, execution_steps, log_content
        )
        
        # 写入文档内容
        print(f"[DEBUG] 准备写入文档，blocks数量: {len(report_content)}")
        # 检查blocks结构
        block_types = [b.get('block_type') for b in report_content[:10]]
        print(f"[DEBUG] 前10个blocks类型: {block_types}")
        success = self._write_document_content(document_id, report_content)
        
        # 更新doc_info，确保包含doc_url
        doc_info['doc_url'] = doc_url
        
        if success:
            print(f"[OK] 报告内容已写入文档")
            return {
                'node_token': node_token,
                'document_id': document_id,
                'doc_url': doc_url,
                'title': doc_title
            }
        else:
            print(f"[!] 警告: 文档已创建但内容写入失败")
            return doc_info
    
    def _generate_report_content(
        self,
        ticket_id: str,
        ticket_info: Dict[str, Any],
        analysis_results: List[Dict[str, Any]],
        execution_steps: Optional[List[Dict[str, Any]]] = None,
        log_content: str = ""
    ) -> List[Dict[str, Any]]:
        """
        生成报告内容结构（综合性总结 + 表格）
        
        Returns:
            块结构列表
        """
        # 调试：检查log_content长度
        print(f"[DEBUG] _generate_report_content: log_content长度={len(log_content)}, analysis_results数量={len(analysis_results)}, execution_steps数量={len(execution_steps) if execution_steps else 0}")
        
        blocks = []
        
        # 1. 标题
        blocks.append({
            "block_type": 3,  # 标题1
            "heading1": {
                "elements": [{
                    "text_run": {
                        "content": "故障分析报告"
                    }
                }]
            }
        })
        
        # 2. 综合性总结
        blocks.append({
            "block_type": 4,  # 标题2
            "heading2": {
                "elements": [{
                    "text_run": {
                        "content": "综合分析总结"
                    }
                }]
            }
        })
        
        # 统计信息
        all_fault_ids = set()
        fault_ids_with_guide = 0
        fault_ids_without_guide = 0
        for result in analysis_results:
            fault_id = result.get('fault_id', '')
            if fault_id:
                all_fault_ids.add(fault_id)
                if result.get('guide_info'):
                    fault_ids_with_guide += 1
                else:
                    fault_ids_without_guide += 1
        
        summary_text = f"""工作项ID: {ticket_info.get('工作项ID', 'N/A')}
记录ID: {ticket_id}
分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

本次分析共提取到 {len(all_fault_ids)} 个Fault ID，其中：
- 找到故障定位指引的Fault ID: {fault_ids_with_guide} 个
- 未找到故障定位指引的Fault ID: {fault_ids_without_guide} 个

"""
        if '日志路径' in ticket_info:
            summary_text += f"日志路径: {ticket_info['日志路径']}\n"
        
        blocks.append({
            "block_type": 2,  # 文本块
            "text": {
                "elements": [{
                    "text_run": {
                        "content": summary_text
                    }
                }]
            }
        })
        
        # 3. 详细分析表格
        blocks.append({
            "block_type": 4,  # 标题2
            "heading2": {
                "elements": [{
                    "text_run": {
                        "content": "Fault ID详细分析表"
                    }
                }]
            }
        })
        
        # 检查analysis_results是否为空
        if not analysis_results:
            blocks.append({
                "block_type": 2,  # 文本块
                "text": {
                    "elements": [{
                        "text_run": {
                            "content": "警告: 未找到分析结果数据"
                        }
                    }]
                }
            })
            return blocks
        
        # 创建表格
        # 表格结构：fa_id | fu_st | 首次出现时间 | 最后出现时刻 | 出现次数 | 故障概要 | 故障可能的原因 | 备注
        table_rows = []
        
        # 表头
        table_rows.append([
            "fa_id",
            "fu_st",
            "首次出现时间",
            "最后出现时刻",
            "出现次数",
            "故障概要",
            "故障可能的原因",
            "备注"
        ])
        
        # 数据行
        for result in analysis_results:
            fault_id = result.get('fault_id', 'N/A')
            if not fault_id or fault_id == 'N/A':
                continue
            
            # 提取统计信息
            # 调试：检查log_content是否为空
            if not log_content:
                print(f"[!] 警告: Fault ID {fault_id} 的log_content为空，无法提取统计信息")
            else:
                # 调试：检查log_content中是否包含SetFunc和fu_st:0x3/0x4
                has_setfunc = 'SetFunc' in log_content
                setfunc_lines = [l for l in log_content.split('\n') if 'SetFunc' in l]
                setfunc_fu_st_lines = [l for l in setfunc_lines if ('fu_st:0x3' in l or 'fu_st:0x4' in l)]
                print(f"[DEBUG] Fault ID {fault_id}: log_content长度={len(log_content)}, 包含SetFunc={has_setfunc}, SetFunc行数={len(setfunc_lines)}, SetFunc+fu_st:0x3/0x4行数={len(setfunc_fu_st_lines)}")
            stats = self.statistics_extractor.extract_statistics(log_content, fault_id)
            
            # 调试：打印统计信息
            if fault_id in ['0x165', '0x0165']:
                print(f"[DEBUG] Fault ID {fault_id} 统计信息: {stats}")
            
            # 获取指引信息（提前获取，供后续使用）
            guide_info = result.get('guide_info', {})
            
            # fa_id
            fa_id = fault_id
            
            # fu_st
            fu_st = stats.get('fu_st', 'N/A')
            if not fu_st:
                fu_st = 'N/A'
            
            # 首次出现时间
            first_occurrence = stats.get('first_occurrence', 'N/A')
            if not first_occurrence:
                first_occurrence = 'N/A'
            
            # 最后出现时刻
            last_occurrence = stats.get('last_occurrence', 'N/A')
            if not last_occurrence:
                last_occurrence = 'N/A'
            
            # 出现次数
            occurrence_count = stats.get('occurrence_count', 0)
            
            # 故障概要（从功能安全业务数据中grep，提取详细信息）
            fault_summary = self.summary_grep.grep_fault_summary(fault_id)
            # 调试：打印故障概要提取结果
            if fault_id in ['0x165', '0x0165']:
                print(f"[DEBUG] Fault ID {fault_id} 故障概要提取结果: {fault_summary[:200] if fault_summary else 'None'}...")
            # 如果提取到的信息太短或未找到，尝试从指引文档中补充
            if (not fault_summary or len(fault_summary) < 50 or "未在功能安全业务数据中找到相关信息" in fault_summary) and guide_info:
                guide_desc = guide_info.get('故障描述', guide_info.get('描述', guide_info.get('故障名称', '')))
                if guide_desc:
                    if fault_summary and "未在功能安全业务数据中找到相关信息" not in fault_summary:
                        fault_summary = guide_desc + "\n" + fault_summary
                    else:
                        fault_summary = guide_desc
            if len(fault_summary) > 500:
                fault_summary = fault_summary[:500] + "..."
            
            # 故障可能的原因（基于故障定位指引文档的语义内容和AI分析）
            analysis = result.get('analysis', {})
            if not analysis:
                analysis = {
                    'summary': '',
                    'key_findings': result.get('analysis_points', []),
                    'recommendations': []
                }
            
            possible_causes = ''
            
            # 优先从指引文档中提取
            if guide_info:
                # 尝试从指引文档内容中提取可能的原因
                guide_content = guide_info.get('content', '')
                if not guide_content:
                    # 尝试从guide_info中获取完整内容
                    guide_content = guide_info.get('完整内容', '')
                if not guide_content:
                    guide_content = str(guide_info)
                
                # 基于指引文档语义进行AI分析
                possible_causes = self._analyze_possible_causes_from_guide(guide_content, fault_id)
                # 调试：打印原因分析结果
                if fault_id in ['0x165', '0x0165']:
                    print(f"[DEBUG] Fault ID {fault_id} 原因分析结果: {possible_causes[:200] if possible_causes else 'None'}...")
                
                # 如果指引中有明确的原因字段，优先使用
                if not possible_causes:
                    possible_causes = guide_info.get('常见原因', guide_info.get('可能原因', guide_info.get('原因', '')))
            
            # 如果指引中没有，使用分析结果
            if not possible_causes:
                if analysis.get('key_findings'):
                    possible_causes = '; '.join(analysis['key_findings'][:3])
                elif result.get('analysis_points'):
                    possible_causes = '; '.join(result['analysis_points'][:3])
                else:
                    possible_causes = '待进一步分析'
            
            if len(possible_causes) > 300:
                possible_causes = possible_causes[:300] + "..."
            
            # 备注
            remarks = '无'
            if result.get('key_errors'):
                error_count = len(result.get('key_errors', []))
                if error_count > 0:
                    remarks = f"发现{error_count}个关键错误"
            if result.get('modules_affected'):
                modules = result.get('modules_affected', [])
                if modules:
                    remarks += f"; 涉及模块: {', '.join(modules[:3])}"
            
            table_rows.append([
                fa_id,
                fu_st,
                first_occurrence,
                last_occurrence,
                str(occurrence_count),
                fault_summary[:500] if len(fault_summary) > 500 else fault_summary,
                possible_causes,
                remarks[:200] if len(remarks) > 200 else remarks
            ])
        
        # 创建表格（使用飞书原生表格API）
        print(f"[DEBUG] 表格数据: 表头数量={len(table_rows[0]) if table_rows else 0}, 数据行数量={len(table_rows)-1 if len(table_rows) > 1 else 0}")
        if len(table_rows) > 1:  # 至少有表头和数据行
            # 使用特殊标记，后续单独处理表格
            blocks.append({
                "block_type": 999,  # 特殊标记，表示这是表格
                "_table_data": {
                    "headers": table_rows[0],
                    "rows": table_rows[1:]
                }
            })
            print(f"[DEBUG] 表格块已添加到blocks，当前blocks数量: {len(blocks)}")
        else:
            # 如果没有数据，显示提示
            blocks.append({
                "block_type": 2,  # 文本块
                "text": {
                    "elements": [{
                        "text_run": {
                            "content": "未找到Fault ID分析数据"
                        }
                    }]
                }
            })
        
        # 4. 系统流程验证（在表格后）
        print(f"[DEBUG] execution_steps: {execution_steps}, 类型: {type(execution_steps)}, 长度: {len(execution_steps) if execution_steps else 0}")
        if execution_steps and len(execution_steps) > 0:
            blocks.append({
                "block_type": 4,  # 标题2
                "heading2": {
                    "elements": [{
                        "text_run": {
                            "content": "系统流程验证"
                        }
                    }]
                }
            })
            
            for i, step in enumerate(execution_steps, 1):
                step_name = step.get('step', '未知步骤')
                success = step.get('success', False)
                status_icon = "✅" if success else "❌"
                
                # 步骤名称映射
                step_name_map = {
                    'get_ticket_info': '步骤1: 获取问题单信息',
                    'extract_log_path': '步骤2: 提取日志路径',
                    'extract_fault_id': '步骤3: 提取Fault ID',
                    'analyze_log': '步骤4: 分析Fault ID',
                    'generate_report': '步骤5: 生成分析报告',
                    'write_result': '步骤6: 回填分析结果'
                }
                step_display_name = step_name_map.get(step_name, f"步骤{i}: {step_name}")
                
                step_text = f"**{step_display_name}** {status_icon}\n"
                
                # 添加详细信息
                if 'log_paths' in step:
                    log_paths = step['log_paths']
                    step_text += f"- 日志路径: {', '.join(log_paths[:3])}\n"
                if 'fault_ids' in step:
                    fault_ids = step['fault_ids']
                    step_text += f"- 提取到 {len(fault_ids)} 个Fault ID: {', '.join(fault_ids[:5])}\n"
                if 'analysis_count' in step:
                    step_text += f"- 分析了 {step['analysis_count']} 个Fault ID\n"
                if 'error' in step:
                    step_text += f"- 错误: {step['error']}\n"
                
                blocks.append({
                    "block_type": 2,  # 文本块
                    "text": {
                        "elements": [{
                            "text_run": {
                                "content": step_text
                            }
                    }]
                }
            })
            print(f"[DEBUG] 系统流程验证已添加，当前blocks数量: {len(blocks)}")
        else:
            print(f"[DEBUG] 警告: execution_steps为空或长度为0，跳过系统流程验证")
        
        print(f"[DEBUG] _generate_report_content完成，总blocks数量: {len(blocks)}")
        return blocks
    
    def _analyze_possible_causes_from_guide(self, guide_content: str, fault_id: str) -> str:
        """
        基于故障定位指引文档的语义内容进行AI分析，提取可能的原因
        
        Args:
            guide_content: 指引文档内容
            fault_id: Fault ID
            
        Returns:
            可能的原因文本
        """
        if not guide_content:
            return ''
        
        # 提取关键信息
        causes = []
        
        # 1. 查找"原因"相关章节
        cause_patterns = [
            r'原因[：:]\s*(.+?)(?:\n|$)',
            r'可能的原因[：:]\s*(.+?)(?:\n|$)',
            r'常见原因[：:]\s*(.+?)(?:\n|$)',
            r'原因分析[：:]\s*(.+?)(?:\n|$)',
        ]
        
        for pattern in cause_patterns:
            matches = re.finditer(pattern, guide_content, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                cause_text = match.group(1).strip()
                if cause_text and len(cause_text) > 5:
                    causes.append(cause_text[:200])
        
        # 2. 基于关键词分析
        if not causes:
            # 检查是否涉及特定模块或功能
            if '轨迹' in guide_content or 'trajectory' in guide_content.lower():
                causes.append('轨迹规划模块异常或通信链路问题')
            if '通信' in guide_content or 'communication' in guide_content.lower() or 'topic' in guide_content.lower():
                causes.append('通信链路异常或消息丢失')
            if '传感器' in guide_content or 'sensor' in guide_content.lower():
                causes.append('传感器数据异常或传感器故障')
            if '规划' in guide_content or 'planning' in guide_content.lower():
                causes.append('规划模块异常或规划算法执行超时')
            if '负载' in guide_content or 'load' in guide_content.lower() or '性能' in guide_content:
                causes.append('系统负载过高或资源耗尽')
            if '上游' in guide_content or 'upstream' in guide_content.lower():
                causes.append('上游依赖模块异常')
        
        # 3. 从指引文档中提取具体原因（查找列表项）
        if not causes:
            # 查找编号列表中的原因
            list_patterns = [
                r'\d+[\.、]\s*([^。\n]+(?:异常|故障|问题|失败|错误))',
                r'[-•]\s*([^。\n]+(?:异常|故障|问题|失败|错误))',
            ]
            
            for pattern in list_patterns:
                matches = re.finditer(pattern, guide_content, re.IGNORECASE)
                for match in matches:
                    cause_text = match.group(1).strip()
                    if cause_text and len(cause_text) > 5 and len(cause_text) < 100:
                        causes.append(cause_text)
                        if len(causes) >= 5:
                            break
                if len(causes) >= 5:
                    break
        
        if causes:
            # 去重并合并
            unique_causes = []
            seen = set()
            for cause in causes:
                if cause not in seen:
                    unique_causes.append(cause)
                    seen.add(cause)
            return '; '.join(unique_causes[:5])
        
        return ''
    
    def _write_document_content(
        self,
        document_id: str,
        blocks: List[Dict[str, Any]]
    ) -> bool:
        """
        写入文档内容
        
        Args:
            document_id: 文档ID
            blocks: 块结构列表
            
        Returns:
            是否成功
        """
        try:
            from feishu_table_helper import create_table_structure
            
            # 按顺序写入块，保持表格在正确位置
            batch_size = 20
            current_batch = []
            last_block_id = document_id  # 用于跟踪最后一个块ID，以便在正确位置插入表格
            
            for i, block in enumerate(blocks):
                if block.get('block_type') == 999 and '_table_data' in block:
                    # 这是表格块，先写入当前批次，然后处理表格
                    if current_batch:
                        result = self.api.create_block(
                            document_id=document_id,
                            block_id=document_id,
                            children=current_batch,
                            use_user_token=True
                        )
                        if not result:
                            print(f"[!] 警告: 写入批次失败")
                            return False
                        current_batch = []
                    
                    # 处理表格块
                    table_data = block.get('_table_data', {})
                    headers = table_data.get('headers', [])
                    rows = table_data.get('rows', [])
                    
                    if headers and rows:
                        # 创建表格结构
                        table_structure = create_table_structure(headers, rows, max_rows=100)
                        if table_structure:
                            # 使用create_descendant创建表格
                            result = self.api.create_descendant(
                                document_id=document_id,
                                block_id=document_id,
                                children_id=table_structure['children_id'],
                                descendants=table_structure['descendants'],
                                use_user_token=True
                            )
                            if not result:
                                print(f"[!] 警告: 创建表格失败，回退到Markdown格式")
                                # 回退到Markdown格式
                                table_header = "| " + " | ".join(headers) + " |\n"
                                table_header += "| " + " | ".join(["---"] * len(headers)) + " |\n"
                                table_body = ""
                                for row in rows:
                                    escaped_row = [str(cell).replace("|", "\\|").replace("\n", " ").replace("\r", " ") for cell in row]
                                    table_body += "| " + " | ".join(escaped_row) + " |\n"
                                table_markdown = table_header + table_body
                                
                                # 作为文本块写入
                                self.api.create_block(
                                    document_id=document_id,
                                    block_id=document_id,
                                    children=[{
                                        "block_type": 2,
                                        "text": {
                                            "elements": [{
                                                "text_run": {
                                                    "content": table_markdown
                                                }
                                            }]
                                        }
                                    }],
                                    use_user_token=True
                                )
                else:
                    # 普通块，添加到批次
                    current_batch.append(block)
                    if len(current_batch) >= batch_size:
                        result = self.api.create_block(
                            document_id=document_id,
                            block_id=document_id,
                            children=current_batch,
                            use_user_token=True
                        )
                        if not result:
                            print(f"[!] 警告: 写入批次失败")
                            return False
                        current_batch = []
            
            # 写入剩余的块
            if current_batch:
                result = self.api.create_block(
                    document_id=document_id,
                    block_id=document_id,
                    children=current_batch,
                    use_user_token=True
                )
                if not result:
                    print(f"[!] 警告: 写入最后批次失败")
                    print(f"[DEBUG] 最后批次blocks数量: {len(current_batch)}")
                    return False
            
            print(f"[OK] 文档内容写入成功，共写入 {len(blocks)} 个blocks")
            return True
        except Exception as e:
            print(f"[X] 写入文档内容失败: {e}")
            import traceback
            traceback.print_exc()
            # 如果表格创建失败，尝试回退到Markdown格式
            try:
                print("[!] 尝试回退到Markdown表格格式...")
                # 重新处理，将所有块都作为普通块写入
                normal_blocks = []
                for block in blocks:
                    if block.get('block_type') == 999 and '_table_data' in block:
                        # 转换为Markdown表格
                        table_data = block.get('_table_data', {})
                        headers = table_data.get('headers', [])
                        rows = table_data.get('rows', [])
                        if headers and rows:
                            table_header = "| " + " | ".join(headers) + " |\n"
                            table_header += "| " + " | ".join(["---"] * len(headers)) + " |\n"
                            table_body = ""
                            for row in rows:
                                escaped_row = [str(cell).replace("|", "\\|").replace("\n", " ").replace("\r", " ") for cell in row]
                                table_body += "| " + " | ".join(escaped_row) + " |\n"
                            table_markdown = table_header + table_body
                            normal_blocks.append({
                                "block_type": 2,
                                "text": {
                                    "elements": [{
                                        "text_run": {
                                            "content": table_markdown
                                        }
                                    }]
                                }
                            })
                    else:
                        normal_blocks.append(block)
                
                # 写入所有块
                batch_size = 20
                for i in range(0, len(normal_blocks), batch_size):
                    batch = normal_blocks[i:i+batch_size]
                    self.api.create_block(
                        document_id=document_id,
                        block_id=document_id,
                        children=batch,
                        use_user_token=True
                    )
                return True
            except Exception as e2:
                print(f"[X] 回退方案也失败: {e2}")
                return False

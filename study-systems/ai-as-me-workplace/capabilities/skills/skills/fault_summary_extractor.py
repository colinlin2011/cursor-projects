# -*- coding: utf-8 -*-
"""
故障概况提取能力

从"06. 安全需求总表"多维表格缓存中查询fa_id相关信息，整合多个来源生成综合故障概况
"""

import sys
import os
import json
import re
from typing import Optional, Dict, List, Any
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 修复Windows控制台编码问题
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

from bitable_query_interface import get_query_interface
from fault_guide_reader import get_guide_reader


class FaultSummaryExtractor:
    """故障概况提取器"""
    
    def __init__(self):
        """初始化提取器"""
        self.bitable_interface = get_query_interface()
        self.guide_reader = get_guide_reader()
        # "功能安全业务数据"是一个多维表格（https://zyt.feishu.cn/wiki/BPddwBxoRiPFSsk8jZJctCMmndg）
        # 包含14个表，其中"06. 安全需求总表(同步Polarion Safety空间需求"就是我们要查询的表
        # 使用表的全局地址来定位，避免表名变更导致的问题
        self.safety_requirement_table_url = "https://zyt.feishu.cn/wiki/BPddwBxoRiPFSsk8jZJctCMmndg?table=tbl3akMZjFE962Db&view=vew5AoL8Jc"
        self.safety_requirement_table_id = "tbl3akMZjFE962Db"  # 从URL中提取的table_id
        self.safety_requirement_table_name = "06. 安全需求总表"  # 保留作为备用（模糊匹配时使用）
        self.cache_file = "new_bitable.json"  # "功能安全业务数据"多维表格的缓存文件
    
    def extract_fault_summary(self, fa_id: str, use_grep: bool = True) -> Dict[str, Any]:
        """
        提取故障概况
        
        从以下来源提取信息：
        1. 故障定位指引文档
        2. "06. 安全需求总表"多维表格
        3. "功能安全业务数据"多维表格（通过grep）
        
        Args:
            fa_id: Fault ID（如0x0165）
            use_grep: 是否使用grep查询（数据量大时使用）
            
        Returns:
            故障概况字典，包含：
            - fault_id: 故障ID
            - guide_info: 指引文档信息
            - safety_requirement_info: 安全需求总表信息
            - bitable_summary: 多维表格概要信息
            - summary_text: 综合故障概况文本
        """
        # 规范化fa_id
        normalized_fa_id = self._normalize_fault_id(fa_id)
        
        print(f"[INFO] 开始提取故障概况: {normalized_fa_id}")
        print()
        
        result = {
            'fault_id': normalized_fa_id,
            'guide_info': None,
            'safety_requirement_info': None,
            'bitable_summary': None,
            'ai_analysis': None,
            'summary_text': ''
        }
        
        # 1. 先从"06. 安全需求总表"获取结构化信息（优先）
        print("[1/3] 查询安全需求总表...")
        safety_info = self._query_safety_requirement_table(normalized_fa_id, use_grep)
        if safety_info:
            result['safety_requirement_info'] = safety_info
            print(f"[OK] 找到安全需求总表信息")
        else:
            print(f"[!] 未找到安全需求总表信息")
        print()
        
        # 2. 基于安全需求总表的信息，在故障定位指引文档中查找相关描述
        print("[2/3] 基于安全需求总表信息，查询故障定位指引文档...")
        guide_info = None
        
        if safety_info:
            # 基于安全需求总表的信息进行语义搜索
            guide_info = self._search_guide_by_semantic(normalized_fa_id, safety_info)
        else:
            # 如果没有安全需求总表信息，使用原来的搜索方式
            guide_info = self.guide_reader.get_guide_by_fault_id(normalized_fa_id)
            if not guide_info:
                print(f"[INFO] 精确匹配失败，尝试在文档内容中搜索...")
                guide_info = self._search_guide_by_content(normalized_fa_id)
        
        if guide_info:
            result['guide_info'] = guide_info
            print(f"[OK] 找到指引文档信息")
        else:
            print(f"[!] 未找到指引文档信息")
        print()
        
        # 3. 从"功能安全业务数据"多维表格获取概要信息
        # 注意："功能安全业务数据"是一个多维表格，包含14个表
        # 其中"06. 安全需求总表(同步Polarion Safety空间需求"就是我们要查询的表
        # 所以这里直接使用步骤1中已经查询过的安全需求总表信息，不需要再单独查询
        print("[3/4] 查询功能安全业务数据...")
        # "功能安全业务数据"就是"06. 安全需求总表"，已经在步骤1中查询过了
        if safety_info:
            # 将安全需求总表信息作为功能安全业务数据的结果
            result['bitable_summary'] = self._format_bitable_summary(safety_info)
            print(f"[OK] 功能安全业务数据查询完成（使用安全需求总表数据）")
        else:
            print(f"[!] 未找到功能安全业务数据信息")
        print()
        
        # 4. 基于专家认知进行原因分析
        print("[4/4] 基于专家认知进行原因分析...")
        if safety_info:
            ai_analysis = self._generate_expert_analysis(normalized_fa_id, safety_info, guide_info)
            result['ai_analysis'] = ai_analysis
            if ai_analysis:
                print(f"[OK] 生成专家分析")
            else:
                print(f"[!] 未生成专家分析")
        else:
            print(f"[!] 缺少安全需求总表信息，无法进行专家分析")
        print()
        
        # 5. 生成综合故障概况文本
        result['summary_text'] = self._generate_summary_text(result)
        
        # 6. 生成AI总结提示词（用于Cursor AI总结）
        result['ai_summary_prompt'] = self._generate_ai_summary_prompt(result)
        
        return result
    
    def _query_safety_requirement_table(self, fa_id: str, use_grep: bool = True) -> Optional[Dict[str, Any]]:
        """
        从"06. 安全需求总表"查询fa_id相关信息
        
        Args:
            fa_id: Fault ID
            use_grep: 是否使用grep查询（数据量大时使用）
            
        Returns:
            匹配的记录信息字典
        """
        # 规范化fa_id用于匹配
        fa_id_patterns = self._get_fault_id_patterns(fa_id)
        
        # 优先使用table_id查询（更可靠，不受表名变更影响）
        print(f"[INFO] 使用table_id查询: {self.safety_requirement_table_id}")
        table_data = self.bitable_interface.get_table_data(
            table_id=self.safety_requirement_table_id,
            cache_file=self.cache_file
        )
        
        # 如果table_id查询失败，尝试使用表名查询（作为备用）
        if not table_data:
            print(f"[INFO] table_id查询失败，尝试使用表名查询...")
            table_data = self.bitable_interface.get_table_data(
                table_name=self.safety_requirement_table_name,
                cache_file=self.cache_file
            )
        
        # 如果表名精确匹配失败，尝试模糊匹配（包含"06. 安全需求总表"的表）
        if not table_data:
            print(f"[INFO] 精确匹配表名失败，尝试模糊匹配...")
            try:
                from bitable_cache_manager import CACHE_DIR
                cache_path = CACHE_DIR / self.cache_file
                if cache_path.exists():
                    with open(cache_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        tables = data.get('tables', {})
                        
                        # 首先尝试通过table_id查找
                        for table_name, table_info in tables.items():
                            if isinstance(table_info, dict) and table_info.get('table_id') == self.safety_requirement_table_id:
                                print(f"[INFO] 通过table_id找到表: {table_name}")
                                table_data = table_info
                                break
                        
                        # 如果table_id查找失败，查找包含"06. 安全需求总表"的表名
                        if not table_data:
                            for table_name in tables.keys():
                                if "06. 安全需求总表" in table_name or "安全需求总表" in table_name:
                                    print(f"[INFO] 找到匹配的表: {table_name}")
                                    table_data = tables[table_name]
                                    break
                        
                        if not table_data:
                            print(f"[!] 未找到匹配的数据表")
                            print(f"[INFO] 可用的数据表: {', '.join(list(tables.keys())[:10])}")
            except Exception as e:
                print(f"[!] 查找表失败: {e}")
                return None
        
        if not table_data:
            return None
        
        records = table_data.get('records', [])
        if not records:
            print(f"[!] 数据表中没有记录")
            return None
        
        print(f"[INFO] 表中共有 {len(records)} 条记录")
        
        # 如果数据量大，使用grep方式
        if use_grep and len(records) > 100:
            print(f"[INFO] 数据量较大，使用grep方式查询")
            return self._grep_in_table(table_data, fa_id_patterns)
        
        # 否则遍历所有记录
        matches = []
        for record in records:
            if not isinstance(record, dict):
                continue
            
            fields = record.get('fields', {})
            if not isinstance(fields, dict):
                continue
            
            # 检查是否包含fa_id
            if self._record_contains_fault_id(fields, fa_id_patterns):
                matches.append({
                    'record_id': record.get('record_id', ''),
                    'fields': fields
                })
        
        if not matches:
            print(f"[!] 在'{self.safety_requirement_table_name}'中未找到fa_id {fa_id}的相关信息")
            return None
        
        print(f"[OK] 找到 {len(matches)} 条匹配记录")
        
        # 提取关键信息
        return self._extract_key_info_from_matches(matches)
    
    def _grep_in_table(self, table_data: Dict, fa_id_patterns: List[str]) -> Optional[Dict[str, Any]]:
        """
        使用grep方式在表中搜索（适用于大数据量）
        
        Args:
            table_data: 表数据
            fa_id_patterns: fa_id匹配模式列表
            
        Returns:
            匹配的信息字典
        """
        # 将表数据序列化为文本进行grep
        records = table_data.get('records', [])
        matches = []
        
        for record in records:
            if not isinstance(record, dict):
                continue
            
            # 将记录转换为文本
            record_text = json.dumps(record, ensure_ascii=False)
            
            # 检查是否匹配fa_id
            for pattern in fa_id_patterns:
                if re.search(pattern, record_text, re.IGNORECASE):
                    matches.append(record)
                    break
        
        if not matches:
            return None
        
        print(f"[OK] grep找到 {len(matches)} 条匹配记录")
        return self._extract_key_info_from_matches(matches)
    
    def _record_contains_fault_id(self, fields: Dict, fa_id_patterns: List[str]) -> bool:
        """
        检查记录是否包含fa_id（智能匹配）
        
        Args:
            fields: 记录字段字典
            fa_id_patterns: fa_id匹配模式列表
            
        Returns:
            是否包含fa_id
        """
        # 将整个记录转换为文本进行搜索（更智能）
        record_text = json.dumps(fields, ensure_ascii=False)
        
        # 使用模式匹配
        for pattern in fa_id_patterns:
            if re.search(pattern, record_text, re.IGNORECASE):
                return True
        
        # 也检查各个字段值（双重检查）
        for field_name, field_value in fields.items():
            if not field_value:
                continue
            
            field_str = str(field_value)
            
            # 使用模式匹配
            for pattern in fa_id_patterns:
                if re.search(pattern, field_str, re.IGNORECASE):
                    return True
        
        return False
    
    def _extract_key_info_from_matches(self, matches: List[Dict]) -> Dict[str, Any]:
        """
        从匹配记录中提取关键信息（去重、去冗余）
        
        Args:
            matches: 匹配的记录列表
            
        Returns:
            关键信息字典
        """
        if not matches:
            return None
        
        # 关键字段映射（优先级从高到低）
        field_mapping = {
            'fault_id': ['Fault ID', 'Fault_ID', 'FaultId', 'fault_id', 'fa_id'],
            'fault_name': ['Fault Name', 'Fault_Name', '故障名称'],
            'fault_description': ['Fault Description', 'Fault_Description', 'Description', '故障描述'],
            'asil': ['ASIL', 'ASIL等级'],
            'element': ['Element', '涉及模块'],
            'element_function': ['Element Function', '涉及功能'],
            'trigger_conditions': ['Fault Trigger Conditions', '触发条件'],
            'detection_period': ['检测周期', 'Detection Period', '检测频率'],
        }
        
        extracted_info = {
            'match_count': len(matches),
            'unique_records': []
        }
        
        # 用于去重的集合（基于关键字段组合）
        seen_combinations = set()
        
        for match in matches:
            fields = match.get('fields', {}) if isinstance(match, dict) else match
            
            # 提取关键信息
            record_info = {}
            for key, field_names in field_mapping.items():
                for field_name, field_value in fields.items():
                    # 检查字段名是否匹配
                    if any(fn.lower() in field_name.lower() or field_name.lower() in fn.lower() 
                           for fn in field_names):
                        if field_value:
                            # 处理列表类型
                            if isinstance(field_value, list):
                                if field_value and isinstance(field_value[0], dict):
                                    field_value = ', '.join([str(v.get('text', v)) for v in field_value if v])
                                else:
                                    field_value = ', '.join([str(v) for v in field_value if v])
                            
                            # 清理描述文本（去除重复内容）
                            if key == 'fault_description':
                                field_value = self._clean_description(str(field_value))
                            
                            record_info[key] = str(field_value).strip()
                            break
            
            # 去重：基于fault_id + fault_name + element的组合
            if record_info:
                combo_key = (
                    record_info.get('fault_id', ''),
                    record_info.get('fault_name', ''),
                    record_info.get('element', '')
                )
                
                if combo_key not in seen_combinations:
                    seen_combinations.add(combo_key)
                    extracted_info['unique_records'].append(record_info)
        
        return extracted_info
    
    def _clean_description(self, description: str) -> str:
        """
        清理描述文本，去除重复内容
        
        Args:
            description: 原始描述文本
            
        Returns:
            清理后的描述文本
        """
        if not description:
            return ""
        
        # 如果描述中包含重复的段落，只保留第一个
        lines = description.split('\n')
        seen_lines = set()
        cleaned_lines = []
        
        for line in lines:
            line_stripped = line.strip()
            if not line_stripped:
                continue
            
            # 检查是否是重复内容（相似度>80%）
            is_duplicate = False
            for seen in seen_lines:
                if self._similarity(line_stripped, seen) > 0.8:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                cleaned_lines.append(line)
                seen_lines.add(line_stripped)
        
        return '\n'.join(cleaned_lines)
    
    def _similarity(self, s1: str, s2: str) -> float:
        """计算两个字符串的相似度（简单实现）"""
        if not s1 or not s2:
            return 0.0
        
        s1_lower = s1.lower()
        s2_lower = s2.lower()
        
        if s1_lower == s2_lower:
            return 1.0
        
        # 计算共同字符数
        common = len(set(s1_lower) & set(s2_lower))
        total = len(set(s1_lower) | set(s2_lower))
        
        return common / total if total > 0 else 0.0
    
    def _get_fault_id_patterns(self, fa_id: str) -> List[str]:
        """
        获取fa_id的匹配模式列表
        
        Args:
            fa_id: Fault ID
            
        Returns:
            匹配模式列表
        """
        # 规范化fa_id
        fa_id_upper = fa_id.upper()
        fa_id_clean = fa_id_upper.replace('0X', '').replace('0x', '')
        fa_id_clean_no_zero = fa_id_clean.lstrip('0') or '0'
        
        patterns = [
            rf'\b{re.escape(fa_id_upper)}\b',  # 完整匹配 0x0165
            rf'\b0x{re.escape(fa_id_clean)}\b',  # 0x0165 (带前导0)
            rf'\b0x{re.escape(fa_id_clean_no_zero)}\b',  # 0x165 (无前导0)
            rf'fa_id[:\s=]+{re.escape(fa_id_upper)}',  # fa_id: 0x0165
            rf'fa_id[:\s=]+0x{re.escape(fa_id_clean)}',  # fa_id: 0x0165
            rf'fa_id[:\s=]+0x{re.escape(fa_id_clean_no_zero)}',  # fa_id: 0x165
            rf'Fault\s*ID[:\s]+{re.escape(fa_id_upper)}',  # Fault ID: 0x0165
            rf'fault_id[:\s=]+{re.escape(fa_id_upper)}',  # fault_id: 0x0165
        ]
        
        return patterns
    
    def _search_guide_by_semantic(self, fa_id: str, safety_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        基于安全需求总表的信息，在指引文档中进行语义搜索
        
        Args:
            fa_id: Fault ID
            safety_info: 安全需求总表信息
            
        Returns:
            指引信息字典（如果找到）
        """
        from fault_diagnosis_config import get_guide_docs
        
        # 从安全需求总表信息中提取关键词
        keywords = self._extract_keywords_from_safety_info(safety_info)
        
        print(f"[INFO] 提取的关键词: {', '.join(keywords[:5])}...")
        
        # 在所有指引文档中搜索
        best_match = None
        best_score = 0
        
        for guide_doc in get_guide_docs():
            node_token = guide_doc['node_token']
            
            # 加载指引文档
            content = self.guide_reader.load_fault_guide(node_token)
            if not content:
                continue
            
            # 计算匹配分数
            score = self._calculate_semantic_match_score(content, fa_id, keywords)
            
            if score > best_score:
                best_score = score
                # 提取相关段落
                relevant_sections = self._extract_relevant_sections(content, fa_id, keywords)
                
                best_match = {
                    'fault_id': fa_id,
                    'content': content,
                    '完整内容': content,
                    'matched_keywords': keywords,
                    'match_score': score,
                    'relevant_sections': relevant_sections
                }
        
        if best_match and best_score > 0.3:  # 设置阈值
            print(f"[INFO] 找到语义匹配的指引文档（匹配度: {best_score:.2f}）")
            return best_match
        
        return None
    
    def _extract_keywords_from_safety_info(self, safety_info: Dict[str, Any]) -> List[str]:
        """
        从安全需求总表信息中提取关键词
        
        Args:
            safety_info: 安全需求总表信息
            
        Returns:
            关键词列表
        """
        keywords = []
        records = safety_info.get('unique_records', safety_info.get('records', []))
        
        for record in records:
            # 提取故障名称关键词
            if record.get('fault_name'):
                fault_name = record['fault_name']
                # 分割下划线和驼峰命名
                keywords.extend(self._split_identifier(fault_name))
            
            # 提取涉及模块
            if record.get('element'):
                keywords.append(record['element'].lower())
            
            # 提取涉及功能
            if record.get('element_function'):
                keywords.append(record['element_function'].lower())
            
            # 提取触发条件关键词
            if record.get('trigger_conditions'):
                trigger = record['trigger_conditions'].lower()
                # 提取关键术语
                keywords.extend(self._extract_terms_from_text(trigger))
            
            # 提取故障描述关键词
            if record.get('fault_description'):
                desc = record['fault_description'].lower()
                keywords.extend(self._extract_terms_from_text(desc))
        
        # 去重并过滤
        keywords = list(set([k for k in keywords if len(k) > 2]))
        return keywords[:20]  # 最多20个关键词
    
    def _split_identifier(self, identifier: str) -> List[str]:
        """分割标识符（下划线、驼峰命名）"""
        import re
        # 分割下划线
        parts = identifier.split('_')
        result = []
        for part in parts:
            # 分割驼峰命名
            camel_parts = re.findall(r'[A-Z]?[a-z]+|[A-Z]+(?=[A-Z]|$)', part)
            result.extend([p.lower() for p in camel_parts if len(p) > 2])
        return result
    
    def _extract_terms_from_text(self, text: str) -> List[str]:
        """从文本中提取关键术语"""
        import re
        # 提取技术术语（英文单词、中文术语）
        terms = []
        # 英文单词（3个字符以上）
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text)
        terms.extend([w.lower() for w in words if w.lower() not in ['the', 'and', 'for', 'are', 'with', 'from']])
        # 中文术语（2-4个字符）
        chinese_terms = re.findall(r'[\u4e00-\u9fa5]{2,4}', text)
        terms.extend(chinese_terms)
        return terms[:10]  # 最多10个术语
    
    def _calculate_semantic_match_score(self, content: str, fa_id: str, keywords: List[str]) -> float:
        """
        计算内容与关键词的语义匹配分数
        
        Args:
            content: 文档内容
            fa_id: Fault ID
            keywords: 关键词列表
            
        Returns:
            匹配分数（0-1）
        """
        if not content or not keywords:
            return 0.0
        
        content_lower = content.lower()
        fa_id_num = fa_id.replace('0x', '').replace('0X', '').lstrip('0') or '0'
        
        score = 0.0
        total_keywords = len(keywords)
        
        if total_keywords == 0:
            return 0.0
        
        # 1. fa_id匹配（权重0.3）
        if fa_id.lower() in content_lower or fa_id_num in content_lower:
            score += 0.3
        
        # 2. 关键词匹配（权重0.7）
        matched_keywords = 0
        for keyword in keywords:
            if keyword.lower() in content_lower:
                matched_keywords += 1
        
        keyword_score = (matched_keywords / total_keywords) * 0.7
        score += keyword_score
        
        return min(score, 1.0)
    
    def _extract_relevant_sections(self, content: str, fa_id: str, keywords: List[str]) -> List[str]:
        """提取相关段落"""
        import re
        sections = []
        
        # 按段落分割
        paragraphs = content.split('\n\n')
        
        for para in paragraphs:
            para_lower = para.lower()
            # 检查是否包含fa_id或关键词
            fa_id_num = fa_id.replace('0x', '').replace('0X', '').lstrip('0') or '0'
            has_fa_id = fa_id.lower() in para_lower or fa_id_num in para_lower
            has_keywords = any(kw.lower() in para_lower for kw in keywords[:5])  # 只检查前5个关键词
            
            if has_fa_id or has_keywords:
                # 限制段落长度
                if len(para) > 500:
                    para = para[:500] + "..."
                sections.append(para)
        
        return sections[:5]  # 最多5个相关段落
    
    def _generate_expert_analysis(self, fa_id: str, safety_info: Dict[str, Any], guide_info: Optional[Dict[str, Any]]) -> Optional[str]:
        """
        基于专家认知生成原因分析
        
        Args:
            fa_id: Fault ID
            safety_info: 安全需求总表信息
            guide_info: 指引文档信息（可选）
            
        Returns:
            专家分析文本
        """
        records = safety_info.get('unique_records', safety_info.get('records', []))
        if not records:
            return None
        
        # 提取关键信息
        fault_names = []
        elements = []
        trigger_conditions = []
        asil_levels = []
        
        for record in records:
            if record.get('fault_name'):
                fault_names.append(record['fault_name'])
            if record.get('element'):
                elements.append(record['element'])
            if record.get('trigger_conditions'):
                trigger_conditions.append(record['trigger_conditions'])
            if record.get('asil'):
                asil_levels.append(record['asil'])
        
        # 生成分析提示词
        analysis_parts = []
        analysis_parts.append(f"## 故障 {fa_id} 的专家分析\n")
        
        # 基本信息
        if fault_names:
            analysis_parts.append(f"**故障名称**: {', '.join(set(fault_names))}\n")
        if elements:
            analysis_parts.append(f"**涉及模块**: {', '.join(set(elements))}\n")
        if asil_levels:
            analysis_parts.append(f"**ASIL等级**: {', '.join(set(asil_levels))}\n")
        if trigger_conditions:
            analysis_parts.append(f"**触发条件**: {', '.join(set(trigger_conditions))}\n")
        
        analysis_parts.append("\n## 可能的原因分析\n")
        
        # 基于故障名称和模块进行专家分析
        for fault_name in set(fault_names):
            if 'TRAJECTORY' in fault_name or '轨迹' in fault_name:
                analysis_parts.append("### 轨迹相关故障\n")
                analysis_parts.append("- **可能原因1**: Planning模块未输出轨迹，可能是上游消息丢失（ego_pose、nn_decision、bev_lane等）\n")
                analysis_parts.append("- **可能原因2**: Planning模块检测到轨迹异常，主动拦截轨迹（横向Jerk过大等）\n")
                analysis_parts.append("- **可能原因3**: 系统负载过高，导致Planning无法及时输出轨迹\n")
                analysis_parts.append("- **可能原因4**: Planning模块挂死或性能问题\n")
            
            elif 'IMU' in fault_name or 'imu' in fault_name.lower():
                analysis_parts.append("### IMU相关故障\n")
                analysis_parts.append("- **可能原因1**: IMU传感器数据异常，时间戳卡住\n")
                analysis_parts.append("- **可能原因2**: IMU数据接收超时或丢失\n")
                analysis_parts.append("- **可能原因3**: IMU硬件故障或通信异常\n")
        
        # 基于涉及模块进行分析
        if 'Planning' in elements:
            analysis_parts.append("\n### Planning模块相关\n")
            analysis_parts.append("- Planning模块是自动驾驶系统的核心规划模块，负责生成行驶轨迹\n")
            analysis_parts.append("- 常见问题包括：上游消息丢失、轨迹验证失败、性能问题、挂死等\n")
        
        if 'Control' in elements:
            analysis_parts.append("\n### Control模块相关\n")
            analysis_parts.append("- Control模块负责车辆控制，依赖IMU等传感器数据\n")
            analysis_parts.append("- 常见问题包括：传感器数据异常、控制算法故障、通信延迟等\n")
        
        # 如果有指引文档信息，添加相关提示
        if guide_info:
            analysis_parts.append("\n### 参考指引文档\n")
            relevant_sections = guide_info.get('relevant_sections', [])
            if relevant_sections:
                for i, section in enumerate(relevant_sections[:2], 1):
                    analysis_parts.append(f"\n**相关描述 {i}**:\n{section[:300]}...\n")
        
        return "\n".join(analysis_parts)
    
    def _search_guide_by_content(self, fa_id: str) -> Optional[Dict[str, Any]]:
        """
        在指引文档内容中直接搜索fa_id（语义搜索）
        
        Args:
            fa_id: Fault ID
            
        Returns:
            指引信息字典（如果找到）
        """
        from fault_diagnosis_config import get_guide_docs
        
        # 获取fa_id的数字部分（用于搜索）
        fa_id_num = fa_id.replace('0x', '').replace('0X', '').lstrip('0') or '0'
        fa_id_variants = [
            fa_id,  # 0x0165
            f"0x{fa_id_num}",  # 0x165
            fa_id_num,  # 165
            f"0x{fa_id_num.zfill(4)}",  # 0x0165
        ]
        
        # 在所有指引文档中搜索
        for guide_doc in get_guide_docs():
            node_token = guide_doc['node_token']
            
            # 加载指引文档
            content = self.guide_reader.load_fault_guide(node_token)
            if not content:
                continue
            
            # 检查内容中是否包含fa_id的变体
            content_lower = content.lower()
            for variant in fa_id_variants:
                # 搜索变体（不区分大小写）
                if variant.lower() in content_lower:
                    # 提取包含fa_id的上下文
                    import re
                    pattern = rf'.{{0,200}}{re.escape(variant)}.{{0,200}}'
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    
                    if matches:
                        # 构建指引信息
                        guide_info = {
                            'fault_id': fa_id,
                            'content': content,
                            '完整内容': content,
                            'matched_variant': variant,
                            'context_matches': matches[:3]  # 前3个匹配上下文
                        }
                        print(f"[INFO] 在文档内容中找到fa_id {variant}的引用")
                        return guide_info
        
        return None
    
    def _normalize_fault_id(self, fault_id: str) -> str:
        """规范化Fault ID格式"""
        if not fault_id:
            return ""
        
        fault_id = fault_id.strip().upper()
        
        if fault_id.startswith('0X'):
            num_part = fault_id[2:]
            try:
                num = int(num_part, 16)
                return f"0x{num:04X}"
            except:
                return fault_id
        elif fault_id.isdigit():
            try:
                num = int(fault_id)
                return f"0x{num:04X}"
            except:
                return fault_id
        
        return fault_id
    
    def _generate_summary_text(self, result: Dict[str, Any]) -> str:
        """
        生成综合故障概况文本（结构化、易读）
        
        Args:
            result: 提取结果字典
            
        Returns:
            综合故障概况文本
        """
        fa_id = result.get('fault_id', '')
        
        # 收集所有关键信息
        key_info = {
            'fault_id': fa_id,
            'fault_names': set(),
            'descriptions': [],
            'asil_levels': set(),
            'elements': set(),
            'element_functions': set(),
            'trigger_conditions': set(),
            'detection_periods': set(),
            'guide_summary': None,
            'bitable_summary': None
        }
        
        # 1. 从安全需求总表提取信息
        safety_info = result.get('safety_requirement_info')
        if safety_info:
            records = safety_info.get('unique_records', safety_info.get('records', []))
            for record in records:
                if record.get('fault_name'):
                    key_info['fault_names'].add(record['fault_name'])
                if record.get('fault_description'):
                    desc = record['fault_description']
                    if desc and desc not in key_info['descriptions']:
                        key_info['descriptions'].append(desc)
                if record.get('asil'):
                    key_info['asil_levels'].add(record['asil'])
                if record.get('element'):
                    key_info['elements'].add(record['element'])
                if record.get('element_function'):
                    key_info['element_functions'].add(record['element_function'])
                if record.get('trigger_conditions'):
                    key_info['trigger_conditions'].add(record['trigger_conditions'])
                if record.get('detection_period'):
                    key_info['detection_periods'].add(record['detection_period'])
        
        # 2. 从指引文档提取关键信息
        guide_info = result.get('guide_info')
        if guide_info:
            content = guide_info.get('content', guide_info.get('完整内容', ''))
            if content:
                # 提取与fa_id相关的关键段落
                key_info['guide_summary'] = self._extract_guide_key_points(content, fa_id)
        
        # 3. 从功能安全业务数据提取
        bitable_summary = result.get('bitable_summary')
        if bitable_summary and "未在功能安全业务数据中找到相关信息" not in bitable_summary:
            key_info['bitable_summary'] = bitable_summary
        
        # 4. 生成结构化的易读文本
        ai_analysis = result.get('ai_analysis')
        return self._format_summary(key_info, ai_analysis)
    
    def _extract_guide_key_points(self, content: str, fa_id: str) -> str:
        """
        从指引文档中提取关键要点
        
        Args:
            content: 文档内容
            fa_id: Fault ID
            
        Returns:
            关键要点文本
        """
        # 查找包含fa_id的段落
        import re
        fa_id_num = fa_id.replace('0x', '').replace('0X', '').lstrip('0') or '0'
        patterns = [
            rf'.{{0,300}}{re.escape(fa_id)}.{{0,300}}',
            rf'.{{0,300}}{re.escape(fa_id_num)}.{{0,300}}',
        ]
        
        key_points = []
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE | re.DOTALL)
            for match in matches[:2]:  # 最多2个匹配
                # 清理文本
                match = match.replace('\n', ' ').strip()
                if len(match) > 50 and match not in key_points:
                    key_points.append(match[:500])  # 限制长度
        
        return ' '.join(key_points) if key_points else None
    
    def _format_summary(self, key_info: Dict[str, Any], ai_analysis: Optional[str] = None) -> str:
        """
        格式化故障概况为易读文本
        
        Args:
            key_info: 关键信息字典
            ai_analysis: 专家分析文本（可选）
            
        Returns:
            格式化的故障概况文本
        """
        lines = []
        fa_id = key_info.get('fault_id', '')
        
        lines.append("=" * 80)
        lines.append(f"故障概况总结 - {fa_id}")
        lines.append("=" * 80)
        lines.append("")
        
        # 基本信息
        lines.append("【基本信息】")
        if key_info.get('fault_names'):
            fault_names = ', '.join(sorted(key_info['fault_names']))
            lines.append(f"故障名称: {fault_names}")
        if key_info.get('asil_levels'):
            asil = ', '.join(sorted(key_info['asil_levels']))
            lines.append(f"ASIL等级: {asil}")
        if key_info.get('elements'):
            elements = ', '.join(sorted(key_info['elements']))
            lines.append(f"涉及模块: {elements}")
        if key_info.get('element_functions'):
            functions = ', '.join(sorted(key_info['element_functions']))
            lines.append(f"涉及功能: {functions}")
        lines.append("")
        
        # 故障描述（去重后）
        if key_info.get('descriptions'):
            lines.append("【故障描述】")
            # 只显示第一个描述（通常最完整）
            desc = key_info['descriptions'][0]
            # 提取核心描述（去除重复段落）
            core_desc = self._extract_core_description(desc)
            lines.append(core_desc)
            lines.append("")
        
        # 触发条件
        if key_info.get('trigger_conditions'):
            lines.append("【触发条件】")
            for condition in sorted(key_info['trigger_conditions']):
                if condition:
                    lines.append(f"  • {condition}")
            lines.append("")
        
        # 检测周期
        if key_info.get('detection_periods'):
            lines.append("【检测周期】")
            for period in sorted(key_info['detection_periods']):
                if period:
                    lines.append(f"  • {period}")
            lines.append("")
        
        # 专家分析（优先显示）
        if ai_analysis:
            lines.append("【专家分析】")
            lines.append(ai_analysis)
            lines.append("")
        
        # 故障定位指引要点
        if key_info.get('guide_summary'):
            lines.append("【故障定位指引要点】")
            guide_text = key_info['guide_summary']
            if len(guide_text) > 500:
                guide_text = guide_text[:500] + "..."
            lines.append(guide_text)
            lines.append("")
        
        # 功能安全业务数据（如果有）
        if key_info.get('bitable_summary'):
            lines.append("【功能安全业务数据】")
            # 只显示前500字符
            bitable_text = key_info['bitable_summary']
            if len(bitable_text) > 500:
                bitable_text = bitable_text[:500] + "..."
            lines.append(bitable_text)
            lines.append("")
        
        # 如果没有找到任何信息
        if not any([
            key_info.get('fault_names'),
            key_info.get('descriptions'),
            key_info.get('guide_summary'),
            key_info.get('bitable_summary')
        ]):
            lines.append("未找到相关信息")
        
        lines.append("=" * 80)
        
        return "\n".join(lines)
    
    def _extract_core_description(self, description: str) -> str:
        """
        提取核心描述（去除重复和冗余）
        
        Args:
            description: 原始描述
            
        Returns:
            核心描述文本
        """
        if not description:
            return ""
        
        # 按段落分割
        paragraphs = [p.strip() for p in description.split('\n') if p.strip()]
        
        if not paragraphs:
            return description
        
        # 提取第一个有意义的段落（通常包含核心信息）
        core_paragraphs = []
        seen_content = set()
        
        for para in paragraphs:
            # 跳过重复内容
            para_lower = para.lower()
            is_duplicate = any(self._similarity(para_lower, seen.lower()) > 0.7 for seen in seen_content)
            
            if not is_duplicate and len(para) > 20:
                core_paragraphs.append(para)
                seen_content.add(para)
                
                # 如果已经收集了足够的核心信息，停止
                if len(core_paragraphs) >= 3:
                    break
        
        return '\n'.join(core_paragraphs) if core_paragraphs else paragraphs[0]
    
    def _format_bitable_summary(self, safety_info: Dict[str, Any]) -> str:
        """
        将安全需求总表信息格式化为功能安全业务数据摘要
        
        Args:
            safety_info: 安全需求总表信息
            
        Returns:
            格式化的摘要文本
        """
        if not safety_info:
            return ""
        
        records = safety_info.get('unique_records', safety_info.get('records', []))
        if not records:
            return ""
        
        summary_parts = []
        for i, record in enumerate(records[:3], 1):  # 最多3条
            summary_parts.append(f"记录 {i}:")
            if record.get('fault_name'):
                summary_parts.append(f"  故障名称: {record['fault_name']}")
            if record.get('fault_description'):
                desc = self._extract_core_description(record['fault_description'])
                summary_parts.append(f"  故障描述: {desc}")
            if record.get('asil'):
                summary_parts.append(f"  ASIL等级: {record['asil']}")
            if record.get('element'):
                summary_parts.append(f"  涉及模块: {record['element']}")
            if record.get('trigger_conditions'):
                summary_parts.append(f"  触发条件: {record['trigger_conditions']}")
            summary_parts.append("")
        
        return "\n".join(summary_parts)
    
    def _generate_ai_summary_prompt(self, result: Dict[str, Any]) -> str:
        """
        生成AI总结提示词（用于Cursor AI进行智能总结）
        
        Args:
            result: 提取结果字典
            
        Returns:
            AI总结提示词文本
        """
        fa_id = result.get('fault_id', '')
        
        # 收集关键信息
        info_parts = []
        
        # 1. 基本信息
        safety_info = result.get('safety_requirement_info')
        if safety_info:
            records = safety_info.get('unique_records', safety_info.get('records', []))
            if records:
                info_parts.append("## 安全需求总表信息：")
                for i, record in enumerate(records[:3], 1):  # 最多3条
                    info_parts.append(f"\n### 记录{i}:")
                    if record.get('fault_name'):
                        info_parts.append(f"- 故障名称: {record['fault_name']}")
                    if record.get('fault_description'):
                        desc = self._extract_core_description(record['fault_description'])
                        info_parts.append(f"- 故障描述: {desc}")
                    if record.get('asil'):
                        info_parts.append(f"- ASIL等级: {record['asil']}")
                    if record.get('element'):
                        info_parts.append(f"- 涉及模块: {record['element']}")
                    if record.get('trigger_conditions'):
                        info_parts.append(f"- 触发条件: {record['trigger_conditions']}")
        
        # 2. 指引文档关键信息
        guide_info = result.get('guide_info')
        if guide_info:
            content = guide_info.get('content', guide_info.get('完整内容', ''))
            if content:
                # 提取与fa_id相关的关键段落
                key_points = self._extract_guide_key_points(content, fa_id)
                if key_points:
                    info_parts.append("\n## 故障定位指引要点：")
                    info_parts.append(key_points)
        
        # 3. 功能安全业务数据（就是安全需求总表，已经在上面包含了，这里不需要重复）
        # 注意："功能安全业务数据"多维表格中的"06. 安全需求总表"已经在上面处理过了
        
        # 生成提示词
        prompt = f"""请基于以下关于故障 {fa_id} 的信息，生成一份简洁、易读的故障概况总结。

要求：
1. 用中文总结，语言简洁专业
2. 突出关键信息：故障名称、ASIL等级、涉及模块、触发条件
3. 整合多个来源的信息，去除重复和冗余
4. 如果信息有冲突，优先使用安全需求总表的信息
5. 格式清晰，使用标题和列表

故障信息：
{chr(10).join(info_parts) if info_parts else '未找到相关信息'}

请生成故障概况总结："""
        
        return prompt
    
    def generate_ai_summary(self, fa_id: str, use_grep: bool = True) -> Dict[str, Any]:
        """
        提取故障信息并生成AI总结提示词
        
        Args:
            fa_id: Fault ID
            use_grep: 是否使用grep查询
            
        Returns:
            包含AI总结提示词的字典
        """
        result = self.extract_fault_summary(fa_id, use_grep)
        
        # 返回AI总结提示词
        return {
            'fault_id': result['fault_id'],
            'summary_text': result['summary_text'],
            'ai_summary_prompt': result.get('ai_summary_prompt', ''),
            'raw_data': {
                'guide_info': result.get('guide_info'),
                'safety_requirement_info': result.get('safety_requirement_info'),
                'bitable_summary': result.get('bitable_summary')
            }
        }


def extract_fault_summary(fa_id: str, use_grep: bool = True) -> Dict[str, Any]:
    """
    提取故障概况（便捷函数）
    
    Args:
        fa_id: Fault ID
        use_grep: 是否使用grep查询
        
    Returns:
        故障概况字典
    """
    extractor = FaultSummaryExtractor()
    return extractor.extract_fault_summary(fa_id, use_grep)


def generate_ai_summary(fa_id: str, use_grep: bool = True) -> Dict[str, Any]:
    """
    生成AI总结提示词（便捷函数）
    
    Args:
        fa_id: Fault ID
        use_grep: 是否使用grep查询
        
    Returns:
        包含AI总结提示词的字典
    """
    extractor = FaultSummaryExtractor()
    return extractor.generate_ai_summary(fa_id, use_grep)

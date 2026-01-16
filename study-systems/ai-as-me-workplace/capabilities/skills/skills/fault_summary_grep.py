# -*- coding: utf-8 -*-
"""
故障概要提取器

从"功能安全业务数据"多维表格中grep查找Fault ID相关信息
"""

import sys
import os
import json
import re
from typing import Optional, Dict, List
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fault_diagnosis_config import DEFECT_TABLE_CACHE_FILE

# 修复Windows控制台编码问题
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass


class FaultSummaryGrep:
    """故障概要提取器"""
    
    def __init__(self):
        """初始化"""
        self.cache_file = DEFECT_TABLE_CACHE_FILE
    
    def grep_fault_summary(self, fault_id: str) -> str:
        """
        从"功能安全业务数据"中grep查找Fault ID相关信息
        
        Args:
            fault_id: Fault ID（如0x0165）
            
        Returns:
            故障概要文本
        """
        if not fault_id:
            return "未提供Fault ID"
        
        # 规范化Fault ID
        fault_id_normalized = self._normalize_fault_id(fault_id)
        
        # 加载缓存数据（支持相对路径和绝对路径）
        # 尝试多个可能的路径
        possible_paths = [
            Path("work/bitable_cache") / self.cache_file,
            Path("capabilities/skills/skills/work/bitable_cache") / self.cache_file,
            Path(__file__).parent.parent.parent / "work" / "bitable_cache" / self.cache_file,
            Path(__file__).parent.parent.parent.parent / "work" / "bitable_cache" / self.cache_file,
            Path("d:/Users/colin.lin/.cursor/work/bitable_cache") / self.cache_file,
        ]
        
        cache_path = None
        for path in possible_paths:
            if path.exists():
                cache_path = path
                break
        
        if not cache_path:
            error_msg = f"缓存文件不存在，尝试过的路径: {[str(p) for p in possible_paths]}"
            print(f"[!] {error_msg}")
            return error_msg
        
        try:
            print(f"[DEBUG] 加载缓存文件: {cache_path}")
            with open(cache_path, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            print(f"[DEBUG] 缓存文件加载成功，表数量: {len(cache_data.get('tables', []))}")
        except Exception as e:
            error_msg = f"读取缓存文件失败: {e}"
            print(f"[!] {error_msg}")
            return error_msg
        
        # 在所有表中搜索Fault ID相关信息
        summary_parts = []
        
        # 遍历所有表
        tables = cache_data.get('tables', [])
        if not isinstance(tables, list):
            tables = []
        
        for table in tables:
            if not isinstance(table, dict):
                continue
            table_name = table.get('name', '')
            records = table.get('records', [])
            if not isinstance(records, list):
                records = []
            
            # 在每条记录中搜索
            for record in records:
                if not isinstance(record, dict):
                    continue
                fields = record.get('fields', {})
                if not isinstance(fields, dict):
                    continue
                
                # 检查是否包含Fault ID（检查Fault ID相关字段）
                fault_id_found = False
                fault_id_value = None
                
                # 查找Fault ID字段（支持多种字段名）
                fault_id_field_names = ['Fault ID', 'Fault_ID', 'FaultId', 'fault_id', 'fa_id', 'FaultID', 'FAULT_ID']
                for field_name in fault_id_field_names:
                    if field_name in fields:
                        field_value = fields[field_name]
                        if field_value:
                            field_str = str(field_value)
                            if self._contains_fault_id(field_str, fault_id_normalized):
                                fault_id_found = True
                                fault_id_value = field_value
                                break
                
                # 如果没找到，尝试在所有字段中搜索
                if not fault_id_found:
                    for field_name, field_value in fields.items():
                        if field_value:
                            field_str = str(field_value)
                            if self._contains_fault_id(field_str, fault_id_normalized):
                                fault_id_found = True
                                fault_id_value = field_value
                                break
                
                # 如果找到匹配的Fault ID，提取详细信息
                if fault_id_found:
                    summary_info = []
                    
                    # 提取关键字段
                    key_fields = {
                        'Fault Name': '故障名称',
                        'Fault_Name': '故障名称',
                        'Fault Description': '故障描述',
                        'Fault_Description': '故障描述',
                        'Description': '描述',
                        'Fault Trigger Conditions': '触发条件',
                        'Fault Operation Condition': '操作条件',
                        'Element': '涉及模块',
                        'Element Function': '涉及功能',
                        'ASIL': 'ASIL等级',
                        '可能的原因': '可能的原因',
                        'Possible Causes': '可能的原因'
                    }
                    
                    for field_name, display_name in key_fields.items():
                        if field_name in fields and fields[field_name]:
                            value = fields[field_name]
                            # 处理列表类型
                            if isinstance(value, list):
                                if value and isinstance(value[0], dict):
                                    # 如果是字典列表，提取text字段
                                    value = ', '.join([str(v.get('text', v)) for v in value if v])
                                else:
                                    value = ', '.join([str(v) for v in value if v])
                            if value:
                                summary_info.append(f"{display_name}: {str(value)}")
                    
                    if summary_info:
                        summary_parts.append("\n".join(summary_info))
        
        if summary_parts:
            # 去重并合并（保留前3条最详细的）
            unique_parts = []
            seen = set()
            for part in summary_parts:
                if part not in seen:
                    unique_parts.append(part)
                    seen.add(part)
                    if len(unique_parts) >= 3:
                        break
            
            return "\n\n".join(unique_parts)
        else:
            return "未在功能安全业务数据中找到相关信息"
    
    def _normalize_fault_id(self, fault_id: str) -> str:
        """规范化Fault ID格式"""
        if not fault_id:
            return ""
        
        fault_id = fault_id.strip().upper()
        
        # 转换为标准格式
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
    
    def _contains_fault_id(self, text: str, fault_id: str) -> bool:
        """检查文本是否包含Fault ID"""
        if not text or not fault_id:
            return False
        
        # 规范化fault_id用于匹配（去掉0x前缀，支持多种格式）
        fault_id_clean = fault_id.upper().replace('0X', '').replace('0x', '')
        # 去掉前导0
        fault_id_clean_no_zero = fault_id_clean.lstrip('0') or '0'
        
        # 支持多种格式匹配（匹配0x0165和0x165）
        patterns = [
            rf'\b{re.escape(fault_id)}\b',  # 完整匹配 0x0165
            rf'Fault\s*ID[:\s]+{re.escape(fault_id)}',  # Fault ID: 0x0165
            rf'fault_id[:\s=]+{re.escape(fault_id)}',  # fault_id: 0x0165
            rf'fa_id[:\s=]+{re.escape(fault_id)}',  # fa_id: 0x0165
            rf'\b0x{re.escape(fault_id_clean)}\b',  # 0x165 (带前导0)
            rf'\b0x{re.escape(fault_id_clean_no_zero)}\b',  # 0x165 (无前导0)
            rf'{re.escape(fault_id_clean)}',  # 165 (纯数字，带前导0)
            rf'{re.escape(fault_id_clean_no_zero)}',  # 165 (纯数字，无前导0)
        ]
        
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        return False
    
    def _extract_context(self, text: str, fault_id: str, context_length: int = 100) -> str:
        """提取包含Fault ID的上下文"""
        if not text or not fault_id:
            return ""
        
        # 查找Fault ID的位置
        patterns = [
            rf'\b{re.escape(fault_id)}\b',
            rf'Fault\s*ID[:\s]+{re.escape(fault_id)}',
            rf'fault_id[:\s]+{re.escape(fault_id)}',
            rf'fa_id[:\s]+{re.escape(fault_id)}',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                start_pos = max(0, match.start() - context_length)
                end_pos = min(len(text), match.end() + context_length)
                context = text[start_pos:end_pos]
                # 清理上下文
                context = context.replace('\n', ' ').replace('\r', ' ').strip()
                if len(context) > 200:
                    context = context[:200] + "..."
                return context
        
        return ""

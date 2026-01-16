# -*- coding: utf-8 -*-
"""
修复fault_statistics_extractor.py文件
"""

import re

file_path = "fault_statistics_extractor.py"

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 修复extract_statistics方法
old_pattern1 = r'(# 规范化Fault ID格式（支持多种格式）\s+fault_id_normalized = self\._normalize_fault_id\(fault_id\)\s+# 提取所有包含该Fault ID的行)'
new_text1 = r'''# 规范化Fault ID格式（支持多种格式）
        fault_id_normalized = self._normalize_fault_id(fault_id)
        # 同时尝试无前导0的格式（日志中可能是0x165而不是0x0165）
        fault_id_no_zero = fault_id_normalized
        if fault_id_normalized.startswith('0X'):
            num_part = fault_id_normalized[2:]
            if num_part.startswith('0') and len(num_part) > 1:
                fault_id_no_zero = '0x' + num_part.lstrip('0') or '0'
        
        # 提取所有包含该Fault ID的行'''

content = re.sub(old_pattern1, new_text1, content, flags=re.MULTILINE)

# 修复匹配逻辑
old_pattern2 = r'if self\._line_contains_fault_id\(line, fault_id_normalized\):'
new_text2 = r'if self._line_contains_fault_id(line, fault_id_normalized) or self._line_contains_fault_id(line, fault_id_no_zero):'
content = content.replace(old_pattern2, new_text2)

# 修复fu_st提取
old_pattern3 = r'(# 提取fu_st值\s+fu_st = self\._extract_fu_st\(log_content, fault_id_normalized\)\s+return)'
new_text3 = r'''# 提取fu_st值（尝试两种格式）
        fu_st = self._extract_fu_st(log_content, fault_id_normalized)
        if not fu_st:
            fu_st = self._extract_fu_st(log_content, fault_id_no_zero)
        
        return'''
content = re.sub(old_pattern3, new_text3, content, flags=re.MULTILINE)

# 修复_line_contains_fault_id方法
old_pattern4 = r'(def _line_contains_fault_id\(self, line: str, fault_id: str\) -> bool:.*?# 支持多种格式\s+patterns = \[.*?rf\'fault_id\[:\\s\]\+{re\.escape\(fault_id\)}\',.*?\])'
new_text4 = '''def _line_contains_fault_id(self, line: str, fault_id: str) -> bool:
        """检查行是否包含Fault ID"""
        if not line or not fault_id:
            return False
        
        # 规范化fault_id用于匹配（去掉0x前缀，支持多种格式）
        fault_id_upper = fault_id.upper()
        fault_id_clean = fault_id_upper.replace('0X', '').replace('0x', '')
        # 去掉前导0
        fault_id_clean_no_zero = fault_id_clean.lstrip('0') or '0'
        # 带前导0的格式（如0165）
        fault_id_clean_with_zero = fault_id_clean.zfill(4)
        
        # 支持多种格式（匹配0x0165和0x165）
        patterns = [
            # 完整匹配（带0x前缀）
            rf'\\b{re.escape(fault_id_upper)}\\b',  # 完整匹配 0x0165
            rf'\\b0x{re.escape(fault_id_clean)}\\b',  # 0x0165 (带前导0)
            rf'\\b0x{re.escape(fault_id_clean_no_zero)}\\b',  # 0x165 (无前导0)
            
            # fa_id格式
            rf'fa_id[:\\s=]+{re.escape(fault_id_upper)}',  # fa_id: 0x0165 或 fa_id=0x0165
            rf'fa_id[:\\s=]+0x{re.escape(fault_id_clean)}',  # fa_id: 0x0165 (带前导0)
            rf'fa_id[:\\s=]+0x{re.escape(fault_id_clean_no_zero)}',  # fa_id: 0x165 (无前导0)
            
            # 括号格式 (e_id, fa_id, fa_st)=( 3,     0x165, 1)
            rf'\\([^)]*fa_id[^)]*\\)[^=]*=\\s*\\([^)]*0x{re.escape(fault_id_clean_no_zero)}',  # (e_id, fa_id, fa_st)=( 3, 0x165, 1)
            rf'\\([^)]*fa_id[^)]*\\)[^=]*=\\s*\\([^)]*0x{re.escape(fault_id_clean)}',  # (e_id, fa_id, fa_st)=( 3, 0x0165, 1)
            
            # Fault ID格式
            rf'Fault\\s*ID[:\\s]+{re.escape(fault_id_upper)}',  # Fault ID: 0x0165
            rf'fault_id[:\\s=]+{re.escape(fault_id_upper)}',  # fault_id: 0x0165
            
            # 其他格式
            rf'faults?[:\\s]*\\(0x{re.escape(fault_id_clean)}',  # faults:(0x165 )
            rf'faults?[:\\s]*\\(0x{re.escape(fault_id_clean_no_zero)}',  # faults:(0x165 )
        ]'''

# 由于正则表达式太复杂，直接替换整个方法
lines = content.split('\n')
new_lines = []
in_method = False
method_start = -1
method_end = -1

for i, line in enumerate(lines):
    if 'def _line_contains_fault_id' in line:
        in_method = True
        method_start = i
    elif in_method and line.strip() and not line.startswith(' ') and not line.startswith('\t'):
        method_end = i
        break

if method_start >= 0:
    # 找到方法结束位置（下一个方法或类定义）
    for i in range(method_start + 1, len(lines)):
        if lines[i].strip() and not lines[i].startswith(' ') and not lines[i].startswith('\t') and not lines[i].startswith('#'):
            if 'def ' in lines[i] or 'class ' in lines[i]:
                method_end = i
                break
    else:
        method_end = len(lines)
    
    # 替换方法
    new_method = '''    def _line_contains_fault_id(self, line: str, fault_id: str) -> bool:
        """检查行是否包含Fault ID"""
        if not line or not fault_id:
            return False
        
        # 规范化fault_id用于匹配（去掉0x前缀，支持多种格式）
        fault_id_upper = fault_id.upper()
        fault_id_clean = fault_id_upper.replace('0X', '').replace('0x', '')
        # 去掉前导0
        fault_id_clean_no_zero = fault_id_clean.lstrip('0') or '0'
        
        # 支持多种格式（匹配0x0165和0x165）
        patterns = [
            # 完整匹配（带0x前缀）
            rf'\\b{re.escape(fault_id_upper)}\\b',  # 完整匹配 0x0165
            rf'\\b0x{re.escape(fault_id_clean)}\\b',  # 0x0165 (带前导0)
            rf'\\b0x{re.escape(fault_id_clean_no_zero)}\\b',  # 0x165 (无前导0)
            
            # fa_id格式
            rf'fa_id[:\\s=]+{re.escape(fault_id_upper)}',  # fa_id: 0x0165 或 fa_id=0x0165
            rf'fa_id[:\\s=]+0x{re.escape(fault_id_clean)}',  # fa_id: 0x0165 (带前导0)
            rf'fa_id[:\\s=]+0x{re.escape(fault_id_clean_no_zero)}',  # fa_id: 0x165 (无前导0)
            
            # 括号格式 (e_id, fa_id, fa_st)=( 3,     0x165, 1)
            rf'\\([^)]*fa_id[^)]*\\)[^=]*=\\s*\\([^)]*0x{re.escape(fault_id_clean_no_zero)}',  # (e_id, fa_id, fa_st)=( 3, 0x165, 1)
            rf'\\([^)]*fa_id[^)]*\\)[^=]*=\\s*\\([^)]*0x{re.escape(fault_id_clean)}',  # (e_id, fa_id, fa_st)=( 3, 0x0165, 1)
            
            # Fault ID格式
            rf'Fault\\s*ID[:\\s]+{re.escape(fault_id_upper)}',  # Fault ID: 0x0165
            rf'fault_id[:\\s=]+{re.escape(fault_id_upper)}',  # fault_id: 0x0165
            
            # 其他格式
            rf'faults?[:\\s]*\\(0x{re.escape(fault_id_clean)}',  # faults:(0x165 )
            rf'faults?[:\\s]*\\(0x{re.escape(fault_id_clean_no_zero)}',  # faults:(0x165 )
        ]
        
        for pattern in patterns:
            if re.search(pattern, line, re.IGNORECASE):
                return True
        
        return False'''
    
    new_content = '\n'.join(lines[:method_start]) + '\n' + new_method + '\n' + '\n'.join(lines[method_end:])
    content = new_content

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("文件修复完成")

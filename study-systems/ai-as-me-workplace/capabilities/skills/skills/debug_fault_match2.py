# -*- coding: utf-8 -*-
"""
调试Fault ID匹配 - 详细版本
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import re
from fault_statistics_extractor import FaultStatisticsExtractor

sys.stdout.reconfigure(encoding='utf-8')

# 测试日志行
test_log = """[20260112_170900][5361.855][I][23][MOD:dji_ad_app][SMOD:dsar_app][DegFL][FaultCollect] |capacity:100|i:  0|func_idx:212|(e_id, fa_id, fa_st)=( 3,     0x165, 1)|deg:1|category:1|time:5363642|
[20260112_170900][5361.766][W][5505][MOD:dji_bf_app][SMOD:ecu_debug]<5363.550>[c2][DSAR]SYS_SetFunc 1: 0 to 0x400, e_id:0x3, fa_id:0x165, fa_st:0x1,fu_st:0x3, fu_st_n:0x1
[20260112_170900][5362.323][W][5517][MOD:dji_bf_app][SMOD:ecu_debug]<5364.110>[c2][DSAR]SYS_SetFunc 1: 0x400 to 0, e_id:0x3, fa_id:0x165, fa_st:0,fu_st:0, fu_st_n:0x0
"""

extractor = FaultStatisticsExtractor()

print("=" * 80)
print("调试extract_statistics方法")
print("=" * 80)
print()

# 手动执行extract_statistics的逻辑
fault_id = '0x0165'
fault_id_normalized = extractor._normalize_fault_id(fault_id)
print(f"输入Fault ID: {fault_id}")
print(f"规范化后: {fault_id_normalized}")

# 计算无前导0格式
fault_id_no_zero = fault_id_normalized
if fault_id_normalized.startswith('0X'):
    num_part = fault_id_normalized[2:]
    if num_part.startswith('0') and len(num_part) > 1:
        fault_id_no_zero = '0x' + num_part.lstrip('0') or '0'

print(f"无前导0格式: {fault_id_no_zero}")
print()

# 提取所有包含该Fault ID的行
lines_with_fault = []
lines = test_log.split('\n')

print("检查每一行:")
for line_num, line in enumerate(lines):
    match1 = extractor._line_contains_fault_id(line, fault_id_normalized)
    match2 = extractor._line_contains_fault_id(line, fault_id_no_zero)
    
    if match1 or match2:
        print(f"  行 {line_num}: 匹配成功")
        fu_st_n = extractor._extract_fu_st_n(line)
        timestamp = extractor._extract_timestamp(line)
        print(f"    fu_st_n: {fu_st_n}")
        print(f"    timestamp: {timestamp}")
        
        lines_with_fault.append({
            'line_num': line_num,
            'line': line,
            'timestamp': timestamp,
            'fu_st_n': fu_st_n
        })
    else:
        print(f"  行 {line_num}: 未匹配")

print()
print(f"找到 {len(lines_with_fault)} 行包含Fault ID")
print()

# 计算出现次数
occurrence_count = 0
last_fu_st_n = None

for line_info in lines_with_fault:
    current_fu_st_n = line_info.get('fu_st_n')
    print(f"行 {line_info['line_num']}: fu_st_n={current_fu_st_n}, last_fu_st_n={last_fu_st_n}")
    if current_fu_st_n is not None:
        if last_fu_st_n == 1 and current_fu_st_n == 0:
            occurrence_count += 1
            print(f"  -> 检测到一次出现（从0x1变成0x0）")
        last_fu_st_n = current_fu_st_n

if occurrence_count == 0 and lines_with_fault:
    has_occurred = any(line_info.get('fu_st_n') == 1 for line_info in lines_with_fault)
    if has_occurred:
        occurrence_count = 1
        print(f"  -> 所有行都是0x1，算1次")

print()
print(f"最终出现次数: {occurrence_count}")

# 提取首次和最后出现时间
first_occurrence = None
last_occurrence = None

if lines_with_fault:
    for line_info in lines_with_fault:
        if line_info.get('fu_st_n') == 1:
            first_occurrence = line_info.get('timestamp')
            break
    
    if not first_occurrence:
        first_occurrence = lines_with_fault[0].get('timestamp')
    
    last_occurrence = lines_with_fault[-1].get('timestamp')

print(f"首次出现: {first_occurrence}")
print(f"最后出现: {last_occurrence}")

print()
print("=" * 80)
print("调用extract_statistics方法")
print("=" * 80)
print()

result = extractor.extract_statistics(test_log, '0x0165')
print(f"结果: {result}")

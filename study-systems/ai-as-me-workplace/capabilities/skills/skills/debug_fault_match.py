# -*- coding: utf-8 -*-
"""
调试Fault ID匹配
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import re
from fault_statistics_extractor import FaultStatisticsExtractor

sys.stdout.reconfigure(encoding='utf-8')

# 测试日志行
test_lines = [
    "[20260112_170900][5361.855][I][23][MOD:dji_ad_app][SMOD:dsar_app][DegFL][FaultCollect] |capacity:100|i:  0|func_idx:212|(e_id, fa_id, fa_st)=( 3,     0x165, 1)|deg:1|category:1|time:5363642|",
    "[20260112_170900][5361.766][W][5505][MOD:dji_bf_app][SMOD:ecu_debug]<5363.550>[c2][DSAR]SYS_SetFunc 1: 0 to 0x400, e_id:0x3, fa_id:0x165, fa_st:0x1,fu_st:0x3, fu_st_n:0x1",
    "[20260112_170900][5362.323][W][5517][MOD:dji_bf_app][SMOD:ecu_debug]<5364.110>[c2][DSAR]SYS_SetFunc 1: 0x400 to 0, e_id:0x3, fa_id:0x165, fa_st:0,fu_st:0, fu_st_n:0x0",
]

extractor = FaultStatisticsExtractor()

print("=" * 80)
print("调试Fault ID匹配")
print("=" * 80)
print()

fault_id_normalized = extractor._normalize_fault_id('0x0165')
fault_id_no_zero = '0x165'

print(f"规范化Fault ID: {fault_id_normalized}")
print(f"无前导0格式: {fault_id_no_zero}")
print()

for i, line in enumerate(test_lines, 1):
    print(f"行 {i}:")
    print(f"  内容: {line[:100]}...")
    
    match1 = extractor._line_contains_fault_id(line, fault_id_normalized)
    match2 = extractor._line_contains_fault_id(line, fault_id_no_zero)
    
    print(f"  匹配0x0165: {match1}")
    print(f"  匹配0x165: {match2}")
    
    if match1 or match2:
        timestamp = extractor._extract_timestamp(line)
        fu_st_n = extractor._extract_fu_st_n(line)
        fu_st = extractor._extract_fu_st(line, fault_id_normalized)
        if not fu_st:
            fu_st = extractor._extract_fu_st(line, fault_id_no_zero)
        
        print(f"  时间戳: {timestamp}")
        print(f"  fu_st_n: {fu_st_n}")
        print(f"  fu_st: {fu_st}")
    
    print()

print("=" * 80)
print("完整测试")
print("=" * 80)
print()

test_log = "\n".join(test_lines)
result = extractor.extract_statistics(test_log, '0x0165')
print(f"Fault ID: 0x0165")
print(f"  首次出现: {result.get('first_occurrence')}")
print(f"  最后出现: {result.get('last_occurrence')}")
print(f"  出现次数: {result.get('occurrence_count')}")
print(f"  fu_st: {result.get('fu_st')}")
print()

result2 = extractor.extract_statistics(test_log, '0x165')
print(f"Fault ID: 0x165")
print(f"  首次出现: {result2.get('first_occurrence')}")
print(f"  最后出现: {result2.get('last_occurrence')}")
print(f"  出现次数: {result2.get('occurrence_count')}")
print(f"  fu_st: {result2.get('fu_st')}")

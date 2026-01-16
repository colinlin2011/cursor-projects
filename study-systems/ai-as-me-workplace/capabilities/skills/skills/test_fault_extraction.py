# -*- coding: utf-8 -*-
"""
测试Fault ID提取和统计信息提取
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fault_statistics_extractor import FaultStatisticsExtractor

# 测试日志行
test_log = """[20260112_170900][5361.855][I][23][MOD:dji_ad_app][SMOD:dsar_app][DegFL][FaultCollect] |capacity:100|i:  0|func_idx:212|(e_id, fa_id, fa_st)=( 3,     0x165, 1)|deg:1|category:1|time:5363642|
[20260112_170900][5361.766][W][5505][MOD:dji_bf_app][SMOD:ecu_debug]<5363.550>[c2][DSAR]SYS_SetFunc 1: 0 to 0x400, e_id:0x3, fa_id:0x165, fa_st:0x1,fu_st:0x3, fu_st_n:0x1
[20260112_170900][5362.323][W][5517][MOD:dji_bf_app][SMOD:ecu_debug]<5364.110>[c2][DSAR]SYS_SetFunc 1: 0x400 to 0, e_id:0x3, fa_id:0x165, fa_st:0,fu_st:0, fu_st_n:0x0
"""

extractor = FaultStatisticsExtractor()

print("=" * 80)
print("测试Fault ID提取")
print("=" * 80)
print()

# 测试0x0165
result = extractor.extract_statistics(test_log, '0x0165')
print(f"Fault ID: 0x0165")
print(f"  首次出现: {result.get('first_occurrence')}")
print(f"  最后出现: {result.get('last_occurrence')}")
print(f"  出现次数: {result.get('occurrence_count')}")
print(f"  fu_st: {result.get('fu_st')}")
print()

# 测试0x165
result2 = extractor.extract_statistics(test_log, '0x165')
print(f"Fault ID: 0x165")
print(f"  首次出现: {result2.get('first_occurrence')}")
print(f"  最后出现: {result2.get('last_occurrence')}")
print(f"  出现次数: {result2.get('occurrence_count')}")
print(f"  fu_st: {result2.get('fu_st')}")
print()

print("=" * 80)

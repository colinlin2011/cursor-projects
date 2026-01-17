# -*- coding: utf-8 -*-
"""
测试增强的SSH日志查询功能

使用指定路径验证功能，应该会提取到0x165的fa_id信息
"""

import sys
import os
from pathlib import Path

# 修复Windows控制台编码问题
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ssh_log_query_engine import create_query_engine


def test_enhanced_query():
    """测试增强的SSH日志查询功能"""
    print("=" * 80)
    print("测试增强的SSH日志查询功能")
    print("=" * 80)
    print()
    
    # 测试路径
    test_path = "/rawdata/roadtestv3/faw/1R10V/FL/cn/2026/1/20260112/14/17-09-14_snapshot/trigger_1768208954556949_5376300000_LK6ADAE47RB757806/"
    
    print(f"测试路径: {test_path}")
    print()
    
    # 创建查询引擎
    engine = create_query_engine()
    
    try:
        # 执行查询
        print("开始执行查询...")
        print()
        
        result = engine.query_setfunc_fault(
            base_path=test_path,
            output_format="both"
        )
        
        # 显示结果
        if 'text' in result:
            print(result['text'])
        
        # 检查是否找到0x165
        if 'json' in result:
            json_result = result['json']
            matches = json_result.get('matches', [])
            
            print()
            print("=" * 80)
            print("详细分析")
            print("=" * 80)
            print()
            
            found_0x165 = False
            fa_ids_found = []
            
            for match in matches:
                fa_id = match.get('fa_id')
                if fa_id:
                    fa_ids_found.append(fa_id)
                    if fa_id.upper() == '0x0165' or fa_id.upper() == '0X0165':
                        found_0x165 = True
                        print(f"[✓] 找到目标FA_ID: {fa_id}")
                        print(f"    行号: {match.get('line_number')}")
                        print(f"    完整行: {match.get('full_line', match.get('line_content', ''))[:200]}...")
                        print()
            
            if found_0x165:
                print("[✓] 测试成功：找到了0x165的fa_id信息")
            else:
                print("[!] 测试结果：未找到0x165的fa_id信息")
                if fa_ids_found:
                    print(f"    找到的其他FA_ID: {', '.join(set(fa_ids_found))}")
            
            # 显示统计信息
            if 'fa_id_summary' in json_result:
                summary = json_result['fa_id_summary']
                print()
                print("FA_ID汇总:")
                print(f"  唯一FA_ID: {', '.join(summary.get('unique_fa_ids', []))}")
                print(f"  总数: {summary.get('total_fa_ids', 0)}")
        
    except Exception as e:
        print(f"[X] 测试失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        engine.close()
        print()
        print("=" * 80)
        print("测试完成")
        print("=" * 80)


if __name__ == "__main__":
    test_enhanced_query()

# -*- coding: utf-8 -*-
"""
测试故障概况提取能力

测试从多个来源提取fa_id相关信息
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

from fault_summary_extractor import extract_fault_summary, FaultSummaryExtractor


def test_extract_0x165():
    """测试提取0x165的故障概况"""
    print("=" * 80)
    print("测试故障概况提取能力 - 0x165")
    print("=" * 80)
    print()
    
    # 提取故障概况
    result = extract_fault_summary("0x165", use_grep=True)
    
    # 显示结果
    print("提取结果:")
    print()
    print(f"故障ID: {result['fault_id']}")
    print()
    
    print("数据来源:")
    print(f"  指引文档: {'✓' if result['guide_info'] else '✗'}")
    print(f"  安全需求总表: {'✓' if result['safety_requirement_info'] else '✗'}")
    print(f"  功能安全业务数据: {'✓' if result['bitable_summary'] else '✗'}")
    print()
    
    # 显示综合概况
    print("=" * 80)
    print("综合故障概况")
    print("=" * 80)
    print()
    print(result['summary_text'])
    print()
    
    # 显示详细信息
    if result['guide_info']:
        print("=" * 80)
        print("指引文档详细信息")
        print("=" * 80)
        guide = result['guide_info']
        print(f"内容预览: {guide.get('content', guide.get('完整内容', ''))[:500]}...")
        print()
    
    if result['safety_requirement_info']:
        print("=" * 80)
        print("安全需求总表详细信息")
        print("=" * 80)
        safety = result['safety_requirement_info']
        print(f"匹配记录数: {safety.get('match_count', 0)}")
        for i, record in enumerate(safety.get('records', [])[:3], 1):
            print(f"\n记录 {i}:")
            for key, value in record.items():
                if value:
                    print(f"  {key}: {value}")
        print()


def test_extract_multiple():
    """测试提取多个fa_id的概况"""
    print("=" * 80)
    print("测试提取多个fa_id的故障概况")
    print("=" * 80)
    print()
    
    fa_ids = ["0x0165", "0x013a", "0x0902"]
    extractor = FaultSummaryExtractor()
    
    for fa_id in fa_ids:
        print(f"\n{'='*80}")
        print(f"FA_ID: {fa_id}")
        print(f"{'='*80}")
        print()
        
        result = extractor.extract_fault_summary(fa_id, use_grep=True)
        
        # 显示简要信息
        print(f"数据来源:")
        print(f"  指引文档: {'✓' if result['guide_info'] else '✗'}")
        print(f"  安全需求总表: {'✓' if result['safety_requirement_info'] else '✗'}")
        print(f"  功能安全业务数据: {'✓' if result['bitable_summary'] else '✗'}")
        print()
        
        # 显示概况文本（前500字符）
        summary_text = result['summary_text']
        if summary_text:
            preview = summary_text[:500] if len(summary_text) > 500 else summary_text
            print("概况预览:")
            print(preview)
            if len(summary_text) > 500:
                print("...")
        print()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='测试故障概况提取能力')
    parser.add_argument('--fa-id', type=str, help='要测试的fa_id（如0x0165）')
    parser.add_argument('--multiple', action='store_true', help='测试多个fa_id')
    args = parser.parse_args()
    
    if args.multiple:
        test_extract_multiple()
    elif args.fa_id:
        result = extract_fault_summary(args.fa_id, use_grep=True)
        print(result['summary_text'])
    else:
        # 默认测试0x165
        test_extract_0x165()

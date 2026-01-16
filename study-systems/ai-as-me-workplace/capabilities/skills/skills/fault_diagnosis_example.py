# -*- coding: utf-8 -*-
"""
故障定位系统使用示例

演示如何使用自动故障定位系统
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 修复Windows控制台编码问题
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

from auto_fault_diagnosis import process_ticket, process_fault_id, run_auto_monitor


def example_process_ticket():
    """示例：处理单个问题单"""
    print("=" * 80)
    print("示例1：处理单个问题单")
    print("=" * 80)
    print()
    
    # 替换为实际的问题单ID
    ticket_id = "recXXXXX"  # 或工作项ID
    
    result = process_ticket(ticket_id)
    
    if result.get('success'):
        print("\n[OK] 处理成功")
        for step in result.get('steps', []):
            step_name = step.get('step', '')
            success = step.get('success', False)
            print(f"  - {step_name}: {'✓' if success else '✗'}")
    else:
        print(f"\n[X] 处理失败: {result.get('error')}")


def example_process_fault_id():
    """示例：直接诊断Fault ID"""
    print("=" * 80)
    print("示例2：直接诊断Fault ID")
    print("=" * 80)
    print()
    
    # 替换为实际的Fault ID和日志路径
    fault_id = "0x0165"
    log_path = "/rawdata/roadtestv3/BAIC/3R7V/roadtest/cn/2025/10/20251016/BAIC/"
    
    result = process_fault_id(fault_id, log_path)
    
    if result.get('success'):
        print("\n[OK] 诊断成功")
        print("\n分析报告：")
        print(result.get('report'))
    else:
        print(f"\n[X] 诊断失败: {result.get('error')}")


def example_load_guide():
    """示例：加载故障定位指引"""
    print("=" * 80)
    print("示例3：加载故障定位指引")
    print("=" * 80)
    print()
    
    from fault_guide_reader import get_guide_reader
    
    reader = get_guide_reader()
    
    # 加载所有指引文档
    reader.load_all_guides()
    
    # 查询特定Fault ID的指引
    fault_id = "0x0165"
    guide_info = reader.get_guide_by_fault_id(fault_id)
    
    if guide_info:
        print(f"\n[OK] 找到Fault ID {fault_id} 的指引")
        print(f"指引信息: {guide_info}")
    else:
        print(f"\n[!] 未找到Fault ID {fault_id} 的指引")


def example_extract_log_path():
    """示例：提取日志路径"""
    print("=" * 80)
    print("示例4：从问题单提取日志路径")
    print("=" * 80)
    print()
    
    from fault_ticket_monitor import get_ticket_monitor
    from log_path_extractor import LogPathExtractor
    
    monitor = get_ticket_monitor()
    extractor = LogPathExtractor()
    
    # 获取问题单信息
    ticket_id = "recXXXXX"  # 替换为实际的问题单ID
    ticket_info = monitor.get_ticket_info(ticket_id)
    
    if ticket_info:
        # 提取日志路径
        log_paths = extractor.extract_from_ticket(ticket_info)
        
        if log_paths:
            print(f"[OK] 找到 {len(log_paths)} 个日志路径:")
            for path in log_paths:
                print(f"  - {path}")
        else:
            print("[!] 未找到日志路径")
    else:
        print("[X] 无法获取问题单信息")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='故障定位系统使用示例')
    parser.add_argument('--example', type=int, choices=[1, 2, 3, 4], help='运行示例编号')
    
    args = parser.parse_args()
    
    if args.example == 1:
        example_process_ticket()
    elif args.example == 2:
        example_process_fault_id()
    elif args.example == 3:
        example_load_guide()
    elif args.example == 4:
        example_extract_log_path()
    else:
        print("请选择要运行的示例:")
        print("  1 - 处理单个问题单")
        print("  2 - 直接诊断Fault ID")
        print("  3 - 加载故障定位指引")
        print("  4 - 提取日志路径")
        print()
        print("使用方法: python fault_diagnosis_example.py --example 1")

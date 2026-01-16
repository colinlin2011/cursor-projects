# -*- coding: utf-8 -*-
"""
测试报告生成
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

sys.stdout.reconfigure(encoding='utf-8')

from fault_report_generator import FaultReportGenerator

# 模拟分析结果
analysis_results = [
    {
        'fault_id': '0x0165',
        'guide_info': {
            '故障描述': '轨迹丢失',
            '常见原因': '传感器故障; 通信异常',
            '排查步骤': '检查传感器数据; 检查通信链路'
        },
        'analysis': {},
        'analysis_points': ['涉及轨迹相关功能', '传感器数据异常'],
        'key_errors': []
    },
    {
        'fault_id': '0x0336',
        'guide_info': {},
        'analysis': {},
        'analysis_points': ['通信模块异常'],
        'key_errors': []
    }
]

ticket_info = {
    '工作项ID': '6683487902',
    '记录ID': 'recv8hWWsiysEn',
    '日志路径': '/rawdata/roadtestv3/faw/1R10V/FL/cn/2026/1/20260112/14/17-09-14_snapshot/trigger_1768208954556949_5376300000_LK6ADAE47RB757806/'
}

print("=" * 80)
print("测试报告生成")
print("=" * 80)
print()

generator = FaultReportGenerator()

# 生成报告内容（不创建文档，只测试内容生成）
report_content = generator._generate_report_content(
    ticket_id='recv8hWWsiysEn',
    ticket_info=ticket_info,
    analysis_results=analysis_results
)

print(f"生成的块数量: {len(report_content)}")
print()

# 检查表格内容
for i, block in enumerate(report_content):
    if block.get('block_type') == 2:  # 文本块
        text_content = block.get('text', {}).get('elements', [{}])[0].get('text_run', {}).get('content', '')
        if '|' in text_content and 'Fault ID' in text_content:
            print(f"找到表格块 (块 {i}):")
            print(text_content[:500])  # 显示前500个字符
            print()
            break

print("=" * 80)

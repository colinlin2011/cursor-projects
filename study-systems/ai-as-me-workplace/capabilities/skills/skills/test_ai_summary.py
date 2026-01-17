# -*- coding: utf-8 -*-
"""
测试AI总结功能

生成AI总结提示词，可在Cursor中调用AI进行总结
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

from fault_summary_extractor import generate_ai_summary


def test_ai_summary(fa_id: str):
    """测试AI总结功能"""
    print("=" * 80)
    print(f"生成故障 {fa_id} 的AI总结提示词")
    print("=" * 80)
    print()
    
    # 生成AI总结提示词
    result = generate_ai_summary(fa_id, use_grep=True)
    
    # 显示结构化总结
    print("【结构化总结】")
    print(result['summary_text'])
    print()
    
    # 显示AI总结提示词
    print("=" * 80)
    print("【AI总结提示词】")
    print("=" * 80)
    print()
    print("您可以将以下提示词复制到Cursor中，让AI进行智能总结：")
    print()
    print("-" * 80)
    print(result['ai_summary_prompt'])
    print("-" * 80)
    print()
    
    # 保存提示词到文件
    output_file = Path(f"ai_summary_prompt_{fa_id.replace('0x', '').replace('0X', '')}.txt")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(result['ai_summary_prompt'])
    
    print(f"[OK] AI总结提示词已保存到: {output_file}")
    print()
    print("提示：在Cursor中，您可以：")
    print("1. 复制上面的提示词")
    print("2. 在Cursor中粘贴并让AI总结")
    print("3. 或者直接使用生成的提示词文件")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='生成故障AI总结提示词')
    parser.add_argument('--fa-id', type=str, default='0x0165', help='要测试的fa_id（如0x0165）')
    args = parser.parse_args()
    
    test_ai_summary(args.fa_id)

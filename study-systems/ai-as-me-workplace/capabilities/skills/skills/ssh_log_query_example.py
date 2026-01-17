# -*- coding: utf-8 -*-
"""
SSH日志查询引擎使用示例

演示各种查询场景的使用方法
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

from ssh_log_query_engine import create_query_engine, SSHLogQueryEngine
from ssh_log_query_config import validate_query_params


def example_1_single_keyword():
    """示例1：单关键字查询"""
    print("=" * 80)
    print("示例1：单关键字查询")
    print("=" * 80)
    print()
    
    engine = create_query_engine()
    
    try:
        result = engine.query(
            remote_path="/rawdata/roadtestv3/faw/1R10V/FL/cn/2026/1/20260112/14/17-09-14_snapshot/trigger_1768208954556949_5376300000_LK6ADAE47RB757806/log",
            keywords="Fault ID",
            context_lines=3,
            output_format="json",
            max_results=10
        )
        
        print(f"查询结果: {result['statistics']['total_matches']} 条匹配")
        print()
        
        for i, match in enumerate(result['matches'][:5], 1):  # 只显示前5条
            print(f"[{i}] 行 {match['line_number']}: {match['line_content'][:80]}...")
            if 'context' in match:
                print(f"    上下文: 前{len(match['context'].get('before', []))}行, 后{len(match['context'].get('after', []))}行")
        
    except Exception as e:
        print(f"[X] 查询失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        engine.close()


def example_2_multi_keyword_and():
    """示例2：多关键字AND查询"""
    print("=" * 80)
    print("示例2：多关键字AND查询")
    print("=" * 80)
    print()
    
    engine = create_query_engine()
    
    try:
        result = engine.query(
            remote_path="/rawdata/roadtestv3/faw/1R10V/FL/cn/2026/1/20260112/14/17-09-14_snapshot/trigger_1768208954556949_5376300000_LK6ADAE47RB757806/log",
            keywords=["SetFunc", "fu_st"],
            logic="AND",
            fuzzy_match=True,
            output_format="text",
            max_results=20
        )
        
        print(result['text'])
        
    except Exception as e:
        print(f"[X] 查询失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        engine.close()


def example_3_regex_extract():
    """示例3：正则表达式提取"""
    print("=" * 80)
    print("示例3：正则表达式提取")
    print("=" * 80)
    print()
    
    engine = create_query_engine()
    
    try:
        result = engine.query(
            remote_path="/rawdata/roadtestv3/faw/1R10V/FL/cn/2026/1/20260112/14/17-09-14_snapshot/trigger_1768208954556949_5376300000_LK6ADAE47RB757806/log",
            keywords="fa_id",
            extract_pattern=r"fa_id[:\s]+(0x[0-9A-Fa-f]+)",
            output_format="json",
            max_results=10
        )
        
        print(f"查询结果: {result['statistics']['total_matches']} 条匹配")
        print()
        
        for match in result['matches']:
            if 'extracted_info' in match and match['extracted_info']:
                for info in match['extracted_info']:
                    if info['groups']:
                        print(f"提取的Fault ID: {info['groups'][0]}")
                        print(f"  完整匹配: {info['full_match']}")
                        print(f"  行号: {match['line_number']}")
                        print()
        
    except Exception as e:
        print(f"[X] 查询失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        engine.close()


def example_4_context_extraction():
    """示例4：上下文提取"""
    print("=" * 80)
    print("示例4：上下文提取")
    print("=" * 80)
    print()
    
    engine = create_query_engine()
    
    try:
        result = engine.query(
            remote_path="/rawdata/roadtestv3/faw/1R10V/FL/cn/2026/1/20260112/14/17-09-14_snapshot/trigger_1768208954556949_5376300000_LK6ADAE47RB757806/log",
            keywords="error",
            context_lines=5,  # 提取前后5行
            output_format="both",
            max_results=5
        )
        
        # 显示文本格式结果
        print(result['text'])
        
        # 也可以查看JSON格式的上下文
        print("\n" + "=" * 80)
        print("JSON格式上下文示例（第一条匹配）:")
        print("=" * 80)
        if result['json']['matches']:
            match = result['json']['matches'][0]
            if 'context' in match:
                ctx = match['context']
                print(f"匹配行 ({ctx['line_number']}): {ctx['line']}")
                if ctx['before']:
                    print(f"\n前文 ({len(ctx['before'])}行):")
                    for line in ctx['before']:
                        print(f"  {line}")
                if ctx['after']:
                    print(f"\n后文 ({len(ctx['after'])}行):")
                    for line in ctx['after']:
                        print(f"  {line}")
        
    except Exception as e:
        print(f"[X] 查询失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        engine.close()


def example_5_force_remote():
    """示例5：强制使用远程grep"""
    print("=" * 80)
    print("示例5：强制使用远程grep")
    print("=" * 80)
    print()
    
    engine = create_query_engine()
    
    try:
        result = engine.query(
            remote_path="/rawdata/roadtestv3/faw/1R10V/FL/cn/2026/1/20260112/14/17-09-14_snapshot/trigger_1768208954556949_5376300000_LK6ADAE47RB757806/log",
            keywords="Fault ID",
            query_method="remote",  # 强制使用远程grep
            max_results=50,
            output_format="json"
        )
        
        print(f"查询结果: {result['statistics']['total_matches']} 条匹配")
        print(f"查询方式: 远程grep")
        
    except Exception as e:
        print(f"[X] 查询失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        engine.close()


def example_6_custom_config():
    """示例6：使用自定义SSH配置"""
    print("=" * 80)
    print("示例6：使用自定义SSH配置")
    print("=" * 80)
    print()
    
    # 自定义SSH配置
    custom_ssh_config = {
        "host": "10.241.120.100",
        "port": 22,
        "username": "dji",
        "password": "AutoXPC.246!",
        "timeout": 30
    }
    
    engine = SSHLogQueryEngine(ssh_config=custom_ssh_config)
    
    try:
        result = engine.query(
            remote_path="/rawdata/roadtestv3/.../log",
            keywords="test",
            output_format="json"
        )
        
        print(f"查询结果: {result['statistics']['total_matches']} 条匹配")
        
    except Exception as e:
        print(f"[X] 查询失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        engine.close()


def example_7_validate_params():
    """示例7：参数验证"""
    print("=" * 80)
    print("示例7：参数验证")
    print("=" * 80)
    print()
    
    # 测试有效参数
    valid_params = {
        'remote_path': '/path/to/log',
        'keywords': 'test',
        'logic': 'OR',
        'output_format': 'json',
        'max_results': 100,
        'context_lines': 5
    }
    
    is_valid, error = validate_query_params(valid_params)
    print(f"有效参数验证: {is_valid}")
    if error:
        print(f"错误: {error}")
    print()
    
    # 测试无效参数
    invalid_params = {
        'remote_path': '/path/to/log',
        'keywords': 'test',
        'logic': 'INVALID',  # 无效的逻辑运算符
        'max_results': -1  # 无效的最大结果数
    }
    
    is_valid, error = validate_query_params(invalid_params)
    print(f"无效参数验证: {is_valid}")
    if error:
        print(f"错误: {error}")


def main():
    """运行所有示例"""
    print("SSH日志查询引擎使用示例")
    print("=" * 80)
    print()
    print("注意：以下示例需要有效的SSH连接和日志文件路径")
    print("请根据实际情况修改路径和关键字")
    print()
    
    # 运行示例
    examples = [
        ("示例1：单关键字查询", example_1_single_keyword),
        ("示例2：多关键字AND查询", example_2_multi_keyword_and),
        ("示例3：正则表达式提取", example_3_regex_extract),
        ("示例4：上下文提取", example_4_context_extraction),
        ("示例5：强制使用远程grep", example_5_force_remote),
        ("示例6：使用自定义SSH配置", example_6_custom_config),
        ("示例7：参数验证", example_7_validate_params),
    ]
    
    print("可用示例:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"  {i}. {name}")
    print()
    
    choice = input("请选择要运行的示例（1-7，或按Enter运行示例7）: ").strip()
    
    if not choice:
        choice = "7"
    
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(examples):
            name, func = examples[idx]
            print()
            func()
        else:
            print("[X] 无效的选择")
    except ValueError:
        print("[X] 无效的输入")
    except KeyboardInterrupt:
        print("\n\n已取消")
    except Exception as e:
        print(f"[X] 运行示例失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
"""
完整的FMEA导入脚本

整合导入流程：
1. 导入架构元素
2. 导入子功能清单
3. 导入失效模式影响分析

改进：详细记录跳过的条目，方便人工检查
"""

import sys
import os
import argparse
import json
from typing import Optional, Dict, Any, List
from pathlib import Path
from datetime import datetime

# 修复Windows控制台编码问题
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from interactive_fmea_import import (
    get_user_access_token,
    get_app_token_and_table_ids,
    step1_import_architecture_elements,
    step2_import_functions,
    step3_import_fmea
)
from fmea_data_reader import FMEADataReader


def print_skipped_items(skipped_items: List[Dict[str, Any]], step_name: str):
    """打印跳过的条目详情"""
    if not skipped_items:
        return
    
    print("\n" + "=" * 80)
    print(f"跳过的条目详情 - {step_name}")
    print("=" * 80)
    print(f"总计: {len(skipped_items)} 条")
    print()
    
    for i, item in enumerate(skipped_items, 1):
        print(f"{i}. {item.get('reason', '未知原因')}")
        if 'data' in item:
            data = item['data']
            if isinstance(data, dict):
                for key, value in data.items():
                    if value:
                        value_str = str(value)
                        if len(value_str) > 100:
                            value_str = value_str[:100] + "..."
                        print(f"   {key}: {value_str}")
            else:
                print(f"   数据: {data}")
        print()


def import_fmea_complete(
    fmea_name: str,
    sheet_name: Optional[str] = None,
    dry_run: bool = False,
    skip_architecture: bool = False,
    skip_functions: bool = False,
    skip_fmea: bool = False
):
    """
    完整的FMEA导入流程
    
    Args:
        fmea_name: FMEA表格名称（如 "Control", "04_Calibration_System_SW_FMEA"）
        dry_run: 是否为试运行
        skip_architecture: 是否跳过架构元素导入
        skip_functions: 是否跳过子功能导入
        skip_fmea: 是否跳过失效模式导入
    """
    print("=" * 80)
    print("完整FMEA导入工具")
    print("=" * 80)
    print(f"FMEA表格: {fmea_name}")
    if sheet_name:
        print(f"指定工作表: {sheet_name}")
    print(f"试运行模式: {'是' if dry_run else '否'}")
    print()
    
    # 步骤0: 获取用户访问令牌
    print("步骤0: 获取用户访问令牌...")
    user_access_token = get_user_access_token()
    if not user_access_token:
        print("[X] 无法获取有效的用户访问令牌")
        return {'success': False, 'error': '无法获取用户访问令牌'}
    print("[OK] 已获取用户访问令牌")
    print()
    
    # 步骤0.5: 读取FMEA数据
    print(f"步骤0.5: 读取FMEA数据 ({fmea_name})...")
    if sheet_name:
        print(f"  指定工作表: {sheet_name}")
    reader = FMEADataReader()
    fmea_data = reader.read_fmea_data(fmea_name, sheet_name=sheet_name)
    if not fmea_data:
        print(f"[X] 无法读取FMEA数据: {fmea_name}")
        if sheet_name:
            print(f"  指定工作表: {sheet_name}")
        return {'success': False, 'error': f'无法读取FMEA数据: {fmea_name}'}
    
    validation = reader.validate_data(fmea_data)
    if not validation['valid']:
        print(f"[X] 数据验证失败: {validation['issues']}")
        return {'success': False, 'error': '数据验证失败', 'issues': validation['issues']}
    
    cleaned_rows = validation['cleaned_rows']
    print(f"[OK] 已读取 {len(cleaned_rows)} 行有效数据")
    print()
    
    # 步骤0.6: 获取app_token和table_ids
    print("步骤0.6: 获取多维表格信息...")
    app_token, table_ids = get_app_token_and_table_ids(user_access_token)
    if not app_token:
        return {'success': False, 'error': '无法获取多维表格信息'}
    
    print(f"[OK] app_token: {app_token[:20]}...")
    for key, table_id in table_ids.items():
        if table_id:
            print(f"[OK] {key}表: {table_id}")
    print()
    
    # 汇总结果
    results = {
        'fmea_name': fmea_name,
        'timestamp': datetime.now().isoformat(),
        'dry_run': dry_run,
        'steps': {}
    }
    
    all_skipped_items = []
    
    # 步骤1: 导入架构元素
    if not skip_architecture:
        print("\n" + "=" * 80)
        print("步骤1: 导入架构元素")
        print("=" * 80)
        print()
        
        if not table_ids.get('architecture'):
            print("[X] 架构元素表未找到，跳过步骤1")
            results['steps']['architecture'] = {'success': False, 'error': '表未找到'}
        else:
            result = step1_import_architecture_elements(
                app_token,
                table_ids['architecture'],
                cleaned_rows,
                user_access_token,
                fmea_name=fmea_name,
                dry_run=dry_run
            )
            results['steps']['architecture'] = result
            
            # 收集跳过的条目
            if 'skipped_items' in result:
                for item in result['skipped_items']:
                    item['step'] = '架构元素'
                all_skipped_items.extend(result['skipped_items'])
    else:
        print("\n[!] 跳过步骤1: 导入架构元素")
        results['steps']['architecture'] = {'skipped': True}
    
    # 步骤2: 导入子功能
    if not skip_functions:
        print("\n" + "=" * 80)
        print("步骤2: 导入子功能清单")
        print("=" * 80)
        print()
        
        if not table_ids.get('function'):
            print("[X] 子功能清单表未找到，跳过步骤2")
            results['steps']['function'] = {'success': False, 'error': '表未找到'}
        elif not table_ids.get('architecture'):
            print("[X] 架构元素表未找到，无法导入子功能（需要关联架构元素）")
            results['steps']['function'] = {'success': False, 'error': '架构元素表未找到'}
        else:
            # 从步骤1的结果中获取element_name_to_record_id
            architecture_result = results['steps'].get('architecture', {})
            element_name_to_record_id = architecture_result.get('element_name_to_record_id', {})
            
            # 如果步骤1被跳过或element_name_to_record_id为空，需要重新加载
            if not element_name_to_record_id:
                # 重新加载架构元素映射
                from fmea_import_utils import FMEAImportUtils
                utils = FMEAImportUtils(app_token, user_access_token)
                records = utils.collaborator.get_all_records(app_token, table_ids['architecture'])
                element_name_to_record_id = {}
                for record in records:
                    record_fields = record.get('fields', {})
                    element_name = record_fields.get('元素名称', '')
                    if element_name:
                        element_name_to_record_id[element_name] = record.get('record_id')
                print(f"[!] 重新加载架构元素映射: {len(element_name_to_record_id)} 个元素")
            
            result = step2_import_functions(
                app_token,
                table_ids['function'],
                cleaned_rows,
                element_name_to_record_id,
                user_access_token,
                dry_run=dry_run
            )
            results['steps']['function'] = result
            
            # 收集跳过的条目
            if 'skipped_items' in result:
                for item in result['skipped_items']:
                    item['step'] = '子功能清单'
                all_skipped_items.extend(result['skipped_items'])
    else:
        print("\n[!] 跳过步骤2: 导入子功能清单")
        results['steps']['function'] = {'skipped': True}
    
    # 步骤3: 导入失效模式
    if not skip_fmea:
        print("\n" + "=" * 80)
        print("步骤3: 导入失效模式影响分析")
        print("=" * 80)
        print()
        
        if not table_ids.get('fmea'):
            print("[X] 失效模式影响分析表未找到，跳过步骤3")
            results['steps']['fmea'] = {'success': False, 'error': '表未找到'}
        elif not table_ids.get('function'):
            print("[X] 子功能清单表未找到，无法导入失效模式（需要关联功能）")
            results['steps']['fmea'] = {'success': False, 'error': '子功能清单表未找到'}
        else:
            result = step3_import_fmea(
                app_token,
                table_ids['fmea'],
                table_ids['function'],
                cleaned_rows,
                user_access_token,
                dry_run=dry_run
            )
            results['steps']['fmea'] = result
            
            # 收集跳过的条目
            if 'skipped_items' in result.get('stats', {}):
                skipped_stats = result['stats'].get('skipped_items', [])
                for item in skipped_stats:
                    item['step'] = '失效模式影响分析'
                all_skipped_items.extend(skipped_stats)
    else:
        print("\n[!] 跳过步骤3: 导入失效模式影响分析")
        results['steps']['fmea'] = {'skipped': True}
    
    # 打印跳过的条目汇总
    if all_skipped_items:
        print("\n" + "=" * 80)
        print("跳过的条目汇总")
        print("=" * 80)
        
        # 按步骤分组
        by_step = {}
        for item in all_skipped_items:
            step = item.get('step', '未知步骤')
            if step not in by_step:
                by_step[step] = []
            by_step[step].append(item)
        
        for step, items in by_step.items():
            print_skipped_items(items, step)
    else:
        print("\n[OK] 没有跳过的条目")
    
    # 打印最终汇总
    print("\n" + "=" * 80)
    print("导入总结")
    print("=" * 80)
    
    for step_name, step_result in results['steps'].items():
        if step_result.get('skipped'):
            print(f"{step_name}: 已跳过")
        elif step_result.get('success'):
            stats = step_result.get('stats', {})
            print(f"{step_name}: 成功")
            if 'created' in stats:
                print(f"  创建: {stats['created']}")
            if 'existing' in stats:
                print(f"  已存在: {stats['existing']}")
            if 'skipped' in stats:
                print(f"  跳过: {stats['skipped']}")
        else:
            print(f"{step_name}: 失败")
            if 'error' in step_result:
                print(f"  错误: {step_result['error']}")
    
    # 保存报告
    report_dir = Path("work")
    report_dir.mkdir(exist_ok=True)
    report_file = report_dir / f"fmea_complete_import_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n报告已保存: {report_file}")
    
    # 计算总体成功状态
    all_success = all(
        step_result.get('skipped') or step_result.get('success', False)
        for step_result in results['steps'].values()
    )
    
    results['success'] = all_success
    return results


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='完整FMEA导入工具')
    parser.add_argument('fmea_name', help='FMEA表格名称（如 Control, 04_Calibration_System_SW_FMEA）')
    parser.add_argument('--sheet-name', '--sheet', dest='sheet_name', help='指定工作表名称（如 System SW FMEA V0.2），如果不指定则自动识别主工作表')
    parser.add_argument('--dry-run', action='store_true', help='试运行模式，不实际导入数据')
    parser.add_argument('--skip-architecture', action='store_true', help='跳过架构元素导入')
    parser.add_argument('--skip-functions', action='store_true', help='跳过子功能导入')
    parser.add_argument('--skip-fmea', action='store_true', help='跳过失效模式导入')
    
    args = parser.parse_args()
    
    result = import_fmea_complete(
        args.fmea_name,
        sheet_name=args.sheet_name,
        dry_run=args.dry_run,
        skip_architecture=args.skip_architecture,
        skip_functions=args.skip_functions,
        skip_fmea=args.skip_fmea
    )
    
    if result.get('success'):
        print("\n[OK] 导入完成！")
        sys.exit(0)
    else:
        print("\n[X] 导入失败")
        sys.exit(1)


if __name__ == "__main__":
    main()

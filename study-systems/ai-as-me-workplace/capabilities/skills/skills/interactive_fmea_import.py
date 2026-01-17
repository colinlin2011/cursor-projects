# -*- coding: utf-8 -*-
"""
交互式FMEA导入主脚本

提供交互式界面，分步导入架构元素、子功能和失效模式
"""

import sys
import os
import argparse
import json
from typing import Optional, Dict, Any, Tuple
from pathlib import Path
from datetime import datetime

# 修复Windows控制台编码问题
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fmea_data_reader import FMEADataReader
from import_architecture_elements import ArchitectureElementImporter
from import_functions import FunctionImporter
from fmea_importer import FMEAImporter
from import_failure_modes import FailureModeImporter
from bitable_cache_manager import (
    BitableCacheManager,
    BITABLE_CONFIGS,
    APP_ID,
    APP_SECRET,
    SPACE_ID,
    CACHE_DIR
)
from token_manager import TokenManager

# 目标多维表格配置
TARGET_NODE_TOKEN = "BPddwBxoRiPFSsk8jZJctCMmndg"
ARCHITECTURE_TABLE_NAME = "架构元素表"
FUNCTION_TABLE_NAME = "子功能清单表"
FMEA_TABLE_NAME = "失效模式影响分析表_SW"


def get_user_access_token() -> Optional[str]:
    """获取有效的用户访问令牌"""
    token_manager = TokenManager()
    return token_manager.get_valid_user_access_token()


def get_app_token_and_table_ids(user_access_token: str) -> Tuple[Optional[str], Dict[str, Optional[str]]]:
    """
    获取app_token和所有表的table_id
    
    Args:
        user_access_token: 用户访问令牌
        
    Returns:
        (app_token, table_ids) 元组，table_ids是字典 {table_name: table_id}
    """
    manager = BitableCacheManager(
        app_id=APP_ID,
        app_secret=APP_SECRET,
        user_access_token=user_access_token,
        space_id=SPACE_ID
    )
    
    # 获取app_token
    app_token = manager.get_app_token_from_wiki(TARGET_NODE_TOKEN, SPACE_ID)
    if not app_token:
        print(f"[X] 无法获取app_token for node_token: {TARGET_NODE_TOKEN}")
        return None, {}
    
    # 从缓存中查找table_id
    cache_file = None
    for config in BITABLE_CONFIGS:
        if config['node_token'] == TARGET_NODE_TOKEN:
            cache_file = config['cache_file']
            break
    
    if not cache_file:
        print(f"[X] 未找到缓存配置 for node_token: {TARGET_NODE_TOKEN}")
        return None, {}
    
    # 加载缓存数据
    cache_path = CACHE_DIR / cache_file
    if not cache_path.exists():
        print(f"[!] 缓存文件不存在，正在同步...")
        manager.load_bitable_data(TARGET_NODE_TOKEN, cache_file, force_refresh=True)
    
    # 读取缓存文件
    try:
        with open(cache_path, 'r', encoding='utf-8') as f:
            cache_data = json.load(f)
    except Exception as e:
        print(f"[X] 读取缓存文件失败: {e}")
        return None, {}
    
    # 查找所有需要的表
    tables = cache_data.get('tables', {})
    table_ids = {}
    
    target_tables = {
        'architecture': ARCHITECTURE_TABLE_NAME,
        'function': FUNCTION_TABLE_NAME,
        'fmea': FMEA_TABLE_NAME
    }
    
    for key, table_name in target_tables.items():
        table_data = None
        
        # 精确匹配
        if table_name in tables:
            table_data = tables[table_name]
        else:
            # 模糊匹配
            for name, data in tables.items():
                if table_name in name or name in table_name:
                    table_data = data
                    break
        
        if table_data:
            table_id = table_data.get('table_id')
            table_ids[key] = table_id
        else:
            print(f"[!] 未找到表: {table_name}")
            table_ids[key] = None
    
    return app_token, table_ids


def step1_import_architecture_elements(
    app_token: str,
    table_id: str,
    fmea_rows: List[Dict[str, Any]],
    user_access_token: str,
    fmea_name: Optional[str] = None,
    dry_run: bool = False
) -> Dict[str, Any]:
    """步骤1：导入架构元素"""
    print("\n" + "=" * 80)
    print("步骤1：导入架构元素")
    print("=" * 80)
    print()
    
    importer = ArchitectureElementImporter(app_token, table_id, user_access_token)
    result = importer.import_elements(fmea_rows, fmea_name=fmea_name, dry_run=dry_run)
    
    return result


def step2_import_functions(
    app_token: str,
    table_id: str,
    fmea_rows: List[Dict[str, Any]],
    element_name_to_record_id: Dict[str, str],
    user_access_token: str,
    dry_run: bool = False
) -> Dict[str, Any]:
    """步骤2：导入子功能"""
    print("\n" + "=" * 80)
    print("步骤2：导入子功能")
    print("=" * 80)
    print()
    
    importer = FunctionImporter(
        app_token,
        table_id,
        element_name_to_record_id,
        user_access_token
    )
    result = importer.import_functions(fmea_rows, dry_run=dry_run)
    
    return result


def step3_import_fmea(
    app_token: str,
    table_id: str,
    function_table_id: str,
    fmea_rows: List[Dict[str, Any]],
    user_access_token: str,
    dry_run: bool = False
) -> Dict[str, Any]:
    """步骤3：导入失效模式（可选）"""
    print("\n" + "=" * 80)
    print("步骤3：导入失效模式影响分析")
    print("=" * 80)
    print()
    
    importer = FailureModeImporter(
        app_token,
        table_id,
        function_table_id,
        user_access_token
    )
    result = importer.import_failure_modes(fmea_rows, dry_run=dry_run)
    
    return result


def interactive_import(
    fmea_name: str,
    steps: List[str] = None,
    dry_run: bool = False
) -> Dict[str, Any]:
    """
    交互式导入
    
    Args:
        fmea_name: FMEA表格名称
        steps: 要执行的步骤列表（['architecture', 'function', 'fmea']），如果为None则交互式选择
        dry_run: 是否为试运行
        
    Returns:
        导入结果字典
    """
    print("=" * 80)
    print("交互式FMEA导入工具")
    print("=" * 80)
    print()
    
    # 1. 获取用户访问令牌
    print("获取用户访问令牌...")
    user_access_token = get_user_access_token()
    if not user_access_token:
        print("[X] 无法获取有效的用户访问令牌")
        return {'success': False, 'error': '无法获取用户访问令牌'}
    print("[OK] 已获取用户访问令牌")
    print()
    
    # 2. 读取FMEA数据
    print(f"读取FMEA数据 ({fmea_name})...")
    reader = FMEADataReader()
    fmea_data = reader.read_fmea_data(fmea_name)
    if not fmea_data:
        return {'success': False, 'error': '无法读取FMEA数据'}
    
    validation = reader.validate_data(fmea_data)
    if not validation['valid']:
        print(f"[X] 数据验证失败: {validation['issues']}")
        return {'success': False, 'error': '数据验证失败', 'issues': validation['issues']}
    
    cleaned_rows = validation['cleaned_rows']
    print(f"[OK] 已读取 {len(cleaned_rows)} 行有效数据")
    print()
    
    # 3. 获取app_token和table_ids
    print("获取多维表格信息...")
    app_token, table_ids = get_app_token_and_table_ids(user_access_token)
    if not app_token:
        return {'success': False, 'error': '无法获取多维表格信息'}
    
    print(f"[OK] app_token: {app_token[:20]}...")
    for key, table_id in table_ids.items():
        if table_id:
            print(f"[OK] {key}表: {table_id}")
        else:
            print(f"[X] {key}表: 未找到")
    print()
    
    # 4. 交互式选择步骤
    if steps is None:
        print("请选择要执行的步骤（可以多选，用逗号分隔）:")
        print("  1. 导入架构元素")
        print("  2. 导入子功能")
        print("  3. 导入失效模式影响分析")
        print("  all. 执行所有步骤")
        print()
        
        choice = input("请输入选择 (1,2,3,all): ").strip().lower()
        
        if choice == 'all':
            steps = ['architecture', 'function', 'fmea']
        else:
            steps = []
            if '1' in choice:
                steps.append('architecture')
            if '2' in choice:
                steps.append('function')
            if '3' in choice:
                steps.append('fmea')
    
    if not steps:
        print("[!] 未选择任何步骤")
        return {'success': False, 'error': '未选择任何步骤'}
    
    print(f"\n将执行以下步骤: {', '.join(steps)}")
    if dry_run:
        print("[试运行模式]")
    print()
    
    # 5. 执行步骤
    results = {}
    element_name_to_record_id = {}
    function_to_record_id = {}
    
    # 步骤1：导入架构元素
    if 'architecture' in steps:
        if not table_ids.get('architecture'):
            print("[X] 架构元素表未找到，跳过步骤1")
        else:
            result = step1_import_architecture_elements(
                app_token,
                table_ids['architecture'],
                cleaned_rows,
                user_access_token,
                dry_run=dry_run
            )
            results['architecture'] = result
            if result.get('success') and not dry_run:
                element_name_to_record_id = result.get('element_name_to_record_id', {})
    
    # 步骤2：导入子功能
    if 'function' in steps:
        if not table_ids.get('function'):
            print("[X] 子功能清单表未找到，跳过步骤2")
        else:
            if not element_name_to_record_id:
                print("[!] 警告: 没有架构元素的映射，正在从架构元素表加载...")
                # 尝试从架构元素表加载映射关系
                from fmea_import_utils import FMEAImportUtils
                utils = FMEAImportUtils(app_token, user_access_token)
                
                if table_ids.get('architecture'):
                    # 获取所有架构元素记录
                    records = utils.collaborator.get_all_records(
                        app_token,
                        table_ids['architecture']
                    )
                    
                    # 建立映射
                    structure_info = utils.get_table_structure_info(table_ids['architecture'])
                    field_name_to_id = structure_info['field_name_to_id']
                    element_name_field_id = field_name_to_id.get('元素名称')
                    
                    # 注意：get_all_records返回的记录中，字段是用字段名作为key的
                    # 所以直接使用字段名查找
                    for record in records:
                        record_fields = record.get('fields', {})
                        element_name_value = record_fields.get('元素名称', '')
                        
                        # 处理不同类型的值
                        if isinstance(element_name_value, list):
                            # 列表类型（通常不会，但处理一下）
                            if element_name_value:
                                element_name = str(element_name_value[0])
                            else:
                                continue
                        else:
                            element_name = str(element_name_value).strip()
                        
                        if element_name:
                            element_name_to_record_id[element_name] = record.get('record_id')
                    
                    print(f"[OK] 从架构元素表加载了 {len(element_name_to_record_id)} 个架构元素的映射")
                    if len(element_name_to_record_id) <= 10:
                        for name, rid in element_name_to_record_id.items():
                            print(f"    {name}: {rid}")
                    else:
                        print("[X] 无法找到'元素名称'字段")
                else:
                    print("[X] 架构元素表未找到，无法加载映射")
                    print("    建议先执行步骤1（导入架构元素）")
                    if sys.stdin.isatty():  # 检查是否在交互式终端
                        response = input("是否继续？(y/n): ")
                        if response.lower() != 'y':
                            return {'success': False, 'error': '用户取消'}
            
            result = step2_import_functions(
                app_token,
                table_ids['function'],
                cleaned_rows,
                element_name_to_record_id,
                user_access_token,
                dry_run=dry_run
            )
            results['function'] = result
            if result.get('success') and not dry_run:
                function_to_record_id = result.get('function_to_record_id', {})
    
    # 步骤3：导入失效模式
    if 'fmea' in steps:
        if not table_ids.get('fmea'):
            print("[X] 失效模式影响分析表未找到，跳过步骤3")
        else:
            if not table_ids.get('function'):
                print("[X] 子功能清单表未找到，无法导入失效模式（需要关联功能）")
            else:
                result = step3_import_fmea(
                    app_token,
                    table_ids['fmea'],
                    table_ids['function'],
                    cleaned_rows,
                    user_access_token,
                    dry_run=dry_run
                )
                results['fmea'] = result
    
    # 6. 生成总结报告
    print("\n" + "=" * 80)
    print("导入总结")
    print("=" * 80)
    
    for step_name, result in results.items():
        print(f"\n{step_name}:")
        if result.get('success'):
            stats = result.get('stats', {})
            print(f"  成功: {stats.get('created', 0) + stats.get('existing', 0)}")
            print(f"  失败: {stats.get('failed', 0)}")
        else:
            print(f"  失败: {result.get('error', '未知错误')}")
    
    # 保存报告
    report_file = Path(f"work/fmea_interactive_import_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    report_file.parent.mkdir(parents=True, exist_ok=True)
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump({
            'fmea_name': fmea_name,
            'steps': steps,
            'dry_run': dry_run,
            'timestamp': datetime.now().isoformat(),
            'results': results,
            'element_name_to_record_id': element_name_to_record_id,
            'function_to_record_id': function_to_record_id
        }, f, ensure_ascii=False, indent=2)
    print(f"\n报告已保存: {report_file}")
    
    return {
        'success': all(r.get('success', False) for r in results.values()),
        'results': results
    }


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='交互式FMEA导入工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 交互式选择步骤
  python interactive_fmea_import.py Control
  
  # 只导入架构元素
  python interactive_fmea_import.py Control --steps architecture
  
  # 导入架构元素和子功能
  python interactive_fmea_import.py Control --steps architecture,function
  
  # 试运行
  python interactive_fmea_import.py Control --dry-run
        """
    )
    
    parser.add_argument(
        'fmea_name',
        help='FMEA表格名称（如 Control, Planning 等）'
    )
    
    parser.add_argument(
        '--steps',
        help='要执行的步骤，用逗号分隔（architecture,function,fmea）'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='试运行模式（不实际创建记录）'
    )
    
    args = parser.parse_args()
    
    steps = None
    if args.steps:
        steps = [s.strip() for s in args.steps.split(',')]
    
    result = interactive_import(
        args.fmea_name,
        steps=steps,
        dry_run=args.dry_run
    )
    
    if result.get('success'):
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()

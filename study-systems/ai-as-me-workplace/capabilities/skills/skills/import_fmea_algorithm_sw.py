# -*- coding: utf-8 -*-
"""
算法软件FMEA导入主脚本

命令行接口，用于将算法软件部分的FMEA在线表格数据导入到多维表格"失效模式影响分析表_SW"中
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
from fmea_importer import FMEAImporter
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
TARGET_TABLE_NAME = "失效模式影响分析表_SW"


def get_user_access_token() -> Optional[str]:
    """获取有效的用户访问令牌"""
    token_manager = TokenManager()
    return token_manager.get_valid_user_access_token()


def get_app_token_and_table_id(
    node_token: str,
    table_name: str,
    user_access_token: str
) -> Tuple[Optional[str], Optional[str]]:
    """
    获取app_token和table_id
    
    Args:
        node_token: Wiki节点token
        table_name: 表名
        user_access_token: 用户访问令牌
        
    Returns:
        (app_token, table_id) 元组
    """
    manager = BitableCacheManager(
        app_id=APP_ID,
        app_secret=APP_SECRET,
        user_access_token=user_access_token,
        space_id=SPACE_ID
    )
    
    # 获取app_token
    app_token = manager.get_app_token_from_wiki(node_token, SPACE_ID)
    if not app_token:
        print(f"[X] 无法获取app_token for node_token: {node_token}")
        return None, None
    
    # 从缓存中查找table_id
    cache_file = None
    for config in BITABLE_CONFIGS:
        if config['node_token'] == node_token:
            cache_file = config['cache_file']
            break
    
    if not cache_file:
        print(f"[X] 未找到缓存配置 for node_token: {node_token}")
        return None, None
    
    # 加载缓存数据
    cache_path = CACHE_DIR / cache_file
    if not cache_path.exists():
        print(f"[!] 缓存文件不存在，正在同步...")
        manager.load_bitable_data(node_token, cache_file, force_refresh=True)
    
    # 读取缓存文件
    try:
        with open(cache_path, 'r', encoding='utf-8') as f:
            cache_data = json.load(f)
    except Exception as e:
        print(f"[X] 读取缓存文件失败: {e}")
        return None, None
    
    # 查找表
    tables = cache_data.get('tables', {})
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
    
    if not table_data:
        print(f"[X] 未找到表: {table_name}")
        print(f"可用的表: {', '.join(tables.keys())}")
        return None, None
    
    table_id = table_data.get('table_id')
    if not table_id:
        print(f"[X] 表数据中缺少table_id")
        return None, None
    
    return app_token, table_id


def import_fmea(
    fmea_name: str,
    dry_run: bool = False,
    skip_relations: bool = True
) -> Dict[str, Any]:
    """
    导入FMEA数据
    
    Args:
        fmea_name: FMEA表格名称（如 "10_Planning_System_SW_FMEA" 或 "Planning"）
        dry_run: 是否为试运行
        skip_relations: 是否跳过关联字段
        
    Returns:
        导入结果字典
    """
    print("=" * 80)
    print("算法软件FMEA导入工具")
    print("=" * 80)
    print()
    
    # 1. 获取用户访问令牌
    print("步骤1: 获取用户访问令牌...")
    user_access_token = get_user_access_token()
    if not user_access_token:
        print("[X] 无法获取有效的用户访问令牌")
        return {'success': False, 'error': '无法获取用户访问令牌'}
    print("[OK] 已获取用户访问令牌")
    print()
    
    # 2. 读取FMEA数据
    print(f"步骤2: 读取FMEA数据 ({fmea_name})...")
    reader = FMEADataReader()
    fmea_data = reader.read_fmea_data(fmea_name)
    if not fmea_data:
        return {'success': False, 'error': '无法读取FMEA数据'}
    
    # 验证数据
    validation = reader.validate_data(fmea_data)
    if not validation['valid']:
        print(f"[X] 数据验证失败: {validation['issues']}")
        return {'success': False, 'error': '数据验证失败', 'issues': validation['issues']}
    
    if validation['issues']:
        print(f"[!] 数据问题: {validation['issues'][:5]}")
    
    cleaned_rows = validation['cleaned_rows']
    print(f"[OK] 已读取 {len(cleaned_rows)} 行有效数据")
    print()
    
    # 3. 获取app_token和table_id
    print("步骤3: 获取多维表格信息...")
    app_token, table_id = get_app_token_and_table_id(
        TARGET_NODE_TOKEN,
        TARGET_TABLE_NAME,
        user_access_token
    )
    if not app_token or not table_id:
        return {'success': False, 'error': '无法获取多维表格信息'}
    print(f"[OK] app_token: {app_token[:20]}...")
    print(f"[OK] table_id: {table_id}")
    print()
    
    # 4. 导入数据
    print("步骤4: 导入数据...")
    importer = FMEAImporter(app_token, table_id, user_access_token)
    result = importer.import_data(
        cleaned_rows,
        skip_relations=skip_relations,
        dry_run=dry_run
    )
    
    # 5. 生成报告
    print()
    print("=" * 80)
    print("导入报告")
    print("=" * 80)
    print(f"FMEA表格: {fmea_name}")
    print(f"目标表: {TARGET_TABLE_NAME}")
    print(f"试运行: {dry_run}")
    print()
    
    stats = result.get('stats', {})
    print(f"总计: {stats.get('total', 0)}")
    print(f"成功: {stats.get('success', 0)}")
    print(f"失败: {stats.get('failed', 0)}")
    print(f"跳过: {stats.get('skipped', 0)}")
    
    if stats.get('errors'):
        error_count = len(stats['errors'])
        print(f"\n错误数: {error_count}")
        if error_count > 0:
            print("\n错误详情（前5个）:")
            for error in stats['errors'][:5]:
                if 'row' in error:
                    print(f"  第{error['row']}行: {error['error']}")
                elif 'batch' in error:
                    print(f"  批次: {error['error']}")
    
    # 保存报告
    report_file = Path(f"work/fmea_import_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    report_file.parent.mkdir(parents=True, exist_ok=True)
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump({
            'fmea_name': fmea_name,
            'target_table': TARGET_TABLE_NAME,
            'dry_run': dry_run,
            'timestamp': datetime.now().isoformat(),
            'result': result
        }, f, ensure_ascii=False, indent=2)
    print(f"\n报告已保存: {report_file}")
    
    return result


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='导入算法软件FMEA数据到多维表格',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 试运行（不实际导入）
  python import_fmea_algorithm_sw.py Planning --dry-run
  
  # 实际导入
  python import_fmea_algorithm_sw.py Planning
  
  # 导入Control模块
  python import_fmea_algorithm_sw.py Control
        """
    )
    
    parser.add_argument(
        'fmea_name',
        help='FMEA表格名称（如 Planning, Control, TSLR 等）'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='试运行模式（不实际创建记录）'
    )
    
    parser.add_argument(
        '--include-relations',
        action='store_true',
        help='包含关联字段（默认跳过）'
    )
    
    args = parser.parse_args()
    
    result = import_fmea(
        args.fmea_name,
        dry_run=args.dry_run,
        skip_relations=not args.include_relations
    )
    
    if result.get('success'):
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()

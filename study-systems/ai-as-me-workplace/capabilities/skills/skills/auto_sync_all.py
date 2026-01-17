# -*- coding: utf-8 -*-
"""
自动同步所有缓存内容（包含token自动刷新）

支持：
1. 自动刷新访问令牌
2. 自动同步多维表格缓存
3. 自动同步在线表格缓存
4. 定时同步任务
"""

import sys
import os
import time
from datetime import datetime
from pathlib import Path

# 修复Windows控制台编码问题
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 配置信息
APP_ID = "cli_a9c92ca516f99bd9"
APP_SECRET = "zlOKnyZkSuSUSr0WlAl6qbh5Qw4eM6wC"
SPACE_ID = "7353073903872868356"

# 同步配置
SYNC_INTERVAL_HOURS = 1  # 默认每小时同步一次


def get_user_access_token():
    """获取有效的user_access_token（自动刷新）"""
    try:
        from token_manager import get_user_access_token as get_token
        token = get_token()
        if token:
            return token
    except ImportError:
        print("[!] token_manager模块未找到，使用环境变量...")
    except Exception as e:
        print(f"[!] 无法从token_manager获取token: {e}")
    
    # 回退到环境变量或默认值
    token = os.getenv("FEISHU_USER_ACCESS_TOKEN")
    if not token:
        print("[X] 无法获取访问令牌，请先运行授权脚本获取token")
        print("    运行: python get_user_token_for_bitable.py")
    return token


def sync_all_caches(force_refresh=False):
    """同步所有缓存（多维表格 + 在线表格）"""
    print("=" * 80)
    print(f"开始同步所有缓存 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print()
    
    # 获取有效的访问令牌（自动刷新）
    user_access_token = get_user_access_token()
    if not user_access_token:
        print("[X] 无法获取有效的访问令牌，同步失败")
        return False
    
    results = {
        'bitable': {},
        'spreadsheet': {}
    }
    
    # 1. 同步多维表格缓存
    print("1. 同步多维表格缓存...")
    print("-" * 80)
    try:
        from bitable_cache_manager import BitableCacheManager, BITABLE_CONFIGS
        
        manager = BitableCacheManager(
            app_id=APP_ID,
            app_secret=APP_SECRET,
            user_access_token=user_access_token,
            space_id=SPACE_ID
        )
        
        print(f"配置的多维表格数: {len(BITABLE_CONFIGS)}")
        bitable_results = manager.sync_all_bitables(force_refresh=force_refresh)
        results['bitable'] = bitable_results
        
        success_count = sum(1 for r in bitable_results.values() if r.get('success'))
        total_count = len(bitable_results)
        print(f"多维表格同步完成: {success_count}/{total_count} 成功")
        
    except Exception as e:
        print(f"[X] 多维表格同步失败: {e}")
        import traceback
        traceback.print_exc()
        results['bitable'] = {'error': str(e)}
    
    print()
    
    # 2. 同步在线表格缓存
    print("2. 同步在线表格缓存...")
    print("-" * 80)
    try:
        from spreadsheet_cache_manager import SpreadsheetCacheManager, SPREADSHEET_CONFIGS
        
        manager = SpreadsheetCacheManager(
            app_id=APP_ID,
            app_secret=APP_SECRET,
            user_access_token=user_access_token,
            space_id=SPACE_ID
        )
        
        print(f"配置的在线表格数: {len(SPREADSHEET_CONFIGS)}")
        spreadsheet_results = manager.sync_all_spreadsheets(force_refresh=force_refresh)
        results['spreadsheet'] = spreadsheet_results
        
        success_count = sum(1 for r in spreadsheet_results.values() if r.get('success'))
        total_count = len(spreadsheet_results)
        print(f"在线表格同步完成: {success_count}/{total_count} 成功")
        
    except Exception as e:
        print(f"[X] 在线表格同步失败: {e}")
        import traceback
        traceback.print_exc()
        results['spreadsheet'] = {'error': str(e)}
    
    print()
    
    # 3. 同步故障定位指引文档缓存
    print("3. 同步故障定位指引文档缓存...")
    print("-" * 80)
    try:
        from fault_guide_reader import get_guide_reader
        from fault_diagnosis_config import get_guide_docs
        
        reader = get_guide_reader()
        guide_docs = get_guide_docs()
        
        print(f"配置的指引文档数: {len(guide_docs)}")
        
        # 刷新token（如果需要）
        reader._refresh_token_if_needed()
        
        # 同步所有指引文档
        reader.load_all_guides(force_refresh=force_refresh)
        
        # 检查同步结果
        from fault_diagnosis_config import GUIDE_CACHE_DIR
        success_count = 0
        for doc in guide_docs:
            node_token = doc['node_token']
            cache_file = GUIDE_CACHE_DIR / f"guide_{node_token}.json"
            if cache_file.exists():
                success_count += 1
        
        print(f"指引文档同步完成: {success_count}/{len(guide_docs)} 成功")
        results['fault_guides'] = {
            'success': success_count == len(guide_docs),
            'total': len(guide_docs),
            'success_count': success_count
        }
        
    except Exception as e:
        print(f"[X] 指引文档同步失败: {e}")
        import traceback
        traceback.print_exc()
        results['fault_guides'] = {'error': str(e)}
    
    print()
    print("=" * 80)
    print("所有缓存同步完成")
    print("=" * 80)
    print()
    
    # 打印汇总
    total_success = 0
    total_count = 0
    
    if 'bitable' in results and isinstance(results['bitable'], dict):
        for name, result in results['bitable'].items():
            if isinstance(result, dict) and result.get('success'):
                total_success += 1
                total_count += 1
                print(f"✓ {name} (多维表格): {result.get('tables_count', 0)} 表, {result.get('total_records', 0)} 记录")
            elif isinstance(result, dict) and not result.get('success'):
                total_count += 1
                print(f"✗ {name} (多维表格): 失败 - {result.get('error', '未知错误')}")
    
    if 'spreadsheet' in results and isinstance(results['spreadsheet'], dict):
        for name, result in results['spreadsheet'].items():
            if isinstance(result, dict) and result.get('success'):
                total_success += 1
                total_count += 1
                print(f"✓ {name} (在线表格): 同步成功")
            elif isinstance(result, dict) and not result.get('success'):
                total_count += 1
                print(f"✗ {name} (在线表格): 失败 - {result.get('error', '未知错误')}")
    
    if 'fault_guides' in results:
        fault_result = results['fault_guides']
        if fault_result.get('success'):
            total_success += 1
            total_count += 1
            print(f"✓ 故障定位指引文档: {fault_result.get('success_count', 0)}/{fault_result.get('total', 0)} 成功")
        else:
            total_count += 1
            print(f"✗ 故障定位指引文档: 失败 - {fault_result.get('error', '未知错误')}")
    
    print()
    print(f"总计: {total_success}/{total_count} 成功")
    print()
    
    return total_success == total_count and total_count > 0


def run_scheduler():
    """运行定时同步任务"""
    try:
        import schedule
    except ImportError:
        print("[!] schedule模块未安装，无法运行定时任务")
        print("    安装: pip install schedule")
        print("    或使用 --once 参数执行一次性同步")
        return
    
    print("=" * 80)
    print("自动同步服务（包含token自动刷新）")
    print("=" * 80)
    print()
    print(f"同步间隔: {SYNC_INTERVAL_HOURS} 小时")
    print("功能:")
    print("  - 自动刷新访问令牌")
    print("  - 自动同步多维表格缓存")
    print("  - 自动同步在线表格缓存")
    print()
    
    # 立即执行一次同步
    print("执行初始同步...")
    sync_all_caches(force_refresh=False)
    
    # 设置定时任务
    schedule.every(SYNC_INTERVAL_HOURS).hours.do(sync_all_caches, force_refresh=False)
    
    print()
    print("=" * 80)
    print("自动同步服务已启动，按 Ctrl+C 停止")
    print("=" * 80)
    print()
    
    # 运行调度器
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # 每分钟检查一次
    except KeyboardInterrupt:
        print("\n\n停止自动同步服务")


def sync_once(force_refresh=False):
    """执行一次同步（不启动定时任务）"""
    print("执行一次性同步...")
    return sync_all_caches(force_refresh=force_refresh)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='自动同步所有缓存（包含token自动刷新）')
    parser.add_argument('--once', action='store_true', help='只执行一次同步，不启动定时任务')
    parser.add_argument('--force', action='store_true', help='强制刷新所有缓存（忽略过期时间）')
    parser.add_argument('--interval', type=int, default=1, help='同步间隔（小时），默认1小时')
    
    args = parser.parse_args()
    
    if args.once:
        sync_once(force_refresh=args.force)
    else:
        # 更新同步间隔（使用模块级别的变量）
        import auto_sync_all
        auto_sync_all.SYNC_INTERVAL_HOURS = args.interval
        run_scheduler()

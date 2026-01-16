# -*- coding: utf-8 -*-
"""
自动同步多维表格缓存

支持定期自动同步多维表格数据
"""

import sys
import os
import time
import schedule
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bitable_cache_manager import BitableCacheManager, BITABLE_CONFIGS

# 配置信息
APP_ID = "cli_a9c92ca516f99bd9"
APP_SECRET = "zlOKnyZkSuSUSr0WlAl6qbh5Qw4eM6wC"
USER_ACCESS_TOKEN = os.getenv("FEISHU_USER_ACCESS_TOKEN", "u-fjEA3Zj5J4eGr.QY6KVnXg14hgJ04kgVOOwaFMy024ps")
SPACE_ID = "7353073903872868356"

# 同步配置
SYNC_INTERVAL_HOURS = 1  # 默认每小时同步一次


def sync_all_bitables():
    """同步所有多维表格"""
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始自动同步...")
    
    manager = BitableCacheManager(
        app_id=APP_ID,
        app_secret=APP_SECRET,
        user_access_token=USER_ACCESS_TOKEN,
        space_id=SPACE_ID
    )
    
    try:
        results = manager.sync_all_bitables(force_refresh=False)
        
        # 打印同步结果
        success_count = sum(1 for r in results.values() if r.get('success'))
        total_count = len(results)
        
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 同步完成: {success_count}/{total_count} 成功")
        
        return success_count == total_count
    except Exception as e:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 同步失败: {e}")
        return False


def run_scheduler():
    """运行定时同步任务"""
    print("=" * 80)
    print("多维表格自动同步服务")
    print("=" * 80)
    print()
    print(f"同步间隔: {SYNC_INTERVAL_HOURS} 小时")
    print(f"配置的多维表格数: {len(BITABLE_CONFIGS)}")
    print()
    
    # 立即执行一次同步
    print("执行初始同步...")
    sync_all_bitables()
    
    # 设置定时任务
    schedule.every(SYNC_INTERVAL_HOURS).hours.do(sync_all_bitables)
    
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


def sync_once():
    """执行一次同步（不启动定时任务）"""
    print("执行一次性同步...")
    return sync_all_bitables()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='多维表格自动同步服务')
    parser.add_argument('--once', action='store_true', help='只执行一次同步，不启动定时任务')
    parser.add_argument('--interval', type=int, default=SYNC_INTERVAL_HOURS, help='同步间隔（小时）')
    
    args = parser.parse_args()
    
    if args.once:
        sync_once()
    else:
        global SYNC_INTERVAL_HOURS
        SYNC_INTERVAL_HOURS = args.interval
        run_scheduler()

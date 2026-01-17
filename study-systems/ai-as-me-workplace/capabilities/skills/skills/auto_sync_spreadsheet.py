# -*- coding: utf-8 -*-
"""
自动同步在线表格缓存

支持定期自动同步在线表格数据
"""

import sys
import os
import time
import schedule
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from spreadsheet_cache_manager import SpreadsheetCacheManager, SPREADSHEET_CONFIGS

# 配置信息
APP_ID = "cli_a9c92ca516f99bd9"
APP_SECRET = "zlOKnyZkSuSUSr0WlAl6qbh5Qw4eM6wC"
SPACE_ID = "7353073903872868356"

# 尝试从token_manager获取token，如果失败则使用环境变量或默认值
def get_user_access_token():
    """获取有效的user_access_token（自动刷新）"""
    try:
        from token_manager import get_user_access_token as get_token
        token = get_token()
        if token:
            return token
    except ImportError:
        pass
    except Exception as e:
        print(f"[!] 无法从token_manager获取token: {e}")
    
    # 回退到环境变量或默认值
    return os.getenv("FEISHU_USER_ACCESS_TOKEN", "u-fjEA3Zj5J4eGr.QY6KVnXg14hgJ04kgVOOwaFMy024ps")

# 同步配置
SYNC_INTERVAL_HOURS = 1  # 默认每小时同步一次

# 修复Windows控制台编码问题
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass


def sync_all_spreadsheets():
    """同步所有在线表格"""
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始自动同步...")
    
    # 自动获取有效的token（会自动刷新）
    user_access_token = get_user_access_token()
    if not user_access_token:
        print("[X] 无法获取有效的访问令牌，请先运行授权脚本获取token")
        return False
    
    manager = SpreadsheetCacheManager(
        app_id=APP_ID,
        app_secret=APP_SECRET,
        user_access_token=user_access_token,
        space_id=SPACE_ID
    )
    
    try:
        results = manager.sync_all_spreadsheets(force_refresh=False)
        
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
    print("在线表格自动同步服务")
    print("=" * 80)
    print()
    print(f"同步间隔: {SYNC_INTERVAL_HOURS} 小时")
    print(f"配置的在线表格数: {len(SPREADSHEET_CONFIGS)}")
    print()
    
    # 立即执行一次同步
    print("执行初始同步...")
    sync_all_spreadsheets()
    
    # 设置定时任务
    schedule.every(SYNC_INTERVAL_HOURS).hours.do(sync_all_spreadsheets)
    
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
    return sync_all_spreadsheets()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='在线表格自动同步服务')
    parser.add_argument('--once', action='store_true', help='只执行一次同步，不启动定时任务')
    parser.add_argument('--interval', type=int, default=SYNC_INTERVAL_HOURS, help='同步间隔（小时）')
    
    args = parser.parse_args()
    
    if args.once:
        sync_once()
    else:
        global SYNC_INTERVAL_HOURS
        SYNC_INTERVAL_HOURS = args.interval
        run_scheduler()

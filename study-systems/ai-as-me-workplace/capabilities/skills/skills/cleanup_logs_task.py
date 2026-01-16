# -*- coding: utf-8 -*-
"""
日志清理任务

定期清理过期的日志文件
"""

import sys
import os
import time
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from log_cleanup_manager import LogCleanupManager

# 修复Windows控制台编码问题
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass


def main():
    """主函数：清理过期的日志文件"""
    print("=" * 80)
    print("日志清理任务")
    print("=" * 80)
    print()
    
    manager = LogCleanupManager()
    
    # 清理过期日志
    cleaned_count = manager.cleanup_expired_logs()
    
    if cleaned_count > 0:
        print(f"[OK] 已清理 {cleaned_count} 个过期日志文件/目录")
    else:
        print("[OK] 没有需要清理的日志文件")
    
    # 清理旧的清理记录
    manager.cleanup_old_records(days=7)
    
    print()
    print("=" * 80)
    print("清理任务完成")
    print("=" * 80)


if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
"""
快速同步所有缓存内容
用于同步过往交互需要的缓存内容
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

print("=" * 80)
print("同步过往交互需要的缓存内容")
print("=" * 80)
print()

# 0. 获取有效的访问令牌（自动刷新）
print("0. 获取有效的访问令牌（自动刷新）...")
print("-" * 80)
try:
    from token_manager import get_user_access_token
    user_access_token = get_user_access_token()
    if not user_access_token:
        print("[!] 无法从token_manager获取token，尝试使用环境变量...")
        import os
        user_access_token = os.getenv("FEISHU_USER_ACCESS_TOKEN")
        if not user_access_token:
            print("[X] 无法获取访问令牌，请先运行授权脚本获取token")
            print("    运行: python get_user_token_for_bitable.py")
            user_access_token = None
except ImportError:
    print("[!] token_manager模块未找到，使用环境变量...")
    import os
    user_access_token = os.getenv("FEISHU_USER_ACCESS_TOKEN")
    if not user_access_token:
        print("[X] 无法获取访问令牌，请先设置环境变量或运行授权脚本")
        user_access_token = None
except Exception as e:
    print(f"[!] 获取token时出错: {e}")
    import os
    user_access_token = os.getenv("FEISHU_USER_ACCESS_TOKEN")
    if not user_access_token:
        user_access_token = None

if not user_access_token:
    print()
    print("[X] 无法继续，请先获取访问令牌")
    print("=" * 80)
    sys.exit(1)

print("[OK] 已获取有效的访问令牌")
print()

# 1. 同步多维表格缓存
print("1. 同步多维表格缓存...")
print("-" * 80)
try:
    from bitable_cache_manager import BitableCacheManager, BITABLE_CONFIGS, APP_ID, APP_SECRET, SPACE_ID
    
    manager = BitableCacheManager(
        app_id=APP_ID,
        app_secret=APP_SECRET,
        user_access_token=user_access_token,
        space_id=SPACE_ID
    )
    
    print(f"配置的多维表格数: {len(BITABLE_CONFIGS)}")
    for config in BITABLE_CONFIGS:
        print(f"  - {config['name']}")
    
    print()
    print("开始同步...")
    results = manager.sync_all_bitables(force_refresh=True)
    
    success_count = sum(1 for r in results.values() if r.get('success'))
    total_count = len(results)
    print(f"多维表格同步完成: {success_count}/{total_count} 成功")
    
    for name, result in results.items():
        if result.get('success'):
            print(f"  ✓ {name}: 成功")
        else:
            print(f"  ✗ {name}: 失败 - {result.get('error', '未知错误')}")
    
except Exception as e:
    print(f"多维表格同步失败: {e}")
    import traceback
    traceback.print_exc()

print()
print()

# 2. 同步在线表格缓存
print("2. 同步在线表格缓存...")
print("-" * 80)
try:
    from spreadsheet_cache_manager import SpreadsheetCacheManager, SPREADSHEET_CONFIGS, APP_ID, APP_SECRET, SPACE_ID
    
    manager = SpreadsheetCacheManager(
        app_id=APP_ID,
        app_secret=APP_SECRET,
        user_access_token=user_access_token,
        space_id=SPACE_ID
    )
    
    print(f"配置的在线表格数: {len(SPREADSHEET_CONFIGS)}")
    for config in SPREADSHEET_CONFIGS:
        print(f"  - {config['name']}")
    
    print()
    print("开始同步...")
    results = manager.sync_all_spreadsheets(force_refresh=True)
    
    success_count = sum(1 for r in results.values() if r.get('success'))
    total_count = len(results)
    print(f"在线表格同步完成: {success_count}/{total_count} 成功")
    
    for name, result in results.items():
        if result.get('success'):
            print(f"  ✓ {name}: 成功")
        else:
            print(f"  ✗ {name}: 失败 - {result.get('error', '未知错误')}")
    
except Exception as e:
    print(f"在线表格同步失败: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 80)
print("缓存同步完成")
print("=" * 80)

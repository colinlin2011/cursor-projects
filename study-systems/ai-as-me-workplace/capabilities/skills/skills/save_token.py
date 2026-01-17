# -*- coding: utf-8 -*-
"""
保存用户提供的访问令牌到缓存
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

# 用户提供的token
USER_ACCESS_TOKEN = "u-e0a.APDd9atpgL8QUi5dmfhk7ub14kOpU2waIRQ00LAV"

# 注意：这个token没有refresh_token，所以无法自动刷新
# 但可以临时使用，有效期约2小时

print("=" * 80)
print("保存访问令牌")
print("=" * 80)
print()

try:
    from token_manager import get_token_manager
    
    # 获取token管理器
    manager = get_token_manager()
    
    # 检查是否已有缓存
    cache = manager.load_token_cache()
    
    # 检查是否有命令行参数（自动确认）
    auto_confirm = '--yes' in sys.argv or '-y' in sys.argv
    
    if cache:
        print("[!] 检测到已有token缓存")
        print(f"    当前token: {cache.get('access_token', 'N/A')[:20]}...")
        print()
        if auto_confirm:
            print("[OK] 自动确认：覆盖现有token")
        else:
            try:
                response = input("是否覆盖现有token？(y/n): ").strip().lower()
                if response != 'y':
                    print("已取消")
                    sys.exit(0)
            except EOFError:
                # 非交互式环境，自动确认
                print("[OK] 非交互式环境，自动确认：覆盖现有token")
    
    # 保存token（注意：没有refresh_token，无法自动刷新）
    # 设置一个合理的过期时间（2小时后）
    import time
    expires_in = 7200  # 2小时
    
    # 尝试从现有缓存获取refresh_token（如果有）
    refresh_token = None
    if cache:
        refresh_token = cache.get('refresh_token')
    
    if refresh_token:
        print("[OK] 保留现有refresh_token，token可以自动刷新")
        manager.save_token_cache({
            'access_token': USER_ACCESS_TOKEN,
            'expires_at': time.time() + expires_in,
            'refresh_token': refresh_token,
            'last_refresh': time.strftime('%Y-%m-%dT%H:%M:%S')
        })
    else:
        print("[!] 注意：没有refresh_token，此token无法自动刷新")
        print("    有效期约2小时，过期后需要重新获取")
        manager.save_token_cache({
            'access_token': USER_ACCESS_TOKEN,
            'expires_at': time.time() + expires_in,
            'refresh_token': None,
            'last_refresh': time.strftime('%Y-%m-%dT%H:%M:%S')
        })
    
    print()
    print("[OK] Token已保存到缓存")
    print(f"    Token: {USER_ACCESS_TOKEN[:30]}...")
    print(f"    过期时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time() + expires_in))}")
    print()
    
except ImportError:
    print("[!] token_manager模块未找到，直接设置环境变量...")
    print()
    print("请设置环境变量：")
    print(f'PowerShell: $env:FEISHU_USER_ACCESS_TOKEN="{USER_ACCESS_TOKEN}"')
    print(f'CMD: set FEISHU_USER_ACCESS_TOKEN={USER_ACCESS_TOKEN}')
    print()
except Exception as e:
    print(f"[X] 保存token失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("=" * 80)
print("Token保存完成")
print("=" * 80)

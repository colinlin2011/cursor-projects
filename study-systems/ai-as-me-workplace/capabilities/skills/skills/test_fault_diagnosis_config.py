# -*- coding: utf-8 -*-
"""
测试故障定位系统配置功能
"""

import sys
import os
import json
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 修复Windows控制台编码问题
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

print("=" * 80)
print("测试故障定位系统配置功能")
print("=" * 80)
print()

# 测试1: 验证指引文档配置加载
print("测试1: 验证指引文档配置加载")
print("-" * 80)
from fault_diagnosis_config import get_guide_docs

docs = get_guide_docs()
print(f"已加载的指引文档数量: {len(docs)}")
print("\n指引文档列表:")
for i, doc in enumerate(docs, 1):
    print(f"  {i}. {doc['name']}")
    print(f"     Node Token: {doc['node_token']}")
    print(f"     URL: {doc['url']}")
print()

# 测试2: 验证Token管理器
print("测试2: 验证Token管理器")
print("-" * 80)
from token_manager import get_token_manager

manager = get_token_manager()
cache = manager.load_token_cache()

print(f"Token缓存文件: {manager.token_cache_file}")
print(f"Token缓存存在: {cache is not None}")

if cache:
    access_token = cache.get('access_token', '')
    refresh_token = cache.get('refresh_token', '')
    expires_at = cache.get('expires_at', 0)
    
    print(f"Access Token: {access_token[:30] + '...' if len(access_token) > 30 else access_token}")
    print(f"Refresh Token: {'存在' if refresh_token else '不存在'}")
    
    if expires_at:
        remaining = expires_at - time.time()
        if remaining > 0:
            print(f"剩余时间: {remaining/3600:.1f}小时 ({remaining/60:.0f}分钟)")
        else:
            print("状态: 已过期")
    
    # 尝试获取有效token
    print("\n尝试获取有效token...")
    valid_token = manager.get_valid_user_access_token()
    if valid_token:
        print(f"[OK] 获取到有效token: {valid_token[:30]}...")
    else:
        print("[!] 无法获取有效token，需要重新授权")
else:
    print("[!] 没有token缓存，需要首次授权")

print()

# 测试3: 验证动态Token获取
print("测试3: 验证动态Token获取")
print("-" * 80)
from fault_diagnosis_config import get_dynamic_user_access_token

try:
    token = get_dynamic_user_access_token()
    if token:
        print(f"[OK] 动态获取token成功: {token[:30]}...")
    else:
        print("[!] 动态获取token失败，使用环境变量或默认值")
except Exception as e:
    print(f"[!] 动态获取token异常: {e}")

print()

# 测试4: 验证配置文件读取
print("测试4: 验证配置文件读取")
print("-" * 80)
from fault_diagnosis_config import GUIDE_DOCS_CONFIG_FILE, load_guide_docs_from_file

print(f"配置文件路径: {GUIDE_DOCS_CONFIG_FILE}")
print(f"配置文件存在: {GUIDE_DOCS_CONFIG_FILE.exists()}")

if GUIDE_DOCS_CONFIG_FILE.exists():
    try:
        with open(GUIDE_DOCS_CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
            file_docs = config.get('guide_docs', [])
            print(f"配置文件中的文档数量: {len(file_docs)}")
            print("[OK] 配置文件格式正确")
    except Exception as e:
        print(f"[!] 读取配置文件失败: {e}")
else:
    print("[!] 配置文件不存在，将使用代码中的默认配置")

print()

print("=" * 80)
print("测试完成")
print("=" * 80)

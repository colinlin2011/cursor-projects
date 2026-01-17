# -*- coding: utf-8 -*-
"""
同步故障定位指引文档缓存

从飞书Wiki同步所有配置的故障定位指引文档到本地缓存
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
print("同步故障定位指引文档缓存")
print("=" * 80)
print()

try:
    from fault_guide_reader import get_guide_reader
    from fault_diagnosis_config import get_guide_docs
    
    # 获取指引读取器
    reader = get_guide_reader()
    
    # 获取配置的指引文档列表
    guide_docs = get_guide_docs()
    
    print(f"配置的指引文档数: {len(guide_docs)}")
    for i, doc in enumerate(guide_docs, 1):
        print(f"  {i}. {doc['name']}")
        print(f"     Node Token: {doc['node_token']}")
    print()
    
    # 强制刷新所有指引文档
    print("开始同步所有指引文档（强制刷新）...")
    print()
    
    reader.load_all_guides(force_refresh=True)
    
    print()
    print("=" * 80)
    print("指引文档同步完成")
    print("=" * 80)
    print()
    
    # 显示同步结果
    from fault_diagnosis_config import GUIDE_CACHE_DIR
    
    success_count = 0
    for doc in guide_docs:
        node_token = doc['node_token']
        cache_file = GUIDE_CACHE_DIR / f"guide_{node_token}.json"
        if cache_file.exists():
            success_count += 1
            # 获取文件大小
            file_size = cache_file.stat().st_size
            print(f"✓ {doc['name']}: 缓存已同步 ({file_size:,} 字节)")
        else:
            print(f"✗ {doc['name']}: 缓存同步失败")
    
    print()
    print(f"总计: {success_count}/{len(guide_docs)} 成功")
    print()
    
except ImportError as e:
    print(f"[X] 导入模块失败: {e}")
    print("    请确保已安装必要的依赖")
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f"[X] 同步失败: {e}")
    import traceback
    traceback.print_exc()

# -*- coding: utf-8 -*-
"""
测试下载日志文件
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

sys.stdout.reconfigure(encoding='utf-8')

from log_fault_id_extractor import LogFaultIdExtractor

print("=" * 80)
print("测试下载日志文件")
print("=" * 80)
print()

extractor = LogFaultIdExtractor()

remote_path = "/rawdata/roadtestv3/faw/1R10V/FL/cn/2026/1/20260112/14/17-09-14_snapshot/trigger_1768208954556949_5376300000_LK6ADAE47RB757806/"

print(f"远程路径: {remote_path}")
print()

# 测试连接
print("步骤1: 连接SSH服务器...")
if not extractor.connect_to_server():
    print("[X] SSH连接失败")
    sys.exit(1)

print("[OK] SSH连接成功")
print()

# 测试查找文件
print("步骤2: 查找日志文件...")
stdin, stdout, stderr = extractor.ssh_client.exec_command(f'find "{remote_path}/log" -type f 2>/dev/null | head -30')
log_files = stdout.read().decode().strip().split('\n')
files = [f for f in log_files if f]

print(f"找到 {len(files)} 个文件")
if files:
    print("前10个文件:")
    for f in files[:10]:
        print(f"  {f}")
else:
    print("[!] 未找到文件，尝试其他方式...")
    stdin, stdout, stderr = extractor.ssh_client.exec_command(f'ls -la "{remote_path}/log" | head -20')
    ls_output = stdout.read().decode()
    print("ls输出:")
    print(ls_output)

print()

# 测试下载
if files:
    print("步骤3: 下载文件...")
    cache_path = extractor.download_log_files(remote_path)
    if cache_path:
        print(f"[OK] 下载成功，缓存路径: {cache_path}")
        
        # 列出下载的文件
        if cache_path.is_dir():
            downloaded = list(cache_path.glob("*"))
            print(f"下载的文件数量: {len(downloaded)}")
            for f in downloaded[:10]:
                print(f"  {f.name} ({f.stat().st_size} 字节)")
    else:
        print("[X] 下载失败")
else:
    print("[!] 没有文件可下载")

print()
print("=" * 80)

# -*- coding: utf-8 -*-
"""
解压已下载的日志文件
"""

import sys
import os
import gzip
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

log_dir = Path("../../work/fault_diagnosis_cache/logs/trigger_1768208954556949_5376300000_LK6ADAE47RB757806")

print("=" * 80)
print("解压日志文件")
print("=" * 80)
print()

if not log_dir.exists():
    print(f"[X] 目录不存在: {log_dir}")
    sys.exit(1)

gz_files = list(log_dir.glob("*.gz"))
print(f"找到 {len(gz_files)} 个.gz文件")
print()

decompressed_count = 0
for gz_file in gz_files:
    try:
        decompressed_file = gz_file.with_suffix('')
        if decompressed_file.exists():
            print(f"[OK] 已存在: {decompressed_file.name}")
            continue
        
        print(f"解压: {gz_file.name}...")
        with gzip.open(gz_file, 'rb') as f_in:
            content = f_in.read()
            with open(decompressed_file, 'wb') as f_out:
                f_out.write(content)
        
        print(f"[OK] 解压成功: {decompressed_file.name} ({len(content)} 字节)")
        decompressed_count += 1
    except Exception as e:
        print(f"[X] 解压失败 {gz_file.name}: {e}")

print()
print(f"解压了 {decompressed_count} 个文件")
print()

# 列出所有文件
all_files = list(log_dir.glob("*"))
print(f"目录中共有 {len(all_files)} 个文件:")
for f in sorted(all_files):
    size = f.stat().st_size if f.is_file() else 0
    print(f"  {f.name} ({size} 字节)")

print()
print("=" * 80)

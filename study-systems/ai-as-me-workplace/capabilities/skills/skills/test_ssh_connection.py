# -*- coding: utf-8 -*-
"""
测试SSH连接
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

sys.stdout.reconfigure(encoding='utf-8')

try:
    import paramiko
    HAS_PARAMIKO = True
except ImportError:
    HAS_PARAMIKO = False
    print("[X] paramiko未安装")
    sys.exit(1)

from fault_diagnosis_config import get_ssh_config

print("=" * 80)
print("测试SSH连接")
print("=" * 80)
print()

ssh_config = get_ssh_config()
print(f"主机: {ssh_config['host']}")
print(f"端口: {ssh_config['port']}")
print(f"用户名: {ssh_config['username']}")
print(f"密码: {'*' * len(ssh_config['password'])}")
print()

try:
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    print("正在连接...")
    ssh_client.connect(
        hostname=ssh_config['host'],
        port=ssh_config['port'],
        username=ssh_config['username'],
        password=ssh_config['password'],
        timeout=ssh_config['timeout'],
        allow_agent=False,
        look_for_keys=False
    )
    
    print("[OK] SSH连接成功")
    print()
    
    # 测试执行命令
    print("测试执行命令...")
    stdin, stdout, stderr = ssh_client.exec_command('echo "SSH连接测试成功"')
    output = stdout.read().decode().strip()
    print(f"命令输出: {output}")
    
    # 测试路径检查
    test_path = "/rawdata/roadtestv3/faw/1R10V/FL/cn/2026/1/20260112/14/17-09-14_snapshot/trigger_1768208954556949_5376300000_LK6ADAE47RB757806/"
    print(f"\n测试路径是否存在: {test_path}")
    stdin, stdout, stderr = ssh_client.exec_command(f'test -d "{test_path}" && echo "存在" || echo "不存在"')
    path_exists = stdout.read().decode().strip()
    print(f"结果: {path_exists}")
    
    if path_exists == "存在":
        print("\n列出路径下的文件（前10个）...")
        stdin, stdout, stderr = ssh_client.exec_command(f'ls -la "{test_path}" | head -10')
        files = stdout.read().decode()
        print(files)
    
    ssh_client.close()
    print()
    print("[OK] SSH连接测试完成")
    
except paramiko.AuthenticationException as e:
    print(f"[X] SSH认证失败: {e}")
    print("请检查用户名和密码是否正确")
except Exception as e:
    print(f"[X] SSH连接失败: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 80)

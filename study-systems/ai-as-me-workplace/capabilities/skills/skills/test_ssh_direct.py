# -*- coding: utf-8 -*-
"""
直接测试SSH连接（使用不同方法）
"""

import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

try:
    import paramiko
except ImportError:
    print("[X] paramiko未安装")
    sys.exit(1)

print("=" * 80)
print("直接测试SSH连接")
print("=" * 80)
print()

# 直接使用用户提供的凭据
host = "10.241.120.100"
port = 22
username = "dj"
password = "AutoXPC.246!"

print(f"主机: {host}")
print(f"端口: {port}")
print(f"用户名: {username}")
print(f"密码: {repr(password)}")
print()

# 方法1: 标准连接
print("方法1: 标准SSH连接")
print("-" * 80)
try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(
        hostname=host,
        port=port,
        username=username,
        password=password,
        timeout=30,
        allow_agent=False,
        look_for_keys=False
    )
    print("[OK] SSH连接成功")
    
    # 测试命令
    stdin, stdout, stderr = ssh.exec_command('echo "test"')
    output = stdout.read().decode().strip()
    print(f"命令输出: {output}")
    
    ssh.close()
except paramiko.AuthenticationException as e:
    print(f"[X] 认证失败: {e}")
    print("可能的原因:")
    print("  1. 用户名或密码错误")
    print("  2. 密码中的特殊字符需要转义")
    print("  3. 服务器要求密钥认证")
except Exception as e:
    print(f"[X] 连接失败: {e}")
    import traceback
    traceback.print_exc()

print()

# 方法2: 使用Transport
print("方法2: 使用Transport连接")
print("-" * 80)
try:
    transport = paramiko.Transport((host, port))
    transport.connect(username=username, password=password)
    print("[OK] Transport连接成功")
    
    ssh = paramiko.SSHClient()
    ssh._transport = transport
    
    # 测试命令
    stdin, stdout, stderr = ssh.exec_command('echo "test"')
    output = stdout.read().decode().strip()
    print(f"命令输出: {output}")
    
    transport.close()
except paramiko.AuthenticationException as e:
    print(f"[X] 认证失败: {e}")
except Exception as e:
    print(f"[X] 连接失败: {e}")

print()
print("=" * 80)

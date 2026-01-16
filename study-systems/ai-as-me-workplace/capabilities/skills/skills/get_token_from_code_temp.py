# -*- coding: utf-8 -*-
"""
临时脚本：使用授权码获取user_access_token
"""

import sys
import requests

# 修复Windows控制台编码问题
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

APP_ID = "cli_a9c92ca516f99bd9"
APP_SECRET = "zlOKnyZkSuSUSr0WlAl6qbh5Qw4eM6wC"
CODE = "0IXqCbbDdGL1Ad0dH908HBaGzBDE69yC"

def get_tenant_access_token():
    """获取tenant_access_token"""
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    headers = {'Content-Type': 'application/json'}
    data = {
        "app_id": APP_ID,
        "app_secret": APP_SECRET
    }
    
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        result = response.json()
        if result.get('code') == 0:
            return result.get('tenant_access_token')
        else:
            print(f"[X] 获取tenant_access_token失败: {result}")
            return None
    else:
        print(f"[X] 请求失败，状态码: {response.status_code}")
        return None

def get_user_access_token(code):
    """使用code获取user_access_token"""
    # 1. 获取tenant_access_token
    tenant_token = get_tenant_access_token()
    if not tenant_token:
        print("[X] 无法获取tenant_access_token")
        return None
    
    print("[OK] tenant_access_token获取成功")
    print()
    
    # 2. 获取user_access_token
    url = "https://open.feishu.cn/open-apis/authen/v1/oidc/access_token"
    headers = {
        "Authorization": f"Bearer {tenant_token}",
        "Content-Type": "application/json"
    }
    data = {
        "grant_type": "authorization_code",
        "code": code
    }
    
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        result = response.json()
        if result.get('code') == 0:
            return result['data']['access_token'], result['data'].get('expires_in', 7200)
        else:
            print(f"[X] 获取user_access_token失败: {result.get('msg')}")
            print(f"完整响应: {result}")
            return None
    else:
        print(f"[X] 请求失败: {response.status_code}, {response.text}")
        return None

if __name__ == "__main__":
    print("=" * 60)
    print("使用授权码获取user_access_token")
    print("=" * 60)
    print()
    
    result = get_user_access_token(CODE)
    
    if result:
        access_token, expires_in = result
        print("=" * 60)
        print("成功获取user_access_token")
        print("=" * 60)
        print()
        print(f"Token: {access_token}")
        print(f"有效期: {expires_in}秒 ({expires_in/3600:.1f}小时)")
        print()
        print("请将以下内容设置为环境变量：")
        print(f'$env:FEISHU_USER_ACCESS_TOKEN="{access_token}"')
        print()
        print("然后运行同步脚本：")
        print("python sync_functional_safety_bitable.py")
    else:
        print("[X] 获取token失败")

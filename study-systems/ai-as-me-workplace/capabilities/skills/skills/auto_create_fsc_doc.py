# -*- coding: utf-8 -*-
"""
自动化创建FSC文档流程
1. 使用code获取token
2. 更新create_fsc_doc_full.py中的token
3. 运行创建文档脚本
"""

import sys
import os
import requests
import re

APP_ID = "cli_a9c92ca516f99bd9"
APP_SECRET = "zlOKnyZkSuSUSr0WlAl6qbh5Qw4eM6wC"
CODE = "2wCiC66H9EG7Acd5bB6eGebKdHbJ9z87"

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
    return None

def get_user_access_token(code):
    """使用code获取user_access_token"""
    # 1. 获取tenant_access_token
    tenant_token = get_tenant_access_token()
    if not tenant_token:
        print("[X] 获取tenant_access_token失败")
        return None
    
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
            print(f"[X] 获取user_access_token失败: {result}")
            return None
    else:
        print(f"[X] 请求失败: {response.status_code}, {response.text}")
        return None

def update_token_in_script(token):
    """更新create_fsc_doc_full.py中的token"""
    script_path = os.path.join(os.path.dirname(__file__), "create_fsc_doc_full.py")
    
    with open(script_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 使用正则表达式替换token
    pattern = r'USER_ACCESS_TOKEN = "[^"]*"'
    replacement = f'USER_ACCESS_TOKEN = "{token}"'
    new_content = re.sub(pattern, replacement, content)
    
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"[OK] 已更新 {script_path} 中的token")

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    
    print("=" * 60)
    print("自动化创建FSC文档流程")
    print("=" * 60)
    print()
    
    # 步骤1：获取token
    print("步骤1：使用code获取user_access_token...")
    result = get_user_access_token(CODE)
    
    if not result:
        print("[X] 获取token失败，流程终止")
        return
    
    user_token, expires_in = result
    print(f"[OK] token获取成功，有效期: {expires_in}秒（约{expires_in//3600}小时）")
    print()
    
    # 步骤2：更新脚本中的token
    print("步骤2：更新create_fsc_doc_full.py中的token...")
    update_token_in_script(user_token)
    print()
    
    # 步骤3：运行创建文档脚本
    print("步骤3：运行创建文档脚本...")
    print("=" * 60)
    print()
    
    # 导入并运行create_fsc_doc_full
    script_path = os.path.join(os.path.dirname(__file__), "create_fsc_doc_full.py")
    sys.path.insert(0, os.path.dirname(script_path))
    
    # 直接执行脚本
    exec(open(script_path).read())

if __name__ == "__main__":
    main()

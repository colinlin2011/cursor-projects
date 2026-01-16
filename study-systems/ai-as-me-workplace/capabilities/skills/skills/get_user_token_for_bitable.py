# -*- coding: utf-8 -*-
"""
获取用于多维表格的user_access_token

需要包含bitable相关权限
"""

import sys
import os
import webbrowser

sys.stdout.reconfigure(encoding='utf-8')

# 配置信息
APP_ID = "cli_a9c92ca516f99bd9"
APP_SECRET = "zlOKnyZkSuSUSr0WlAl6qbh5Qw4eM6wC"
REDIRECT_URI = "https://open.feishu.cn/app/cli_a9c92ca516f99bd9/auth"

# 所需权限范围（包含读取记录权限）
REQUIRED_SCOPE = "bitable:app bitable:app:readonly base:app:read base:field:read base:view:read base:record:read"

def get_tenant_access_token():
    """获取tenant_access_token"""
    import requests
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    headers = {'Content-Type': 'application/json'}
    data = {
        "app_id": APP_ID,
        "app_secret": APP_SECRET
    }
    
    try:
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
            print(f"响应: {response.text}")
            return None
    except Exception as e:
        print(f"[X] 获取tenant_access_token发生错误: {e}")
        return None

def main():
    print("=" * 60)
    print("获取多维表格访问权限的user_access_token")
    print("=" * 60)
    print()
    print("所需权限：")
    print("  - bitable:app")
    print("  - bitable:app:readonly")
    print("  - base:app:read")
    print("  - base:field:read")
    print("  - base:view:read")
    print("  - base:record:read (读取记录)")
    print()
    
    # 生成授权URL
    auth_url = (
        f"https://open.feishu.cn/open-apis/authen/v1/index?"
        f"app_id={APP_ID}&"
        f"redirect_uri={REDIRECT_URI}&"
        f"scope={REQUIRED_SCOPE}"
    )
    
    print("授权URL：")
    print(auth_url)
    print()
    print("请按照以下步骤操作：")
    print("1. 点击授权URL（将自动在浏览器中打开）")
    print("2. 在浏览器中完成授权")
    print("3. 授权完成后，从浏览器URL中获取code参数")
    print("4. 将code提供给脚本，获取user_access_token")
    print()
    
    # 自动打开浏览器
    try:
        webbrowser.open(auth_url)
        print("[OK] 已在浏览器中打开授权页面")
    except:
        print("[!] 无法自动打开浏览器，请手动复制上面的URL到浏览器中打开")
    
    print()
    print("=" * 60)
    print("步骤2：获取授权码（code）")
    print("=" * 60)
    print()
    code = input("请输入授权码（code）: ").strip()
    
    if not code:
        print("[X] 未提供授权码")
        return
    
    print()
    print("=" * 60)
    print("步骤3：获取user_access_token")
    print("=" * 60)
    print()
    
    # 先获取tenant_access_token
    print("正在获取tenant_access_token...")
    tenant_token = get_tenant_access_token()
    if not tenant_token:
        print("[X] 无法获取tenant_access_token，流程终止")
        return
    
    print("[OK] tenant_access_token获取成功")
    print()
    
    # 使用tenant_access_token获取user_access_token
    import requests
    
    url = "https://open.feishu.cn/open-apis/authen/v1/oidc/access_token"
    headers = {
        "Authorization": f"Bearer {tenant_token}",
        "Content-Type": "application/json"
    }
    data = {
        "grant_type": "authorization_code",
        "code": code
    }
    
    try:
        print("正在使用授权码获取user_access_token...")
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            result = response.json()
            if result.get('code') == 0:
                data = result.get('data', {})
                access_token = data.get('access_token')
                expires_in = data.get('expires_in', 7200)
                refresh_token = data.get('refresh_token')  # 获取refresh_token
                
                # 保存token到缓存（如果token_manager可用）
                try:
                    from token_manager import get_token_manager
                    if refresh_token:
                        token_manager = get_token_manager()
                        token_manager.save_initial_token(access_token, expires_in, refresh_token)
                        print("[OK] Token已保存到缓存，将自动刷新")
                except ImportError:
                    print("[!] token_manager模块未找到，无法自动刷新token")
                except Exception as e:
                    print(f"[!] 保存token失败: {e}")
                
                print("[OK] 成功获取user_access_token")
                print()
                print("=" * 60)
                print("user_access_token信息")
                print("=" * 60)
                print()
                print(f"Token: {access_token}")
                print(f"有效期: {expires_in}秒 ({expires_in/3600:.1f}小时)")
                if refresh_token:
                    print(f"Refresh Token: {refresh_token}")
                    print("（已保存，系统将自动刷新）")
                print()
                print("请将以下内容设置为环境变量（如果自动刷新失败时使用）：")
                print(f'$env:FEISHU_USER_ACCESS_TOKEN="{access_token}"')
                print()
                print("或在脚本中直接使用：")
                print(f'USER_ACCESS_TOKEN = "{access_token}"')
            else:
                print(f"[X] 获取token失败: {result.get('msg')}")
                print(f"完整响应: {result}")
        else:
            print(f"[X] 请求失败，状态码: {response.status_code}")
            print(f"响应: {response.text}")
    except Exception as e:
        print(f"[X] 发生错误: {e}")

if __name__ == "__main__":
    main()

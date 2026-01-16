# -*- coding: utf-8 -*-
"""
使用授权码获取token
"""

import sys
import os
import requests

sys.stdout.reconfigure(encoding='utf-8')

# 配置信息
APP_ID = "cli_a9c92ca516f99bd9"
APP_SECRET = "zlOKnyZkSuSUSr0WlAl6qbh5Qw4eM6wC"
CODE = "fDRlIbaybKwaA0b6F5GC9C74yB15zdGD"  # 用户提供的授权码

def get_tenant_access_token():
    """获取tenant_access_token"""
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
            return None
    except Exception as e:
        print(f"[X] 获取tenant_access_token发生错误: {e}")
        return None

def main():
    print("=" * 80)
    print("使用授权码获取user_access_token")
    print("=" * 80)
    print()
    
    # 先获取tenant_access_token
    print("步骤1: 获取tenant_access_token...")
    tenant_token = get_tenant_access_token()
    if not tenant_token:
        print("[X] 无法获取tenant_access_token，流程终止")
        return
    
    print("[OK] tenant_access_token获取成功")
    print()
    
    # 使用tenant_access_token获取user_access_token
    print("步骤2: 使用授权码获取user_access_token...")
    url = "https://open.feishu.cn/open-apis/authen/v1/oidc/access_token"
    headers = {
        "Authorization": f"Bearer {tenant_token}",
        "Content-Type": "application/json"
    }
    data = {
        "grant_type": "authorization_code",
        "code": CODE
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            result = response.json()
            if result.get('code') == 0:
                data = result.get('data', {})
                access_token = data.get('access_token')
                expires_in = data.get('expires_in', 7200)
                refresh_token = data.get('refresh_token')
                
                print("[OK] 成功获取user_access_token")
                print()
                
                # 保存token到缓存
                try:
                    from token_manager import get_token_manager
                    if refresh_token:
                        token_manager = get_token_manager()
                        token_manager.save_initial_token(access_token, expires_in, refresh_token)
                        print("[OK] Token已保存到缓存，将自动刷新")
                    else:
                        print("[!] 未获取到refresh_token")
                except ImportError as e:
                    print(f"[!] token_manager模块未找到: {e}")
                except Exception as e:
                    print(f"[!] 保存token失败: {e}")
                    import traceback
                    traceback.print_exc()
                
                print()
                print("=" * 80)
                print("user_access_token信息")
                print("=" * 80)
                print()
                print(f"Access Token: {access_token}")
                print(f"有效期: {expires_in}秒 ({expires_in/3600:.1f}小时)")
                if refresh_token:
                    print(f"Refresh Token: {refresh_token}")
                    print("（已保存，系统将自动刷新）")
                print()
                print("=" * 80)
                print("验证Token")
                print("=" * 80)
                print()
                
                # 验证token是否有效
                try:
                    from token_manager import get_token_manager
                    manager = get_token_manager()
                    valid_token = manager.get_valid_user_access_token()
                    if valid_token:
                        print(f"[OK] Token验证成功: {valid_token[:30]}...")
                    else:
                        print("[!] Token验证失败")
                except Exception as e:
                    print(f"[!] Token验证异常: {e}")
                
                print()
                print("=" * 80)
                print("完成")
                print("=" * 80)
                print()
                print("Token已成功保存，系统将自动刷新。")
                print("现在可以运行故障定位系统了。")
                
            else:
                print(f"[X] 获取token失败: {result.get('msg')}")
                print(f"完整响应: {result}")
        else:
            print(f"[X] 请求失败，状态码: {response.status_code}")
            print(f"响应: {response.text}")
    except Exception as e:
        print(f"[X] 发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

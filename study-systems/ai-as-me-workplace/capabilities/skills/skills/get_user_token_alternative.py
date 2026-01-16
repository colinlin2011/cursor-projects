# -*- coding: utf-8 -*-
"""
获取用户身份凭证（user_access_token）的替代方案

由于OAuth流程可能比较复杂，这个脚本提供了多种获取token的方法
"""

import requests
import json

APP_ID = "cli_a9c92ca516f99bd9"
APP_SECRET = "zlOKnyZkSuSUSr0WlAl6qbh5Qw4eM6wC"

def method1_api_debug_tool():
    """方法1：使用飞书开放平台API调试工具（推荐）"""
    print("=" * 60)
    print("方法1：使用飞书开放平台API调试工具")
    print("=" * 60)
    print()
    print("步骤：")
    print("1. 访问：https://open.feishu.cn/app/cli_a9c92ca516f99bd9")
    print("2. 在左侧菜单找到'API调试工具'或'测试工具'")
    print("3. 找到'OAuth授权'或'用户授权'功能")
    print("4. 点击'测试'或'授权'按钮")
    print("5. 【重要】在授权页面，确保勾选以下权限：")
    print("   - wiki:wiki")
    print("   - wiki:node:create")
    print("6. 完成授权后，会显示user_access_token")
    print()
    print("这是最简单的方法，无需配置redirect_uri")
    print("但必须确保在授权时勾选了wiki相关权限")
    print()

def method2_manual_code():
    """方法2：手动获取授权码"""
    print("=" * 60)
    print("方法2：手动获取授权码")
    print("=" * 60)
    print()
    print("如果授权后跳转到权限管理页面，可以尝试：")
    print()
    print("步骤1：检查浏览器地址栏")
    print("授权后，即使跳转到权限管理页面，浏览器地址栏的URL可能包含code参数")
    print("请检查完整URL，查找类似以下格式的参数：")
    print("  ?code=xxx")
    print("  ?code=xxx&state=xxx")
    print()
    
    code = input("如果找到code参数，请输入（直接回车跳过）: ").strip()
    
    if code:
        # 获取tenant_access_token
        print()
        print("正在获取user_access_token...")
        tenant_url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
        tenant_response = requests.post(tenant_url, json={
            "app_id": APP_ID,
            "app_secret": APP_SECRET
        })
        
        if tenant_response.status_code == 200:
            tenant_result = tenant_response.json()
            if tenant_result.get('code') == 0:
                tenant_token = tenant_result.get('tenant_access_token')
                
                # 获取user_access_token
                user_url = "https://open.feishu.cn/open-apis/authen/v1/oidc/access_token"
                user_response = requests.post(user_url,
                    headers={"Authorization": f"Bearer {tenant_token}"},
                    json={
                        "grant_type": "authorization_code",
                        "code": code
                    }
                )
                
                if user_response.status_code == 200:
                    user_result = user_response.json()
                    if user_result.get('code') == 0:
                        user_token = user_result['data']['access_token']
                        expires_in = user_result['data'].get('expires_in', 7200)
                        
                        print()
                        print("=" * 60)
                        print("[OK] user_access_token获取成功！")
                        print("=" * 60)
                        print()
                        print(f"user_access_token: {user_token}")
                        print(f"有效期: {expires_in}秒（约{expires_in//3600}小时）")
                        print()
                        print("使用方法：")
                        print("1. 设置环境变量：")
                        print(f'   $env:FEISHU_USER_ACCESS_TOKEN="{user_token}"')
                        print()
                        print("2. 运行创建文档脚本：")
                        print("   python create_fsc_doc_now.py")
                        return user_token
                    else:
                        print(f"[X] 获取user_access_token失败: {user_result}")
                else:
                    print(f"[X] 请求失败: {user_response.status_code}, {user_response.text}")
            else:
                print(f"[X] 获取tenant_access_token失败: {tenant_result}")
        else:
            print(f"[X] 请求失败: {tenant_response.status_code}, {tenant_response.text}")
    
    return None

def method3_direct_input():
    """方法3：直接输入已有的user_access_token"""
    print("=" * 60)
    print("方法3：直接输入已有的user_access_token")
    print("=" * 60)
    print()
    print("如果你已经从其他渠道获取了user_access_token，可以直接使用")
    print()
    token = input("请输入user_access_token（直接回车跳过）: ").strip()
    
    if token:
        print()
        print("=" * 60)
        print("token已设置")
        print("=" * 60)
        print()
        print("使用方法：")
        print("1. 设置环境变量：")
        print(f'   $env:FEISHU_USER_ACCESS_TOKEN="{token}"')
        print()
        print("2. 运行创建文档脚本：")
        print("   python create_fsc_doc_now.py")
        return token
    
    return None

def method4_check_url():
    """方法4：检查授权URL中的参数"""
    print("=" * 60)
    print("方法4：从授权URL中提取code")
    print("=" * 60)
    print()
    print("授权后，即使跳转到其他页面，完整的授权URL可能包含code参数")
    print("请复制授权后浏览器地址栏的完整URL（包括所有参数）")
    print()
    full_url = input("请输入完整的授权URL: ").strip()
    
    if full_url:
        # 尝试从URL中提取code
        from urllib.parse import urlparse, parse_qs
        parsed = urlparse(full_url)
        params = parse_qs(parsed.query)
        
        if 'code' in params:
            code = params['code'][0]
            print(f"找到code: {code}")
            print()
            # 使用code获取token
            return method2_manual_code_with_code(code)
        else:
            print("[X] URL中未找到code参数")
            print("请检查URL是否正确，或者尝试其他方法")
    
    return None

def method2_manual_code_with_code(code):
    """使用code获取token的辅助函数"""
    # 获取tenant_access_token
    tenant_url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    tenant_response = requests.post(tenant_url, json={
        "app_id": APP_ID,
        "app_secret": APP_SECRET
    })
    
    if tenant_response.status_code == 200:
        tenant_result = tenant_response.json()
        if tenant_result.get('code') == 0:
            tenant_token = tenant_result.get('tenant_access_token')
            
            # 获取user_access_token
            user_url = "https://open.feishu.cn/open-apis/authen/v1/oidc/access_token"
            user_response = requests.post(user_url,
                headers={"Authorization": f"Bearer {tenant_token}"},
                json={
                    "grant_type": "authorization_code",
                    "code": code
                }
            )
            
            if user_response.status_code == 200:
                user_result = user_response.json()
                if user_result.get('code') == 0:
                    user_token = user_result['data']['access_token']
                    expires_in = user_result['data'].get('expires_in', 7200)
                    
                    print()
                    print("=" * 60)
                    print("[OK] user_access_token获取成功！")
                    print("=" * 60)
                    print()
                    print(f"user_access_token: {user_token}")
                    print(f"有效期: {expires_in}秒（约{expires_in//3600}小时）")
                    print()
                    print("使用方法：")
                    print("1. 设置环境变量：")
                    print(f'   $env:FEISHU_USER_ACCESS_TOKEN="{user_token}"')
                    print()
                    print("2. 运行创建文档脚本：")
                    print("   python create_fsc_doc_now.py")
                    return user_token
                else:
                    print(f"[X] 获取user_access_token失败: {user_result}")
            else:
                print(f"[X] 请求失败: {user_response.status_code}, {user_response.text}")
        else:
            print(f"[X] 获取tenant_access_token失败: {tenant_result}")
    else:
        print(f"[X] 请求失败: {tenant_response.status_code}, {tenant_response.text}")
    
    return None

def main():
    print("=" * 60)
    print("获取用户身份凭证（user_access_token）- 多种方法")
    print("=" * 60)
    print()
    print("请选择获取方式：")
    print("1. 使用飞书开放平台API调试工具（推荐，最简单）")
    print("2. 手动输入授权码（code）")
    print("3. 从授权URL中提取code")
    print("4. 直接输入已有的user_access_token")
    print()
    
    choice = input("请选择（1-4，直接回车使用方法1）: ").strip()
    
    if choice == "2":
        method2_manual_code()
    elif choice == "3":
        method4_check_url()
    elif choice == "4":
        method3_direct_input()
    else:
        method1_api_debug_tool()
        print()
        print("如果API调试工具不可用，可以尝试其他方法：")
        print()
        choice2 = input("是否尝试其他方法？(y/n): ").strip().lower()
        if choice2 == 'y':
            method2_manual_code()

if __name__ == "__main__":
    main()

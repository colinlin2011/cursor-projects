# -*- coding: utf-8 -*-
"""
获取用户身份凭证（user_access_token）的简化脚本

使用方法：
1. 运行此脚本
2. 按照提示访问授权URL
3. 授权后获取code
4. 输入code获取user_access_token
"""

import requests
import json
import webbrowser

APP_ID = "cli_a9c92ca516f99bd9"
APP_SECRET = "zlOKnyZkSuSUSr0WlAl6qbh5Qw4eM6wC"

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

def main():
    print("=" * 60)
    print("获取用户身份凭证（user_access_token）")
    print("=" * 60)
    print()
    
    # 获取tenant_access_token
    print("步骤1：获取tenant_access_token...")
    tenant_token = get_tenant_access_token()
    if not tenant_token:
        print("[X] 获取tenant_access_token失败")
        return
    print("[OK] tenant_access_token获取成功")
    print()
    
    # 生成授权URL
    print("步骤2：配置重定向URL（重要！）")
    print("=" * 60)
    print("在继续之前，请先在飞书开放平台配置重定向URL：")
    print("1. 访问：https://open.feishu.cn/app/cli_a9c92ca516f99bd9")
    print("2. 进入：开发配置 > 安全设置")
    print("3. 在'重定向URL'中添加以下URL：")
    print("   - https://open.feishu.cn/app/cli_a9c92ca516f99bd9/auth")
    print()
    redirect_uri = input("请输入你在应用配置中设置的重定向URL（直接回车使用默认值）: ").strip()
    if not redirect_uri:
        redirect_uri = "https://open.feishu.cn/app/cli_a9c92ca516f99bd9/auth"
        print(f"使用默认重定向URL: {redirect_uri}")
        print("（请确保此URL已在应用配置中设置）")
    
    print()
    print("步骤3：生成授权URL...")
    # URL编码redirect_uri
    from urllib.parse import quote
    encoded_redirect_uri = quote(redirect_uri, safe='')
    # 添加scope参数，包含完整的文档协作权限
    # 注意：wiki:node:delete 不是有效权限，删除操作通过 docx:document 权限实现
    scope = "wiki:wiki wiki:node:create wiki:node:read wiki:node:update docx:document"
    encoded_scope = quote(scope, safe='')
    auth_url = f"https://open.feishu.cn/open-apis/authen/v1/authorize?app_id={APP_ID}&redirect_uri={encoded_redirect_uri}&response_type=code&scope={encoded_scope}"
    
    print("注意：授权URL已包含以下权限：")
    print(f"  - {scope}")
    print("在授权页面，请确保这些权限已被勾选")
    
    print("请访问以下URL进行授权：")
    print(auth_url)
    print()
    print("或者按回车键自动打开浏览器...")
    input()
    
    try:
        webbrowser.open(auth_url)
    except:
        pass
    
    print()
    print("步骤4：获取授权码（code）")
    print("授权后，浏览器会重定向到你配置的redirect_uri，URL中会包含code参数")
    print(f"例如：{redirect_uri}?code=xxx")
    print("或者：{redirect_uri}?code=xxx&state=xxx")
    print()
    print("提示：如果重定向到localhost，你可能需要手动复制URL中的code参数")
    print()
    code = input("请输入授权码（code）: ").strip()
    
    if not code:
        print("[X] 未输入授权码")
        return
    
    # 获取user_access_token
    print()
    print("步骤4：获取user_access_token...")
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
            user_token = result['data']['access_token']
            expires_in = result['data'].get('expires_in', 7200)
            
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
            print()
            print("或者直接在脚本中设置：")
            print(f'   USER_ACCESS_TOKEN = "{user_token}"')
        else:
            print(f"[X] 获取user_access_token失败: {result}")
    else:
        print(f"[X] 请求失败: {response.status_code}, {response.text}")

if __name__ == "__main__":
    main()

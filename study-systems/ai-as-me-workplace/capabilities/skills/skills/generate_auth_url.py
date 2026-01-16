# -*- coding: utf-8 -*-
"""生成包含完整权限的授权URL"""

from urllib.parse import quote

APP_ID = "cli_a9c92ca516f99bd9"
REDIRECT_URI = "https://open.feishu.cn/app/cli_a9c92ca516f99bd9/auth"
# 注意：wiki:node:delete 不是有效权限，删除操作通过 docx:document 权限实现
SCOPE = "wiki:wiki wiki:node:create wiki:node:read wiki:node:update docx:document"

# URL编码
encoded_redirect_uri = quote(REDIRECT_URI, safe='')
encoded_scope = quote(SCOPE, safe='')

# 生成授权URL
auth_url = f"https://open.feishu.cn/open-apis/authen/v1/authorize?app_id={APP_ID}&redirect_uri={encoded_redirect_uri}&response_type=code&scope={encoded_scope}"

print("=" * 60)
print("授权URL（包含完整权限）")
print("=" * 60)
print()
print(auth_url)
print()
print("=" * 60)
print("使用说明")
print("=" * 60)
print()
print("1. 确保已在飞书开放平台配置重定向URL：")
print(f"   {REDIRECT_URI}")
print()
print("2. 复制上面的授权URL到浏览器访问")
print()
print("3. 登录并授权，确保勾选所有wiki相关权限")
print()
print("4. 授权后，浏览器会跳转到权限管理页面")
print("   请检查浏览器地址栏的完整URL，查找code参数")
print()
print("5. 复制code值，然后运行：")
print("   python get_user_token_with_scope.py")
print("   或使用其他方式获取user_access_token")

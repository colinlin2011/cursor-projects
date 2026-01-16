# 快速获取包含完整权限的user_access_token

## 当前问题

你当前的 `user_access_token` 缺少以下权限：
- `wiki:wiki`
- `wiki:node:create`

## 解决方案

### 步骤1：配置重定向URL（如果还没配置）

1. 访问：https://open.feishu.cn/app/cli_a9c92ca516f99bd9/security
2. 在"重定向URL"中添加：`https://open.feishu.cn/app/cli_a9c92ca516f99bd9/auth`
3. 保存

### 步骤2：访问授权URL

点击或复制以下授权URL到浏览器（已包含所有所需权限）：

```
https://open.feishu.cn/open-apis/authen/v1/authorize?app_id=cli_a9c92ca516f99bd9&redirect_uri=https://open.feishu.cn/app/cli_a9c92ca516f99bd9/auth&response_type=code&scope=wiki:wiki%20wiki:node:create%20wiki:node:read%20wiki:node:update%20docx:document
```

**注意**：已移除 `wiki:node:delete`，因为这不是有效权限。删除操作通过 `docx:document` 权限实现。

**重要**：
1. 确保你已经在飞书开放平台配置了重定向URL：`https://open.feishu.cn/app/cli_a9c92ca516f99bd9/auth`
2. 如果没有配置，请先访问：https://open.feishu.cn/app/cli_a9c92ca516f99bd9/security
3. 在"重定向URL"中添加：`https://open.feishu.cn/app/cli_a9c92ca516f99bd9/auth`

### 步骤3：完成授权

1. 访问授权URL后，会跳转到飞书登录页面
2. 登录并授权
3. **重要**：在授权页面，确保勾选了所有wiki相关权限
4. 完成授权后，浏览器会重定向到应用权限管理页面，URL中会包含 `code` 参数

### 步骤4：获取授权码（code）

授权后，浏览器地址栏的URL会包含 `code` 参数，例如：
```
https://open.feishu.cn/app/cli_a9c92ca516f99bd9/auth?code=abc123def456
```

**注意**：如果跳转到权限管理页面，请检查浏览器地址栏的完整URL，查找 `code` 参数。

复制这个 `code` 值（`abc123def456`）。

### 步骤5：使用code获取token

运行以下Python代码获取token：

```python
import requests

APP_ID = "cli_a9c92ca516f99bd9"
APP_SECRET = "zlOKnyZkSuSUSr0WlAl6qbh5Qw4eM6wC"
CODE = "你的code值"  # 从步骤3获取

# 1. 获取tenant_access_token
tenant_url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
tenant_response = requests.post(tenant_url, json={
    "app_id": APP_ID,
    "app_secret": APP_SECRET
})

if tenant_response.status_code == 200:
    tenant_result = tenant_response.json()
    if tenant_result.get('code') == 0:
        tenant_token = tenant_result.get('tenant_access_token')
        
        # 2. 获取user_access_token
        user_url = "https://open.feishu.cn/open-apis/authen/v1/oidc/access_token"
        user_response = requests.post(user_url,
            headers={"Authorization": f"Bearer {tenant_token}"},
            json={
                "grant_type": "authorization_code",
                "code": CODE
            }
        )
        
        if user_response.status_code == 200:
            user_result = user_response.json()
            if user_result.get('code') == 0:
                user_token = user_result['data']['access_token']
                print(f"user_access_token: {user_token}")
                print()
                print("请复制这个token，然后更新 create_fsc_doc_full.py 中的 USER_ACCESS_TOKEN 变量")
```

或者直接运行脚本：

```bash
python get_user_token_with_scope.py
```

然后按照提示输入code。

## 快速方式：使用飞书开放平台API调试工具

1. 访问：https://open.feishu.cn/app/cli_a9c92ca516f99bd9
2. 在左侧菜单找到"API调试工具"或"测试工具"
3. 找到"OAuth授权"或"用户授权"功能
4. **重要**：在授权时，确保勾选了以下权限：
   - `wiki:wiki`
   - `wiki:node:create`
   - `wiki:node:read`
   - `wiki:node:update`
   - `wiki:node:delete`
   - `docx:document`
5. 完成授权后，会直接显示 `user_access_token`

## 获取token后

更新 `create_fsc_doc_full.py` 中的 `USER_ACCESS_TOKEN` 变量（第28行），然后运行：

```bash
python create_fsc_doc_full.py
```

脚本会自动：
1. 创建Wiki文档节点
2. 获取document_id
3. 添加完整的FSC文档章节结构

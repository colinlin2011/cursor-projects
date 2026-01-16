# 手动获取user_access_token指南

## 问题说明

如果自动获取token遇到redirect_uri错误，可以手动获取user_access_token。

## 方法1：通过飞书开放平台API调试工具（最简单）

### 步骤1：访问API调试工具

1. 访问飞书开放平台：https://open.feishu.cn/
2. 进入你的应用：https://open.feishu.cn/app/cli_a9c92ca516f99bd9
3. 找到**API调试工具**或**测试工具**（通常在左侧菜单）

### 步骤2：使用OAuth测试

1. 在API调试工具中，找到**OAuth授权**或**用户授权**相关功能
2. 点击**测试**或**授权**
3. 完成授权后，会显示`user_access_token`

## 方法2：手动配置redirect_uri后获取

### 步骤1：配置重定向URL

1. 访问应用管理页面：https://open.feishu.cn/app/cli_a9c92ca516f99bd9
2. 进入**开发配置** > **安全设置**
3. 在**重定向URL**中添加：
   - `http://localhost:8080/callback`
   - 或 `https://open.feishu.cn/app/cli_a9c92ca516f99bd9/auth`
   - 或你的自定义URL（需要是公网可访问的）

### 步骤2：获取授权码

访问以下URL（替换`YOUR_REDIRECT_URI`为你配置的URL）：

```
https://open.feishu.cn/open-apis/authen/v1/authorize?app_id=cli_a9c92ca516f99bd9&redirect_uri=YOUR_REDIRECT_URI&response_type=code
```

例如：
```
https://open.feishu.cn/open-apis/authen/v1/authorize?app_id=cli_a9c92ca516f99bd9&redirect_uri=http://localhost:8080/callback&response_type=code
```

授权后，浏览器会重定向，URL中包含`code`参数。

### 步骤3：使用code获取token

使用以下Python代码获取token：

```python
import requests

APP_ID = "cli_a9c92ca516f99bd9"
APP_SECRET = "zlOKnyZkSuSUSr0WlAl6qbh5Qw4eM6wC"
CODE = "your_code_here"  # 从步骤2获取的code

# 1. 获取tenant_access_token
tenant_url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
tenant_response = requests.post(tenant_url, json={
    "app_id": APP_ID,
    "app_secret": APP_SECRET
})
tenant_token = tenant_response.json()['tenant_access_token']

# 2. 使用code获取user_access_token
user_url = "https://open.feishu.cn/open-apis/authen/v1/oidc/access_token"
user_response = requests.post(user_url, 
    headers={"Authorization": f"Bearer {tenant_token}"},
    json={
        "grant_type": "authorization_code",
        "code": CODE
    }
)

result = user_response.json()
if result.get('code') == 0:
    user_token = result['data']['access_token']
    print(f"user_access_token: {user_token}")
else:
    print(f"错误: {result}")
```

## 方法3：使用飞书开放平台的网页应用功能

如果你的应用有网页应用功能：

1. 在应用管理页面，进入**网页应用**配置
2. 配置重定向URL
3. 使用网页应用的OAuth流程获取token

## 方法4：临时解决方案 - 使用应用token（如果Wiki允许）

如果Wiki知识库允许应用访问，可以尝试：

1. 确保应用有`wiki:wiki`和`wiki:node:create`权限
2. 在知识库设置中，检查是否有"允许应用访问"的选项
3. 或者联系知识库管理员，将应用添加到允许列表

## 推荐方案

**最简单的方式**：使用飞书开放平台的API调试工具，直接获取`user_access_token`，无需配置redirect_uri。

## 获取token后

获取到`user_access_token`后：

1. 设置环境变量：
   ```powershell
   $env:FEISHU_USER_ACCESS_TOKEN="your_user_access_token_here"
   ```

2. 运行创建文档脚本：
   ```bash
   python create_fsc_doc_now.py
   ```

## 注意事项

- `user_access_token`有效期约2小时，过期后需要重新获取
- 如果token过期，需要重新授权获取新的token
- 建议将token保存到环境变量或配置文件中，方便重复使用

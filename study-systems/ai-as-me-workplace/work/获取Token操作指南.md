# 获取Token操作指南

## 方法1：使用交互式脚本（推荐）

在终端中运行：

```bash
cd capabilities/skills/skills
python get_token_manual.py
```

脚本会：
1. 自动打开浏览器到授权页面
2. 等待你输入授权码
3. 自动获取并保存token

## 方法2：手动获取授权码

### 步骤1：打开授权页面

复制以下URL到浏览器中打开：

```
https://open.feishu.cn/open-apis/authen/v1/index?app_id=cli_a9c92ca516f99bd9&redirect_uri=https://open.feishu.cn/app/cli_a9c92ca516f99bd9/auth&scope=bitable:app bitable:app:readonly base:app:read base:field:read base:view:read base:record:read wiki:wiki wiki:node:read
```

### 步骤2：完成授权

在浏览器中：
1. 登录飞书账号
2. 确认授权权限
3. 点击"同意授权"

### 步骤3：获取授权码

授权完成后，浏览器会跳转到类似以下URL：

```
https://open.feishu.cn/app/cli_a9c92ca516f99bd9/auth?code=xxxxx
```

从URL中复制 `code=` 后面的值（xxxxx部分）

### 步骤4：使用授权码获取Token

运行以下Python代码（或使用 `get_token_manual.py`）：

```python
import requests

# 配置
APP_ID = "cli_a9c92ca516f99bd9"
APP_SECRET = "zlOKnyZkSuSUSr0WlAl6qbh5Qw4eM6wC"
CODE = "你的授权码"  # 从步骤3中获取

# 1. 获取tenant_access_token
url1 = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
response1 = requests.post(url1, json={
    "app_id": APP_ID,
    "app_secret": APP_SECRET
})
tenant_token = response1.json()['tenant_access_token']

# 2. 获取user_access_token
url2 = "https://open.feishu.cn/open-apis/authen/v1/oidc/access_token"
response2 = requests.post(url2, headers={
    "Authorization": f"Bearer {tenant_token}",
    "Content-Type": "application/json"
}, json={
    "grant_type": "authorization_code",
    "code": CODE
})

result = response2.json()
if result.get('code') == 0:
    data = result['data']
    access_token = data['access_token']
    refresh_token = data['refresh_token']
    expires_in = data['expires_in']
    
    print(f"Access Token: {access_token}")
    print(f"Refresh Token: {refresh_token}")
    print(f"有效期: {expires_in}秒")
    
    # 保存到缓存
    from token_manager import get_token_manager
    manager = get_token_manager()
    manager.save_initial_token(access_token, expires_in, refresh_token)
    print("Token已保存到缓存")
```

## 验证Token

获取token后，运行测试脚本验证：

```bash
cd capabilities/skills/skills
python test_fault_diagnosis_config.py
```

应该看到：
- Token缓存存在: True
- 获取到有效token

## 注意事项

1. **授权码有效期**：授权码（code）只能使用一次，且有效期很短（通常几分钟）
2. **Token有效期**：access_token有效期2小时，refresh_token有效期14天
3. **自动刷新**：保存refresh_token后，系统会自动刷新token，14天内无需重新授权
4. **权限范围**：确保授权时包含了所需的所有权限（bitable和wiki相关权限）

## 故障排查

### 问题1：授权码无效

- 检查授权码是否从正确的URL中复制
- 确保授权码没有过期（尽快使用）
- 确保授权码只使用一次

### 问题2：获取token失败

- 检查APP_ID和APP_SECRET是否正确
- 检查网络连接
- 查看错误信息中的详细说明

### 问题3：Token保存失败

- 检查 `work` 目录是否存在
- 检查是否有写入权限
- 查看错误日志

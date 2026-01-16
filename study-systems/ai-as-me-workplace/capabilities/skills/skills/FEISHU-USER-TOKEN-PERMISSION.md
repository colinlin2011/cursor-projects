# 用户身份凭证权限问题解决指南

## 错误码99991679说明

错误信息：
```
Unauthorized. You do not have permission to perform the requested operation on the resource. 
Please request user re-authorization and try again. 
required one of these privileges under the user identity: [wiki:wiki, wiki:node:create]
```

**含义**：用户身份凭证（user_access_token）在获取时，用户没有授权`wiki:wiki`和`wiki:node:create`权限。

## 解决方法

### 方法1：重新授权获取user_access_token（推荐）

在获取`user_access_token`时，需要确保用户授权了以下权限：
- `wiki:wiki`
- `wiki:node:create`

#### 步骤1：使用正确的授权URL

授权URL需要包含`scope`参数，指定所需的权限：

```
https://open.feishu.cn/open-apis/authen/v1/authorize?app_id=cli_a9c92ca516f99bd9&redirect_uri=YOUR_REDIRECT_URI&response_type=code&scope=wiki:wiki wiki:node:create
```

**注意**：
- 替换`YOUR_REDIRECT_URI`为你配置的重定向URL
- `scope`参数包含所需权限，用空格分隔

#### 步骤2：在授权页面确认权限

授权时，确保：
1. 授权页面显示了wiki相关权限
2. 勾选了所有需要的权限
3. 完成授权

#### 步骤3：重新获取token

使用新的授权码（code）重新获取`user_access_token`。

### 方法2：使用飞书开放平台API调试工具

1. 访问：https://open.feishu.cn/app/cli_a9c92ca516f99bd9
2. 使用API调试工具中的OAuth测试功能
3. **重要**：在授权时，确保勾选了`wiki:wiki`和`wiki:node:create`权限
4. 完成授权后获取新的`user_access_token`

### 方法3：检查应用权限配置

确保应用已配置了以下权限：
1. 访问应用管理页面：https://open.feishu.cn/app/cli_a9c92ca516f99bd9
2. 进入**权限管理**或**Scope配置**
3. 确认以下权限已添加：
   - `wiki:wiki`
   - `wiki:node:create`
4. 如果未添加，先添加权限，然后重新授权获取token

## 验证权限

获取新的`user_access_token`后，可以验证权限：

```python
import requests

token = "your_user_access_token"

# 测试调用（使用一个简单的查询接口）
url = "https://open.feishu.cn/open-apis/wiki/v2/spaces"
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

response = requests.get(url, headers=headers)
print(response.json())
```

如果返回成功，说明权限正确。

## 常见问题

### Q1: 为什么需要重新授权？

**A**: `user_access_token`在获取时会记录用户授权的权限范围。如果获取时没有授权wiki权限，后续即使应用有权限，token也无法使用。

### Q2: 如何确保授权时包含所需权限？

**A**: 
- 在授权URL中添加`scope`参数
- 在授权页面确认显示了所需权限
- 勾选所有需要的权限

### Q3: token有效期是多久？

**A**: `user_access_token`有效期约2小时。过期后需要重新授权获取新的token。

### Q4: 可以刷新token吗？

**A**: 可以，使用刷新token接口。但如果权限不足，刷新后的token仍然没有所需权限，需要重新授权。

## 相关文档

- [飞书开放平台 - 获取user_access_token](https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/authentication-management/access-token/get-user-access-token)
- [错误码99991679解决方案](https://open.feishu.cn/document/uAjLw4CM/ugTN1YjL4UTN24CO1UjN/trouble-shooting/how-to-resolve-error-99991679)

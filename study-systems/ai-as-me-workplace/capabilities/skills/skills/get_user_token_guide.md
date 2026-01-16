# 获取用户身份凭证（user_access_token）指南

## 问题说明

飞书Wiki的成员管理只支持真实用户，应用无法直接作为成员添加。因此，创建Wiki文档需要使用**用户身份凭证（user_access_token）**，以用户身份操作，权限由用户的权限决定。

## 解决方案

### 方案1：使用用户身份凭证（推荐）

使用`user_access_token`，以你的用户身份创建文档，这样就不需要将应用添加到Wiki成员了。

### 方案2：手动获取user_access_token

#### 方法A：通过飞书开放平台工具获取（最简单）

1. 访问飞书开放平台：https://open.feishu.cn/
2. 进入你的应用（APP ID: `cli_a9c92ca516f99bd9`）
3. 在应用详情页，找到**API调试工具**或**测试工具**
4. 使用OAuth授权流程获取`user_access_token`

#### 方法B：通过OAuth流程获取

1. **配置重定向URL**：
   - 在应用管理页面 > **开发配置** > **安全设置**
   - 配置重定向URL（可以是本地地址，如：`http://localhost:8080/callback`）

2. **获取授权码**：
   - 访问授权URL：
     ```
     https://open.feishu.cn/open-apis/authen/v1/authorize?app_id=cli_a9c92ca516f99bd9&redirect_uri=http://localhost:8080/callback&response_type=code
     ```
   - 登录并授权
   - 重定向后会得到`code`参数

3. **获取user_access_token**：
   ```python
   import requests
   
   # 先获取tenant_access_token
   tenant_token = get_tenant_access_token(app_id, app_secret)
   
   # 使用code获取user_access_token
   url = "https://open.feishu.cn/open-apis/authen/v1/oidc/access_token"
   headers = {
       "Authorization": f"Bearer {tenant_token}",
       "Content-Type": "application/json"
   }
   data = {
       "grant_type": "authorization_code",
       "code": "your_code_here"
   }
   response = requests.post(url, headers=headers, json=data)
   result = response.json()
   user_access_token = result['data']['access_token']
   ```

### 方案3：使用临时解决方案（快速测试）

如果只是临时测试，可以：

1. **手动创建文档**：在飞书中手动创建文档
2. **使用API编辑**：获取文档token后，使用API编辑内容
3. **使用脚本辅助**：创建一个脚本，生成文档模板，然后手动复制到飞书

## 更新后的脚本使用方式

### 方式1：提供user_access_token

```python
from feishu_api_wrapper import FeishuAPI

api = FeishuAPI(
    plugin_id="",
    plugin_secret="",
    app_id="cli_a9c92ca516f99bd9",
    app_secret="zlOKnyZkSuSUSr0WlAl6qbh5Qw4eM6wC"
)

# 设置用户身份凭证
api.set_user_access_token("your_user_access_token_here")

# 创建文档
doc = api.create_wiki_doc(
    space_id="7353073903872868356",
    parent_node_token="V7FXwKKdLiEus3kU9oMcgLwGnpe",
    title="舱驾一体域控的FSC文档",
    use_user_token=True
)
```

### 方式2：更新脚本支持user_access_token

我已经更新了脚本，支持通过环境变量或输入提供`user_access_token`。

## 快速获取user_access_token的方法

### 使用Postman或curl测试

1. **获取tenant_access_token**：
   ```bash
   curl -X POST "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal" \
     -H "Content-Type: application/json" \
     -d '{
       "app_id": "cli_a9c92ca516f99bd9",
       "app_secret": "zlOKnyZkSuSUSr0WlAl6qbh5Qw4eM6wC"
     }'
   ```

2. **使用OAuth获取user_access_token**（需要用户授权）

## 推荐方案

**最简单的方式**：如果你有飞书开放平台的API调试工具，直接在那里获取`user_access_token`，然后更新脚本使用该token。

或者，我可以帮你创建一个简化的脚本，通过浏览器授权流程获取token。

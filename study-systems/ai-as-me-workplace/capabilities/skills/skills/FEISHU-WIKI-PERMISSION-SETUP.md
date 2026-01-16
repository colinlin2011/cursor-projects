# 飞书Wiki权限配置指南

## 问题说明

在创建Wiki文档时，如果遇到错误码`99991672`，表示应用缺少必要的权限。

## 错误信息示例

```
错误码：99991672
错误信息：Access denied. One of the following scopes is required: [wiki:wiki, wiki:node:create]
```

## 解决方法

### 步骤1：访问应用管理页面

1. 访问飞书开放平台：https://open.feishu.cn/
2. 登录你的账号
3. 进入应用管理页面
4. 找到你的应用（APP ID: `cli_a9c92ca516f99bd9`）

### 步骤2：配置权限

1. 在应用详情页面，找到**权限管理**或**Scope配置**
2. 添加以下权限：
   - `wiki:wiki` - Wiki知识库权限
   - `wiki:node:create` - 创建Wiki节点权限

### 步骤3：授权权限

1. 点击**申请权限**或**授权**
2. 选择需要授权的权限范围
3. 提交申请（如果是企业自建应用，可能需要管理员审批）

### 步骤4：直接授权链接（快速方式）

访问以下链接，直接授权权限：

```
https://open.feishu.cn/app/cli_a9c92ca516f99bd9/auth?q=wiki:wiki,wiki:node:create
```

或者使用完整的授权链接：

```
https://open.feishu.cn/app/cli_a9c92ca516f99bd9/auth?q=wiki:wiki,wiki:node:create&op_from=openapi&token_type=tenant
```

### 步骤5：验证权限

授权完成后，重新运行创建文档的脚本：

```bash
python create_fsc_doc_now.py
```

## 其他可能需要的权限

根据你的使用场景，可能还需要以下权限：

- **云文档权限**：
  - `drive:drive` - 云文档基础权限
  - `drive:drive:readonly` - 只读权限
  - `drive:drive:writeonly` - 只写权限

- **知识库权限**：
  - `wiki:wiki` - Wiki知识库权限（已包含）
  - `wiki:node:create` - 创建节点权限（已包含）
  - `wiki:node:read` - 读取节点权限
  - `wiki:node:update` - 更新节点权限
  - `wiki:node:delete` - 删除节点权限

## 权限授权状态检查

在应用管理页面的**权限管理**中，可以查看：
- 已申请的权限列表
- 权限的授权状态（已授权/待审批/已拒绝）
- 权限的使用范围

## 注意事项

1. **企业自建应用**：某些权限可能需要企业管理员审批
2. **权限生效时间**：授权后可能需要几分钟才能生效
3. **权限范围**：确保权限范围包含你使用的知识库
4. **Token刷新**：授权新权限后，可能需要重新获取token

## 相关文档

- [飞书开放平台 - 权限管理](https://open.feishu.cn/document/ukTMukTMukTM/uYjL14iM2EjL2ITN)
- [飞书开放平台 - Wiki API](https://open.feishu.cn/document/ukTMukTMukTM/uUDN04SN0QjL1QDN/wiki-v2/space/get_node)
- [错误码99991672解决方案](https://open.feishu.cn/document/uAjLw4CM/ugTN1YjL4UTN24CO1UjN/trouble-shooting/how-to-fix-the-99991672-error)

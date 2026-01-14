# 飞书开放平台 API 概述

**文档来源**：https://open.feishu.cn/document/server-docs/api-call-guide/calling-process/overview  
**最后更新**：2026-01-13

---

## 概述

飞书开放平台提供多种API能力，包括：
- **多维表格（Bitable）API**：用于访问和操作多维表格数据
- **Wiki API**：用于访问和操作Wiki文档
- **消息API**：用于发送和接收消息
- **其他服务API**：日历、通讯录等

---

## API调用流程

### 1. 创建自建应用
- 登录飞书开放平台：https://open.feishu.cn
- 创建自建应用
- 获取 App ID 和 App Secret

### 2. 配置权限
- 在"权限管理"中添加所需权限
- 多维表格需要：`bitable:app`、`bitable:app:readonly` 等权限
- Wiki需要：`wiki:wiki`、`wiki:wiki:readonly` 等权限

### 3. 获取访问令牌（Access Token）
- 使用 App ID 和 App Secret 获取 access_token
- API地址：`https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal`
- 参考：https://open.feishu.cn/document/server-docs/authentication-management/access-token/tenant_access_token_internal

### 4. 调用API
- 使用 access_token 调用相应的API接口
- Header中需要包含：`Authorization: Bearer {access_token}`

---

## 多维表格（Bitable）API

### 获取记录列表
- **API地址**：`GET https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records`
- **参考文档**：https://open.feishu.cn/document/server-docs/docs/bitable-v1/app-table-record/list

### 获取记录详情
- **API地址**：`GET https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records/{record_id}`
- **参考文档**：https://open.feishu.cn/document/server-docs/docs/bitable-v1/app-table-record/get

### 创建记录
- **API地址**：`POST https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records`
- **参考文档**：https://open.feishu.cn/document/server-docs/docs/bitable-v1/app-table-record/create

### 更新记录
- **API地址**：`PUT https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records/{record_id}`
- **参考文档**：https://open.feishu.cn/document/server-docs/docs/bitable-v1/app-table-record/update

### 删除记录
- **API地址**：`DELETE https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records/{record_id}`
- **参考文档**：https://open.feishu.cn/document/server-docs/docs/bitable-v1/app-table-record/delete

### 批量获取记录
- **API地址**：`POST https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records/batch_get`
- **参考文档**：https://open.feishu.cn/document/server-docs/docs/bitable-v1/app-table-record/batch_get

---

## Wiki API

### 获取文档内容
- **API地址**：`GET https://open.feishu.cn/open-apis/drive/v1/files/{file_token}/content`
- **参考文档**：https://open.feishu.cn/document/server-docs/docs/drive-v1/file/get

### 获取文档元信息
- **API地址**：`GET https://open.feishu.cn/open-apis/drive/v1/files/{file_token}/meta`
- **参考文档**：https://open.feishu.cn/document/server-docs/docs/drive-v1/file/get_meta

---

## 链接格式

### 多维表格链接格式
- **格式**：`https://bitable.feishu.cn/app/{app_token}/table/{table_id}`
- **示例**：`https://bitable.feishu.cn/app/xxxxxxxxxx/table/xxxxxxxxxx`

### Wiki链接格式
- **格式**：`https://{domain}.feishu.cn/wiki/{wiki_id}`
- **示例**：`https://zyt.feishu.cn/wiki/CGMnwhxzLixWhGk87jYcDRfonsh`

---

## 认证方式

### Tenant Access Token（企业内部应用）
- 使用 App ID 和 App Secret 获取
- 适用于企业内部应用
- 参考：https://open.feishu.cn/document/server-docs/authentication-management/access-token/tenant_access_token_internal

### User Access Token（用户身份）
- 需要用户授权
- 适用于需要用户身份的场景
- 参考：https://open.feishu.cn/document/server-docs/authentication-management/access-token/user_access_token

---

## 重要说明

1. **API限制**：注意QPS限制和频率限制
2. **权限要求**：确保应用有相应的权限
3. **错误处理**：参考错误码文档处理错误
4. **文档更新**：API文档可能更新，请参考最新文档

---

## 参考资源

- **飞书开放平台文档**：https://open.feishu.cn/document/
- **API调用指南**：https://open.feishu.cn/document/server-docs/api-call-guide/calling-process/overview
- **多维表格API**：https://open.feishu.cn/document/server-docs/docs/bitable-v1/overview
- **Wiki API**：https://open.feishu.cn/document/server-docs/docs/drive-v1/overview

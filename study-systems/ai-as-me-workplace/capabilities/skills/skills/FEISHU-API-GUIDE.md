# 飞书API使用指南

## 重要说明

**所有飞书API调用必须参考reference文档！**

### Reference文档位置
- **路径**：`c:\Users\colin.lin\.cursor\cursor-projects\tools\feishu interaction\reference\`
- **API文档**：`api_docs/`目录
- **快速开始**：`quick_start_example.py`
- **Postman示例**：`postman_examples/`

---

## 使用流程

### 步骤1：查阅Reference文档

在调用任何飞书API之前，**必须**：

1. **查找对应的API文档**：
   - 查看`api_docs/API-列表.md`找到需要的API
   - 查看对应的详细文档（如`工作项-8.md`表示创建工作项）

2. **参考示例代码**：
   - 查看`quick_start_example.py`了解基本用法
   - 查看`postman_examples/`了解请求格式

3. **理解API要求**：
   - URL结构
   - Header格式
   - 请求体格式
   - 响应格式
   - 错误处理

### 步骤2：获取认证信息

参考`api_docs/调用流程-1.md`（获取访问凭证）：

- **plugin_id**：插件ID
- **plugin_secret**：插件密钥
- **project_key**：空间ID（双击空间图标获取）
- **user_key**：用户密钥（双击用户头像获取）

### 步骤3：构建请求

按照API文档要求构建请求：

- **URL**：`https://project.feishu.cn/open_api/{project_key}/...`
- **Header**：
  - `Content-Type: application/json`
  - `X-PLUGIN-TOKEN: {plugin_token}`
  - `X-USER-KEY: {user_key}`（如需要）
- **Body**：按照API文档格式

### 步骤4：调用API

使用Python requests库或封装工具调用API。

### 步骤5：处理响应

- 检查HTTP状态码
- 检查响应中的error字段
- 参考`api_docs/格式说明-5.md`（错误码）处理错误

---

## 常用API场景

### 场景1：消息通讯

**参考文档**：
- 飞书开放平台文档（非项目API）

**注意事项**：
- 需要飞书开放平台的应用凭证
- 参考飞书开放平台API文档

### 场景2：Wiki云文档

**参考文档**：
- 飞书开放平台文档（云文档API）

**注意事项**：
- 需要飞书开放平台的应用凭证
- 参考飞书开放平台API文档

### 场景3：在线表格/多维表格

**参考文档**：
- 飞书开放平台文档（表格API）

**注意事项**：
- 需要飞书开放平台的应用凭证
- 参考飞书开放平台API文档

### 场景4：飞书项目工作项

**参考文档**：
- `api_docs/工作项-8.md`：创建工作项
- `api_docs/工作项-9.md`：更新工作项
- `api_docs/工作项-6.md`：查询工作项
- `api_docs/工作项-13.md`：删除工作项
- `api_docs/工作项-1.md`：搜索工作项

**示例代码**：
```python
# 参考 quick_start_example.py
from feishu_api import get_plugin_token, create_work_item

# 获取token
plugin_token = get_plugin_token(plugin_id, plugin_secret)

# 创建工作项
response = create_work_item(
    project_key=project_key,
    work_item_type_key="story",
    plugin_token=plugin_token,
    user_key=user_key,
    fields={"name": "新工作项"}
)
```

### 场景5：飞书项目流程

**参考文档**：
- `api_docs/流程与节点-1.md`：获取工作流详情
- `api_docs/流程与节点-3.md`：更新节点
- `api_docs/流程与节点-4.md`：节点完成/回滚
- `api_docs/流程与节点-5.md`：状态流转

---

## 注意事项

### 1. 必须引用Reference文档
- **所有API调用前必须查阅reference文档**
- 不要凭记忆或猜测调用API
- 确保遵循最新的API格式要求

### 2. QPS限制
- 大部分接口：15 QPS
- 部分接口有特殊限制（参考`api_docs/Open-API-概述.md`）
- 需要合理设计调用逻辑

### 3. 幂等性
- 写类型接口支持`X-IDEM-UUID`幂等串
- 可以设置幂等串避免重复操作

### 4. 错误处理
- 必须检查HTTP状态码
- 必须检查响应中的error字段
- 参考错误码文档进行排查

### 5. 认证信息
- plugin_token需要定期刷新
- 确保认证信息的安全性
- 不要将认证信息硬编码在代码中

---

## 快速参考

### API文档索引
- `api_docs/_index.md`：完整的API文档索引

### 核心文档
- `api_docs/Open-API-概述.md`：API概述和基本格式
- `api_docs/API-列表.md`：完整的API列表
- `api_docs/格式说明-5.md`：错误码说明

### 示例代码
- `quick_start_example.py`：快速开始示例
- `postman_examples/`：Postman示例集合

---

## 故障排除

### 常见问题

1. **认证失败**
   - 检查plugin_id和plugin_secret是否正确
   - 检查plugin_token是否过期
   - 参考`api_docs/调用流程-1.md`

2. **API调用失败**
   - 检查URL格式是否正确
   - 检查Header格式是否正确
   - 检查请求体格式是否正确
   - 参考对应的API文档

3. **QPS限制**
   - 检查是否超过QPS限制
   - 实现请求重试和限流机制

4. **错误码**
   - 参考`api_docs/格式说明-5.md`（错误码说明）
   - 根据错误码进行相应处理

---

## 关联记录

### 相关能力
- [MCP-001 飞书API集成](../mcps/mcps/feishu-api.md)
- [SKILL-001 飞书API封装工具](feishu-api-wrapper.md)

### 参考文档
- **Reference位置**：`c:\Users\colin.lin\.cursor\cursor-projects\tools\feishu interaction\reference\`

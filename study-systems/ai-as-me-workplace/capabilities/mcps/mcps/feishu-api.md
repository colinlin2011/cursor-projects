# 飞书API能力

**能力ID**：MCP-001  
**能力名称**：飞书API集成  
**能力类型**：MCP  
**创建日期**：2026-01-13  
**最后更新**：2026-01-13  
**版本**：v1.0  
**状态**：可用  
**维护人**：系统

---

## 能力描述

### 功能概述
飞书API能力提供与飞书平台各功能模块的集成，包括：
- **消息通讯**：发送消息、接收消息、群组管理
- **云文档（Wiki）**：创建、编辑、查询云文档
- **在线表格**：创建、编辑、查询在线表格
- **多维表格**：创建、编辑、查询多维表格
- **飞书项目**：工作项管理、流程管理、视图管理

### 适用场景
- 与飞书消息通讯
- 管理飞书Wiki云文档
- 操作飞书在线表格
- 操作飞书多维表格
- 管理飞书项目工作项
- 查询和更新飞书项目流程

---

## API参考文档

### 重要说明
**所有飞书API调用必须参考以下文档**：
- **参考文档位置**：`c:\Users\colin.lin\.cursor\cursor-projects\tools\feishu interaction\reference\`
- **API文档目录**：`api_docs/`
- **快速开始示例**：`quick_start_example.py`
- **Postman示例**：`postman_examples/`

### 核心文档
1. **Open-API-概述.md**：API概述、URL结构、Header格式、调用流程
2. **API-列表.md**：完整的API列表和说明
3. **_index.md**：API文档索引
4. **quick_start_example.py**：快速开始示例代码

### 关键API模块
- **用户&用户组**：用户查询、用户搜索、用户组管理
- **空间**：空间列表、空间详情
- **工作项**：工作项CRUD、搜索、过滤
- **流程与节点**：工作流管理、节点操作、状态流转
- **子任务**：子任务管理
- **视图与度量**：视图管理、度量图表
- **配置**：工作项类型、字段、流程模板
- **评论**：评论查询、添加评论
- **附件**：附件上传、下载、删除

---

## 能力接口

### 认证接口
- **获取插件访问凭证**：`get_plugin_token(plugin_id, plugin_secret)`
- **获取用户访问凭证**：`get_user_token()`

### 消息通讯接口
- **发送消息**：`send_message()`
- **接收消息**：`receive_message()`
- **群组管理**：`manage_group()`

### 云文档（Wiki）接口
- **创建云文档**：`create_wiki_doc()`
- **编辑云文档**：`update_wiki_doc()`
- **查询云文档**：`query_wiki_doc()`

### 在线表格接口
- **创建在线表格**：`create_spreadsheet()`
- **编辑在线表格**：`update_spreadsheet()`
- **查询在线表格**：`query_spreadsheet()`

### 多维表格接口
- **创建多维表格**：`create_bitable()`
- **编辑多维表格**：`update_bitable()`
- **查询多维表格**：`query_bitable()`

### 飞书项目接口
- **工作项管理**：
  - `create_work_item()` - 创建工作项
  - `update_work_item()` - 更新工作项
  - `query_work_item()` - 查询工作项
  - `delete_work_item()` - 删除工作项
  - `search_work_items()` - 搜索工作项
- **流程管理**：
  - `get_workflow()` - 获取工作流详情
  - `update_node()` - 更新节点
  - `operate_node()` - 节点完成/回滚
  - `state_change()` - 状态流转
- **视图管理**：
  - `get_views()` - 获取视图列表
  - `create_view()` - 创建视图
  - `get_view_items()` - 获取视图下工作项

---

## 使用要求

### 必须引用Reference文档
**所有飞书API调用必须遵循以下规则**：

1. **调用前必须查阅**：
   - 对应的API文档（`api_docs/`目录下）
   - 快速开始示例（`quick_start_example.py`）
   - Postman示例（如需要）

2. **必须遵循的格式**：
   - URL结构：`https://project.feishu.cn/open_api/{project_key}/...`
   - Header格式：必须包含`X-PLUGIN-TOKEN`和`X-USER-KEY`（如需要）
   - 请求格式：`Content-Type: application/json`

3. **必须注意的限制**：
   - QPS限制：15 QPS（部分接口有特殊限制）
   - 幂等性：写类型接口支持`X-IDEM-UUID`幂等串

### 调用流程
1. 获取访问凭证（plugin_token或user_plugin_token）
2. 授权接口（在飞书项目开放平台插件详情页）
3. 调用API（参考API文档和示例）

---

## 配置要求

### 必需配置
- **plugin_id**：插件ID
- **plugin_secret**：插件密钥
- **project_key**：空间ID（双击空间图标获取）
- **user_key**：用户密钥（双击用户头像获取）

### 可选配置
- **base_url**：API基础URL（默认：`https://project.feishu.cn`）
- **timeout**：请求超时时间（默认：30秒）

---

## 使用示例

### 示例1：获取插件访问凭证
```python
from feishu_api import get_plugin_token

plugin_token = get_plugin_token(
    plugin_id="your_plugin_id",
    plugin_secret="your_plugin_secret"
)
```

### 示例2：创建工作项
```python
from feishu_api import create_work_item

response = create_work_item(
    project_key="your_project_key",
    work_item_type_key="story",
    plugin_token=plugin_token,
    user_key="your_user_key",
    fields={
        "name": "新工作项",
        "description": "工作项描述"
    }
)
```

### 示例3：查询工作项
```python
from feishu_api import query_work_item

work_item = query_work_item(
    project_key="your_project_key",
    work_item_type_key="story",
    work_item_id="work_item_id",
    plugin_token=plugin_token,
    user_key="your_user_key"
)
```

---

## 错误处理

### 常见错误码
参考`api_docs/格式说明-5.md`（Open API错误码）

### 错误处理策略
- 检查HTTP状态码
- 检查响应中的error字段
- 参考错误码文档进行排查

---

## 能力使用记录

### 使用统计
- **总调用次数**：0
- **成功次数**：0
- **失败次数**：0
- **成功率**：0%

### 使用历史
| 日期 | 调用次数 | 成功率 | 平均响应时间 | 备注 |
|------|---------|--------|------------|------|
| - | - | - | - | - |

---

## 关联记录

### 相关注册表
- [能力注册表链接](../registry.md)

### 相关MCP定义
- [MCP定义链接](../MCP-TEMPLATE.md)

### 相关使用记录
- [使用记录链接](../../usage/usage-history.md)

### 参考文档
- **Reference位置**：`c:\Users\colin.lin\.cursor\cursor-projects\tools\feishu interaction\reference\`
- **API文档**：`api_docs/`
- **示例代码**：`quick_start_example.py`

---

## 版本历史

| 版本 | 日期 | 更新内容 | 更新人 |
|------|------|---------|--------|
| v1.0 | 2026-01-13 | 初始创建 | 系统 |

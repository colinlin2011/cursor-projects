# 飞书交互能力

**Skill ID**：SKILL-003  
**Skill名称**：飞书交互能力  
**创建日期**：2026-01-13  
**最后更新**：2026-01-13  
**版本**：v1.0  
**状态**：可用  
**维护人**：系统

---

## Skill描述

### 功能概述

飞书交互能力提供与飞书平台各功能模块的完整集成，包括：

1. **即时通讯**
   - 发送消息（文本、富文本、卡片等）
   - 接收消息（需要配置webhook）
   - 群组管理

2. **Wiki云文档**
   - 创建、编辑、查询云文档
   - 文档内容管理
   - 文档权限管理

3. **在线表格**
   - 创建、编辑在线表格
   - 单元格读写
   - 表格数据管理

4. **多维表格**
   - 创建、编辑多维表格
   - 记录CRUD操作
   - 视图管理

5. **飞书项目**
   - 工作项管理（创建、更新、查询、删除）
   - 流程管理（节点操作、状态流转）
   - 视图管理（获取视图、查询视图工作项）
   - 操作记录查询

### 适用场景

- **即时通讯**：
  - 自动发送工作通知
  - 发送任务提醒
  - 发送报告摘要

- **Wiki云文档**：
  - 自动创建项目文档
  - 更新文档内容
  - 同步文档信息

- **在线表格**：
  - 数据导入导出
  - 表格数据更新
  - 报表生成

- **多维表格**：
  - 任务管理
  - 数据收集
  - 数据分析

- **飞书项目**：
  - 工作项自动化管理
  - 流程自动化
  - 项目数据同步

### 不适用场景

- 需要实时双向通信的场景（建议使用webhook）
- 需要复杂权限控制的场景（需要额外配置）
- 需要大量并发操作的场景（受QPS限制）

---

## Skill接口

### 调用方式

- **方式**：Python SDK
- **接口文件**：`capabilities/skills/skills/feishu_api_wrapper.py`
- **调用示例**：
```python
from feishu_api_wrapper import FeishuAPI

# 初始化（飞书项目API）
api = FeishuAPI(
    plugin_id="your_plugin_id",
    plugin_secret="your_plugin_secret",
    project_key="your_project_key",
    user_key="your_user_key"
)

# 初始化（包含开放平台API）
api = FeishuAPI(
    plugin_id="your_plugin_id",
    plugin_secret="your_plugin_secret",
    project_key="your_project_key",
    user_key="your_user_key",
    app_id="your_app_id",  # 开放平台应用ID
    app_secret="your_app_secret"  # 开放平台应用密钥
)
```

### 输入参数

#### 初始化参数

| 参数名 | 类型 | 必填 | 默认值 | 描述 |
|--------|------|------|--------|------|
| plugin_id | string | 是 | - | 飞书项目插件ID |
| plugin_secret | string | 是 | - | 飞书项目插件密钥 |
| project_key | string | 否 | None | 空间ID（双击空间图标获取） |
| user_key | string | 否 | None | 用户密钥（双击用户头像获取） |
| app_id | string | 否 | None | 飞书开放平台应用ID（用于即时通讯、Wiki、表格） |
| app_secret | string | 否 | None | 飞书开放平台应用密钥 |
| base_url | string | 否 | "https://project.feishu.cn" | 飞书项目API基础URL |
| open_platform_base_url | string | 否 | "https://open.feishu.cn" | 飞书开放平台API基础URL |
| timeout | int | 否 | 30 | 请求超时时间（秒） |

#### 方法参数

各方法的参数请参考`feishu_api_wrapper.py`中的方法定义。

### 输出结果

- **结果格式**：Dict（Python字典）或None
- **结果示例**：
```python
{
    "work_item_id": "xxx",
    "work_item_type_key": "story",
    "fields": {...}
}
```
- **错误处理**：返回None时表示调用失败，错误信息会打印到控制台

---

## Skill使用示例

### 示例1：创建工作项

```python
from feishu_api_wrapper import FeishuAPI

api = FeishuAPI(
    plugin_id="your_plugin_id",
    plugin_secret="your_plugin_secret",
    project_key="your_project_key",
    user_key="your_user_key"
)

# 创建工作项
work_item = api.create_work_item(
    work_item_type_key="story",
    fields={
        "name": "新功能需求",
        "description": "实现XX功能",
        "priority": "high"
    }
)

if work_item:
    print(f"工作项创建成功: {work_item.get('work_item_id')}")
else:
    print("工作项创建失败")
```

### 示例2：发送消息

```python
from feishu_api_wrapper import FeishuAPI

api = FeishuAPI(
    plugin_id="your_plugin_id",
    plugin_secret="your_plugin_secret",
    app_id="your_app_id",
    app_secret="your_app_secret"
)

# 发送文本消息
result = api.send_message(
    receive_id="user_open_id",
    receive_id_type="open_id",
    msg_type="text",
    content={
        "text": "这是一条测试消息"
    }
)

if result:
    print(f"消息发送成功: {result.get('message_id')}")
```

### 示例3：创建Wiki文档

```python
from feishu_api_wrapper import FeishuAPI

api = FeishuAPI(
    app_id="your_app_id",
    app_secret="your_app_secret"
)

# 创建Wiki文档
doc = api.create_wiki_doc(
    space_id="knowledge_space_id",
    title="项目文档"
)

if doc:
    print(f"文档创建成功: {doc.get('token')}")
```

### 示例4：查询多维表格记录

```python
from feishu_api_wrapper import FeishuAPI

api = FeishuAPI(
    app_id="your_app_id",
    app_secret="your_app_secret"
)

# 获取多维表格记录
records = api.get_bitable_records(
    app_token="app_token",
    table_id="table_id",
    page_size=100
)

if records:
    print(f"获取到 {len(records.get('items', []))} 条记录")
```

### 示例5：获取工作项操作记录

```python
from feishu_api_wrapper import FeishuAPI

api = FeishuAPI(
    plugin_id="your_plugin_id",
    plugin_secret="your_plugin_secret",
    project_key="your_project_key",
    user_key="your_user_key"
)

# 获取工作项操作记录
records = api.get_work_item_operation_records(
    work_item_ids=["work_item_id_1", "work_item_id_2"]
)

if records:
    print(f"获取到 {len(records.get('operation_records', []))} 条操作记录")
```

---

## Skill集成

### 依赖项

- **requests**：>= 2.25.0（HTTP请求库）
- **json**：Python标准库（JSON处理）
- **typing**：Python标准库（类型提示）

### 配置项

| 配置项 | 类型 | 默认值 | 描述 |
|--------|------|--------|------|
| plugin_id | string | - | 飞书项目插件ID |
| plugin_secret | string | - | 飞书项目插件密钥 |
| project_key | string | None | 空间ID |
| user_key | string | None | 用户密钥 |
| app_id | string | None | 开放平台应用ID |
| app_secret | string | None | 开放平台应用密钥 |
| base_url | string | "https://project.feishu.cn" | 项目API基础URL |
| open_platform_base_url | string | "https://open.feishu.cn" | 开放平台API基础URL |
| timeout | int | 30 | 请求超时时间（秒） |

### 环境要求

- **操作系统**：Windows/Linux/macOS
- **Python版本**：3.7+
- **网络要求**：能够访问飞书API服务器

### 安装步骤

1. 确保已安装Python 3.7+
2. 安装依赖：
   ```bash
   pip install requests
   ```
3. 将`feishu_api_wrapper.py`放在Python路径中
4. 配置认证信息（plugin_id、plugin_secret等）
5. 开始使用

---

## 重要说明

### 必须引用Reference文档

**所有飞书API调用必须参考以下文档**：

- **参考文档位置**：`c:\Users\colin.lin\.cursor\cursor-projects\tools\feishu interaction\reference\`
- **API文档目录**：`api_docs/`
- **快速开始示例**：`quick_start_example.py`
- **Postman示例**：`postman_examples/`

### 调用前必须查阅

1. 对应的API文档（`api_docs/`目录下）
2. 快速开始示例（`quick_start_example.py`）
3. Postman示例（如需要）

### API限制

- **QPS限制**：大部分接口限制15 QPS
- **部分接口特殊限制**：参考`api_docs/Open-API-概述.md`
- **幂等性**：写类型接口支持`X-IDEM-UUID`幂等串

### 认证信息获取

- **plugin_id/plugin_secret**：在飞书项目开放平台插件详情页获取
- **project_key**：双击空间图标获取
- **user_key**：双击用户头像获取
- **app_id/app_secret**：在飞书开放平台应用详情页获取

---

## Skill使用记录

### 使用统计

- **总调用次数**：0
- **成功次数**：0
- **失败次数**：0
- **成功率**：0%

### 使用历史

| 日期 | 调用次数 | 成功率 | 平均响应时间 | 备注 |
|------|---------|--------|------------|------|
| - | - | - | - | - |

### 效果分析

- **优点**：
  - 统一的API封装，使用简单
  - 支持Token自动缓存和刷新
  - 支持飞书项目和开放平台API
  - 完整的错误处理

- **缺点**：
  - 需要配置多个认证信息
  - 部分功能需要额外配置（如webhook）

- **改进建议**：
  - 增加更多API方法
  - 增加重试机制
  - 增加日志记录功能

---

## Skill版本历史

| 版本 | 日期 | 更新内容 | 更新人 |
|------|------|---------|--------|
| v1.0 | 2026-01-13 | 初始版本，支持飞书项目和开放平台API | 系统 |

---

## 关联记录

### 相关注册表

- [能力注册表](../../registry.md)

### 相关Skill定义

- [SKILL-001 飞书API封装工具](feishu-api-wrapper.md)
- [SKILL-002 飞书多维表格今日更新总结](feishu-bitable-daily-summary.md)

### 相关使用记录

- [使用记录](../../usage/usage-history.md)

### 参考文档

- **Reference位置**：`c:\Users\colin.lin\.cursor\cursor-projects\tools\feishu interaction\reference\`
- **API文档**：`api_docs/`
- **示例代码**：`quick_start_example.py`

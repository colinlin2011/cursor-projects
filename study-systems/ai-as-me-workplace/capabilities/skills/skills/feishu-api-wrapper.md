# 飞书API封装工具

**Tool ID**：SKILL-001  
**Tool名称**：飞书API封装工具  
**封装日期**：2026-01-13  
**最后更新**：2026-01-13  
**版本**：v1.0  
**状态**：可用  
**维护人**：系统

---

## 工具描述

### 原始工具
- **工具名称**：飞书Open API
- **工具类型**：RESTful API
- **官方文档**：参考`reference/api_docs/`目录

### 工具功能
封装飞书Open API，提供Python封装接口，支持：
- 飞书消息通讯
- 飞书Wiki云文档操作
- 飞书在线表格操作
- 飞书多维表格操作
- 飞书项目工作项管理
- 飞书项目流程管理

### 适用场景
- 与飞书进行消息通讯
- 管理飞书Wiki云文档
- 操作飞书在线表格和多维表格
- 管理飞书项目工作项和流程

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

---

## 工具封装

### 封装方式
- **封装类型**：Python SDK封装
- **封装文件**：`capabilities/skills/skills/feishu_api_wrapper.py`

### Skill接口定义
- **接口名称**：`FeishuAPI`
- **接口参数**：
  - `plugin_id`：插件ID（必填）
  - `plugin_secret`：插件密钥（必填）
  - `project_key`：空间ID（必填）
  - `user_key`：用户密钥（必填）
- **接口返回值**：API响应结果

---

## 工具使用

### 基本使用
```python
from feishu_api_wrapper import FeishuAPI

# 初始化
api = FeishuAPI(
    plugin_id="your_plugin_id",
    plugin_secret="your_plugin_secret",
    project_key="your_project_key",
    user_key="your_user_key"
)

# 创建工作项
work_item = api.create_work_item(
    work_item_type_key="story",
    fields={"name": "新工作项"}
)

# 查询工作项
work_item = api.query_work_item(
    work_item_type_key="story",
    work_item_id="work_item_id"
)
```

### 使用示例
- **示例1**：创建工作项
  ```python
  api.create_work_item(
      work_item_type_key="story",
      fields={"name": "新工作项", "description": "描述"}
  )
  ```

- **示例2**：查询工作项列表
  ```python
  work_items = api.search_work_items(
      work_item_type_key="story",
      filter_conditions={...}
  )
  ```

---

## 工具集成

### 依赖项
- **requests**：HTTP请求库
- **json**：JSON处理

### 配置项
| 配置项 | 类型 | 默认值 | 描述 |
|--------|------|--------|------|
| plugin_id | string | - | 插件ID |
| plugin_secret | string | - | 插件密钥 |
| project_key | string | - | 空间ID |
| user_key | string | - | 用户密钥 |
| base_url | string | "https://project.feishu.cn" | API基础URL |
| timeout | int | 30 | 请求超时时间（秒） |

### 环境要求
- **Python版本**：3.7+
- **操作系统**：Windows/Linux/macOS

---

## 关联记录

### 相关注册表
- [能力注册表链接](../registry.md)

### 相关Skill定义
- [Skill定义链接](../SKILL-TEMPLATE.md)

### 相关使用记录
- [使用记录链接](../../usage/usage-history.md)

### 参考文档
- **Reference位置**：`c:\Users\colin.lin\.cursor\cursor-projects\tools\feishu interaction\reference\`

---

## 工具版本历史

| 版本 | 日期 | 更新内容 | 更新人 |
|------|------|---------|--------|
| v1.0 | 2026-01-13 | 初始封装 | 系统 |

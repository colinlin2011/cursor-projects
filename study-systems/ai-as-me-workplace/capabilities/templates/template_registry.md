# 业务流程模板注册表

**最后更新**：2026-01-16  
**版本**：v1.0

---

## 模板说明

本注册表管理所有可用的业务流程模板，支持快速复用和定制。

---

## 模板列表

| 模板ID | 模板名称 | 描述 | 版本 | 状态 | 创建日期 |
|--------|---------|------|------|------|---------|
| TEMPLATE-001 | 故障信息查询 | 通过单号查询故障信息的完整工作流 | v1.0.0 | 可用 | 2026-01-16 |
| TEMPLATE-002 | 数据分析工作流 | 从多维表格加载数据并进行分析 | v1.0.0 | 可用 | 2026-01-16 |
| TEMPLATE-003 | 文档生成工作流 | 基于数据生成文档并同步到飞书 | v1.0.0 | 可用 | 2026-01-16 |

---

## 模板详情

### TEMPLATE-001: 故障信息查询

**模板文件**：`workflow_templates/fault_query_workflow.yaml`

**功能描述**：
通过单号（工作项ID、记录ID、问题单号）查询故障信息的完整工作流。

**工作流步骤**：
1. 获取问题单信息（`fault_ticket_monitor.get_ticket_info`）
2. 从多维表格获取数据（`bitable_query.get_table_data`）
3. 查询故障信息（`fault_query.query_by_ticket_id`）

**参数**：
- `ticket_id` (必需): 问题单ID

**使用示例**：
```python
from capabilities.templates.template_engine import TemplateEngine

engine = TemplateEngine()
result = engine.execute_template(
    "fault_query_workflow",
    parameters={"ticket_id": "6683487902"}
)
```

---

### TEMPLATE-002: 数据分析工作流

**模板文件**：`business_processes/data_analysis_workflow.yaml`

**功能描述**：
从多维表格加载数据，进行数据分析，生成分析报告。

**工作流步骤**：
1. 加载多维表格数据（`bitable_cache.load`）
2. 数据查询和分析（`bitable_query.analyze`）
3. 生成分析报告（`report_generator.generate`）

**参数**：
- `table_name` (必需): 表格名称
- `cache_file` (必需): 缓存文件名
- `analysis_type` (可选): 分析类型

**使用示例**：
```python
engine = TemplateEngine()
result = engine.execute_template(
    "data_analysis_workflow",
    parameters={
        "table_name": "功能安全部人力盘点",
        "cache_file": "hr_inventory.json",
        "analysis_type": "summary"
    }
)
```

---

### TEMPLATE-003: 文档生成工作流

**模板文件**：`business_processes/document_generation_workflow.yaml`

**功能描述**：
基于数据生成文档，并同步到飞书Wiki。

**工作流步骤**：
1. 加载数据（`data_loader.load`）
2. 生成文档内容（`doc_generator.generate`）
3. 同步到飞书（`feishu_doc.sync`）

**参数**：
- `data_source` (必需): 数据源
- `doc_template` (必需): 文档模板
- `parent_node` (可选): 父节点Token

**使用示例**：
```python
engine = TemplateEngine()
result = engine.execute_template(
    "document_generation_workflow",
    parameters={
        "data_source": "bitable",
        "doc_template": "fsc_template",
        "parent_node": "GCrNwnjWFiNw1UkLOraclXVynO1"
    }
)
```

---

## 模板创建指南

### 1. 创建模板文件

在 `business_processes/` 目录下创建YAML或JSON文件：

```yaml
workflow:
  name: "模板名称"
  version: "1.0.0"
  description: "模板描述"
  steps:
    - capability: "能力ID"
      action: "动作名称"
      input:
        param1: "{{param1}}"
      output: "output_var"
```

### 2. 注册模板

在本文件中添加模板记录。

### 3. 测试模板

使用 `TemplateEngine` 测试模板执行。

---

## 模板版本管理

- **版本格式**：`主版本.次版本.修订版本`
- **版本更新**：修改模板时更新版本号
- **向后兼容**：尽量保持向后兼容，必要时创建新版本

---

## 模板最佳实践

1. **参数化**：使用 `{{param_name}}` 格式定义参数
2. **错误处理**：在步骤中定义重试和超时
3. **条件执行**：使用 `condition` 字段控制步骤执行
4. **文档化**：为每个模板提供清晰的文档说明

---

## 关联记录

### 相关工作流引擎
- [工作流引擎](../orchestration/workflow_engine.py)
- [工作流定义](../orchestration/workflow_definition.py)

### 相关能力
- [能力注册表](../registry.md)
- [API路由配置](../integration/api-routes.md)

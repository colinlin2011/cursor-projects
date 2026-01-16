# 文档生成工作流模板

## 模板信息

- **模板ID**: TEMPLATE-003
- **模板名称**: 文档生成工作流
- **版本**: v1.0.0
- **创建日期**: 2026-01-16

## 功能描述

基于数据生成文档，并同步到飞书Wiki。

## 工作流步骤

1. **加载数据**
   - 能力: `data_loader`
   - 动作: `load`
   - 输入: `data_source`
   - 输出: `data`

2. **生成文档内容**
   - 能力: `doc_generator`
   - 动作: `generate`
   - 输入: `data`, `doc_template`
   - 输出: `doc_content`

3. **同步到飞书**
   - 能力: `feishu_doc`
   - 动作: `sync`
   - 输入: `doc_content`, `parent_node`
   - 输出: `doc_url`

## 参数说明

| 参数名 | 类型 | 必需 | 描述 | 示例 |
|--------|------|------|------|------|
| data_source | string | 是 | 数据源 | "bitable" |
| doc_template | string | 是 | 文档模板 | "fsc_template" |
| parent_node | string | 否 | 父节点Token | "GCrNwnjWFiNw1UkLOraclXVynO1" |

## 使用示例

```python
from capabilities.templates.template_engine import TemplateEngine

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

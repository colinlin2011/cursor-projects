# 数据分析工作流模板

## 模板信息

- **模板ID**: TEMPLATE-002
- **模板名称**: 数据分析工作流
- **版本**: v1.0.0
- **创建日期**: 2026-01-16

## 功能描述

从多维表格加载数据，进行数据分析，生成分析报告。

## 工作流步骤

1. **加载多维表格数据**
   - 能力: `bitable_cache`
   - 动作: `load`
   - 输入: `table_name`, `cache_file`
   - 输出: `table_data`

2. **数据查询和分析**
   - 能力: `bitable_query`
   - 动作: `analyze`
   - 输入: `table_data`, `analysis_type`
   - 输出: `analysis_result`

3. **生成分析报告**
   - 能力: `report_generator`
   - 动作: `generate`
   - 输入: `analysis_result`
   - 输出: `report`

## 参数说明

| 参数名 | 类型 | 必需 | 描述 | 示例 |
|--------|------|------|------|------|
| table_name | string | 是 | 表格名称 | "功能安全部人力盘点" |
| cache_file | string | 是 | 缓存文件名 | "hr_inventory.json" |
| analysis_type | string | 否 | 分析类型 | "summary" |

## 使用示例

```python
from capabilities.templates.template_engine import TemplateEngine

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

# 通过单号查询故障信息模板

## 模板信息

- **模板ID**: TEMPLATE-001
- **模板名称**: 故障信息查询
- **版本**: v1.0.0
- **创建日期**: 2026-01-16

## 功能描述

通过单号（工作项ID、记录ID、问题单号）查询故障信息的完整工作流。

## 工作流步骤

1. **获取问题单信息**
   - 能力: `fault_ticket_monitor`
   - 动作: `get_ticket_info`
   - 输入: `ticket_id`
   - 输出: `ticket_info`

2. **从多维表格获取数据**
   - 能力: `bitable_query`
   - 动作: `get_table_data`
   - 输入: `table_name`, `cache_file`
   - 输出: `table_data`

3. **查询故障信息**
   - 能力: `fault_query`
   - 动作: `query_by_ticket_id`
   - 输入: `ticket_id`, `include_analysis`
   - 输出: `fault_result`

## 参数说明

| 参数名 | 类型 | 必需 | 描述 | 示例 |
|--------|------|------|------|------|
| ticket_id | string | 是 | 问题单ID | "6683487902" |
| include_analysis | boolean | 否 | 是否包含故障分析 | true |

## 使用示例

### Python调用

```python
from capabilities.templates.template_engine import TemplateEngine

engine = TemplateEngine()
result = engine.execute_template(
    "fault_query_workflow",
    parameters={
        "ticket_id": "6683487902",
        "include_analysis": True
    }
)
```

### AI对话中使用

```
用户: "查询单号6683487902的故障信息"
AI: 调用故障信息查询模板，返回查询结果
```

## 返回结果

```json
{
  "success": true,
  "workflow_name": "故障信息查询",
  "duration": 2.5,
  "context": {
    "variables": {
      "ticket_info": {...},
      "table_data": {...},
      "fault_result": {...}
    },
    "step_results": {...},
    "errors": []
  }
}
```

## 错误处理

- **未找到问题单**: 返回错误信息，不中断流程
- **缓存失效**: 自动刷新缓存
- **数据格式异常**: 记录错误，返回部分结果

## 扩展方向

1. 支持批量查询多个单号
2. 支持历史故障信息查询
3. 支持关联故障信息查询
4. 支持统计分析功能

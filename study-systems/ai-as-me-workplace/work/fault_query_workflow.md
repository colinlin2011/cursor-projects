# 通过单号查询故障信息工作流

## 概述

本工作流实现了通过单号（工作项ID、记录ID、问题单号）查询故障信息的完整链路。

## 工作流步骤

```
单号输入 → 问题单信息获取 → 多维表格查询 → 故障信息提取 → 结果格式化输出
```

### 步骤1: 单号规范化

- **输入**: 原始单号（支持多种格式）
- **处理**: 规范化单号格式
- **支持格式**:
  - 工作项ID：`6683487902`
  - 记录ID：`recv8hWWsiysEn`
  - 包含URL的记录ID：`https://zyt.feishu.cn/wiki/recv8hWWsiysEn`
  - 其他格式：自动提取ID

### 步骤2: 问题单信息获取

- **能力**: `FaultTicketMonitor.get_ticket_info()`
- **数据源**: 多维表格缓存（`DEFECT_TABLE_CACHE_FILE`）
- **输出**: 
  - `record_id`: 记录ID
  - `work_item_id`: 工作项ID
  - `fields`: 问题单字段数据

### 步骤3: 多维表格查询

- **能力**: `BitableQueryInterface.get_table_data()`
- **数据源**: 多维表格缓存
- **查询条件**: 根据记录ID或工作项ID匹配
- **输出**: 完整的缺陷记录

### 步骤4: 关键信息提取

- **提取字段**:
  - 工作项id
  - 问题描述
  - 问题状态
  - 优先级
  - 创建时间
  - 更新时间
  - 负责人
  - 工具回传

### 步骤5: 故障分析（可选）

- **能力**: `FaultQueryByTicket._analyze_fault()`
- **分析内容**:
  - 问题摘要
  - 状态分析
  - 优先级分析
  - 处理建议

### 步骤6: 结果格式化

- **格式**: 结构化的文本输出
- **包含内容**:
  - 单号信息
  - 问题单基本信息
  - 关键信息
  - 故障分析（如果启用）

## 使用方法

### Python调用

```python
from fault_query_by_ticket import FaultQueryByTicket

# 创建查询器
query = FaultQueryByTicket()

# 基本查询
result = query.query_by_ticket_id("6683487902")

# 包含分析的查询
result = query.query_by_ticket_id("6683487902", include_analysis=True)

# 格式化输出
formatted = query.format_result(result)
print(formatted)
```

### 命令行调用

```bash
# 基本查询
python fault_query_by_ticket.py 6683487902

# 包含分析的查询
python fault_query_by_ticket.py 6683487902 --analysis
```

### AI对话中使用

```
用户: "查询单号6683487902的故障信息"
AI: 调用 fault_query_by_ticket 能力，返回格式化结果
```

## 返回结果格式

```json
{
  "ticket_id": "6683487902",
  "normalized_id": "6683487902",
  "success": true,
  "data": {
    "ticket_info": {
      "record_id": "recv8hWWsiysEn",
      "work_item_id": "6683487902",
      "fields": {...}
    },
    "defect_data": {
      "record_id": "recv8hWWsiysEn",
      "fields": {...}
    },
    "key_info": {
      "record_id": "recv8hWWsiysEn",
      "work_item_id": "6683487902",
      "fields": {
        "工作项id": "6683487902",
        "问题描述": "...",
        "问题状态": "待处理",
        ...
      }
    },
    "fault_analysis": {
      "summary": "...",
      "status": "待处理",
      "priority": "高",
      "recommendations": [...]
    }
  },
  "error": null
}
```

## 依赖能力

1. **FaultTicketMonitor**: 问题单监控能力
2. **BitableQueryInterface**: 多维表格查询能力
3. **缓存系统**: 统一缓存管理框架

## 错误处理

- **未找到问题单**: 返回错误信息，不中断流程
- **缓存失效**: 自动刷新缓存
- **数据格式异常**: 记录错误，返回部分结果

## 性能优化

- 使用缓存避免频繁API调用
- 支持批量查询（未来扩展）
- 异步处理（未来扩展）

## 扩展方向

1. **批量查询**: 支持一次查询多个单号
2. **历史查询**: 查询历史故障信息
3. **关联查询**: 查询关联的故障信息
4. **统计分析**: 基于查询结果进行统计分析

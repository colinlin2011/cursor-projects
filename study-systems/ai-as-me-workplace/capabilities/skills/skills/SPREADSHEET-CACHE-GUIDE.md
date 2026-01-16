# 在线表格缓存系统使用指南

## 概述

在线表格缓存系统提供了以下功能：

1. **自动缓存**: 自动从飞书API加载在线表格数据并缓存到本地
2. **定期同步**: 支持自动定期同步在线表格的变更内容
3. **自然语言查询**: 基于缓存数据提供便捷的查询接口
4. **多表格支持**: 支持同时管理多个在线表格

## 系统架构

```
spreadsheet_cache_manager.py    # 缓存管理器（核心）
├── 加载和缓存在线表格数据
├── 管理多个在线表格配置
├── 自动检测缓存过期
└── 处理工作表数据

spreadsheet_query_interface.py # 查询接口
├── 基于缓存数据的查询API
├── 工作表数据查询
├── 工作表内搜索
└── 行数据查询

auto_sync_spreadsheet.py        # 自动同步服务
├── 定时同步任务
└── 一次性同步
```

## 快速开始

### 1. 初始同步

首次使用需要同步所有在线表格数据：

```bash
python spreadsheet_cache_manager.py
```

这会：
- 从API加载所有配置的在线表格数据
- 处理所有工作表的数据
- 保存到 `work/spreadsheet_cache/` 目录

### 2. 查询数据

在Python代码中使用查询接口：

```python
from spreadsheet_query_interface import get_query_interface

# 获取查询接口
interface = get_query_interface()

# 获取工作表数据
sheet = interface.get_sheet_data("System SW FMEA")
if sheet:
    print(f"工作表: {sheet['title']}")
    print(f"行数: {sheet['row_count']}")
    print(f"表头: {sheet['headers']}")

# 在工作表中搜索
results = interface.search_in_sheet("System SW FMEA", "FMEA")
for row in results:
    print(row)
```

### 3. 自动同步

#### 方式一：定时同步服务

启动自动同步服务（每小时同步一次）：

```bash
python auto_sync_spreadsheet.py
```

#### 方式二：一次性同步

只执行一次同步：

```bash
python auto_sync_spreadsheet.py --once
```

#### 方式三：自定义同步间隔

设置同步间隔（例如每2小时）：

```bash
python auto_sync_spreadsheet.py --interval 2
```

## 配置在线表格

在 `spreadsheet_cache_manager.py` 中配置要缓存的在线表格：

```python
SPREADSHEET_CONFIGS = [
    {
        "name": "在线表格示例",
        "node_token": "TDlnwRfpBikbUIk5guDcRyN5neh",
        "url": "https://zyt.feishu.cn/wiki/TDlnwRfpBikbUIk5guDcRyN5neh",
        "cache_file": "spreadsheet_example.json"
    }
]
```

## 缓存文件结构

缓存文件保存在 `work/spreadsheet_cache/` 目录：

```
work/spreadsheet_cache/
├── cache_config.json              # 缓存配置（同步时间、spreadsheet_token等）
└── spreadsheet_example.json        # 在线表格缓存
```

每个缓存文件包含：

```json
{
  "cache_time": 1768450979.5731914,
  "sync_interval": 3600,
  "node_token": "TDlnwRfpBikbUIk5guDcRyN5neh",
  "spreadsheet_token": "NI2ksibZHhzVoBtg65Fc3Jdznnf",
  "space_id": "7353073903872868356",
  "sheets": {
    "System SW FMEA": {
      "sheet_id": "4xjxsi",
      "title": "System SW FMEA",
      "headers": ["列1", "列2", ...],
      "rows": [[...], [...], ...],
      "row_count": 134,
      "column_count": 12
    }
  },
  "analysis": {...}
}
```

## API参考

### SpreadsheetQueryInterface

#### get_sheet_data(sheet_name, cache_file=None)

获取工作表数据。

**参数**:
- `sheet_name`: 工作表名称
- `cache_file`: 缓存文件名（可选，如果为None会在所有缓存中搜索）

**返回**: 工作表数据字典，包含 `sheet_id`, `title`, `headers`, `rows`, `row_count`, `column_count`

#### search_in_sheet(sheet_name, search_text, cache_file=None)

在工作表中搜索包含指定文本的行。

**参数**:
- `sheet_name`: 工作表名称
- `search_text`: 搜索文本
- `cache_file`: 缓存文件名（可选）

**返回**: 匹配的行列表（每行是一个字典）

#### get_row_by_index(sheet_name, row_index, cache_file=None)

根据行索引获取行数据。

**参数**:
- `sheet_name`: 工作表名称
- `row_index`: 行索引（0-based，不包括表头）
- `cache_file`: 缓存文件名（可选）

**返回**: 行数据字典

#### get_all_sheets(cache_file=None)

获取所有工作表名称列表。

**参数**:
- `cache_file`: 缓存文件名（可选）

**返回**: 工作表名称列表

#### get_cache_summary()

获取缓存数据摘要。

**返回**: 缓存摘要信息字典

## 在AI对话中使用

现在你可以在对话中直接询问基于在线表格数据的问题，AI会自动从缓存中读取数据并回答：

**示例问题**:
- "System SW FMEA工作表有多少行数据？"
- "在System SW FMEA工作表中搜索包含'FMEA'的行"
- "列出所有工作表的名称"
- "System SW FMEA工作表的第一行数据是什么？"

AI会自动：
1. 从缓存中读取数据（如果缓存过期会自动同步）
2. 基于数据回答问题
3. 提供详细的分析和总结

## 注意事项

1. **缓存过期**: 默认缓存1小时后过期，过期后会自动从API刷新
2. **权限要求**: 需要确保 `user_access_token` 有访问在线表格的权限
3. **网络连接**: 同步时需要能够访问飞书API
4. **数据量**: 如果数据量很大，首次同步可能需要一些时间
5. **工作表名称**: 查询时需要使用准确的工作表名称（区分大小写）

## 故障排查

### 问题：无法获取spreadsheet_token

**可能原因**:
- `space_id` 不正确
- `node_token` 不正确
- 节点类型不是sheet
- 没有访问权限

**解决方法**:
- 检查 `SPREADSHEET_CONFIGS` 中的配置
- 确认 `user_access_token` 有相应权限

### 问题：缓存文件不存在

**解决方法**:
- 运行 `python spreadsheet_cache_manager.py` 进行初始同步

### 问题：数据不是最新的

**解决方法**:
- 运行 `python auto_sync_spreadsheet.py --once` 强制同步
- 或等待自动同步服务刷新

### 问题：工作表数据为空

**可能原因**:
- 工作表确实没有数据
- API返回格式解析错误

**解决方法**:
- 检查工作表是否真的有数据
- 查看API返回的原始数据格式

## 扩展

### 添加新的在线表格

1. 在 `SPREADSHEET_CONFIGS` 中添加配置
2. 运行 `python spreadsheet_cache_manager.py` 同步数据

### 自定义查询

在 `SpreadsheetQueryInterface` 中添加新的查询方法。

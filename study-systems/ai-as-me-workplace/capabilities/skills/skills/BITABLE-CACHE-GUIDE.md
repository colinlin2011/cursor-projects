# 多维表格缓存系统使用指南

## 概述

多维表格缓存系统提供了以下功能：

1. **自动缓存**: 自动从飞书API加载多维表格数据并缓存到本地
2. **定期同步**: 支持自动定期同步多维表格的变更内容
3. **自然语言查询**: 基于缓存数据提供便捷的查询接口
4. **多表格支持**: 支持同时管理多个多维表格

## 系统架构

```
bitable_cache_manager.py    # 缓存管理器（核心）
├── 加载和缓存多维表格数据
├── 管理多个多维表格配置
├── 自动检测缓存过期
└── 建立索引（人员、工作包、投入分配等）

bitable_query_interface.py # 查询接口
├── 基于缓存数据的查询API
├── 人员信息查询
├── 工作包信息查询
└── 字段搜索

auto_sync_bitable.py        # 自动同步服务
├── 定时同步任务
└── 一次性同步
```

## 快速开始

### 1. 初始同步

首次使用需要同步所有多维表格数据：

```bash
python bitable_cache_manager.py
```

这会：
- 从API加载所有配置的多维表格数据
- 建立索引（人员、工作包、投入分配等）
- 保存到 `work/bitable_cache/` 目录

### 2. 查询数据

在Python代码中使用查询接口：

```python
from bitable_query_interface import get_query_interface

# 获取查询接口
interface = get_query_interface()

# 查询人员信息
person = interface.get_person_info("林广义")
if person:
    print(f"姓名: {person['fields']['姓名']}")
    print(f"所属小组: {person['fields']['所属小组']}")
    print(f"实际投入: {person['fields']['实际投入']}")

# 查询人员投入分配
allocations = interface.get_person_allocations("林广义")
for alloc in allocations:
    print(f"工作包: {alloc['fields']['工作包']}")
    print(f"全年投入: {alloc['fields']['全年总投入']}")

# 查询工作包信息
wp = interface.get_work_package_info("WP_001")
if wp:
    print(f"工作包: {wp['fields']['工作包']}")
    print(f"人力总需求: {wp['fields']['人力总需求']}")
```

### 3. 自动同步

#### 方式一：定时同步服务

启动自动同步服务（每小时同步一次）：

```bash
python auto_sync_bitable.py
```

#### 方式二：一次性同步

只执行一次同步：

```bash
python auto_sync_bitable.py --once
```

#### 方式三：自定义同步间隔

设置同步间隔（例如每2小时）：

```bash
python auto_sync_bitable.py --interval 2
```

## 配置多维表格

在 `bitable_cache_manager.py` 中配置要缓存的多维表格：

```python
BITABLE_CONFIGS = [
    {
        "name": "功能安全部人力盘点",
        "node_token": "CGMnwhxzLixWhGk87jYcDRfonsh",
        "url": "https://zyt.feishu.cn/wiki/CGMnwhxzLixWhGk87jYcDRfonsh",
        "cache_file": "hr_inventory.json"
    },
    {
        "name": "新多维表格",
        "node_token": "BPddwBxoRiPFSsk8jZJctCMmndg",
        "url": "https://zyt.feishu.cn/wiki/BPddwBxoRiPFSsk8jZJctCMmndg",
        "cache_file": "new_bitable.json"
    }
]
```

## 缓存文件结构

缓存文件保存在 `work/bitable_cache/` 目录：

```
work/bitable_cache/
├── cache_config.json          # 缓存配置（同步时间、app_token等）
├── hr_inventory.json          # 功能安全部人力盘点缓存
└── new_bitable.json           # 新多维表格缓存
```

每个缓存文件包含：

```json
{
  "cache_time": 1768450979.5731914,
  "sync_interval": 3600,
  "node_token": "CGMnwhxzLixWhGk87jYcDRfonsh",
  "app_token": "EDy2bwLFZao1g2svU1wcgwvznFe",
  "space_id": "7353073903872868356",
  "tables": {
    "业务规划表_做什么": {
      "table_id": "...",
      "fields": [...],
      "records": [...],
      "record_count": 84
    }
  },
  "indexes": {
    "people": {...},
    "work_packages": {...},
    "allocations": {...},
    "by_field": {...}
  }
}
```

## API参考

### BitableQueryInterface

#### get_person_info(person_name, cache_file=None)

查询人员信息。

**参数**:
- `person_name`: 人员姓名
- `cache_file`: 缓存文件名（可选，如果为None会在所有缓存中搜索）

**返回**: 人员信息字典，包含 `record_id` 和 `fields`

#### get_person_allocations(person_name, cache_file=None)

查询人员的投入分配。

**参数**:
- `person_name`: 人员姓名
- `cache_file`: 缓存文件名（可选）

**返回**: 投入分配记录列表

#### get_work_package_info(task_id, cache_file=None)

查询工作包信息。

**参数**:
- `task_id`: 任务ID（如WP_001）
- `cache_file`: 缓存文件名（可选）

**返回**: 工作包信息字典

#### search_by_field(field_name, field_value, cache_file=None)

按字段值搜索记录。

**参数**:
- `field_name`: 字段名
- `field_value`: 字段值
- `cache_file`: 缓存文件名（可选）

**返回**: 匹配的记录列表

#### get_table_data(table_name, cache_file=None)

获取整个数据表的数据。

**参数**:
- `table_name`: 数据表名称
- `cache_file`: 缓存文件名（可选）

**返回**: 数据表信息字典

#### get_all_people(cache_file=None)

获取所有人员姓名列表。

**参数**:
- `cache_file`: 缓存文件名（可选）

**返回**: 人员姓名列表

#### get_cache_summary()

获取缓存数据摘要。

**返回**: 缓存摘要信息字典

## 在AI对话中使用

现在你可以在对话中直接询问基于多维表格数据的问题，AI会自动从缓存中读取数据并回答：

**示例问题**:
- "林广义的人力盘点情况是怎样的？"
- "哪些人员参与了WP_001工作包？"
- "系统组有哪些人员？"
- "管理带宽相关的工作包有哪些？"

AI会自动：
1. 从缓存中读取数据（如果缓存过期会自动同步）
2. 基于数据回答问题
3. 提供详细的分析和总结

## 注意事项

1. **缓存过期**: 默认缓存1小时后过期，过期后会自动从API刷新
2. **权限要求**: 需要确保 `user_access_token` 有访问多维表格的权限
3. **网络连接**: 同步时需要能够访问飞书API
4. **数据量**: 如果数据量很大，首次同步可能需要一些时间

## 故障排查

### 问题：无法获取app_token

**可能原因**:
- `space_id` 不正确
- `node_token` 不正确
- 节点类型不是bitable
- 没有访问权限

**解决方法**:
- 检查 `BITABLE_CONFIGS` 中的配置
- 确认 `user_access_token` 有相应权限

### 问题：缓存文件不存在

**解决方法**:
- 运行 `python bitable_cache_manager.py` 进行初始同步

### 问题：数据不是最新的

**解决方法**:
- 运行 `python auto_sync_bitable.py --once` 强制同步
- 或等待自动同步服务刷新

## 扩展

### 添加新的多维表格

1. 在 `BITABLE_CONFIGS` 中添加配置
2. 运行 `python bitable_cache_manager.py` 同步数据

### 自定义索引

在 `_build_indexes` 方法中添加自定义索引逻辑。

### 自定义查询

在 `BitableQueryInterface` 中添加新的查询方法。

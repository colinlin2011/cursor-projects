# 快速开始 - 飞书多维表格协作

## 最简单的使用方式

### 方式1：使用Python API

```python
from feishu_bitable_collaborator import create_bitable_collaborator

# 创建协作器
collaborator = create_bitable_collaborator(
    app_id="cli_a9c92ca516f99bd9",
    app_secret="your_secret",
    user_access_token="your_token"
)

# 从多维表格URL中提取app_token和table_id
# 例如：https://bitable.feishu.cn/app/xxxxxxxxxx/table/xxxxxxxxxx
app_token = "your_app_token"
table_id = "your_table_id"

# 1. 获取表格结构
structure = collaborator.get_table_structure(app_token, table_id)
print(f"字段数量: {len(structure['fields'])}")

# 2. 分析数据表
analysis = collaborator.analyze_table(app_token, table_id)
print(f"总记录数: {analysis['statistics']['total_records']}")

# 3. 生成数据表总结
summary = collaborator.summarize_table(app_token, table_id)
print(summary)
```

## 典型使用场景

### 场景1：快速了解数据表

```python
collaborator = create_bitable_collaborator(...)

# 获取表格结构
structure = collaborator.get_table_structure(app_token, table_id)

# 查看字段
for field in structure['fields']:
    print(f"{field['field_name']}: {field['type']}")
```

### 场景2：数据分析和洞察

```python
# 分析数据表
analysis = collaborator.analyze_table(app_token, table_id)

# 查看统计信息
stats = analysis['statistics']
print(f"总记录数: {stats['total_records']}")
print(f"总字段数: {stats['total_fields']}")

# 查看数据洞察
for insight in analysis['insights']:
    print(f"{insight['title']}: {insight['content']}")
```

### 场景3：生成数据报告

```python
# 生成完整的数据表总结
summary = collaborator.summarize_table(
    app_token,
    table_id,
    include_structure=True,
    include_statistics=True,
    include_insights=True
)

# 保存到文件
with open('table_summary.md', 'w', encoding='utf-8') as f:
    f.write(summary)
```

### 场景4：数据操作

```python
# 创建记录
record = collaborator.create_record(
    app_token,
    table_id,
    fields={
        "字段名1": "值1",
        "字段名2": "值2"
    }
)

# 获取所有记录
records = collaborator.get_all_records(app_token, table_id)

# 更新记录
if records:
    record_id = records[0]['record_id']
    collaborator.update_record(
        app_token,
        table_id,
        record_id,
        fields={"字段名1": "新值"}
    )
```

## 获取app_token和table_id

### 方法1：从URL提取

多维表格URL格式：`https://bitable.feishu.cn/app/{app_token}/table/{table_id}`

例如：
- URL: `https://bitable.feishu.cn/app/xxxxxxxxxx/table/yyyyyyyyyy`
- app_token: `xxxxxxxxxx`
- table_id: `yyyyyyyyyy`

### 方法2：通过API获取

```python
# 列出所有数据表
tables = collaborator.list_tables(app_token)
for table in tables:
    print(f"表名: {table['name']}, ID: {table['table_id']}")
```

## 配置

### 环境变量

```bash
# 设置用户身份凭证
$env:FEISHU_USER_ACCESS_TOKEN="your_token"
```

### 默认配置

脚本使用以下默认配置（可在代码中修改）：

- APP_ID: `cli_a9c92ca516f99bd9`

## 数据洞察示例

协作器会自动生成以下类型的数据洞察：

### 完整性分析
- ⚠️ **字段"状态"完整性较低**：该字段的填充率为45.2%，建议检查数据质量

### 值分布分析
- ℹ️ **字段"类型"值分布集中**：最常见的值为"任务"，占比82.5%

### 数据量分析
- ℹ️ **数据量较大**：当前数据表包含1250条记录，建议考虑数据归档或分表

## 更多信息

- 完整API文档：`BITABLE-COLLABORATOR-GUIDE.md`
- 使用示例：`bitable_collaborator_example.py`

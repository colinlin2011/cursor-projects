# 飞书多维表格协作器使用指南

## 概述

`FeishuBitableCollaborator` 是一个通用的飞书多维表格协作能力包，提供了简洁的API接口，支持：

- ✅ 获取多维表格信息
- ✅ 数据表的CRUD操作（创建、读取、更新、删除）
- ✅ 获取表格结构（字段、视图等）
- ✅ 数据分析和总结
- ✅ 导出为Markdown格式

## 快速开始

### 1. 创建协作器实例

```python
from feishu_bitable_collaborator import create_bitable_collaborator

collaborator = create_bitable_collaborator(
    app_id="your_app_id",
    app_secret="your_app_secret",
    user_access_token="your_user_access_token"
)
```

### 2. 获取表格结构

```python
# 从多维表格URL中提取app_token和table_id
# 例如：https://bitable.feishu.cn/app/xxxxxxxxxx/table/xxxxxxxxxx
app_token = "your_app_token"
table_id = "your_table_id"

# 获取表格结构
structure = collaborator.get_table_structure(app_token, table_id)

print(f"字段数量: {len(structure['fields'])}")
print(f"视图数量: {len(structure['views'])}")
```

### 3. 分析数据表

```python
# 分析数据表，获取统计信息和洞察
analysis = collaborator.analyze_table(app_token, table_id)

print(f"总记录数: {analysis['statistics']['total_records']}")
print(f"总字段数: {analysis['statistics']['total_fields']}")

# 查看数据洞察
for insight in analysis['insights']:
    print(f"- {insight['title']}: {insight['content']}")
```

### 4. 生成数据表总结

```python
# 生成完整的数据表总结报告
summary = collaborator.summarize_table(
    app_token,
    table_id,
    include_structure=True,
    include_statistics=True,
    include_insights=True
)

print(summary)
```

## API参考

### FeishuBitableCollaborator类

#### 初始化

```python
collaborator = FeishuBitableCollaborator(
    app_id: str,
    app_secret: str,
    user_access_token: Optional[str] = None,
    tenant_access_token: Optional[str] = None
)
```

#### 主要方法

##### get_table_structure()

获取数据表结构（字段、视图等）

```python
structure = collaborator.get_table_structure(
    app_token: str,
    table_id: str
) -> Dict[str, Any]
```

**返回**：
```python
{
    'table_id': '数据表ID',
    'fields': [字段列表],
    'views': [视图列表]
}
```

##### get_all_records()

获取所有记录（自动分页）

```python
records = collaborator.get_all_records(
    app_token: str,
    table_id: str,
    page_size: int = 500
) -> List[Dict]
```

##### analyze_table()

分析数据表，提供统计信息和洞察

```python
analysis = collaborator.analyze_table(
    app_token: str,
    table_id: str
) -> Dict[str, Any]
```

**返回**：
```python
{
    'structure': {...},      # 表格结构
    'statistics': {...},     # 统计信息
    'insights': [...]        # 数据洞察
}
```

##### summarize_table()

生成数据表总结报告

```python
summary = collaborator.summarize_table(
    app_token: str,
    table_id: str,
    include_structure: bool = True,
    include_statistics: bool = True,
    include_insights: bool = True
) -> str
```

##### create_record()

创建记录

```python
record = collaborator.create_record(
    app_token: str,
    table_id: str,
    fields: Dict[str, Any]
) -> Optional[Dict]
```

##### update_record()

更新记录

```python
record = collaborator.update_record(
    app_token: str,
    table_id: str,
    record_id: str,
    fields: Dict[str, Any]
) -> Optional[Dict]
```

##### delete_record()

删除记录

```python
success = collaborator.delete_record(
    app_token: str,
    table_id: str,
    record_id: str
) -> bool
```

##### export_to_markdown()

将数据表导出为Markdown格式

```python
md_content = collaborator.export_to_markdown(
    app_token: str,
    table_id: str,
    output_file: Optional[str] = None
) -> str
```

## 使用场景

### 场景1：快速了解数据表结构

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
print(f"总记录数: {analysis['statistics']['total_records']}")
print(f"字段类型分布: {analysis['statistics']['field_types']}")

# 查看数据洞察
for insight in analysis['insights']:
    print(f"{insight['type']}: {insight['title']}")
    print(f"  {insight['content']}")
```

### 场景3：生成数据报告

```python
# 生成完整的数据表总结
summary = collaborator.summarize_table(app_token, table_id)

# 保存到文件
with open('table_summary.md', 'w', encoding='utf-8') as f:
    f.write(summary)
```

### 场景4：批量数据操作

```python
# 获取所有记录
records = collaborator.get_all_records(app_token, table_id)

# 处理数据
for record in records:
    record_id = record['record_id']
    fields = record['fields']
    
    # 更新记录
    collaborator.update_record(
        app_token,
        table_id,
        record_id,
        fields={'新字段': '新值'}
    )
```

### 场景5：数据导出

```python
# 导出为Markdown
md_content = collaborator.export_to_markdown(
    app_token,
    table_id,
    output_file="work/table_export.md"
)
```

## 数据洞察类型

协作器会自动生成以下类型的数据洞察：

### 完整性分析
- 检测字段填充率，识别数据质量较低的字段
- 提示：填充率低于50%的字段会生成警告

### 值分布分析
- 分析字段值的分布情况
- 提示：值过于集中的字段会生成信息提示

### 数据量分析
- 分析数据表的数据量
- 提示：数据量过大或过小会生成相应建议

## 权限要求

- `bitable:app:readonly` - 查看、评论和导出多维表格
- `bitable:app` - 查看、评论、编辑和管理多维表格

## 注意事项

1. **app_token获取**：从多维表格URL中提取，格式：`https://bitable.feishu.cn/app/{app_token}/table/{table_id}`
2. **table_id获取**：同样从URL中提取，或通过`list_tables()`方法获取
3. **分页处理**：`get_all_records()`会自动处理分页，无需手动管理
4. **字段类型**：不同字段类型的数据格式不同，需要注意处理
5. **API限制**：注意飞书API的QPS限制和频率限制

## 相关文件

- **核心类**：`feishu_bitable_collaborator.py`
- **使用示例**：`bitable_collaborator_example.py`
- **API封装**：`feishu_api_wrapper.py`

## 优势

1. **简洁API**：只需几行代码即可完成复杂操作
2. **自动分析**：自动生成数据洞察和统计信息
3. **完整功能**：支持CRUD、分析、导出等完整功能
4. **易于扩展**：基于类的设计，易于扩展和定制

# 飞书交互能力使用指南

## 概述

本指南介绍如何在AI as me工作协作平台中使用飞书交互能力，包括即时通讯、Wiki云文档、在线表格、多维表格和飞书项目的完整集成方案。

---

## 快速开始

### 1. 准备工作

#### 1.1 获取飞书项目API认证信息

1. **创建飞书项目插件**：
   - 访问飞书项目开放平台
   - 创建插件，获取`plugin_id`和`plugin_secret`
   - 在插件详情页授权接口

2. **获取空间和用户信息**：
   - `project_key`：双击空间图标获取
   - `user_key`：双击用户头像获取

#### 1.2 获取飞书开放平台API认证信息（可选）

如果需要使用即时通讯、Wiki、表格等功能：

1. **创建飞书开放平台应用**：
   - 访问飞书开放平台
   - 创建企业自建应用
   - 获取`app_id`和`app_secret`

2. **配置应用权限**：
   - 消息与群组：发送消息、接收消息
   - 云文档：查看、编辑、管理云文档
   - 多维表格：查看、编辑多维表格
   - 电子表格：查看、编辑电子表格

### 2. 初始化API客户端

```python
from feishu_api_wrapper import FeishuAPI

# 仅使用飞书项目API
api = FeishuAPI(
    plugin_id="your_plugin_id",
    plugin_secret="your_plugin_secret",
    project_key="your_project_key",
    user_key="your_user_key"
)

# 使用完整功能（包括开放平台API）
api = FeishuAPI(
    plugin_id="your_plugin_id",
    plugin_secret="your_plugin_secret",
    project_key="your_project_key",
    user_key="your_user_key",
    app_id="your_app_id",
    app_secret="your_app_secret"
)
```

---

## 功能模块使用指南

### 模块1：即时通讯

#### 发送文本消息

```python
result = api.send_message(
    receive_id="user_open_id",  # 或群ID
    receive_id_type="open_id",  # open_id/user_id/chat_id
    msg_type="text",
    content={
        "text": "这是一条测试消息"
    }
)
```

#### 发送富文本消息

```python
result = api.send_message(
    receive_id="user_open_id",
    receive_id_type="open_id",
    msg_type="post",
    content={
        "post": {
            "zh_cn": {
                "title": "标题",
                "content": [
                    [
                        {
                            "tag": "text",
                            "text": "消息内容"
                        }
                    ]
                ]
            }
        }
    }
)
```

#### 注意事项

- 需要配置飞书开放平台应用权限
- 需要获取接收者的open_id或user_id
- 消息类型参考飞书开放平台文档

---

### 模块2：Wiki云文档

#### 创建Wiki文档

```python
doc = api.create_wiki_doc(
    space_id="knowledge_space_id",
    parent_node_token="parent_token",  # 可选
    title="新文档标题"
)

if doc:
    file_token = doc.get('token')
    print(f"文档创建成功: {file_token}")
```

#### 获取Wiki文档

```python
doc = api.get_wiki_doc(
    file_token="file_token"
)

if doc:
    print(f"文档标题: {doc.get('name')}")
```

#### 注意事项

- 需要配置云文档权限
- 需要获取知识库ID（space_id）
- 文档内容编辑需要使用其他API（参考飞书开放平台文档）

---

### 模块3：在线表格

#### 创建在线表格

```python
spreadsheet = api.create_spreadsheet(
    name="新表格",
    folder_token="folder_token"  # 可选
)

if spreadsheet:
    spreadsheet_token = spreadsheet.get('token')
    print(f"表格创建成功: {spreadsheet_token}")
```

#### 更新单元格

```python
result = api.update_spreadsheet_cell(
    spreadsheet_token="spreadsheet_token",
    range="A1:B2",
    values=[
        ["列1", "列2"],
        ["值1", "值2"]
    ]
)
```

#### 获取表格信息

```python
spreadsheet = api.get_spreadsheet(
    spreadsheet_token="spreadsheet_token"
)
```

#### 注意事项

- 需要配置电子表格权限
- 单元格范围格式：如"A1:B2"
- 值必须是二维数组

---

### 模块4：多维表格

#### 创建多维表格

```python
bitable = api.create_bitable(
    name="新多维表格",
    folder_token="folder_token"  # 可选
)

if bitable:
    app_token = bitable.get('app_token')
    print(f"多维表格创建成功: {app_token}")
```

#### 获取记录

```python
records = api.get_bitable_records(
    app_token="app_token",
    table_id="table_id",
    page_size=100,
    page_token=None  # 可选，用于分页
)

if records:
    items = records.get('items', [])
    print(f"获取到 {len(items)} 条记录")
    # 处理下一页
    if records.get('has_more'):
        next_page_token = records.get('page_token')
```

#### 创建记录

```python
record = api.create_bitable_record(
    app_token="app_token",
    table_id="table_id",
    fields={
        "字段名1": "值1",
        "字段名2": "值2"
    }
)

if record:
    print(f"记录创建成功: {record.get('record_id')}")
```

#### 注意事项

- 需要配置多维表格权限
- 需要获取app_token和table_id
- 字段值格式需要符合字段类型要求

---

### 模块5：飞书项目

#### 创建工作项

```python
work_item = api.create_work_item(
    work_item_type_key="story",  # 工作项类型
    fields={
        "name": "新功能需求",
        "description": "功能描述",
        "priority": "high"
    },
    project_key="project_key"  # 可选，默认使用初始化时的project_key
)

if work_item:
    work_item_id = work_item.get('work_item_id')
    print(f"工作项创建成功: {work_item_id}")
```

#### 更新工作项

```python
result = api.update_work_item(
    work_item_type_key="story",
    work_item_id="work_item_id",
    update_fields=[
        {
            "field_key": "name",
            "field_value": "更新后的标题"
        },
        {
            "field_key": "status",
            "field_value": "in_progress"
        }
    ]
)
```

#### 查询工作项

```python
work_item = api.query_work_item(
    work_item_type_key="story",
    work_item_id="work_item_id"
)

if work_item:
    print(f"工作项标题: {work_item.get('fields', {}).get('name')}")
```

#### 搜索工作项

```python
work_items = api.search_work_items(
    work_item_type_key="story",
    filter_conditions={
        "field_key": "status",
        "operator": "equal",
        "field_value": "open"
    }
)

if work_items:
    items = work_items.get('work_items', [])
    print(f"找到 {len(items)} 个工作项")
```

#### 获取工作项操作记录

```python
records = api.get_work_item_operation_records(
    work_item_ids=["work_item_id_1", "work_item_id_2"]
)

if records:
    operation_records = records.get('operation_records', [])
    for record in operation_records:
        print(f"操作类型: {record.get('operation_type')}")
        print(f"操作时间: {record.get('operation_time')}")
```

#### 获取工作流详情

```python
workflow = api.get_workflow(
    work_item_type_key="story",
    work_item_id="work_item_id"
)

if workflow:
    nodes = workflow.get('nodes', [])
    print(f"工作流有 {len(nodes)} 个节点")
```

#### 更新节点

```python
result = api.update_node(
    work_item_type_key="story",
    work_item_id="work_item_id",
    node_id="node_id",
    update_fields=[
        {
            "field_key": "assignee",
            "field_value": "user_key"
        }
    ]
)
```

#### 获取视图列表

```python
views = api.get_views(
    project_key="project_key"  # 可选
)

if views:
    view_list = views.get('views', [])
    for view in view_list:
        print(f"视图名称: {view.get('name')}, ID: {view.get('view_id')}")
```

#### 获取视图下工作项

```python
view_items = api.get_view_items(
    view_id="view_id",
    project_key="project_key"  # 可选
)

if view_items:
    items = view_items.get('work_items', [])
    print(f"视图下有 {len(items)} 个工作项")
```

#### 注意事项

- **必须参考reference文档**：所有API调用前必须查阅`api_docs/`目录下的对应文档
- **QPS限制**：大部分接口限制15 QPS
- **字段格式**：字段key和value格式需要参考API文档
- **工作项类型**：需要先了解空间中的工作项类型key

---

## 最佳实践

### 1. 错误处理

```python
def safe_api_call(api_func, *args, **kwargs):
    """安全的API调用包装器"""
    try:
        result = api_func(*args, **kwargs)
        if result:
            return result
        else:
            print(f"API调用失败: {api_func.__name__}")
            return None
    except Exception as e:
        print(f"API调用异常: {e}")
        return None

# 使用示例
work_item = safe_api_call(
    api.create_work_item,
    work_item_type_key="story",
    fields={"name": "新工作项"}
)
```

### 2. Token管理

API封装工具已经实现了Token自动缓存和刷新，无需手动管理。但如果需要强制刷新：

```python
# 强制刷新plugin_token
api.get_plugin_token(force_refresh=True)

# 强制刷新app_access_token
api.get_app_access_token(force_refresh=True)
```

### 3. 批量操作

对于需要批量操作的场景，注意QPS限制：

```python
import time

def batch_create_work_items(api, work_items_data):
    """批量创建工作项（考虑QPS限制）"""
    results = []
    for item_data in work_items_data:
        result = api.create_work_item(
            work_item_type_key=item_data['type'],
            fields=item_data['fields']
        )
        results.append(result)
        # 控制请求频率（15 QPS = 每66ms一个请求）
        time.sleep(0.07)
    return results
```

### 4. 配置管理

建议将认证信息存储在配置文件中，不要硬编码：

```python
import json

# config.json
{
    "feishu": {
        "plugin_id": "your_plugin_id",
        "plugin_secret": "your_plugin_secret",
        "project_key": "your_project_key",
        "user_key": "your_user_key",
        "app_id": "your_app_id",
        "app_secret": "your_app_secret"
    }
}

# 使用配置
with open('config.json', 'r') as f:
    config = json.load(f)
    feishu_config = config['feishu']

api = FeishuAPI(**feishu_config)
```

### 5. 日志记录

建议添加日志记录功能：

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def log_api_call(func_name, success, result=None):
    """记录API调用"""
    if success:
        logger.info(f"{func_name} 调用成功")
    else:
        logger.error(f"{func_name} 调用失败: {result}")

# 使用示例
result = api.create_work_item(...)
log_api_call("create_work_item", result is not None, result)
```

---

## 常见问题

### Q1: 如何获取project_key和user_key？

**A**: 
- `project_key`：在飞书项目中，双击空间图标，会显示空间ID
- `user_key`：在飞书项目中，双击用户头像，会显示用户密钥

### Q2: API调用返回None怎么办？

**A**: 
1. 检查认证信息是否正确
2. 检查网络连接
3. 查看控制台错误信息
4. 参考API文档检查参数格式

### Q3: 如何获取工作项类型key？

**A**: 
- 在飞书项目中查看工作项类型
- 或使用API：`GET /open_api/:project_key/work_item/:work_item_type_key/meta`

### Q4: 如何获取多维表格的app_token和table_id？

**A**: 
- `app_token`：在多维表格URL中，`/base/`后面的部分
- `table_id`：在多维表格URL中，`/table/`后面的部分

### Q5: 如何发送消息到群组？

**A**: 
- 使用`chat_id`作为`receive_id`
- `receive_id_type`设置为`"chat_id"`
- 需要先获取群组的chat_id

---

## 参考文档

### 飞书项目API

- **Reference位置**：`c:\Users\colin.lin\.cursor\cursor-projects\tools\feishu interaction\reference\`
- **API文档**：`api_docs/`
- **快速开始**：`quick_start_example.py`

### 飞书开放平台API

- **官方文档**：https://open.feishu.cn/document/
- **消息API**：https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/reference/im-v1/message/create
- **云文档API**：https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/reference/drive-v1/file/create
- **多维表格API**：https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/reference/bitable-v1/app-table-record/create
- **电子表格API**：https://open.feishu.cn/document/ukTMukTMukTM/uUDN04SN0QjL1QDN

---

## 关联记录

### 相关能力

- [SKILL-001 飞书API封装工具](feishu-api-wrapper.md)
- [SKILL-002 飞书多维表格今日更新总结](feishu-bitable-daily-summary.md)
- [SKILL-003 飞书交互能力](feishu-interaction-capabilities.md)
- [MCP-001 飞书API集成](../../mcps/mcps/feishu-api.md)

### 相关文档

- [飞书API使用指南](FEISHU-API-GUIDE.md)
- [能力注册表](../../registry.md)

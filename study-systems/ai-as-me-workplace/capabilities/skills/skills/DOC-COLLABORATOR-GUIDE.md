# 飞书文档协作器使用指南

## 概述

`FeishuDocCollaborator` 是一个通用的飞书文档协作能力包，提供了简洁的API接口，支持：

- ✅ 创建或查找文档（自动去重）
- ✅ 本地Markdown编辑
- ✅ Markdown与飞书文档双向同步
- ✅ 直接添加内容到文档
- ✅ 内容管理和更新

## 快速开始

### 1. 创建协作器实例

```python
from feishu_doc_collaborator import create_doc_collaborator

collaborator = create_doc_collaborator(
    app_id="your_app_id",
    app_secret="your_app_secret",
    user_access_token="your_user_access_token",
    space_id="your_space_id"
)
```

### 2. 创建或查找文档

```python
doc_info = collaborator.create_or_find_doc(
    doc_title="我的文档",
    parent_node_token="父节点token（可选）",
    auto_create=True  # 如果不存在，自动创建
)

if doc_info:
    node_token = doc_info['node_token']
    document_id = doc_info['document_id']
    doc_url = doc_info['doc_url']
```

### 3. 本地Markdown编辑

```python
# 获取本地Markdown文件路径
md_path = collaborator.get_local_md_path("我的文档")
# 返回: work/docs/我的文档.md

# 在本地Markdown文件中编辑内容
# ...
```

### 4. 同步到飞书

```python
# 方式1：指定Markdown文件路径
collaborator.sync_to_feishu(
    node_token=node_token,
    md_file_path="work/docs/我的文档.md",
    clear_first=True
)

# 方式2：自动查找Markdown文件（根据文档标题）
collaborator.sync_to_feishu(
    node_token=node_token,
    doc_title="我的文档",
    clear_first=True
)
```

### 5. 从飞书同步到本地

```python
collaborator.sync_from_feishu(
    node_token=node_token,
    doc_title="我的文档"
)
```

## 完整工作流程示例

```python
from feishu_doc_collaborator import create_doc_collaborator

# 1. 创建协作器
collaborator = create_doc_collaborator(
    app_id="cli_a9c92ca516f99bd9",
    app_secret="your_secret",
    user_access_token="your_token",
    space_id="7353073903872868356"
)

# 2. 创建或查找文档
doc_info = collaborator.create_or_find_doc(
    doc_title="项目文档",
    parent_node_token="V7FXwKKdLiEus3kU9oMcgLwGnpe"
)

if doc_info:
    node_token = doc_info['node_token']
    
    # 3. 从飞书读取到本地（如果文档已有内容）
    collaborator.sync_from_feishu(
        node_token=node_token,
        doc_title="项目文档"
    )
    
    # 4. 在本地Markdown文件中编辑
    # 文件位置：work/docs/项目文档.md
    # 编辑完成后...
    
    # 5. 同步到飞书
    collaborator.sync_to_feishu(
        node_token=node_token,
        doc_title="项目文档",
        clear_first=True
    )
```

## API参考

### FeishuDocCollaborator类

#### 初始化

```python
collaborator = FeishuDocCollaborator(
    app_id: str,
    app_secret: str,
    user_access_token: str,
    space_id: str,
    work_dir: Optional[str] = None
)
```

#### 主要方法

##### create_or_find_doc()

创建或查找文档

```python
doc_info = collaborator.create_or_find_doc(
    doc_title: str,
    parent_node_token: Optional[str] = None,
    auto_create: bool = True
) -> Optional[Dict]
```

**返回**：
```python
{
    'node_token': '节点token',
    'document_id': '文档ID',
    'title': '文档标题',
    'doc_url': '文档链接'
}
```

##### sync_to_feishu()

将本地Markdown同步到飞书文档

```python
success = collaborator.sync_to_feishu(
    node_token: str,
    md_file_path: Optional[str] = None,
    doc_title: Optional[str] = None,
    clear_first: bool = True
) -> bool
```

##### sync_from_feishu()

从飞书文档读取内容并保存为本地Markdown

```python
success = collaborator.sync_from_feishu(
    node_token: str,
    md_file_path: Optional[str] = None,
    doc_title: Optional[str] = None
) -> bool
```

##### add_content()

直接添加内容到文档

```python
success = collaborator.add_content(
    node_token: str,
    content: str,
    content_type: str = "text"  # "text", "heading1", "heading2", "heading3", "bullet"
) -> bool
```

##### get_local_md_path()

获取本地Markdown文件路径

```python
md_path = collaborator.get_local_md_path(doc_title: str) -> Path
```

## 使用场景

### 场景1：创建新文档并编辑

```python
# 1. 创建文档
doc_info = collaborator.create_or_find_doc("新文档")

# 2. 获取本地Markdown路径
md_path = collaborator.get_local_md_path("新文档")

# 3. 在本地编辑Markdown文件
# ...

# 4. 同步到飞书
collaborator.sync_to_feishu(
    node_token=doc_info['node_token'],
    doc_title="新文档"
)
```

### 场景2：更新现有文档

```python
# 1. 查找文档
doc_info = collaborator.create_or_find_doc("现有文档", auto_create=False)

# 2. 从飞书读取到本地
collaborator.sync_from_feishu(
    node_token=doc_info['node_token'],
    doc_title="现有文档"
)

# 3. 在本地编辑
# ...

# 4. 同步回飞书
collaborator.sync_to_feishu(
    node_token=doc_info['node_token'],
    doc_title="现有文档"
)
```

### 场景3：快速添加内容

```python
# 直接添加内容，无需Markdown
collaborator.add_content(
    node_token=node_token,
    content="新章节",
    content_type="heading2"
)

collaborator.add_content(
    node_token=node_token,
    content="这是内容",
    content_type="text"
)
```

## 文件组织

```
work/
  docs/
    文档标题1.md
    文档标题2.md
    ...
```

本地Markdown文件统一存储在 `work/docs/` 目录下，文件名自动从文档标题生成。

## 优势

1. **简洁API**：只需几行代码即可完成文档协作
2. **自动去重**：自动检测已存在的文档，避免重复创建
3. **灵活工作流**：支持本地编辑、直接添加、双向同步等多种方式
4. **统一管理**：本地文件统一管理，易于版本控制
5. **易于扩展**：基于类的设计，易于扩展和定制

## 注意事项

1. **权限要求**：确保`user_access_token`包含所需权限
2. **频率限制**：大量内容同步时，会自动控制请求频率
3. **格式支持**：目前支持标题、文本、列表等基本格式
4. **清空内容**：`sync_to_feishu`默认会清空现有内容，注意备份

## 相关文件

- **核心类**：`feishu_doc_collaborator.py`
- **使用示例**：`doc_collaborator_example.py`
- **API封装**：`feishu_api_wrapper.py`

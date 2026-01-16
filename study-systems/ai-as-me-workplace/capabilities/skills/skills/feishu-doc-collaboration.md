# 飞书文档协作能力（SKILL-004）

## 能力概述

完整的飞书Wiki文档协作能力，支持与AI协同完成文档撰写，包括：
- 创建文档
- 读取文档内容
- 创建内容模块（块）
- 更新内容
- 删除内容

## 所需权限

### Wiki权限
- `wiki:wiki` - Wiki知识库基础权限
- `wiki:node:create` - 创建Wiki节点权限
- `wiki:node:read` - 读取Wiki节点权限
- `wiki:node:update` - 更新Wiki节点权限
- **注意**：`wiki:node:delete` 不是有效权限，删除操作通过 `docx:document` 权限实现

### 文档权限
- `docx:document` - 创建及编辑新版文档权限（包含删除文档内容的权限）

## 完整权限列表（用于授权）

```
wiki:wiki wiki:node:create wiki:node:read wiki:node:update docx:document
```

## 功能列表

### 1. 文档管理
- **创建Wiki文档**：在指定知识库和目录下创建文档
- **获取文档信息**：获取文档基本信息（标题、版本等）
- **获取文档内容**：获取文档所有块的内容

### 2. 内容读取
- **获取所有块**：获取文档的所有块（分页支持）
- **获取块内容**：获取指定块的详细内容

### 3. 内容创建
- **创建文本块**：创建文本、标题、列表等文本类块
- **创建表格块**：创建表格、多维表格等数据类块
- **创建媒体块**：创建图片、文件等媒体类块
- **创建容器块**：创建高亮块、引用容器等容器类块

### 4. 内容更新
- **更新块内容**：更新指定块的内容
- **批量更新块**：批量更新多个块的内容

### 5. 内容删除
- **删除块**：删除指定块的子块

## API方法

### 文档管理
```python
# 创建Wiki文档
api.create_wiki_doc(
    space_id="知识库ID",
    parent_node_token="父节点token（可选）",
    title="文档标题",
    use_user_token=True
)

# 获取文档信息
api.get_document_info(
    document_id="文档ID",
    use_user_token=True
)

# 获取文档所有块
api.get_document_blocks(
    document_id="文档ID",
    page_size=500,
    page_token=None,
    document_revision_id=-1,
    use_user_token=True
)
```

### 内容读取
```python
# 获取块内容
api.get_block_content(
    document_id="文档ID",
    block_id="块ID",
    document_revision_id=-1,
    use_user_token=True
)
```

### 内容创建
```python
# 创建文本块
api.create_block(
    document_id="文档ID",
    block_id="父块ID（或document_id）",
    children=[
        {
            "block_type": 3,  # 标题1
            "text": {
                "elements": [
                    {
                        "text_run": {
                            "content": "标题内容"
                        }
                    }
                ]
            }
        }
    ],
    document_revision_id=-1,
    use_user_token=True
)
```

### 内容更新
```python
# 更新块内容
api.update_block(
    document_id="文档ID",
    block_id="块ID",
    requests=[
        {
            "update_text": {
                "elements": [
                    {
                        "text_run": {
                            "content": "更新后的内容"
                        }
                    }
                ]
            }
        }
    ],
    document_revision_id=-1,
    use_user_token=True
)
```

### 内容删除
```python
# 删除块
api.delete_blocks(
    document_id="文档ID",
    block_id="父块ID",
    start_index=0,
    end_index=1,
    document_revision_id=-1,
    use_user_token=True
)
```

## 使用示例

### 示例1：创建文档并添加内容

```python
from feishu_api_wrapper import FeishuAPI

# 初始化API
api = FeishuAPI(
    app_id="your_app_id",
    app_secret="your_app_secret"
)
api.set_user_access_token("your_user_access_token")

# 1. 创建文档
doc = api.create_wiki_doc(
    space_id="知识库ID",
    parent_node_token="父节点token",
    title="新文档标题",
    use_user_token=True
)

if doc:
    node = doc.get('node', {})
    node_token = node.get('node_token')
    # 获取document_id（需要从Wiki节点信息中获取obj_token）
    # 这里假设已经获取到document_id
    document_id = "文档ID"
    
    # 2. 添加标题
    api.create_block(
        document_id=document_id,
        block_id=document_id,  # 文档根节点
        children=[
            {
                "block_type": 3,  # 标题1
                "text": {
                    "elements": [
                        {
                            "text_run": {
                                "content": "第一章 概述"
                            }
                        }
                    ]
                }
            }
        ],
        use_user_token=True
    )
    
    # 3. 添加文本内容
    api.create_block(
        document_id=document_id,
        block_id=document_id,
        children=[
            {
                "block_type": 2,  # 文本块
                "text": {
                    "elements": [
                        {
                            "text_run": {
                                "content": "这是文档的第一段内容。"
                            }
                        }
                    ]
                }
            }
        ],
        use_user_token=True
    )
```

### 示例2：读取文档内容

```python
# 获取文档所有块
blocks = api.get_document_blocks(
    document_id="文档ID",
    use_user_token=True
)

if blocks:
    items = blocks.get('data', {}).get('items', [])
    for block in items:
        block_id = block.get('block_id')
        block_type = block.get('block_type')
        print(f"块ID: {block_id}, 类型: {block_type}")
        
        # 获取块详细内容
        block_content = api.get_block_content(
            document_id="文档ID",
            block_id=block_id,
            use_user_token=True
        )
        if block_content:
            # 处理块内容
            pass
```

### 示例3：更新文档内容

```python
# 更新文本块内容
api.update_block(
    document_id="文档ID",
    block_id="块ID",
    requests=[
        {
            "update_text": {
                "elements": [
                    {
                        "text_run": {
                            "content": "更新后的内容"
                        }
                    }
                ]
            }
        }
    ],
    use_user_token=True
)
```

### 示例4：删除文档内容

```python
# 删除第一个子块
api.delete_blocks(
    document_id="文档ID",
    block_id="父块ID",
    start_index=0,
    end_index=1,
    use_user_token=True
)
```

## 块类型参考

常用块类型：
- `1` - 页面块（Page）
- `2` - 文本块（Text）
- `3` - 标题1（Heading1）
- `4` - 标题2（Heading2）
- `5` - 标题3（Heading3）
- `12` - 无序列表（Bullet）
- `13` - 有序列表（Ordered）
- `14` - 代码块（Code）
- `15` - 引用块（Quote）
- `17` - 待办事项（Todo）
- `19` - 高亮块（Callout）
- `22` - 分割线（Divider）
- `27` - 图片块（Image）
- `31` - 表格块（Table）

完整块类型列表参考：[文档概述](https://open.feishu.cn/document/ukTMukTMukTM/uUDN04SN0QjL1QDN/document-docx/docx-overview)

## 注意事项

1. **权限要求**：所有操作都需要用户身份凭证（user_access_token），并确保用户已授权所需权限
2. **频率限制**：
   - 应用频率限制：每秒3-5次（不同接口不同）
   - 文档频率限制：单篇文档并发编辑上限为每秒3次
3. **版本控制**：使用`document_revision_id=-1`表示最新版本
4. **块父子关系**：创建块时需要遵循块的父子关系规则
5. **幂等性**：更新操作支持`client_token`参数实现幂等性

## 相关文档

- [飞书开放平台 - 文档概述](https://open.feishu.cn/document/ukTMukTMukTM/uUDN04SN0QjL1QDN/document-docx/docx-overview)
- [飞书开放平台 - Wiki v2 API](https://open.feishu.cn/document/ukTMukTMukTM/uUDN04SN0QjL1QDN/wiki-v2/space-node/create)
- [API封装代码](../skills/feishu_api_wrapper.py)

# 飞书文档协作使用指南

## 快速开始

### 1. 获取用户身份凭证

使用更新后的脚本获取包含完整权限的`user_access_token`：

```bash
python get_user_token_with_scope.py
```

脚本会自动在授权URL中包含以下权限：
- `wiki:wiki`
- `wiki:node:create`
- `wiki:node:read`
- `wiki:node:update`
- `wiki:node:delete`
- `docx:document`

### 2. 初始化API客户端

```python
from feishu_api_wrapper import FeishuAPI

api = FeishuAPI(
    app_id="your_app_id",
    app_secret="your_app_secret"
)
api.set_user_access_token("your_user_access_token")
```

### 3. 创建文档

```python
doc = api.create_wiki_doc(
    space_id="知识库ID",
    parent_node_token="父节点token（可选）",
    title="文档标题",
    use_user_token=True
)
```

### 4. 获取文档ID

创建文档后，需要获取`document_id`才能进行内容操作：

```python
# 方法1：从Wiki节点信息获取
# 创建文档后，需要通过Wiki API获取节点的obj_token
node_token = doc.get('node', {}).get('node_token')
# 然后调用获取节点信息接口获取obj_token（即document_id）

# 方法2：从文档URL获取
# 文档URL格式：https://xxx.feishu.cn/wiki/知识库ID/节点token
# 打开文档后，在浏览器地址栏可以看到document_id
```

## 常见使用场景

### 场景1：创建FSC文档并添加章节

```python
# 1. 创建文档
doc = api.create_wiki_doc(
    space_id="7353073903872868356",
    parent_node_token="V7FXwKKdLiEus3kU9oMcgLwGnpe",
    title="舱驾一体域控的FSC文档",
    use_user_token=True
)

# 获取document_id（假设已获取）
document_id = "doxc..."

# 2. 添加章节标题
sections = [
    "1. 项目概述",
    "2. 系统边界",
    "3. 安全目标",
    "4. 功能安全概念",
    "5. 安全机制",
    "6. 安全需求"
]

for section in sections:
    api.create_block(
        document_id=document_id,
        block_id=document_id,
        children=[
            {
                "block_type": 3,  # 标题1
                "text": {
                    "elements": [
                        {
                            "text_run": {
                                "content": section
                            }
                        }
                    ]
                }
            }
        ],
        use_user_token=True
    )
```

### 场景2：读取文档内容并分析

```python
# 获取文档所有块
blocks = api.get_document_blocks(
    document_id="文档ID",
    use_user_token=True
)

if blocks:
    items = blocks.get('data', {}).get('items', [])
    content_summary = []
    
    for block in items:
        block_id = block.get('block_id')
        block_type = block.get('block_type')
        
        # 获取块详细内容
        block_content = api.get_block_content(
            document_id="文档ID",
            block_id=block_id,
            use_user_token=True
        )
        
        if block_content:
            block_data = block_content.get('data', {}).get('block', {})
            # 提取文本内容
            if block_type in [2, 3, 4, 5]:  # 文本或标题
                text_elements = block_data.get('text', {}).get('elements', [])
                for element in text_elements:
                    if 'text_run' in element:
                        content = element['text_run'].get('content', '')
                        content_summary.append(content)
    
    # 分析内容
    print("文档内容摘要：")
    print("\n".join(content_summary))
```

### 场景3：更新文档内容

```python
# 更新指定块的内容
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

### 场景4：删除文档内容

```python
# 删除指定范围的子块
api.delete_blocks(
    document_id="文档ID",
    block_id="父块ID",
    start_index=0,  # 删除第一个子块
    end_index=1,
    use_user_token=True
)
```

## 块类型快速参考

### 文本类块
```python
# 标题1
{"block_type": 3, "text": {"elements": [{"text_run": {"content": "标题"}}]}}

# 标题2
{"block_type": 4, "text": {"elements": [{"text_run": {"content": "标题"}}]}}

# 文本块
{"block_type": 2, "text": {"elements": [{"text_run": {"content": "文本"}}]}}

# 无序列表
{"block_type": 12, "text": {"elements": [{"text_run": {"content": "列表项"}}]}}

# 有序列表
{"block_type": 13, "text": {"elements": [{"text_run": {"content": "列表项"}}]}}

# 代码块
{"block_type": 14, "code": {"language": 49, "elements": [{"text_run": {"content": "代码"}}]}}

# 引用块
{"block_type": 15, "quote": {"elements": [{"text_run": {"content": "引用内容"}}]}}
```

### 容器类块
```python
# 高亮块
{"block_type": 19, "callout": {"background_color": "LightYellowBackground"}}

# 分割线
{"block_type": 22}
```

## 错误处理

### 权限错误（99991679）

```
错误：Unauthorized. You do not have permission to perform the requested operation.
解决：重新获取user_access_token，确保授权时勾选了所有所需权限
```

### 频率限制（99991400）

```
错误：请求频率过高
解决：降低请求频率，使用指数退避算法重试
```

### 版本冲突（1770021）

```
错误：too old document
解决：使用document_revision_id=-1获取最新版本
```

## 最佳实践

1. **批量操作**：尽量使用批量更新接口，减少API调用次数
2. **错误重试**：实现指数退避算法处理频率限制
3. **版本管理**：始终使用最新版本（document_revision_id=-1）
4. **幂等性**：更新操作使用client_token确保幂等性
5. **内容验证**：创建块前验证块的父子关系是否合法

## 相关资源

- [完整API文档](../skills/feishu-doc-collaboration.md)
- [API封装代码](../skills/feishu_api_wrapper.py)
- [获取token脚本](../skills/get_user_token_with_scope.py)

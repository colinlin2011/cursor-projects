# 快速开始 - 飞书文档协作

## 最简单的使用方式

### 方式1：使用命令行工具（推荐）

```bash
# 1. 创建或查找文档
python quick_doc.py create "文档标题" --parent "父节点token"

# 2. 在本地Markdown文件中编辑
# 文件位置：work/docs/文档标题.md

# 3. 同步到飞书
python quick_doc.py sync-to "节点token" --title "文档标题"
```

### 方式2：使用Python API

```python
from feishu_doc_collaborator import create_doc_collaborator

# 创建协作器
collaborator = create_doc_collaborator(
    app_id="cli_a9c92ca516f99bd9",
    app_secret="your_secret",
    user_access_token="your_token",
    space_id="7353073903872868356"
)

# 创建或查找文档
doc_info = collaborator.create_or_find_doc(
    doc_title="我的文档",
    parent_node_token="V7FXwKKdLiEus3kU9oMcgLwGnpe"
)

# 同步Markdown到飞书
collaborator.sync_to_feishu(
    node_token=doc_info['node_token'],
    doc_title="我的文档"
)
```

## 典型使用场景

### 场景：创建新文档并协作编辑

```python
from feishu_doc_collaborator import create_doc_collaborator

collaborator = create_doc_collaborator(
    app_id="cli_a9c92ca516f99bd9",
    app_secret="your_secret",
    user_access_token="your_token",
    space_id="7353073903872868356"
)

# 1. 创建文档
doc_info = collaborator.create_or_find_doc("项目文档")

# 2. 获取本地Markdown路径
md_path = collaborator.get_local_md_path("项目文档")
print(f"请在 {md_path} 中编辑内容")

# 3. 编辑完成后，同步到飞书
collaborator.sync_to_feishu(
    node_token=doc_info['node_token'],
    doc_title="项目文档"
)
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
- SPACE_ID: `7353073903872868356`

## 更多信息

- 完整API文档：`DOC-COLLABORATOR-GUIDE.md`
- 工作流程说明：`FEISHU-MD-WORKFLOW.md`
- 使用示例：`doc_collaborator_example.py`

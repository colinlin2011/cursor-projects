# 飞书文档协作器 - 能力总结

## 能力概述

**SKILL-005 飞书文档协作器**是一个通用的飞书文档协作能力包，将FSC文档协作过程中的所有经验抽象为简洁易用的API，支持在任何文档上快速应用。

## 核心特性

### 1. 自动去重
- ✅ 自动检测已存在的文档，避免重复创建
- ✅ 智能选择最新文档（按编辑时间）

### 2. 本地Markdown编辑
- ✅ 本地文件统一管理（`work/docs/`）
- ✅ 支持版本控制（Git）
- ✅ 离线编辑，不受网络限制

### 3. 双向同步
- ✅ Markdown → 飞书：将本地编辑同步到飞书
- ✅ 飞书 → Markdown：从飞书读取内容到本地

### 4. 简洁API
- ✅ 只需几行代码即可完成文档协作
- ✅ 支持多种使用方式（Python API、命令行）

## 文件结构

```
capabilities/skills/skills/
├── feishu_doc_collaborator.py    # 核心协作器类
├── doc_collaborator_example.py   # 使用示例
├── quick_doc.py                  # 命令行工具
├── DOC-COLLABORATOR-GUIDE.md     # 完整使用指南
├── FEISHU-MD-WORKFLOW.md         # 工作流程说明
└── QUICK-START.md                # 快速开始指南
```

## 使用方式

### 方式1：命令行工具（最简单）

```bash
# 创建文档
python quick_doc.py create "文档标题" --parent "父节点token"

# 同步到飞书
python quick_doc.py sync-to "节点token" --title "文档标题"

# 从飞书同步
python quick_doc.py sync-from "节点token" --title "文档标题"
```

### 方式2：Python API（最灵活）

```python
from feishu_doc_collaborator import create_doc_collaborator

# 创建协作器
collaborator = create_doc_collaborator(
    app_id="your_app_id",
    app_secret="your_app_secret",
    user_access_token="your_token",
    space_id="your_space_id"
)

# 创建或查找文档
doc_info = collaborator.create_or_find_doc("文档标题")

# 同步Markdown到飞书
collaborator.sync_to_feishu(
    node_token=doc_info['node_token'],
    doc_title="文档标题"
)
```

## 典型工作流程

```
1. 创建/查找文档
   ↓
2. 从飞书读取到本地（如果文档已有内容）
   ↓
3. 在本地Markdown中编辑
   ↓
4. 同步到飞书
```

## 应用场景

### 场景1：创建新文档
```python
doc_info = collaborator.create_or_find_doc("新文档")
# 在 work/docs/新文档.md 中编辑
collaborator.sync_to_feishu(doc_info['node_token'], doc_title="新文档")
```

### 场景2：更新现有文档
```python
doc_info = collaborator.create_or_find_doc("现有文档", auto_create=False)
collaborator.sync_from_feishu(doc_info['node_token'], doc_title="现有文档")
# 编辑 work/docs/现有文档.md
collaborator.sync_to_feishu(doc_info['node_token'], doc_title="现有文档")
```

### 场景3：快速添加内容
```python
collaborator.add_content(node_token, "新章节", "heading2")
collaborator.add_content(node_token, "内容", "text")
```

## 优势对比

| 特性 | 之前（写脚本） | 现在（协作器） |
|------|--------------|--------------|
| 创建文档 | 需要写脚本 | 1行代码 |
| 查找文档 | 需要写脚本 | 自动检测 |
| 同步内容 | 需要写脚本 | 1行代码 |
| 本地编辑 | 手动管理 | 自动管理 |
| 重复创建 | 可能重复 | 自动去重 |

## 技术实现

### 核心类：FeishuDocCollaborator

封装了所有文档协作逻辑：
- 文档创建和查找
- Markdown解析和生成
- 块的管理和同步
- 错误处理和重试

### 依赖

- `feishu_api_wrapper.py` - 飞书API封装
- Python标准库：`pathlib`, `re`, `time`

## 权限要求

- `wiki:wiki` - Wiki知识库基础权限
- `wiki:node:create` - 创建Wiki节点权限
- `wiki:node:read` - 读取Wiki节点权限
- `wiki:node:update` - 更新Wiki节点权限
- `docx:document` - 创建及编辑新版文档权限

## 快速示例

### 示例：创建并编辑文档

```python
from feishu_doc_collaborator import create_doc_collaborator

collaborator = create_doc_collaborator(
    app_id="cli_a9c92ca516f99bd9",
    app_secret="your_secret",
    user_access_token="your_token",
    space_id="7353073903872868356"
)

# 创建文档
doc_info = collaborator.create_or_find_doc(
    doc_title="项目文档",
    parent_node_token="V7FXwKKdLiEus3kU9oMcgLwGnpe"
)

print(f"文档已创建/找到: {doc_info['doc_url']}")
print(f"本地Markdown: {collaborator.get_local_md_path('项目文档')}")

# 在本地编辑后，同步到飞书
collaborator.sync_to_feishu(
    node_token=doc_info['node_token'],
    doc_title="项目文档"
)
```

## 相关文档

- **完整指南**：`DOC-COLLABORATOR-GUIDE.md`
- **工作流程**：`FEISHU-MD-WORKFLOW.md`
- **快速开始**：`QUICK-START.md`
- **使用示例**：`doc_collaborator_example.py`

## 未来改进

- [ ] 支持增量同步（只更新变化的部分）
- [ ] 支持冲突检测和合并
- [ ] 支持更多Markdown元素（表格、代码块、链接等）
- [ ] 支持文档模板
- [ ] 支持批量操作

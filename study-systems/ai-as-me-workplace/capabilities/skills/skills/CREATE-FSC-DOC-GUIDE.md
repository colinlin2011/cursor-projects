# 创建舱驾一体域控FSC文档指南

## 概述

本指南介绍如何使用脚本在飞书云文档指定目录创建"舱驾一体域控的FSC文档"。

---

## 前置准备

### 1. 获取飞书开放平台应用凭证

1. **访问飞书开放平台**：https://open.feishu.cn/
2. **创建企业自建应用**（如果还没有）
3. **获取应用凭证**：
   - `app_id`：应用ID
   - `app_secret`：应用密钥

### 2. 配置应用权限

在应用管理页面，确保应用具有以下权限：
- **云文档**：查看、编辑、管理云文档
- **知识库**：查看、编辑知识库

### 3. 获取知识库信息

#### 方法1：从Wiki链接获取

1. 打开飞书Wiki，进入目标知识库
2. 查看浏览器地址栏，URL格式类似：
   ```
   https://xxx.feishu.cn/wiki/WikiID
   ```
3. `WikiID`就是`space_id`

#### 方法2：从指定目录获取

1. 在飞书Wiki中，进入目标目录
2. 查看浏览器地址栏，URL格式类似：
   ```
   https://xxx.feishu.cn/wiki/WikiID/NodeID
   ```
3. `WikiID`是`space_id`
4. `NodeID`是`parent_node_token`（如果要在该目录下创建文档）

---

## 使用方法

### 方法1：使用脚本（推荐）

#### 步骤1：配置环境变量（可选）

```bash
# Windows PowerShell
$env:FEISHU_APP_ID = "your_app_id"
$env:FEISHU_APP_SECRET = "your_app_secret"
$env:FEISHU_SPACE_ID = "your_space_id"
$env:FEISHU_PARENT_NODE_TOKEN = "your_parent_node_token"  # 可选

# Linux/macOS
export FEISHU_APP_ID="your_app_id"
export FEISHU_APP_SECRET="your_app_secret"
export FEISHU_SPACE_ID="your_space_id"
export FEISHU_PARENT_NODE_TOKEN="your_parent_node_token"  # 可选
```

#### 步骤2：运行脚本

```bash
cd cursor-projects/study-systems/ai-as-me-workplace/capabilities/skills/skills
python create_fsc_doc.py
```

#### 步骤3：按提示输入信息

如果未设置环境变量，脚本会提示输入：
- 飞书开放平台应用ID
- 飞书开放平台应用密钥
- 知识库ID
- 父节点token（可选，直接回车跳过）

### 方法2：直接调用API

```python
from feishu_api_wrapper import FeishuAPI

# 初始化API客户端
api = FeishuAPI(
    plugin_id="",  # Wiki不需要项目API
    plugin_secret="",
    app_id="your_app_id",
    app_secret="your_app_secret"
)

# 创建FSC文档
doc = api.create_wiki_doc(
    space_id="your_space_id",
    parent_node_token="your_parent_node_token",  # 可选
    title="舱驾一体域控的FSC文档"
)

if doc:
    print(f"文档创建成功: {doc.get('token')}")
    print(f"文档链接: https://bytedance.larkoffice.com/docx/{doc.get('token')}")
```

---

## 常见问题

### Q1: 如何获取space_id？

**A**: 
1. 打开飞书Wiki，进入目标知识库
2. 查看浏览器地址栏URL，格式：`https://xxx.feishu.cn/wiki/WikiID`
3. `WikiID`就是`space_id`

### Q2: 如何获取parent_node_token？

**A**: 
1. 在飞书Wiki中，进入目标目录
2. 查看浏览器地址栏URL，格式：`https://xxx.feishu.cn/wiki/WikiID/NodeID`
3. `NodeID`就是`parent_node_token`

### Q3: 如果不知道parent_node_token怎么办？

**A**: 
- 可以不提供`parent_node_token`，文档会在知识库根目录创建
- 或者使用API查询目录结构，找到目标目录的节点token

### Q4: 创建文档后如何添加内容？

**A**: 
- 文档创建后，可以在飞书中直接打开编辑
- 或者使用飞书开放平台的文档内容编辑API（参考飞书开放平台文档）

### Q5: 文档创建失败怎么办？

**A**: 
1. 检查`app_id`和`app_secret`是否正确
2. 检查应用是否有云文档和知识库权限
3. 检查`space_id`是否正确
4. 检查`parent_node_token`是否正确（如果指定了）
5. 查看控制台错误信息

---

## FSC文档建议结构

创建文档后，建议添加以下章节：

1. **项目概述**
   - 项目背景
   - 项目目标
   - 项目范围

2. **系统边界**
   - 系统定义
   - 系统边界图
   - 接口定义

3. **安全目标**
   - HARA分析结果
   - 安全目标列表
   - ASIL等级分配

4. **功能安全概念（FSC）**
   - 安全机制设计
   - 故障检测与处理
   - 降级策略

5. **安全需求**
   - 功能安全需求
   - 安全需求可追溯性

6. **验证与确认**
   - 验证计划
   - 验证结果

---

## 相关文档

- [飞书交互能力使用指南](FEISHU-INTERACTION-GUIDE.md)
- [飞书API封装工具](feishu-api-wrapper.md)
- [飞书开放平台文档](https://open.feishu.cn/document/)

---

## 注意事项

1. **权限要求**：确保应用具有云文档和知识库的相应权限
2. **API限制**：注意QPS限制，避免频繁调用
3. **文档位置**：如果不指定`parent_node_token`，文档会在知识库根目录创建
4. **文档内容**：脚本只创建空文档，内容需要手动或通过API添加

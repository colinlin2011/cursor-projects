# 飞书多维表格今日更新记录工具

**Tool ID**：SKILL-002  
**Tool名称**：飞书多维表格今日更新记录总结  
**创建日期**：2026-01-13  
**最后更新**：2026-01-13  
**版本**：v1.0  
**状态**：可用  
**维护人**：系统

---

## 工具描述

### 功能概述
获取飞书多维表格（或飞书项目表格视图）今日的更新记录，并生成总结报告。

### 适用场景
- 每日工作回顾
- 团队协作跟踪
- 数据变更监控
- 工作进度总结

---

## 重要说明

### 必须引用Reference文档
**所有飞书API调用必须参考以下文档**：

- **参考文档位置**：`c:\Users\colin.lin\.cursor\cursor-projects\tools\feishu interaction\reference\`
- **API文档目录**：`api_docs/`
- **相关API文档**：
  - `工作项-16.md`：获取工作项操作记录
  - `工作项-1.md`：获取工作项列表（支持按更新时间筛选）
  - `视图与度量-2.md`：获取视图下工作项列表

### 注意事项
1. **飞书多维表格 vs 飞书项目表格**：
   - 如果目标表格是飞书多维表格（Bitable），需要飞书开放平台的多维表格API
   - 如果目标表格是飞书项目中的表格视图，可以使用reference中的工作项API
   
2. **识别方式**：
   - 通过链接识别：从URL中提取project_key、view_id等信息
   - 通过ID识别：直接使用project_key、view_id等

---

## 工具接口

### 接口定义
```python
def get_bitable_daily_summary(
    table_identifier: str,  # 表格标识（链接或ID）
    date: str = None,  # 日期（YYYY-MM-DD），默认今天
    # 飞书项目API凭证（用于项目视图）
    plugin_id: str = None,
    plugin_secret: str = None,
    project_key: str = None,
    user_key: str = None,
    work_item_type_keys: List[str] = None,
    # 飞书开放平台API凭证（用于多维表格）
    app_id: str = None,
    app_secret: str = None
) -> dict
```

### 参数说明
- **table_identifier**：表格标识
  - 可以是飞书多维表格链接
  - 可以是飞书项目视图链接
  - 可以是project_key和view_id的组合
- **date**：日期（可选，默认今天）
- **plugin_id**：插件ID（必需）
- **plugin_secret**：插件密钥（必需）
- **project_key**：空间ID（如果table_identifier是链接，会自动提取）
- **user_key**：用户密钥（必需）

### 返回值
```python
{
    "date": "2026-01-13",
    "table_name": "表格名称",
    "table_type": "bitable" | "project_view",
    "summary": {
        "total_updates": 10,
        "new_items": 3,
        "modified_items": 5,
        "deleted_items": 2
    },
    "updates": [
        {
            "time": "2026-01-13 10:30:00",
            "operator": "用户名称",
            "operation": "create" | "modify" | "delete",
            "item_id": "工作项ID",
            "item_name": "工作项名称",
            "changes": ["字段1: 旧值 -> 新值", "字段2: 旧值 -> 新值"]
        }
    ],
    "summary_text": "今日更新总结文本"
}
```

---

## 实现方案

### 方案1：飞书项目表格视图（基于reference文档）

如果目标表格是飞书项目中的表格视图，可以使用reference中的API：

1. **识别表格**：
   - 从链接中提取`project_key`和`view_id`
   - 或直接使用提供的`project_key`和`view_id`

2. **获取今日更新记录**：
   - 使用`工作项-16.md`中的操作记录API
   - 筛选今日的操作记录（使用`start`和`end`参数）
   - 参考文档：`api_docs/工作项-16.md`

3. **获取工作项详情**：
   - 使用`工作项-1.md`中的工作项列表API
   - 按更新时间筛选今日更新的工作项
   - 参考文档：`api_docs/工作项-1.md`

### 方案2：飞书多维表格（Bitable）

如果目标表格是飞书多维表格（Bitable），使用飞书开放平台API：

1. **获取app_token和table_id**：
   - 从多维表格链接中提取：`https://bitable.feishu.cn/app/{app_token}/table/{table_id}`
   - 或直接提供app_token和table_id

2. **获取访问令牌**：
   - 使用app_id和app_secret获取tenant_access_token
   - 参考文档：`api_docs/飞书开放平台-API概述.md`

3. **获取记录列表**：
   - 调用多维表格API获取所有记录
   - 参考文档：`api_docs/多维表格-获取记录列表.md`

4. **筛选今日更新**：
   - 检查每条记录的`last_modified_time`
   - 筛选出今日更新的记录

**参考文档**：
- `api_docs/飞书开放平台-API概述.md`：飞书开放平台API概述
- `api_docs/多维表格-获取记录列表.md`：获取记录列表API
- `api_docs/多维表格-获取记录变更历史.md`：变更历史说明

---

## 使用示例

### 示例1：通过多维表格链接获取今日更新
```python
from feishu_bitable_daily_summary import get_bitable_daily_summary

result = get_bitable_daily_summary(
    table_identifier="https://bitable.feishu.cn/app/xxxxxxxxxx/table/xxxxxxxxxx",
    app_id="your_app_id",
    app_secret="your_app_secret"
)

print(result["summary_text"])
```

### 示例2：通过项目视图链接获取今日更新
```python
result = get_bitable_daily_summary(
    table_identifier="https://project.feishu.cn/doc/view_text",
    plugin_id="your_plugin_id",
    plugin_secret="your_plugin_secret",
    user_key="your_user_key"
)

print(result["summary_text"])
```

### 示例2：通过ID获取今日更新
```python
result = get_bitable_daily_summary(
    table_identifier="project_key:view_id",
    date="2026-01-13",
    plugin_id="your_plugin_id",
    plugin_secret="your_plugin_secret",
    project_key="your_project_key",
    user_key="your_user_key"
)
```

### 示例3：获取指定日期更新
```python
result = get_bitable_daily_summary(
    table_identifier="https://project.feishu.cn/doc/view_text",
    date="2026-01-12",
    plugin_id="your_plugin_id",
    plugin_secret="your_plugin_secret",
    user_key="your_user_key"
)
```

---

## 实现细节

### 步骤1：识别表格类型和参数
- 解析链接或ID，提取必要信息
- 判断是飞书项目视图还是多维表格

### 步骤2：获取认证信息
- 参考`quick_start_example.py`获取plugin_token
- 参考文档：`api_docs/调用流程-1.md`

### 步骤3：获取更新记录
- **飞书项目视图**：
  - 使用操作记录API（`工作项-16.md`）
  - 筛选今日的操作记录
- **多维表格**：
  - 使用多维表格的记录变更API（需要额外文档）

### 步骤4：处理和分析数据
- 解析操作记录
- 获取工作项详情
- 生成变更摘要

### 步骤5：生成总结报告
- 统计更新数量
- 分类更新类型
- 生成可读的总结文本

---

## 关联记录

### 相关注册表
- [能力注册表链接](../registry.md)

### 相关Skill定义
- [Skill定义链接](../SKILL-TEMPLATE.md)

### 相关使用记录
- [使用记录链接](../../usage/usage-history.md)

### 参考文档
- **Reference位置**：`c:\Users\colin.lin\.cursor\cursor-projects\tools\feishu interaction\reference\`
- **飞书项目API文档**（用于项目视图）：
  - `api_docs/工作项-16.md`：获取工作项操作记录
  - `api_docs/工作项-1.md`：获取工作项列表
  - `api_docs/视图与度量-2.md`：获取视图下工作项列表
- **飞书开放平台API文档**（用于多维表格）：
  - `api_docs/飞书开放平台-API概述.md`：API概述和调用流程
  - `api_docs/多维表格-获取记录列表.md`：获取记录列表API
  - `api_docs/多维表格-获取记录变更历史.md`：变更历史说明

---

## 工具版本历史

| 版本 | 日期 | 更新内容 | 更新人 |
|------|------|---------|--------|
| v1.0 | 2026-01-13 | 初始创建 | 系统 |

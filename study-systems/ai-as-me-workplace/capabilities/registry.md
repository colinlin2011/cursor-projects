# 能力注册表

**最后更新**：2026-01-13  
**版本**：v1.1

---

## 注册表说明

本注册表用于管理所有可用的AI能力，包括Skill、Agent、MCP和本地工具。所有能力都需要在此注册后才能使用。

### 能力状态说明
- **可用**：能力已注册且可用
- **不可用**：能力已注册但当前不可用
- **维护中**：能力正在维护，暂时不可用
- **已废弃**：能力已废弃，不再使用

---

## Skill能力

| 能力ID | 名称 | 类型 | 描述 | 接口 | 参数 | 状态 | 版本 | 创建日期 | 最后更新 |
|--------|------|------|------|------|------|------|------|---------|---------|
| SKILL-001 | 飞书API封装工具 | skill | 飞书API的Python封装工具 | Python SDK | plugin_id, plugin_secret, project_key, user_key | 可用 | v1.0 | 2026-01-13 | 2026-01-13 |
| SKILL-002 | 飞书多维表格今日更新总结 | skill | 获取飞书多维表格或项目表格视图的今日更新记录并生成总结 | Python脚本 | table_identifier, date, plugin_id, plugin_secret, user_key | 可用 | v1.0 | 2026-01-13 | 2026-01-13 |
| SKILL-003 | 飞书交互能力 | skill | 完整的飞书交互能力，包括即时通讯、Wiki、表格、多维表格、飞书项目 | Python SDK | plugin_id, plugin_secret, project_key, user_key, app_id, app_secret | 可用 | v1.0 | 2026-01-13 | 2026-01-13 |

### Skill能力详情
- **SKILL-001 飞书API封装工具**：[feishu-api-wrapper.md](skills/skills/feishu-api-wrapper.md)
  - 功能：飞书API的Python封装
  - 参考文档：`c:\Users\colin.lin\.cursor\cursor-projects\tools\feishu interaction\reference\`
  - 重要：所有飞书API调用必须参考reference文档

- **SKILL-002 飞书多维表格今日更新总结**：[feishu-bitable-daily-summary.md](skills/skills/feishu-bitable-daily-summary.md)
  - 功能：获取飞书多维表格或项目表格视图的今日更新记录并生成总结
  - 实现文件：`feishu_bitable_daily_summary.py`
  - 参考文档：`api_docs/工作项-16.md`、`api_docs/工作项-1.md`、`api_docs/视图与度量-2.md`
  - 重要：所有飞书API调用必须参考reference文档

- **SKILL-003 飞书交互能力**：[feishu-interaction-capabilities.md](skills/skills/feishu-interaction-capabilities.md)
  - 功能：完整的飞书交互能力，包括即时通讯、Wiki云文档、在线表格、多维表格、飞书项目
  - 实现文件：`feishu_api_wrapper.py`
  - 使用指南：`FEISHU-INTERACTION-GUIDE.md`
  - 参考文档：`c:\Users\colin.lin\.cursor\cursor-projects\tools\feishu interaction\reference\`
  - 重要：所有飞书API调用必须参考reference文档

---

## Agent能力

| 能力ID | 名称 | 类型 | 描述 | 接口 | 参数 | 状态 | 版本 | 创建日期 | 最后更新 |
|--------|------|------|------|------|------|------|------|---------|---------|
| AGENT-001 | [示例Agent] | agent | [描述] | [接口] | [参数] | 可用 | v1.0 | YYYY-MM-DD | YYYY-MM-DD |

### Agent能力详情
- **AGENT-001**：[链接到Agent定义文件]

---

## MCP能力

| 能力ID | 名称 | 类型 | 描述 | 接口 | 参数 | 状态 | 版本 | 创建日期 | 最后更新 |
|--------|------|------|------|------|------|------|------|---------|---------|
| MCP-001 | 飞书API集成 | mcp | 飞书消息、Wiki、表格、项目等API集成 | RESTful API | plugin_id, plugin_secret, project_key, user_key | 可用 | v1.0 | 2026-01-13 | 2026-01-13 |

### MCP能力详情
- **MCP-001 飞书API集成**：[feishu-api.md](mcps/mcps/feishu-api.md)
  - 功能：飞书消息、Wiki、表格、项目等API集成
  - 参考文档：`c:\Users\colin.lin\.cursor\cursor-projects\tools\feishu interaction\reference\`
  - 重要：所有飞书API调用必须参考reference文档

---

## 本地工具

| 能力ID | 名称 | 类型 | 描述 | 接口 | 参数 | 状态 | 版本 | 创建日期 | 最后更新 |
|--------|------|------|------|------|------|------|------|---------|---------|
| TOOL-001 | Pandoc文档转换器 | local-tool | 将Markdown文件转换为Word或PDF格式 | PowerShell脚本 | InputFile, OutputFile, TemplateFile, Format | 可用 | v1.0 | 2026-01-13 | 2026-01-13 |

### 本地工具详情
- **TOOL-001 Pandoc文档转换器**：[pandoc-converter.md](skills/local-tools/pandoc-converter.md)
  - 功能：Markdown转Word/PDF
  - 封装脚本：`pandoc-wrapper.ps1`
  - 模板位置：`templates/reference.docx`

---

## 能力统计

### 按类型统计
- **Skill能力**：3个
- **Agent能力**：0个
- **MCP能力**：1个
- **本地工具**：1个
- **总计**：5个

### 按状态统计
- **可用**：5个
- **不可用**：0个
- **维护中**：0个
- **已废弃**：0个

---

## 能力更新历史

| 日期 | 能力ID | 操作 | 版本 | 说明 |
|------|--------|------|------|------|
| 2026-01-13 | SKILL-001 | 注册 | v1.0 | 飞书API封装工具 |
| 2026-01-13 | SKILL-002 | 注册 | v1.0 | 飞书多维表格今日更新总结 |
| 2026-01-13 | SKILL-003 | 注册 | v1.0 | 飞书交互能力（完整功能） |
| 2026-01-13 | MCP-001 | 注册 | v1.0 | 飞书API集成 |
| 2026-01-13 | TOOL-001 | 注册 | v1.0 | Pandoc文档转换器 |

---

## 注册新能力

### 注册流程
1. 创建能力定义文件（使用对应模板）
2. 填写能力信息
3. 在本注册表中添加记录
4. 更新能力索引

### 注册要求
- 必须提供完整的能力信息
- 必须使用标准模板
- 必须通过测试验证

---

## 关联记录

### 相关能力索引
- [能力索引链接]

### 相关使用记录
- [使用记录链接]

### 相关知识库
- [知识库链接]

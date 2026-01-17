# 能力注册表

**最后更新**：2026-01-17（FMEA数据导入能力）  
**版本**：v2.3

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
| SKILL-004 | 飞书文档协作能力 | skill | 完整的飞书Wiki文档协作能力，支持创建、读取、更新、删除文档内容，用于AI协同文档撰写 | Python SDK | app_id, app_secret, user_access_token, space_id, document_id | 可用 | v1.0 | 2026-01-14 | 2026-01-14 |
| SKILL-005 | 飞书文档协作器 | skill | 通用的飞书文档协作能力包，提供简洁API支持本地Markdown编辑和飞书文档双向同步 | Python SDK | app_id, app_secret, user_access_token, space_id, doc_title, node_token | 可用 | v1.0 | 2026-01-15 | 2026-01-15 |
| SKILL-006 | 飞书多维表格协作器 | skill | 通用的飞书多维表格协作能力包，支持CRUD操作、数据分析和总结 | Python SDK | app_id, app_secret, user_access_token, app_token, table_id | 可用 | v1.0 | 2026-01-15 | 2026-01-15 |
| SKILL-007 | 飞书在线表格协作器 | skill | 通用的飞书在线表格协作能力包，支持数据缓存、定期同步、查询与总结 | Python SDK | app_id, app_secret, user_access_token, spreadsheet_token, sheet_id | 可用 | v1.0 | 2026-01-15 | 2026-01-15 |
| SKILL-008 | SSH日志泛化查询引擎 | skill | 通用的SSH日志查询和提取能力，支持自定义关键字查询（模糊匹配、多关键字AND/OR组合）和自定义信息提取（正则表达式、上下文提取） | Python SDK | remote_path, keywords, extract_pattern, context_lines, logic, output_format, fuzzy_match, max_results, query_method | 可用 | v1.0 | 2026-01-16 | 2026-01-16 |
| SKILL-009 | 故障概况提取能力 | skill | 从故障定位指引文档、"06. 安全需求总表"多维表格和功能安全业务数据中整合提取fa_id相关信息，生成综合故障概况 | Python SDK | fa_id, use_grep | 可用 | v1.0 | 2026-01-16 | 2026-01-16 |
| SKILL-010 | Markdown转Word文档转换器 | skill | 将Markdown格式文档转换为Word格式，支持批量转换和自定义模板 | Python模块 | source_file, output_file, template_file | 可用 | v1.0 | 2025-01-15 | 2025-01-15 |
| SKILL-011 | FMEA数据导入能力 | skill | 将飞书在线表格中的FMEA数据导入到飞书多维表格，支持架构元素、子功能清单、失效模式影响分析的完整导入流程 | Python脚本 | fmea_name, sheet_name, dry_run, skip_architecture, skip_functions, skip_fmea | 可用 | v1.0 | 2026-01-17 | 2026-01-17 |

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

- **SKILL-004 飞书文档协作能力**：[feishu-doc-collaboration.md](skills/skills/feishu-doc-collaboration.md)
  - 功能：完整的飞书Wiki文档协作能力，支持创建、读取、更新、删除文档内容，用于AI协同文档撰写
  - 实现文件：`feishu_api_wrapper.py`
  - 使用指南：`FEISHU-DOC-COLLABORATION-GUIDE.md`
  - 所需权限：`wiki:wiki wiki:node:create wiki:node:read wiki:node:update wiki:node:delete docx:document`
  - 参考文档：`c:\Users\colin.lin\.cursor\cursor-projects\tools\feishu interaction\reference\api_docs\#文档概述.md`
  - 重要：所有飞书API调用必须参考reference文档

- **SKILL-005 飞书文档协作器**：[DOC-COLLABORATOR-GUIDE.md](skills/skills/DOC-COLLABORATOR-GUIDE.md)
  - 功能：通用的飞书文档协作能力包，提供简洁API支持本地Markdown编辑和飞书文档双向同步
  - 实现文件：`feishu_doc_collaborator.py`
  - 使用示例：`doc_collaborator_example.py`
  - 命令行工具：`quick_doc.py`
  - 工作流程：`FEISHU-MD-WORKFLOW.md`
  - 所需权限：`wiki:wiki wiki:node:create wiki:node:read wiki:node:update docx:document`
  - 特点：自动去重、本地编辑、双向同步、简洁API

- **SKILL-006 飞书多维表格协作器**：[BITABLE-COLLABORATOR-GUIDE.md](skills/skills/BITABLE-COLLABORATOR-GUIDE.md)
  - 功能：通用的飞书多维表格协作能力包，支持CRUD操作、数据分析和总结
  - 实现文件：`feishu_bitable_collaborator.py`
  - 使用示例：`bitable_collaborator_example.py`
  - 所需权限：`bitable:app:readonly` 或 `bitable:app`
  - 特点：自动分析、数据洞察、Markdown导出、简洁API

- **SKILL-007 飞书在线表格协作器**：[SPREADSHEET-CACHE-GUIDE.md](skills/skills/SPREADSHEET-CACHE-GUIDE.md)
  - 功能：通用的飞书在线表格协作能力包，支持缓存、同步、查询、总结
  - 实现文件：`feishu_spreadsheet_collaborator.py`、`spreadsheet_cache_manager.py`、`spreadsheet_query_interface.py`
  - 使用示例：`spreadsheet_query_interface.py`
  - 所需权限：`sheets:spreadsheet:readonly` 或 `sheets:spreadsheet`
  - 特点：自动缓存、定期同步、自然语言查询、简洁API

- **SKILL-008 SSH日志泛化查询引擎**：[ssh-log-query-engine.md](skills/skills/ssh-log-query-engine.md)
  - 功能：通用的SSH日志查询和提取能力，支持自定义关键字查询和自定义信息提取
  - 实现文件：`ssh_log_query_engine.py`
  - 配置文件：`ssh_log_query_config.py`
  - 使用示例：`ssh_log_query_example.py`
  - 特点：支持模糊匹配、多关键字AND/OR组合、正则表达式提取、上下文提取、自动选择查询方式

- **SKILL-009 故障概况提取能力**：[fault-profile-extractor.md](skills/skills/fault-profile-extractor.md)
  - 功能：从故障定位指引文档、"06. 安全需求总表"多维表格和功能安全业务数据中整合提取fa_id相关信息，生成综合故障概况
  - 实现文件：`fault_profile_extractor.py`
  - 使用场景：故障分析、安全需求分析

- **SKILL-010 Markdown转Word文档转换器**：[document-converter.md](skills/document-converter.md)
  - 功能：将Markdown格式文档转换为Word格式，支持批量转换和自定义模板
  - 实现文件：`document-converter/converter.py`
  - 使用场景：工作文档转换、项目文档转换、批量文档转换
  - 特点：支持批量转换、自定义模板、格式保持、跨平台支持

- **SKILL-011 FMEA数据导入能力**：[SKILL-011-FMEA-Import.md](skills/skills/SKILL-011-FMEA-Import.md)
  - 功能：将飞书在线表格中的FMEA数据导入到飞书多维表格，支持架构元素、子功能清单、失效模式影响分析的完整导入流程
  - 实现文件：`import_fmea_complete.py`、`import_architecture_elements.py`、`import_functions.py`、`import_failure_modes.py`、`fmea_data_reader.py`
  - 使用场景：批量导入FMEA数据、数据迁移、数据同步
  - 特点：支持富文本处理、合并单元格处理、Element Name推断、跳过条目详细记录、导入报告生成

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
- **Skill能力**：11个
- **Agent能力**：0个
- **MCP能力**：1个
- **本地工具**：1个
- **总计**：13个

### 按状态统计
- **可用**：13个
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
| 2026-01-14 | SKILL-004 | 注册 | v1.0 | 飞书文档协作能力（AI协同文档撰写） |
| 2026-01-15 | SKILL-005 | 注册 | v1.0 | 飞书文档协作器（通用文档协作能力包） |
| 2026-01-15 | SKILL-006 | 注册 | v1.0 | 飞书多维表格协作器（通用多维表格协作能力包） |
| 2026-01-15 | SKILL-007 | 注册 | v1.0 | 飞书在线表格协作器 |
| 2026-01-16 | SKILL-008 | 注册 | v1.0 | SSH日志泛化查询引擎 |
| 2026-01-16 | SKILL-009 | 注册 | v1.0 | 故障概况提取能力 |
| 2026-01-17 | SKILL-011 | 注册 | v1.0 | FMEA数据导入能力 |
| 2026-01-13 | MCP-001 | 注册 | v1.0 | 飞书API集成 |
| 2026-01-13 | TOOL-001 | 注册 | v1.0 | Pandoc文档转换器 |
| 2026-01-16 | FRAMEWORK-001 | 新增 | v1.0 | 原子能力标准化抽象层 |
| 2026-01-16 | FRAMEWORK-002 | 新增 | v1.0 | 统一缓存管理框架 |
| 2026-01-16 | FRAMEWORK-003 | 新增 | v1.0 | 能力编排引擎 |
| 2026-01-16 | FRAMEWORK-004 | 新增 | v1.0 | 业务流程模板库 |
| 2026-01-16 | FRAMEWORK-005 | 新增 | v1.0 | 能力自动发现和组合 |

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

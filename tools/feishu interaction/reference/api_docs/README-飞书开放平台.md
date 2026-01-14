# 飞书开放平台 API 文档说明

**文档来源**：https://open.feishu.cn/document/server-docs/api-call-guide/calling-process/overview  
**最后更新**：2026-01-13

---

## 文档说明

本目录包含飞书开放平台（open.feishu.cn）的API文档，与飞书项目API（project.feishu.cn）不同。

---

## 文档列表

### 概述文档
- **飞书开放平台-API概述.md**：API概述、调用流程、认证方式

### 多维表格（Bitable）API
- **多维表格-获取记录列表.md**：获取记录列表API
- **多维表格-获取记录变更历史.md**：获取变更历史说明

### Wiki API
- （待补充）

---

## 重要区别

### 飞书项目API vs 飞书开放平台API

| 特性 | 飞书项目API | 飞书开放平台API |
|------|------------|----------------|
| 域名 | project.feishu.cn | open.feishu.cn |
| 认证 | plugin_token | access_token |
| 凭证 | plugin_id, plugin_secret | app_id, app_secret |
| 用途 | 项目管理、工作项 | 多维表格、Wiki、消息等 |
| 文档位置 | 本目录（项目API） | 本目录（开放平台API） |

---

## 使用指南

### 多维表格API使用
1. 创建自建应用，获取app_id和app_secret
2. 获取tenant_access_token
3. 从链接中提取app_token和table_id
4. 调用API获取记录
5. 筛选今日更新的记录

### 参考文档
- **官方文档**：https://open.feishu.cn/document/
- **API调用指南**：https://open.feishu.cn/document/server-docs/api-call-guide/calling-process/overview
- **多维表格API**：https://open.feishu.cn/document/server-docs/docs/bitable-v1/overview

---

## 注意事项

1. **API限制**：注意QPS限制和频率限制
2. **权限要求**：确保应用有相应的权限
3. **时间戳格式**：多维表格API使用秒级时间戳
4. **文档更新**：API文档可能更新，请参考最新文档

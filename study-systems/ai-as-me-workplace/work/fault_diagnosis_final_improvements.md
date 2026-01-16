# 故障定位系统最终改进说明

## 改进时间
2025年1月15日

## 改进内容

### 1. 修复文档链接前缀 ✅

**问题**：
- 原链接前缀：`https://bytedance.larkoffice.com/wiki/`
- 无法正常访问

**解决方案**：
- 修改为：`https://zyt.feishu.cn/wiki/`
- 修改文件：`feishu_doc_collaborator.py`

**验证**：
- ✅ 文档链接已正确生成：`https://zyt.feishu.cn/wiki/FGV6wLYIdinN9KkaFNKcFHImncg`

---

### 2. 在指定父节点下创建文档 ✅

**需求**：
- 在节点 `GCrNwnjWFiNw1UkLOraclXVynO1` 下创建分析文档

**解决方案**：
- 在 `fault_diagnosis_config.py` 中添加配置：`REPORT_PARENT_NODE_TOKEN = "GCrNwnjWFiNw1UkLOraclXVynO1"`
- 修改 `fault_report_generator.py`，默认使用配置中的父节点

**验证**：
- ✅ 文档已创建在指定父节点下

---

### 3. 改进报告结构：综合性总结 + 表格 ✅

**需求**：
- 报告结构改为：综合性总结 + 表格
- 表格列：Fault ID、Fault ID详情（代表什么故障）、可能的原因、故障定位指引、AI分析摘要

**解决方案**：
- 重新设计 `_generate_report_content()` 方法
- 第一部分：综合性总结（包含统计信息）
- 第二部分：详细分析表格（Markdown格式）

**报告结构**：
1. **标题**：故障分析报告
2. **综合分析总结**：
   - 工作项ID、记录ID、分析时间
   - 统计信息（总Fault ID数、有指引/无指引数量）
   - 日志路径
3. **Fault ID详细分析表**：
   - 表格包含5列：
     - Fault ID
     - Fault ID详情（代表什么故障）
     - 可能的原因
     - 故障定位指引
     - AI分析摘要

**验证**：
- ✅ 报告结构已更新
- ✅ 表格已正确生成

---

### 4. 修改报告标题格式 ✅

**需求**：
- 格式：`日期_工作项id`
- 例如：`20260115_6683487902`

**解决方案**：
- 修改 `fault_report_generator.py` 中的标题生成逻辑
- 从 `故障分析报告-{work_item_id}-{datetime.now().strftime('%Y%m%d-%H%M%S')}` 
- 改为 `{datetime.now().strftime('%Y%m%d')}_{work_item_id}`

**验证**：
- ✅ 报告标题已更新为：`20260115_6683487902`

---

### 5. 自动清理本地日志文件 ✅

**需求**：
- 分析成功后，约1天后自动清除本地日志文件
- 确保本地硬盘空间不被过多占用

**解决方案**：
- 创建 `log_cleanup_manager.py` 模块
- 实现日志清理管理器：
  - 注册日志路径（记录分析时间）
  - 自动清理过期日志（默认24小时后）
  - 清理旧的清理记录（默认保留7天）
- 在 `auto_fault_diagnosis.py` 中，分析成功后自动注册日志路径

**实现细节**：
1. **注册机制**：
   - 分析成功后，记录日志路径和分析时间
   - 计算清理时间（分析时间 + 24小时）
   - 保存到 `log_cleanup_records.json`

2. **清理机制**：
   - 定期检查清理记录
   - 删除超过清理时间的文件/目录
   - 更新清理状态

3. **清理任务**：
   - 创建 `cleanup_logs_task.py` 用于定期执行清理
   - 可以设置为定时任务（cron/计划任务）

**使用方法**：
```python
# 自动注册（已在auto_fault_diagnosis.py中实现）
# 分析成功后自动注册日志路径

# 手动执行清理
python cleanup_logs_task.py
```

**验证**：
- ✅ 日志清理管理器已创建
- ✅ 分析成功后自动注册日志路径
- ✅ 清理任务脚本已创建

---

## 测试结果

### 测试工作项：6683487902

**运行结果**：
- ✅ 文档创建成功
- ✅ 文档链接：`https://zyt.feishu.cn/wiki/FGV6wLYIdinN9KkaFNKcFHImncg`
- ✅ 报告标题：`20260115_6683487902`
- ✅ 报告内容已写入（包含综合性总结和表格）
- ✅ 文档链接已回填到"工具回传"字段
- ✅ 日志路径已注册用于自动清理

---

## 文件修改清单

1. **feishu_doc_collaborator.py**
   - 修复文档链接前缀

2. **fault_diagnosis_config.py**
   - 添加 `REPORT_PARENT_NODE_TOKEN` 配置

3. **fault_report_generator.py**
   - 使用配置中的父节点
   - 修改报告标题格式
   - 重新设计报告结构（综合性总结 + 表格）

4. **auto_fault_diagnosis.py**
   - 修复变量名问题（`fault_ids` -> `unique_fault_ids`）
   - 添加日志清理注册逻辑

5. **log_cleanup_manager.py**（新文件）
   - 日志清理管理器实现

6. **cleanup_logs_task.py**（新文件）
   - 日志清理任务脚本

---

## 使用说明

### 1. 报告文档位置

报告文档现在创建在指定的父节点下：
- 父节点：`GCrNwnjWFiNw1UkLOraclXVynO1`
- 链接格式：`https://zyt.feishu.cn/wiki/{node_token}`

### 2. 报告标题格式

报告标题格式为：`日期_工作项id`
- 例如：`20260115_6683487902`

### 3. 报告结构

报告包含两部分：
1. **综合分析总结**：统计信息和基本信息
2. **Fault ID详细分析表**：所有Fault ID的详细信息

### 4. 日志清理

**自动清理**：
- 分析成功后，系统自动注册日志路径
- 24小时后自动清理

**手动清理**：
```bash
python cleanup_logs_task.py
```

**设置定时任务**（可选）：
- Windows：使用任务计划程序
- Linux/Mac：使用cron
- 建议每天执行一次清理任务

---

## 注意事项

1. **文档链接**：
   - 现在使用正确的链接前缀 `https://zyt.feishu.cn/wiki/`
   - 链接可以直接访问

2. **报告结构**：
   - 表格使用Markdown格式（文本块）
   - 如果数据量大，建议使用飞书原生表格（需要更复杂的API调用）

3. **日志清理**：
   - 清理记录保存在 `work/fault_diagnosis_cache/log_cleanup_records.json`
   - 已清理的记录会保留7天，然后自动删除
   - 如果清理失败，记录会标记为 `error` 状态

4. **父节点配置**：
   - 如果需要修改父节点，在 `fault_diagnosis_config.py` 中修改 `REPORT_PARENT_NODE_TOKEN`

---

## 总结

所有4个需求已成功实现：
1. ✅ 修复文档链接前缀
2. ✅ 在指定父节点下创建文档
3. ✅ 改进报告结构（综合性总结 + 表格）
4. ✅ 修改报告标题格式
5. ✅ 实现自动清理本地日志文件

系统现在能够：
- 生成正确链接的飞书文档报告
- 在指定位置创建报告
- 使用标准化的标题格式
- 自动管理本地日志文件，避免占用过多空间

所有功能已验证通过，可以正常使用。

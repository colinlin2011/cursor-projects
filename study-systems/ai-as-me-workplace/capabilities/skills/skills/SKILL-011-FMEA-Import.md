# SKILL-011: FMEA数据导入能力

**能力ID**：SKILL-011  
**能力名称**：FMEA数据导入能力  
**能力类型**：Skill  
**创建日期**：2026-01-17  
**最后更新**：2026-01-17  
**状态**：已发布

## 能力概述

将飞书在线表格中的FMEA（失效模式与影响分析）数据导入到飞书多维表格中，实现统一的数据管理和维护。支持完整的导入流程：架构元素 → 子功能清单 → 失效模式影响分析。

## 能力功能

### 核心功能

1. **架构元素导入**
   - 从FMEA数据提取Element Name
   - 自动创建或查找Control父元素
   - 支持从FMEA名称推断Element Name（当数据中为空时）
   - 批量导入架构元素

2. **子功能清单导入**
   - 处理合并单元格（Element Name列）
   - 过滤删除线和空内容的Function Description
   - 关联架构元素
   - 支持Element Name为空时的推断

3. **失效模式影响分析导入**
   - 处理Function Description合并单元格（一个功能对应多个Guide Word）
   - 导入引导词、失效模式、失效影响、SW_Safety Related字段
   - 关联子功能清单表的功能
   - 引导词选项值映射

### 辅助功能

- **富文本格式处理**：自动提取纯文本，检测删除线
- **合并单元格处理**：正确处理合并单元格，确保数据关联正确
- **跳过条目记录**：详细记录跳过的条目，便于人工检查
- **导入报告生成**：生成详细的导入报告，包含统计信息和错误详情
- **工作表指定**：支持指定要导入的工作表名称

## 技术实现

### 核心模块

1. **fmea_data_reader.py**
   - FMEA数据读取器
   - 支持自动识别主工作表或指定工作表
   - 处理富文本格式，提取纯文本

2. **import_architecture_elements.py**
   - 架构元素导入器
   - Element Name提取和推断
   - Control父元素自动管理

3. **import_functions.py**
   - 子功能导入器
   - 合并单元格处理
   - 删除线过滤
   - 架构元素关联

4. **import_failure_modes.py**
   - 失效模式导入器
   - 引导词映射
   - 双向关联字段处理

5. **import_fmea_complete.py**
   - 完整导入流程整合
   - 三步导入流程
   - 跳过条目详细记录
   - 导入报告生成

### 工具模块

- **fmea_import_utils.py** - 导入工具类
- **fmea_import_config.py** - 导入配置（字段映射、选项值映射等）
- **fmea_field_mapper.py** - 字段映射器

## 使用方法

### 基本用法

```bash
# 完整导入（三个步骤）
python import_fmea_complete.py <FMEA名称>

# 示例
python import_fmea_complete.py Control
python import_fmea_complete.py 04_Calibration_System_SW_FMEA
```

### 高级用法

```bash
# 指定工作表名称
python import_fmea_complete.py 10_Planning_System_SW_FMEA --sheet-name "System SW FMEA V0.2"

# 试运行模式（不实际导入数据）
python import_fmea_complete.py Control --dry-run

# 跳过某些步骤
python import_fmea_complete.py Control --skip-architecture
python import_fmea_complete.py Control --skip-functions
python import_fmea_complete.py Control --skip-fmea
```

### 交互式导入

```bash
# 交互式选择步骤
python interactive_fmea_import.py Control

# 指定步骤
python interactive_fmea_import.py Control --steps architecture,function,fmea
```

## 参数说明

### import_fmea_complete.py

- `fmea_name`（必需）：FMEA表格名称（如 Control, 04_Calibration_System_SW_FMEA）
- `--sheet-name` / `--sheet`（可选）：指定工作表名称，如果不指定则自动识别主工作表
- `--dry-run`（可选）：试运行模式，不实际导入数据
- `--skip-architecture`（可选）：跳过架构元素导入
- `--skip-functions`（可选）：跳过子功能导入
- `--skip-fmea`（可选）：跳过失效模式导入

### interactive_fmea_import.py

- `fmea_name`（必需）：FMEA表格名称
- `--steps`（可选）：要执行的步骤列表（architecture,function,fmea），用逗号分隔
- `--dry-run`（可选）：试运行模式

## 输出结果

### 导入报告

导入完成后会生成详细的导入报告，保存在 `work/fmea_complete_import_report_YYYYMMDD_HHMMSS.json`，包含：

- 导入时间戳
- FMEA表格名称
- 各步骤的导入结果
- 统计信息（总计、成功、失败、跳过）
- 跳过的条目详情（原因和相关数据）
- 错误详情

### 控制台输出

- 实时显示导入进度
- 显示跳过的条目详情
- 显示最终汇总统计

## 配置说明

### 字段映射

在 `fmea_import_config.py` 中配置字段映射关系：

```python
FIELD_MAPPING = {
    "Guide Word": "引导词",
    "Potential Failure Mode": "实际识别的失效模式",
    "Potential Failure Effect": "潜在失效影响",
    "Safety Related？": "SW_Safety Related",
    # ...
}
```

### 选项值映射

在 `fmea_import_config.py` 中配置选项值映射：

```python
GUIDE_WORD_MAPPING = {
    "no/loss": "缺失",
    "stuck": "错误",
    "earlier": "过早",
    "later": "过晚",
    # ...
}
```

## 依赖关系

### 外部依赖

- `feishu_api_wrapper.py` - 飞书API封装
- `feishu_bitable_collaborator.py` - 飞书多维表格协作器
- `token_manager.py` - Token管理
- `bitable_cache_manager.py` - 多维表格缓存管理

### 数据依赖

- FMEA表格缓存文件（`work/spreadsheet_cache/wiki_*.json`）
- 多维表格缓存文件（`work/bitable_cache/new_bitable.json`）

## 使用场景

1. **批量导入FMEA数据**：将多个FMEA表格的数据导入到多维表格
2. **数据迁移**：从在线表格迁移到多维表格
3. **数据同步**：定期同步FMEA数据更新
4. **数据验证**：通过试运行模式验证数据格式

## 注意事项

1. **数据格式**：确保FMEA表格包含必要的列（Element Name, Function Description, Guide Word等）
2. **缓存文件**：需要先同步FMEA表格缓存（使用`cache_wiki_spreadsheets.py`）
3. **权限要求**：需要有效的用户访问令牌（user_access_token）
4. **数据质量**：导入前建议先运行试运行模式检查数据
5. **跳过条目**：仔细检查跳过的条目，可能需要人工处理

## 已知限制

1. 目前只支持System SW FMEA类型的表格
2. 关联字段（如安全机制关联）需要单独处理
3. 大量数据导入可能需要较长时间

## 更新历史

- **2026-01-17**：初始版本发布
  - 实现架构元素、子功能、失效模式三个步骤的导入
  - 支持富文本格式处理、合并单元格处理
  - 支持Element Name推断、删除线过滤
  - 支持跳过条目详细记录、导入报告生成

## 相关文档

- `knowledge/technical/bitable-logic-framework.md` - 多维表格逻辑框架
- `knowledge/technical/fmea-tables-cache.md` - FMEA表格缓存知识库
- `work/projects/projects/20260117-fmea-import-capability.md` - 开发过程记录

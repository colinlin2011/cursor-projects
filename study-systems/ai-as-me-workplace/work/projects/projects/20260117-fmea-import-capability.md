# FMEA数据导入能力开发项目

**项目日期**：2026-01-17  
**项目类型**：能力开发  
**状态**：已完成

## 项目背景

需要将飞书在线表格中的FMEA（失效模式与影响分析）数据导入到飞书多维表格中，实现统一的数据管理和维护。涉及多个FMEA表格的批量导入，包括架构元素、子功能清单和失效模式影响分析三个维度的数据。

## 项目目标

1. 设计多维表格的逻辑框架，支持FMEA数据的统一管理
2. 开发FMEA数据导入工具，支持从在线表格导入到多维表格
3. 处理数据格式不一致、合并单元格、富文本格式等复杂情况
4. 实现完整的导入流程：架构元素 → 子功能清单 → 失效模式影响分析

## 开发过程

### 阶段1：需求分析与框架设计

**时间**：2026-01-17 上午

**工作内容**：
- 分析6个关键多维表格的结构（架构元素表、非期待事件表、子功能清单表、失效模式影响分析表_HW/SW、安全机制表）
- 设计逻辑框架，支持三个动态视图（需求识别、实现、缺陷闭环）
- 确定字段映射关系和优化建议

**成果**：
- `knowledge/technical/bitable-logic-framework.md` - 逻辑框架文档

### 阶段2：FMEA数据读取模块开发

**时间**：2026-01-17 下午

**工作内容**：
- 开发`fmea_data_reader.py`，实现从缓存文件读取FMEA数据
- 支持自动识别主工作表（System SW FMEA）
- 处理富文本格式，提取纯文本
- 支持指定工作表名称

**关键功能**：
- 自动识别主工作表
- 富文本格式处理（提取纯文本，检测删除线）
- 支持指定工作表名称

### 阶段3：架构元素导入模块开发

**时间**：2026-01-17 下午

**工作内容**：
- 开发`import_architecture_elements.py`
- 实现从FMEA数据提取Element Name
- 支持从FMEA名称推断Element Name（当数据中为空时）
- 自动创建或查找Control父元素
- 批量导入架构元素

**关键功能**：
- Element Name提取和推断
- Control父元素自动管理
- 批量导入支持

### 阶段4：子功能清单导入模块开发

**时间**：2026-01-17 下午

**工作内容**：
- 开发`import_functions.py`
- 处理合并单元格（Element Name列）
- 过滤删除线和空内容的Function Description
- 关联架构元素
- 支持Element Name为空时的推断

**关键功能**：
- 合并单元格处理
- 删除线过滤
- 架构元素关联
- Element Name推断

### 阶段5：失效模式导入模块开发

**时间**：2026-01-17 下午-晚上

**工作内容**：
- 开发`import_failure_modes.py`
- 处理Function Description合并单元格（一个功能对应多个Guide Word）
- 导入引导词、失效模式、失效影响、SW_Safety Related字段
- 关联子功能清单表的功能
- 引导词选项值映射

**关键功能**：
- 合并单元格处理（Function Description）
- 引导词映射（如"no/loss" → "缺失"）
- 双向关联字段处理
- 富文本格式处理

### 阶段6：完整导入流程整合

**时间**：2026-01-17 晚上

**工作内容**：
- 开发`import_fmea_complete.py`，整合三个导入步骤
- 实现跳过条目详细记录
- 支持指定工作表名称
- 生成详细导入报告

**关键功能**：
- 三步导入流程整合
- 跳过条目详细记录
- 工作表名称指定
- 导入报告生成

### 阶段7：问题修复与优化

**时间**：2026-01-17 晚上

**修复的问题**：
1. **富文本格式问题**：Function Description显示为富文本乱码
   - 修复：在数据读取时提取纯文本，在功能映射时使用纯文本匹配

2. **合并单元格问题**：Element Name和Function Description合并单元格导致数据关联错误
   - 修复：实现合并单元格填充逻辑，确保所有功能正确关联到架构元素

3. **Element Name为空问题**：08_SceneNet_System_SW_FMEA表格Element Name为空
   - 修复：从FMEA表格名称推断Element Name（如"08_SceneNet_System_SW_FMEA" → "SceneNet"）

4. **删除线过滤问题**：需要过滤带删除线的Function Description
   - 修复：在富文本提取时检测`strikeThrough`属性，返回None表示跳过

5. **跳过条目记录问题**：需要详细记录跳过的条目，便于人工检查
   - 修复：在各导入模块中记录跳过原因和相关数据，在最终报告中汇总显示

## 导入结果统计

### 已导入的FMEA表格

1. **Control_System_SW_FMEA**
   - 架构元素：5个（CtrlReciver, PoseCalc, Trajectory, Behavior, SafetyMonitor）
   - 子功能：199个
   - 失效模式：316条

2. **04_Calibration_System_SW_FMEA**
   - 架构元素：1个（Calibration，已存在）
   - 子功能：15个（新建3个，已存在12个）
   - 失效模式：132条

3. **05_EgoMotion_System_SW_FMEA**
   - 架构元素：1个（EgoMotion，已存在）
   - 子功能：31个（新建）
   - 失效模式：31条

4. **08_SceneNet_System_SW_FMEA**
   - 架构元素：1个（SceneNet，已存在）
   - 子功能：11个（新建）
   - 失效模式：11条

5. **10_Planning_System_SW_FMEA**（主工作表）
   - 架构元素：1个（Planning，已存在）
   - 子功能：2个（新建）
   - 失效模式：2条

6. **10_Planning_System_SW_FMEA**（System SW FMEA V0.2工作表）
   - 架构元素：6个（新建）
   - 子功能：27个（新建）
   - 失效模式：27条

## 技术要点

### 1. 富文本格式处理
- 检测`strikeThrough`属性，过滤带删除线的内容
- 提取纯文本，避免在关联字段中显示富文本乱码

### 2. 合并单元格处理
- Element Name列：填充空的Element Name为上一个非空值
- Function Description列：一个功能对应多个Guide Word，需要正确关联

### 3. Element Name推断
- 当Element Name为空时，从FMEA表格名称推断
- 支持从唯一非Control架构元素推断

### 4. 字段映射
- 引导词映射（"no/loss" → "缺失"，"Stuck" → "错误"等）
- Safety Related映射（"Yes"/"是" → "是"，"No"/"否" → "否"）

### 5. 跳过条目记录
- 记录跳过原因（找不到对应的功能/架构元素）
- 记录相关数据（功能描述、元素名称、引导词等）
- 在最终报告中汇总显示

## 项目成果

### 核心文件

1. **数据读取模块**
   - `fmea_data_reader.py` - FMEA数据读取器

2. **导入模块**
   - `import_architecture_elements.py` - 架构元素导入器
   - `import_functions.py` - 子功能导入器
   - `import_failure_modes.py` - 失效模式导入器
   - `import_fmea_complete.py` - 完整导入流程

3. **工具模块**
   - `fmea_import_utils.py` - 导入工具类
   - `fmea_import_config.py` - 导入配置
   - `fmea_field_mapper.py` - 字段映射器

4. **交互式导入**
   - `interactive_fmea_import.py` - 交互式导入脚本

### 配置文件

- `fmea_import_config.py` - 字段映射、选项值映射等配置

### 文档

- `knowledge/technical/bitable-logic-framework.md` - 多维表格逻辑框架
- `knowledge/technical/fmea-tables-cache.md` - FMEA表格缓存知识库

## 经验总结

### 成功经验

1. **模块化设计**：将导入流程拆分为三个独立模块，便于维护和扩展
2. **错误处理**：完善的错误处理和跳过条目记录，便于问题排查
3. **灵活性**：支持指定工作表、跳过步骤、试运行等灵活配置
4. **数据质量**：处理富文本、合并单元格等复杂情况，确保数据质量

### 改进建议

1. **性能优化**：对于大量数据，可以考虑并行处理
2. **增量导入**：支持增量导入，避免重复导入已存在的数据
3. **数据验证**：增加更严格的数据验证，提前发现数据问题
4. **回滚机制**：支持导入回滚，便于错误恢复

## 后续工作

1. 封装为标准的Skill能力
2. 创建使用文档和示例
3. 注册到能力注册表
4. 支持更多FMEA表格的导入

# FMEA数据导入快速开始指南

**能力ID**：SKILL-011  
**最后更新**：2026-01-17

## 快速开始

### 基本用法

```bash
# 完整导入（三个步骤：架构元素 → 子功能 → 失效模式）
python import_fmea_complete.py <FMEA名称>

# 示例
python import_fmea_complete.py Control
python import_fmea_complete.py 04_Calibration_System_SW_FMEA
```

### 指定工作表

```bash
# 如果FMEA表格有多个工作表，可以指定要导入的工作表
python import_fmea_complete.py 10_Planning_System_SW_FMEA --sheet-name "System SW FMEA V0.2"
```

### 试运行模式

```bash
# 试运行模式，不实际导入数据，用于检查数据格式
python import_fmea_complete.py Control --dry-run
```

### 跳过某些步骤

```bash
# 只导入失效模式（假设架构元素和子功能已存在）
python import_fmea_complete.py Control --skip-architecture --skip-functions

# 只导入架构元素和子功能
python import_fmea_complete.py Control --skip-fmea
```

## 完整参数说明

| 参数 | 说明 | 必需 | 示例 |
|------|------|------|------|
| `fmea_name` | FMEA表格名称 | 是 | `Control`、`04_Calibration_System_SW_FMEA` |
| `--sheet-name` / `--sheet` | 指定工作表名称 | 否 | `"System SW FMEA V0.2"` |
| `--dry-run` | 试运行模式 | 否 | - |
| `--skip-architecture` | 跳过架构元素导入 | 否 | - |
| `--skip-functions` | 跳过子功能导入 | 否 | - |
| `--skip-fmea` | 跳过失效模式导入 | 否 | - |

## 导入流程

1. **步骤0**：获取用户访问令牌
2. **步骤0.5**：读取FMEA数据（从缓存文件）
3. **步骤0.6**：获取多维表格信息
4. **步骤1**：导入架构元素
   - 自动创建或查找Control父元素
   - 提取Element Name
   - 批量导入架构元素
5. **步骤2**：导入子功能清单
   - 处理合并单元格（Element Name列）
   - 过滤删除线和空内容
   - 关联架构元素
6. **步骤3**：导入失效模式影响分析
   - 处理Function Description合并单元格
   - 导入引导词、失效模式、失效影响、SW_Safety Related
   - 关联子功能清单表的功能

## 输出结果

### 控制台输出

导入过程中会实时显示：
- 导入进度
- 跳过的条目详情
- 最终汇总统计

### 导入报告

导入完成后会生成详细的导入报告，保存在：
```
work/fmea_complete_import_report_YYYYMMDD_HHMMSS.json
```

报告包含：
- 导入时间戳
- FMEA表格名称
- 各步骤的导入结果
- 统计信息（总计、成功、失败、跳过）
- 跳过的条目详情（原因和相关数据）
- 错误详情

## 常见问题

### 1. 找不到FMEA缓存文件

**问题**：`[X] 未找到FMEA缓存文件: <FMEA名称>`

**解决方案**：
```bash
# 先同步FMEA表格缓存
python cache_wiki_spreadsheets.py --force-refresh
```

### 2. Element Name为空

**问题**：某些FMEA表格的Element Name列为空

**解决方案**：
- 工具会自动从FMEA表格名称推断Element Name
- 例如：`08_SceneNet_System_SW_FMEA` → `SceneNet`

### 3. 功能关联错误

**问题**：功能被错误关联到其他架构元素

**解决方案**：
- 检查FMEA表格中的Element Name列是否正确
- 如果Element Name为空，工具会尝试推断
- 可以使用`fix_function_relations.py`修正已导入的数据

### 4. 富文本乱码

**问题**：关联功能字段显示为富文本乱码

**解决方案**：
- 工具已自动处理富文本格式，提取纯文本
- 如果仍有问题，可以使用`fix_fmea_function_relations_direct.py`修正

### 5. 跳过条目过多

**问题**：导入时跳过了很多条目

**解决方案**：
- 查看导入报告中的跳过条目详情
- 检查FMEA表格数据格式是否正确
- 确认Function Description不为空且没有删除线
- 确认Element Name正确或可以推断

## 使用示例

### 示例1：导入Control模块

```bash
python import_fmea_complete.py Control
```

**预期结果**：
- 架构元素：5个（CtrlReciver, PoseCalc, Trajectory, Behavior, SafetyMonitor）
- 子功能：199个
- 失效模式：316条

### 示例2：导入指定工作表

```bash
python import_fmea_complete.py 10_Planning_System_SW_FMEA --sheet-name "System SW FMEA V0.2"
```

**预期结果**：
- 架构元素：6个
- 子功能：27个
- 失效模式：27条

### 示例3：试运行检查

```bash
python import_fmea_complete.py 04_Calibration_System_SW_FMEA --dry-run
```

**用途**：检查数据格式，不实际导入数据

## 注意事项

1. **数据格式**：确保FMEA表格包含必要的列（Element Name, Function Description, Guide Word等）
2. **缓存文件**：需要先同步FMEA表格缓存（使用`cache_wiki_spreadsheets.py`）
3. **权限要求**：需要有效的用户访问令牌（user_access_token）
4. **数据质量**：导入前建议先运行试运行模式检查数据
5. **跳过条目**：仔细检查跳过的条目，可能需要人工处理

## 相关文档

- [SKILL-011能力定义](SKILL-011-FMEA-Import.md)
- [开发过程记录](../../../work/projects/projects/20260117-fmea-import-capability.md)
- [多维表格逻辑框架](../../../knowledge/technical/bitable-logic-framework.md)

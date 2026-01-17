# 故障概况提取能力

**Tool ID**：SKILL-009  
**Tool名称**：故障概况提取能力  
**创建日期**：2026-01-16  
**最后更新**：2026-01-16  
**版本**：v1.0  
**状态**：可用  
**维护人**：系统

---

## 工具描述

### 功能概述

故障概况提取能力是一个综合性的故障信息整合工具，能够从多个数据源提取fa_id相关信息，生成综合故障概况：

- **故障定位指引文档**：从飞书Wiki的故障定位指引文档中获取故障定位方法
- **06. 安全需求总表**：从多维表格缓存中查询安全需求相关信息
- **功能安全业务数据**：从功能安全业务数据多维表格中提取故障概要信息

### 适用场景

- 故障分析：快速获取故障的全面信息
- 故障定位：整合多个来源的故障信息，辅助定位
- 报告生成：自动生成故障概况，用于报告和文档

---

## 核心功能

### 1. 多源信息整合

从三个主要来源提取信息：

1. **故障定位指引文档**
   - 故障定位方法
   - grep命令和查询模式
   - 故障原因分析

2. **06. 安全需求总表**
   - 安全需求信息
   - ASIL等级
   - 涉及模块和功能
   - 触发条件

3. **功能安全业务数据**
   - 故障名称和描述
   - 故障概要信息
   - 可能的原因

### 2. 智能查询

- **自动选择查询方式**：数据量大时自动使用grep方式
- **模糊匹配**：支持多种fa_id格式（0x0165、0x165、165等）
- **高效查询**：基于缓存的快速查询

### 3. 综合概况生成

自动整合多个来源的信息，生成结构化的故障概况文本。

---

## 工具接口

### 接口定义

```python
from fault_summary_extractor import FaultSummaryExtractor, extract_fault_summary

# 方式1：使用类
extractor = FaultSummaryExtractor()
result = extractor.extract_fault_summary(
    fa_id: str,           # Fault ID（如0x0165）
    use_grep: bool = True # 是否使用grep查询（数据量大时使用）
) -> Dict[str, Any]

# 方式2：使用便捷函数
result = extract_fault_summary(fa_id="0x0165", use_grep=True)
```

### 参数说明

#### fa_id (必需)

Fault ID，支持多种格式：
- `"0x0165"` - 标准格式
- `"0x165"` - 无前导0格式
- `"165"` - 纯数字格式

#### use_grep (可选，默认True)

是否使用grep查询方式：
- `True`：数据量大时使用grep方式（推荐）
- `False`：遍历所有记录（适用于小数据量）

### 返回值

```python
{
    'fault_id': '0x0165',                    # 规范化后的Fault ID
    'guide_info': {...},                     # 指引文档信息（如果有）
    'safety_requirement_info': {...},        # 安全需求总表信息（如果有）
    'bitable_summary': '...',                # 功能安全业务数据概要（如果有）
    'summary_text': '...'                    # 综合故障概况文本
}
```

---

## 使用示例

### 示例1：基本使用

```python
from fault_summary_extractor import extract_fault_summary

# 提取0x165的故障概况
result = extract_fault_summary("0x165")

# 查看综合概况
print(result['summary_text'])

# 查看各个来源的信息
if result['guide_info']:
    print("指引文档:", result['guide_info'])

if result['safety_requirement_info']:
    print("安全需求:", result['safety_requirement_info'])
```

### 示例2：在SSH日志查询中自动使用

```python
from ssh_log_query_engine import create_query_engine

engine = create_query_engine()
result = engine.query_setfunc_fault(
    base_path="/rawdata/roadtestv3/.../",
    output_format="both"
)

# 结果中自动包含故障概况
if 'json' in result and 'fault_summaries' in result['json']:
    for fa_id, summary in result['json']['fault_summaries'].items():
        print(f"FA_ID {fa_id} 的故障概况:")
        print(summary['summary_text'])
```

### 示例3：单独提取故障概况

```python
from fault_summary_extractor import FaultSummaryExtractor

extractor = FaultSummaryExtractor()

# 提取多个fa_id的概况
fa_ids = ["0x0165", "0x013a", "0x0902"]
summaries = {}

for fa_id in fa_ids:
    summary = extractor.extract_fault_summary(fa_id)
    summaries[fa_id] = summary['summary_text']

# 输出所有概况
for fa_id, summary_text in summaries.items():
    print(f"\n{'='*80}")
    print(f"FA_ID: {fa_id}")
    print(f"{'='*80}")
    print(summary_text)
```

---

## 实现细节

### 数据源配置

- **故障定位指引文档**：通过 `fault_guide_reader.py` 访问
- **06. 安全需求总表**：从 `new_bitable.json` 缓存中查询
- **功能安全业务数据**：通过 `fault_summary_grep.py` 查询

### 查询逻辑

1. **规范化fa_id**：统一转换为 `0x0165` 格式
2. **多模式匹配**：支持多种fa_id格式的匹配
3. **智能查询**：根据数据量自动选择查询方式
4. **信息整合**：合并多个来源的信息

### 输出格式

综合故障概况文本包含：
- 故障定位指引（如果有）
- 安全需求总表信息（如果有）
- 功能安全业务数据概要（如果有）

---

## 集成说明

### 与SSH日志查询引擎集成

故障概况提取能力已集成到 `SSHLogQueryEngine.query_setfunc_fault()` 方法中：

- 自动提取所有唯一fa_id的故障概况
- 在JSON和文本输出中都包含故障概况
- 无需额外调用

### 独立使用

也可以独立使用，不依赖SSH日志查询：

```python
from fault_summary_extractor import extract_fault_summary

summary = extract_fault_summary("0x0165")
print(summary['summary_text'])
```

---

## 注意事项

1. **缓存依赖**：
   - 需要确保多维表格缓存已同步（`new_bitable.json`）
   - 需要确保故障定位指引文档缓存已同步

2. **数据量**：
   - 数据量大时建议使用 `use_grep=True`（默认）
   - 小数据量时可以设置 `use_grep=False` 进行精确匹配

3. **错误处理**：
   - 如果某个数据源不可用，会继续从其他数据源提取信息
   - 所有数据源都不可用时，返回"未找到相关信息"

---

## 故障排查

### 问题1：未找到安全需求总表信息

**可能原因**：
- 缓存文件不存在或未同步
- 表名不匹配（应为"06. 安全需求总表"）

**解决方案**：
1. 运行 `python auto_sync_all.py --once` 同步缓存
2. 检查缓存文件 `work/bitable_cache/new_bitable.json` 是否存在

### 问题2：grep查询失败

**可能原因**：
- 数据格式问题
- 正则表达式匹配失败

**解决方案**：
- 尝试设置 `use_grep=False` 使用遍历方式

---

## 关联记录

### 相关能力

- **SKILL-008**：SSH日志泛化查询引擎（已集成故障概况提取）
- **故障定位系统**：故障定位指引文档读取

### 相关文件

- `fault_summary_extractor.py` - 核心实现
- `fault_summary_grep.py` - 功能安全业务数据查询
- `fault_guide_reader.py` - 故障定位指引文档读取
- `bitable_query_interface.py` - 多维表格查询接口

---

## 工具版本历史

| 版本 | 日期 | 更新内容 | 更新人 |
|------|------|---------|--------|
| v1.0 | 2026-01-16 | 初始创建 | 系统 |

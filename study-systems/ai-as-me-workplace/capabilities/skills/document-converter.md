# 文档转换Skill

**Skill ID**：SKILL-010  
**Skill名称**：Markdown转Word文档转换器  
**创建日期**：2025-01-15  
**最后更新**：2025-01-15  
**版本**：v1.0  
**状态**：可用  
**维护人**：系统

---

## Skill描述

### 功能概述
将Markdown格式的文档转换为Word格式（.docx），支持批量转换、自定义模板、格式保持等功能。特别适用于工作文档、项目文档、报告等正式文档的格式转换。

### 适用场景
- 工作文档转换（项目文档、会议纪要、报告等）
- 技术文档转换（设计文档、技术方案、评审文档等）
- 管理文档转换（工作计划、工作总结、汇报材料等）
- 批量文档转换

### 不适用场景
- 需要复杂排版的文档（建议使用专业排版工具）
- 包含大量图表的文档（图表可能需要手动调整）
- 需要实时编辑的文档（建议直接使用Word）

---

## Skill接口

### 调用方式
- **方式**：Python模块调用
- **接口地址**：`capabilities/skills/document-converter/converter.py`
- **调用示例**：
  ```python
  from capabilities.skills.document_converter import convert_markdown_to_word
  
  result = convert_markdown_to_word(
      source_file="work/documents/documents/20260113-report.md",
      output_file="word-output/report.docx"
  )
  ```

### 输入参数
| 参数名 | 类型 | 必填 | 默认值 | 描述 |
|--------|------|------|--------|------|
| source_file | string | 是 | - | 源Markdown文件路径 |
| output_file | string | 否 | 自动生成 | 输出Word文件路径 |
| template_file | string | 否 | None | Word模板文件路径（可选） |
| output_dir | string | 否 | word-output | 输出目录 |
| batch_mode | boolean | 否 | False | 是否批量转换模式 |

### 输出结果
- **结果格式**：字典
- **结果示例**：
  ```python
  {
      "success": True,
      "output_file": "word-output/report.docx",
      "message": "转换成功"
  }
  ```
- **错误码**：
  - `SUCCESS`: 转换成功
  - `FILE_NOT_FOUND`: 源文件不存在
  - `PANDOC_NOT_FOUND`: Pandoc未安装
  - `CONVERSION_FAILED`: 转换失败
  - `DEPENDENCY_MISSING`: 依赖缺失

### 错误处理
| 错误码 | 错误信息 | 处理方式 |
|--------|---------|---------|
| FILE_NOT_FOUND | 源文件不存在 | 检查文件路径是否正确 |
| PANDOC_NOT_FOUND | Pandoc未安装 | 安装Pandoc或使用Docker版本 |
| CONVERSION_FAILED | 转换失败 | 检查文件格式和依赖 |
| DEPENDENCY_MISSING | 依赖缺失 | 安装pypandoc: pip install pypandoc |

---

## Skill使用示例

### 示例1：单个文件转换
```python
from capabilities.skills.document_converter import convert_markdown_to_word

# 转换工作文档
result = convert_markdown_to_word(
    source_file="work/documents/documents/20260113-safety-plan.md",
    output_file="word-output/safety-plan.docx"
)

if result["success"]:
    print(f"转换成功: {result['output_file']}")
else:
    print(f"转换失败: {result['message']}")
```

### 示例2：批量转换
```python
from capabilities.skills.document_converter import batch_convert_to_word

# 批量转换工作文档
files = [
    {"source": "work/documents/documents/20260113-report.md", "output": "report.docx"},
    {"source": "work/documents/documents/20260113-plan.md", "output": "plan.docx"},
]

results = batch_convert_to_word(files, output_dir="word-output")
for result in results:
    print(f"{result['file']}: {result['status']}")
```

### 示例3：使用命令行
```bash
# 单个文件转换
python capabilities/skills/document-converter/converter.py \
    --source work/documents/documents/20260113-report.md \
    --output word-output/report.docx

# 批量转换
python capabilities/skills/document-converter/converter.py \
    --batch \
    --source-dir work/documents/documents \
    --output-dir word-output
```

---

## Skill集成

### 依赖项
- **pypandoc**: >=1.11
- **pandoc**: >=3.0（需要系统安装或使用Docker）

### 配置项
| 配置项 | 类型 | 默认值 | 描述 |
|--------|------|--------|------|
| pandoc_path | string | "pandoc" | Pandoc可执行文件路径 |
| template_path | string | None | 默认模板文件路径 |
| output_dir | string | "word-output" | 默认输出目录 |
| use_docker | boolean | False | 是否使用Docker版本 |

### 环境要求
- **操作系统**：Windows/Linux/macOS
- **运行时**：Python 3.7+
- **其他要求**：
  - Pandoc（本地安装或Docker）
  - pypandoc Python包

### 安装步骤
1. **安装Python依赖**：
   ```bash
   pip install -r capabilities/skills/document-converter/requirements.txt
   ```

2. **安装Pandoc**（选择一种方式）：
   - **方式1（推荐）**：使用Docker
     ```bash
     docker pull pandoc/latex:latest
     ```
   - **方式2**：本地安装
     - Windows: `winget install --id JohnMacFarlane.Pandoc`
     - 或下载：https://pandoc.org/installing.html

3. **验证安装**：
   ```bash
   pandoc --version
   ```

---

## Skill使用记录

### 使用统计
- **总调用次数**：0
- **成功次数**：0
- **失败次数**：0
- **成功率**：0%

### 使用历史
| 日期 | 调用次数 | 成功率 | 平均响应时间 | 备注 |
|------|---------|--------|------------|------|
| - | - | - | - | - |

### 效果分析
- **优点**：
  - 支持批量转换
  - 格式保持良好
  - 支持自定义模板
  - 跨平台支持
- **缺点**：
  - 需要安装Pandoc
  - 复杂格式可能需要手动调整
- **改进建议**：
  - 添加进度显示
  - 支持更多输出格式
  - 添加格式验证

---

## Skill版本历史

| 版本 | 日期 | 更新内容 | 更新人 |
|------|------|---------|--------|
| v1.0 | 2025-01-15 | 初始版本，支持Markdown转Word | 系统 |

---

## 关联记录

### 相关注册表
- [能力注册表](../registry.md)

### 相关使用记录
- [使用记录](../usage/usage-history.md)

### 相关知识库
- [文档处理知识库](../../knowledge/)

### 相关模式
- [文档处理模式](../../knowledge/patterns/)

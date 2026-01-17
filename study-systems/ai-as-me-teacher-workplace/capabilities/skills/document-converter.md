# 文档转换Skill

**Skill ID**：SKILL-DOC-CONVERT-001  
**Skill名称**：Markdown转Word文档转换器  
**创建日期**：2025-01-15  
**最后更新**：2025-01-15  
**版本**：v1.0  
**状态**：可用  
**维护人**：系统

---

## Skill描述

### 功能概述
将Markdown格式的文档转换为Word格式（.docx），支持批量转换、自定义模板、格式保持等功能。特别适用于专利申请文档、工作文档、报告等正式文档的格式转换。

### 适用场景
- 专利申请文档转换（权利要求书、说明书、摘要等）
- 工作文档转换（项目文档、会议纪要、报告等）
- 教学文档转换（课程设计、教案、教学材料等）
- 科研文档转换（论文、课题申报书、研究报告等）
- 批量文档转换

### 不适用场景
- 需要复杂排版的文档（建议使用专业排版工具）
- 包含大量图表的文档（图表可能需要手动调整）
- 需要实时编辑的文档（建议直接使用Word）

---

## Skill接口

### 调用方式
- **方式**：Python脚本调用
- **接口地址**：`capabilities/skills/document-converter/convert_to_word.py`
- **调用示例**：
  ```python
  from capabilities.skills.document_converter import convert_markdown_to_word
  
  result = convert_markdown_to_word(
      source_file="patent/03-权利要求书.md",
      output_file="word-output/权利要求书.docx"
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
      "output_file": "word-output/权利要求书.docx",
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

# 转换权利要求书
result = convert_markdown_to_word(
    source_file="patent/03-权利要求书.md",
    output_file="word-output/权利要求书.docx"
)

if result["success"]:
    print(f"转换成功: {result['output_file']}")
else:
    print(f"转换失败: {result['message']}")
```

### 示例2：批量转换
```python
from capabilities.skills.document_converter import batch_convert_to_word

# 批量转换专利申请文档
files = [
    {"source": "patent/03-权利要求书.md", "output": "权利要求书.docx"},
    {"source": "patent/04-说明书.md", "output": "说明书.docx"},
    {"source": "patent/05-说明书摘要.md", "output": "说明书摘要.docx"},
]

results = batch_convert_to_word(files, output_dir="word-output")
for result in results:
    print(f"{result['file']}: {result['status']}")
```

### 示例3：使用命令行
```bash
# 单个文件转换
python capabilities/skills/document-converter/convert_to_word.py \
    --source patent/03-权利要求书.md \
    --output word-output/权利要求书.docx

# 批量转换
python capabilities/skills/document-converter/convert_to_word.py \
    --batch \
    --source-dir patent \
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
   pip install pypandoc
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
- [文档转换知识库](../../knowledge/)

### 相关模式
- [文档处理模式](../../knowledge/patterns/)

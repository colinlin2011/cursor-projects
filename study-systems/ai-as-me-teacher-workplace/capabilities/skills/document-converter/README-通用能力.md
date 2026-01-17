# 文档转换通用能力

## 概述

文档转换Skill已封装为通用能力，可在以下两个项目中复用：
- `ai-as-me-teacher-workplace`：用于专利申请文档、教学文档转换
- `ai-as-me-workplace`：用于工作文档、项目文档转换

## 能力位置

### ai-as-me-teacher-workplace
- **能力定义**：`capabilities/skills/document-converter.md`
- **实现代码**：`capabilities/skills/document-converter/converter.py`
- **能力ID**：SKILL-DOC-CONVERT-001
- **注册表**：`capabilities/registry.md`

### ai-as-me-workplace
- **能力定义**：`capabilities/skills/document-converter.md`
- **实现代码**：`capabilities/skills/document-converter/converter.py`
- **能力ID**：SKILL-010
- **注册表**：`capabilities/registry.md`

## 核心功能

1. **单个文件转换**：将单个Markdown文件转换为Word文档
2. **批量转换**：批量转换多个Markdown文件
3. **自定义模板**：支持使用Word模板文件
4. **依赖检查**：自动检查并安装依赖
5. **错误处理**：完善的错误处理和提示

## 使用方法

### Python调用

```python
from capabilities.skills.document_converter import convert_markdown_to_word

result = convert_markdown_to_word(
    source_file="document.md",
    output_file="document.docx"
)
```

### 命令行调用

```bash
python capabilities/skills/document-converter/converter.py \
    --source document.md \
    --output document.docx
```

## 文件结构

```
capabilities/skills/document-converter/
├── __init__.py              # 模块初始化
├── converter.py             # 核心转换逻辑
├── requirements.txt         # Python依赖
├── README.md               # 快速开始
└── 使用指南.md              # 详细使用指南
```

## 依赖要求

- **Python**: 3.7+
- **pypandoc**: >=1.11
- **pandoc**: >=3.0（需要系统安装）

## 安装步骤

1. 安装Python依赖：
   ```bash
   pip install -r capabilities/skills/document-converter/requirements.txt
   ```

2. 安装Pandoc：
   ```bash
   winget install --id JohnMacFarlane.Pandoc
   ```

## 在两个项目中使用

### ai-as-me-teacher-workplace

```python
# 转换专利申请文档
from capabilities.skills.document_converter import convert_markdown_to_word

result = convert_markdown_to_word(
    source_file="patent/03-权利要求书.md",
    output_file="patent/word-output/权利要求书.docx"
)
```

### ai-as-me-workplace

```python
# 转换工作文档
from capabilities.skills.document_converter import convert_markdown_to_word

result = convert_markdown_to_word(
    source_file="work/documents/documents/20260113-report.md",
    output_file="word-output/report.docx"
)
```

## 能力注册

### ai-as-me-teacher-workplace
- **注册表**：`capabilities/registry.md`
- **能力ID**：SKILL-DOC-CONVERT-001
- **状态**：可用

### ai-as-me-workplace
- **注册表**：`capabilities/registry.md`
- **能力ID**：SKILL-010
- **状态**：可用

## 相关文档

- **能力定义**：`document-converter.md`
- **使用指南**：`使用指南.md`
- **快速开始**：`README.md`
- **能力注册表**：`../registry.md`

## 更新记录

- **2025-01-15**：初始版本，封装为通用能力
- 支持两个项目复用
- 完整的错误处理和依赖检查
- 支持单个和批量转换

# 文档转换Skill

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

还需要安装Pandoc：
- Windows: `winget install --id JohnMacFarlane.Pandoc`
- 或访问: https://pandoc.org/installing.html

### 使用方法

#### Python调用

```python
from capabilities.skills.document_converter import convert_markdown_to_word

result = convert_markdown_to_word(
    source_file="work/documents/documents/20260113-report.md",
    output_file="word-output/report.docx"
)
```

#### 命令行调用

```bash
python converter.py --source work/documents/documents/20260113-report.md --output word-output/report.docx
```

## 详细文档

查看 [document-converter.md](../document-converter.md) 了解完整文档。

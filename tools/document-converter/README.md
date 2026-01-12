# 文档转换工具

## 功能介绍

将PDF、Word、Excel等办公文档转换为Markdown格式，方便AI助手（Cursor）读取和分析文档内容。

## 支持的文件类型

- **PDF** (.pdf) - 使用PyMuPDF
- **Word** (.docx, .doc) - 使用python-docx
- **Excel** (.xlsx, .xls) - 使用pandas

## 安装依赖

```bash
pip install -r requirements.txt
```

或者单独安装：

```bash
# PDF支持
pip install pymupdf

# Word支持
pip install python-docx

# Excel支持
pip install pandas openpyxl tabulate
```

## 使用方法

### 方法1：使用Streamlit UI（推荐）

```bash
streamlit run main.py
```

然后在浏览器中打开显示的URL（通常是 http://localhost:8501）

### 方法2：命令行使用

```python
from utils.document_converter import DocumentConverter

converter = DocumentConverter()

# 转换PDF
result, success = converter.convert_pdf_to_markdown("input.pdf", "output.md")

# 转换Word
result, success = converter.convert_word_to_markdown("input.docx", "output.md")

# 转换Excel
result, success = converter.convert_excel_to_markdown("input.xlsx", "output.md")

# 自动识别文件类型
result, success = converter.convert("input.pdf", "output.md")
```

## 使用场景

### 场景1：转换标准文档供AI分析

1. 将组合辅助驾驶强标PDF转换为Markdown
2. 保存到 `study-systems/autonomous-safety-study/materials/01_Standards/`
3. AI助手可以直接读取和分析

### 场景2：转换现有材料文档

1. 从飞书Wiki或Polarion导出Word/PDF文档
2. 转换为Markdown格式
3. 保存到对应的材料目录
4. AI助手可以读取并帮助完善条款对应矩阵

## 转换特性

- **PDF**: 提取文本内容，保留页面结构
- **Word**: 保留标题层级、段落、表格
- **Excel**: 转换为Markdown表格格式

## 注意事项

1. PDF转换可能无法完美保留复杂格式
2. Word中的图片不会被提取（仅提取文本）
3. Excel中的公式会显示为计算结果
4. 转换后的Markdown文件使用UTF-8编码

## 项目结构

```
document-converter/
├── main.py                 # Streamlit主程序
├── config.py              # 配置文件
├── requirements.txt       # 依赖列表
├── README.md             # 说明文档
└── utils/
    ├── __init__.py
    └── document_converter.py  # 核心转换模块
```

## 快速开始

1. 安装依赖：`pip install -r requirements.txt`
2. 运行工具：`streamlit run main.py`
3. 上传文档并转换
4. 下载或保存Markdown文件

## 故障排除

### PDF转换失败
- 确保安装了 `pymupdf`: `pip install pymupdf`
- 某些加密的PDF可能无法转换

### Word转换失败
- 确保安装了 `python-docx`: `pip install python-docx`
- 旧版.doc格式支持有限，建议使用.docx

### Excel转换失败
- 确保安装了 `pandas` 和 `openpyxl`: `pip install pandas openpyxl`
- 大文件可能需要较长时间

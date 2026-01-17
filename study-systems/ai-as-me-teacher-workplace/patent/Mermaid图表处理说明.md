# Mermaid图表处理说明

## 转换结果

所有专利文档已成功转换为Word格式，保存在各自的 `word-output/` 目录中。

**专利2-物流数字孪生教学平台**：
- 位置：`patent/专利2-物流数字孪生教学平台/word-output/`
- 包含7个Word文档

**专利3-物流实践课程智能设计系统**：
- 位置：`patent/专利3-物流实践课程智能设计系统/word-output/`
- 包含7个Word文档

## Mermaid图表处理

Mermaid图表代码已保留在Word文档中（在 `06-附图（Mermaid图表）.docx` 文件中），但需要转换为图片格式才能作为正式专利附图使用。

### 方法1：使用在线工具（推荐，最简单）

1. **访问 Mermaid Live Editor**：https://mermaid.live/
2. **复制Mermaid代码**：从Word文档中复制Mermaid代码块
3. **粘贴到编辑器**：将代码粘贴到在线编辑器中
4. **导出图片**：点击"Actions" → "Download PNG" 或 "Download SVG"
5. **插入Word**：将下载的图片插入到Word文档的相应位置

### 方法2：使用Mermaid CLI（适合批量处理）

1. **安装Node.js**：https://nodejs.org/
2. **安装Mermaid CLI**：
   ```bash
   npm install -g @mermaid-js/mermaid-cli
   ```
3. **转换Mermaid文件**：
   ```bash
   mmdc -i input.mmd -o output.png
   ```
4. **批量转换**：可以编写脚本批量转换所有图表

### 方法3：使用Python工具

1. **安装依赖**：
   ```bash
   pip install mermaid
   ```
2. **使用Python脚本转换**（需要安装Playwright）：
   ```python
   from mermaid import Mermaid
   m = Mermaid()
   m.render('graph TB\n    A-->B', output='output.png')
   ```

### 方法4：使用VS Code插件

1. **安装插件**：在VS Code中安装 "Markdown Preview Mermaid Support"
2. **预览图表**：打开包含Mermaid代码的Markdown文件
3. **导出图片**：右键点击预览的图表，选择"Save Image"

## 专利附图要求

根据专利局要求，附图需要满足以下条件：

1. **格式**：PNG、JPG或PDF格式
2. **分辨率**：建议300 DPI以上
3. **尺寸**：A4纸张大小，留出页边距
4. **清晰度**：文字清晰可读，线条清晰
5. **编号**：按照图1、图2、图3...的顺序编号

## 建议的处理流程

1. **打开Word文档**：打开 `06-附图（Mermaid图表）.docx`
2. **逐个处理图表**：
   - 复制每个Mermaid代码块
   - 使用在线工具转换为PNG图片
   - 将图片插入到Word文档的相应位置
   - 删除原始代码块
3. **调整图片**：
   - 调整图片大小以适应页面
   - 确保文字清晰可读
   - 添加图号（图1、图2等）
4. **检查完整性**：确保所有图表都已转换并插入

## 快速处理脚本（可选）

如果需要批量处理，可以使用以下Python脚本：

```python
import subprocess
import re
from pathlib import Path

def extract_mermaid_blocks(md_file):
    """从Markdown文件中提取Mermaid代码块"""
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 匹配mermaid代码块
    pattern = r'```mermaid\n(.*?)```'
    matches = re.findall(pattern, content, re.DOTALL)
    return matches

def convert_mermaid_to_png(mermaid_code, output_file):
    """使用mermaid-cli转换Mermaid代码为PNG"""
    # 创建临时文件
    temp_file = Path('temp.mmd')
    temp_file.write_text(mermaid_code, encoding='utf-8')
    
    try:
        # 使用mmdc转换
        subprocess.run(['mmdc', '-i', str(temp_file), '-o', str(output_file)], check=True)
        return True
    except:
        return False
    finally:
        if temp_file.exists():
            temp_file.unlink()

# 使用示例
md_file = Path('06-附图（Mermaid图表）.md')
mermaid_blocks = extract_mermaid_blocks(md_file)

for i, code in enumerate(mermaid_blocks, 1):
    output = Path(f'图{i}.png')
    if convert_mermaid_to_png(code, output):
        print(f'图{i}转换成功')
```

## 注意事项

1. **保持原代码**：建议保留原始的Mermaid代码，以便后续修改
2. **检查准确性**：转换后检查图片是否与代码一致
3. **文件命名**：使用清晰的命名规则（如：图1-系统整体架构图.png）
4. **备份文件**：转换前备份原始Word文档

## 技术支持

如有问题，请参考：
- Mermaid官方文档：https://mermaid.js.org/
- Mermaid Live Editor：https://mermaid.live/
- Mermaid CLI文档：https://github.com/mermaid-js/mermaid-cli

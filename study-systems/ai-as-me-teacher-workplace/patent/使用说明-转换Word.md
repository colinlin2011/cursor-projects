# 专利申请文档转Word使用说明

本文档说明如何将Markdown格式的专利申请文档转换为Word格式。

## 方法1：使用Python脚本（推荐）

### 前置要求

1. **安装Python**
   - 确保已安装Python 3.7或更高版本
   - 下载地址：https://www.python.org/downloads/

2. **安装pandoc**
   - Windows: 下载安装包 https://github.com/jgm/pandoc/releases
   - 或使用Chocolatey: `choco install pandoc`
   - 或使用Scoop: `scoop install pandoc`

3. **安装Python依赖**
   ```bash
   pip install -r requirements.txt
   ```
   或直接安装：
   ```bash
   pip install pypandoc
   ```

### 使用方法

1. **打开终端/命令行**
   - 在patent目录下打开终端
   - 或使用Cursor/VSCode的集成终端

2. **运行转换脚本**
   ```bash
   python convert_to_word.py
   ```

3. **查看输出**
   - 转换后的Word文档将保存在 `word-output/` 目录
   - 脚本会自动打开输出目录

### 输出文件

转换后的文件：
- `权利要求书.docx`
- `说明书.docx`
- `说明书摘要.docx`
- `附图说明.docx`

可选文件（根据提示选择）：
- `技术方案分析.docx`
- `专利申请文档结构.docx`
- `现有技术检索.docx`

## 方法2：使用VSCode/Cursor插件

### 推荐插件

#### 方案A：Markdown PDF（推荐）

1. **安装插件**
   - 在VSCode/Cursor中打开扩展市场
   - 搜索并安装 "Markdown PDF" (yzane)
   - 插件ID: `yzane.markdown-pdf`

2. **使用方法**
   - 打开要转换的Markdown文件（如 `03-权利要求书.md`）
   - 按 `F1` 或 `Ctrl+Shift+P` 打开命令面板
   - 输入 "Markdown PDF: Export (docx)"
   - 选择该命令
   - 文件将转换为Word格式并保存在同一目录

3. **配置（可选）**
   在 `.vscode/settings.json` 中添加：
   ```json
   {
     "markdown-pdf.type": ["docx"],
     "markdown-pdf.outputDirectory": "word-output",
     "markdown-pdf.styles": [],
     "markdown-pdf.includeDefaultStyles": true
   }
   ```

#### 方案B：Docs Markdown

1. **安装插件**
   - 搜索并安装 "Docs Markdown" (Microsoft)
   - 插件ID: `docsmsft.docs-markdown`

2. **使用方法**
   - 打开Markdown文件
   - 右键选择 "Export to Word"
   - 或使用命令面板：`Docs: Export to Word`

#### 方案C：Pandoc（需要安装pandoc）

1. **安装插件**
   - 搜索并安装 "Pandoc" (DougFinke)
   - 插件ID: `DougFinke.vscode-pandoc`

2. **使用方法**
   - 打开Markdown文件
   - 按 `F1` 打开命令面板
   - 输入 "Pandoc: Export to DOCX"
   - 选择该命令

### 插件配置示例

创建 `.vscode/settings.json` 文件（在项目根目录）：

```json
{
  "markdown-pdf.type": ["docx"],
  "markdown-pdf.outputDirectory": "patent/word-output",
  "markdown-pdf.includeDefaultStyles": true,
  "markdown-pdf.styles": [],
  "markdown-pdf.markdownItOptions": {
    "html": true,
    "breaks": true
  }
}
```

## 方法3：手动转换

如果上述方法都不适用，可以手动转换：

1. **在Word中新建文档**
2. **打开Markdown文件，复制内容**
3. **粘贴到Word中**
   - 使用 "保留源格式" 粘贴
   - 或使用 "仅保留文本" 然后手动格式化
4. **调整格式**
   - 设置字体：中文用宋体或微软雅黑，英文用Times New Roman
   - 设置字号：正文12pt
   - 设置行距：1.5倍行距
   - 设置页边距：上下2.5cm，左右2cm

## 专利文档格式要求

转换后需要检查并调整以下格式：

### 基本格式
- **字体**：中文用宋体或微软雅黑，英文用Times New Roman
- **字号**：正文12pt，标题可适当放大
- **行距**：1.5倍行距
- **页边距**：上下2.5cm，左右2cm
- **页码**：页脚居中

### 标题格式
- 一级标题：加粗，可适当增大字号
- 二级标题：加粗
- 三级标题：加粗或正常

### 特殊要求
- **权利要求书**：每个权利要求单独一段，编号清晰
- **说明书**：结构清晰，段落分明
- **附图说明**：与附图对应，编号一致

## 常见问题

### Q1: Python脚本报错 "pandoc not found"
**A**: 需要先安装pandoc，参考"前置要求"部分。

### Q2: 转换后的Word文档格式不对
**A**: 
- 可以创建 `reference.docx` 作为模板
- 或手动调整格式
- 或使用Word的样式功能统一格式

### Q3: 中文字体显示不正确
**A**: 
- 确保系统已安装中文字体（如微软雅黑、宋体）
- 在Word中手动设置字体
- 或修改脚本中的字体设置

### Q4: 插件无法使用
**A**: 
- 检查插件是否正确安装
- 重启VSCode/Cursor
- 查看插件文档了解使用方法

## 创建参考文档模板（可选）

如果需要统一的格式，可以创建 `reference.docx`：

1. 在Word中创建新文档
2. 设置好字体、字号、行距、页边距等格式
3. 保存为 `reference.docx` 放在patent目录
4. 转换脚本会自动使用该模板

## 批量转换

如果需要批量转换所有文件，可以：

1. **使用Python脚本**：脚本会自动转换所有核心文件
2. **使用命令行**：
   ```bash
   # 单个文件转换
   pandoc 03-权利要求书.md -o word-output/权利要求书.docx --from markdown --to docx
   
   # 批量转换（PowerShell）
   Get-ChildItem *.md | ForEach-Object {
       pandoc $_.Name -o "word-output/$($_.BaseName).docx" --from markdown --to docx
   }
   ```

## 技术支持

如有问题，请检查：
1. Python和pandoc是否正确安装
2. 依赖包是否正确安装
3. 文件路径是否正确
4. 查看错误信息并搜索解决方案

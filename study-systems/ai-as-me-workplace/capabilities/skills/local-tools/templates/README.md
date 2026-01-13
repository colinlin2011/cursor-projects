# Word模板说明

## 模板位置

本目录用于存放Pandoc转换使用的Word模板文件。

## 默认模板

- **文件名**：`reference.docx`
- **用途**：Pandoc转换Markdown到Word时使用的参考模板

## 模板要求

### 样式设置

Word模板应包含以下样式：

#### 标题样式
- **标题1（Heading 1）**：一级标题
  - 字体：微软雅黑/宋体，16pt，加粗
  - 段落：段前12pt，段后6pt
  
- **标题2（Heading 2）**：二级标题
  - 字体：微软雅黑/宋体，14pt，加粗
  - 段落：段前10pt，段后4pt
  
- **标题3（Heading 3）**：三级标题
  - 字体：微软雅黑/宋体，12pt，加粗
  - 段落：段前8pt，段后2pt

#### 正文样式
- **正文（Normal）**：正文段落
  - 字体：微软雅黑/宋体，10.5pt或12pt
  - 段落：首行缩进2字符，行距1.5倍

#### 列表样式
- **列表段落**：用于有序和无序列表
- **列表编号**：用于有序列表

#### 表格样式
- **表格样式**：用于表格
  - 边框：外边框1.5pt，内边框0.5pt
  - 表头：加粗，背景色浅灰

### 页面设置

#### 页边距
- 上：2.54cm
- 下：2.54cm
- 左：3.17cm
- 右：3.17cm

#### 页眉
- 位置：页眉区域
- 内容建议：
  - 左侧：文档标题或公司名称
  - 右侧：日期或版本号
- 字体：10pt，宋体

#### 页脚
- 位置：页脚区域
- 内容建议：
  - 居中：页码（格式：第X页 共Y页）
  - 或：页码（格式：- X -）
- 字体：10pt，宋体

### 字体设置

#### 中文字体
- 标题：微软雅黑或宋体
- 正文：微软雅黑或宋体

#### 英文字体
- 标题：Times New Roman或Arial
- 正文：Times New Roman或Arial

#### 字号
- 一级标题：16pt
- 二级标题：14pt
- 三级标题：12pt
- 正文：10.5pt或12pt
- 页眉页脚：10pt

## 创建模板步骤

1. **打开Word**，创建新文档

2. **设置页面格式**：
   - 页面布局 → 页边距 → 自定义边距
   - 设置页边距（上2.54cm，下2.54cm，左3.17cm，右3.17cm）

3. **设置页眉**：
   - 插入 → 页眉 → 编辑页眉
   - 添加文档标题或公司名称
   - 设置字体和格式

4. **设置页脚**：
   - 插入 → 页脚 → 编辑页脚
   - 插入页码
   - 设置页码格式

5. **定义样式**：
   - 开始 → 样式 → 修改样式
   - 修改标题1、标题2、标题3样式
   - 修改正文样式
   - 创建列表样式（如需要）

6. **保存模板**：
   - 文件 → 另存为
   - 文件名：`reference.docx`
   - 保存位置：`capabilities/skills/local-tools/templates/`

## 使用模板

转换Markdown文件时，Pandoc会自动使用此模板：

```powershell
# 使用默认模板
.\pandoc-wrapper.ps1 -Action word -InputFile "report.md"

# 指定其他模板
.\pandoc-wrapper.ps1 -Action word -InputFile "report.md" -TemplateFile "custom-template.docx"
```

## 模板示例

可以创建多个模板用于不同场景：
- `reference.docx`：默认模板（通用）
- `report-template.docx`：报告模板
- `proposal-template.docx`：提案模板
- `meeting-template.docx`：会议纪要模板

## 注意事项

1. 模板文件必须是`.docx`格式
2. 模板中的样式名称必须与Pandoc期望的样式名称匹配
3. 建议在模板中至少包含一个段落，以便Pandoc识别样式
4. 模板中的页眉页脚会被应用到转换后的文档

## 参考资源

- [Pandoc文档](https://pandoc.org/MANUAL.html)
- [Pandoc Word模板说明](https://pandoc.org/MANUAL.html#option--reference-doc)

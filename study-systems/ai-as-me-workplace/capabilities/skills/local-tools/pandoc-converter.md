# Pandoc文档转换工具

**Tool ID**：TOOL-001  
**Tool名称**：Pandoc文档转换器  
**封装日期**：2026-01-13  
**最后更新**：2026-01-13  
**版本**：v2.0（支持Docker）  
**状态**：可用  
**维护人**：系统

---

## 版本说明

### v2.0 - Docker版本（推荐）
- 使用Docker运行Pandoc
- 无需安装LaTeX包
- 环境隔离，不污染系统
- 生成效果一致

### v1.0 - 本地版本
- 需要本地安装Pandoc和LaTeX
- 适合不想使用Docker的场景

---

## 工具描述

### 原始工具
- **工具名称**：Pandoc
- **工具路径**：`pandoc`（命令行工具）
- **工具类型**：命令行工具
- **工具版本**：3.8.3
- **官方链接**：https://github.com/jgm/pandoc/releases/tag/3.8.3

### 工具功能
Pandoc是一个强大的文档转换工具，支持多种文档格式之间的转换，特别适合将Markdown文件转换为Word（.docx）或PDF格式。

### 适用场景
- 将Markdown工作文档转换为Word格式（用于正式文档、报告）
- 将Markdown文档转换为PDF格式（用于打印、分享）
- 批量转换多个Markdown文件
- 使用自定义Word模板生成专业格式文档

---

## 工具封装

### 封装方式
- **封装类型**：命令封装
- **封装语言**：PowerShell/Batch脚本
- **封装文件**：`capabilities/skills/local-tools/pandoc-wrapper.ps1`

### Skill接口定义
- **接口名称**：`Convert-MarkdownToWord` / `Convert-MarkdownToPDF`
- **接口参数**：
  - `InputFile`：输入Markdown文件路径（必填）
  - `OutputFile`：输出文件路径（可选，默认自动生成）
  - `TemplateFile`：Word模板文件路径（可选，默认使用reference.docx）
  - `Format`：输出格式（word/pdf，默认word）
- **接口返回值**：转换结果状态和输出文件路径

### 封装脚本

- **Docker版本**：`pandoc-wrapper-docker.ps1`（推荐）
- **本地版本**：`pandoc-wrapper.ps1`

### 封装代码

#### Docker版本（推荐）
```powershell
# pandoc-wrapper-docker.ps1
# 使用Docker运行Pandoc，无需安装LaTeX包

# 转换为Word
.\pandoc-wrapper-docker.ps1 -Action word -InputFile "README.md"

# 转换为PDF
.\pandoc-wrapper-docker.ps1 -Action pdf -InputFile "README.md"
```

#### 本地版本
```powershell
# pandoc-wrapper.ps1
# Pandoc文档转换封装脚本

function Convert-MarkdownToWord {
    param(
        [Parameter(Mandatory=$true)]
        [string]$InputFile,
        
        [Parameter(Mandatory=$false)]
        [string]$OutputFile,
        
        [Parameter(Mandatory=$false)]
        [string]$TemplateFile = "reference.docx"
    )
    
    # 检查输入文件是否存在
    if (-not (Test-Path $InputFile)) {
        Write-Error "输入文件不存在: $InputFile"
        return $false
    }
    
    # 如果没有指定输出文件，自动生成
    if ([string]::IsNullOrEmpty($OutputFile)) {
        $OutputFile = [System.IO.Path]::ChangeExtension($InputFile, ".docx")
    }
    
    # 检查模板文件是否存在
    $templatePath = Join-Path $PSScriptRoot "templates" $TemplateFile
    if (-not (Test-Path $templatePath)) {
        Write-Warning "模板文件不存在，使用默认格式: $templatePath"
        $templatePath = $null
    }
    
    # 构建Pandoc命令
    $pandocCmd = "pandoc `"$InputFile`" -o `"$OutputFile`" -f markdown -t docx"
    
    if ($templatePath) {
        $pandocCmd += " --reference-doc=`"$templatePath`""
    }
    
    # 执行转换
    try {
        Invoke-Expression $pandocCmd
        if ($LASTEXITCODE -eq 0) {
            Write-Host "转换成功: $OutputFile"
            return @{
                Success = $true
                OutputFile = $OutputFile
            }
        } else {
            Write-Error "转换失败，退出码: $LASTEXITCODE"
            return $false
        }
    } catch {
        Write-Error "转换过程中发生错误: $_"
        return $false
    }
}

function Convert-MarkdownToPDF {
    param(
        [Parameter(Mandatory=$true)]
        [string]$InputFile,
        
        [Parameter(Mandatory=$false)]
        [string]$OutputFile,
        
        [Parameter(Mandatory=$false)]
        [string]$TemplateFile = "reference.docx"
    )
    
    # 检查输入文件是否存在
    if (-not (Test-Path $InputFile)) {
        Write-Error "输入文件不存在: $InputFile"
        return $false
    }
    
    # 如果没有指定输出文件，自动生成
    if ([string]::IsNullOrEmpty($OutputFile)) {
        $OutputFile = [System.IO.Path]::ChangeExtension($InputFile, ".pdf")
    }
    
    # 检查模板文件是否存在
    $templatePath = Join-Path $PSScriptRoot "templates" $TemplateFile
    if (-not (Test-Path $templatePath)) {
        Write-Warning "模板文件不存在，使用默认格式: $templatePath"
        $templatePath = $null
    }
    
    # 构建Pandoc命令
    # 对于PDF，先转换为docx，再转换为PDF，或直接使用LaTeX引擎
    $pandocCmd = "pandoc `"$InputFile`" -o `"$OutputFile`" -f markdown -t pdf"
    
    if ($templatePath) {
        # PDF转换时，模板主要用于样式参考
        $pandocCmd += " --pdf-engine=xelatex"
    }
    
    # 执行转换
    try {
        Invoke-Expression $pandocCmd
        if ($LASTEXITCODE -eq 0) {
            Write-Host "转换成功: $OutputFile"
            return @{
                Success = $true
                OutputFile = $OutputFile
            }
        } else {
            Write-Error "转换失败，退出码: $LASTEXITCODE"
            return $false
        }
    } catch {
        Write-Error "转换过程中发生错误: $_"
        return $false
    }
}
```

---

## 工具使用

### 原始工具使用
```powershell
# 基本转换（Markdown to Word）
pandoc input.md -o output.docx -f markdown -t docx

# 使用模板转换
pandoc input.md -o output.docx -f markdown -t docx --reference-doc=reference.docx

# 转换为PDF
pandoc input.md -o output.pdf -f markdown -t pdf --pdf-engine=xelatex
```

### 封装后使用

#### 本地版本
```powershell
# 导入封装脚本
. .\pandoc-wrapper.ps1

# 转换为Word（使用默认模板）
Convert-MarkdownToWord -InputFile "work/documents/documents/20260113-report.md"

# 转换为Word（指定模板）
Convert-MarkdownToWord -InputFile "work/documents/documents/20260113-report.md" -TemplateFile "reference.docx"

# 转换为PDF
Convert-MarkdownToPDF -InputFile "work/documents/documents/20260113-report.md"
```

#### Docker版本（推荐）
```powershell
# 使用Docker版本（无需安装LaTeX包）
.\pandoc-wrapper-docker.ps1 -Action word -InputFile "work/documents/documents/20260113-report.md"

# 转换为PDF
.\pandoc-wrapper-docker.ps1 -Action pdf -InputFile "work/documents/documents/20260113-report.md"
```

**Docker版本优势**：
- 无需在本地安装LaTeX包
- 不污染系统环境
- 生成效果一致
- 包含完整的LaTeX环境

### 使用示例
- **示例1**：转换工作文档为Word
  ```powershell
  Convert-MarkdownToWord -InputFile "work/documents/documents/20260113-safety-plan.md"
  ```

- **示例2**：批量转换多个文档
  ```powershell
  Get-ChildItem "work/documents/documents/*.md" | ForEach-Object {
      Convert-MarkdownToWord -InputFile $_.FullName
  }
  ```

---

## 工具集成

### 依赖项
- **Pandoc**：3.8.3或更高版本
- **LaTeX引擎**（PDF转换需要）：XeLaTeX或pdfLaTeX

### 配置项
| 配置项 | 类型 | 默认值 | 描述 |
|--------|------|--------|------|
| PandocPath | string | "pandoc" | Pandoc可执行文件路径 |
| TemplatePath | string | "templates/reference.docx" | 默认模板文件路径 |
| PdfEngine | string | "xelatex" | PDF转换引擎 |

### 环境要求

#### 本地版本
- **操作系统**：Windows/Linux/macOS
- **工具安装**：需要安装Pandoc（https://pandoc.org/installing.html）
- **PDF支持**：需要安装LaTeX发行版（如MiKTeX、TeX Live）

#### Docker版本（推荐）
- **操作系统**：Windows/Linux/macOS
- **Docker Desktop**：需要安装Docker Desktop
- **Docker镜像**：使用官方镜像 `pandoc/latex:3.8.3`（自动下载）
- **优势**：无需安装LaTeX包，环境隔离，效果一致

### 安装步骤

#### Docker版本（推荐）
1. **安装Docker Desktop**：
   - Windows: 使用winget安装：`winget install --id Docker.DockerDesktop`
   - 或从官网下载：https://www.docker.com/products/docker-desktop

2. **启动Docker Desktop**：
   - 确保Docker Desktop正在运行

3. **拉取Pandoc镜像**（首次使用会自动下载）：
   ```powershell
   docker pull pandoc/latex:3.8.3
   ```

4. **验证安装**：
   ```powershell
   docker run --rm pandoc/latex:3.8.3 pandoc --version
   ```

#### 本地版本
1. **安装Pandoc**：
   - Windows: 下载安装包从 https://github.com/jgm/pandoc/releases
   - 或使用包管理器：`winget install --id JohnMacFarlane.Pandoc`

2. **安装LaTeX**（PDF转换需要）：
   - Windows: 安装MiKTeX或TeX Live
   - 或使用包管理器：`winget install --id MiKTeX.MiKTeX`

3. **验证安装**：
   ```powershell
   pandoc --version
   ```

---

## Word模板说明

### 模板位置
- **模板目录**：`capabilities/skills/local-tools/templates/`
- **默认模板**：`reference.docx`

### 模板要求
Word模板（reference.docx）应包含以下样式和设置：

#### 样式设置
1. **标题样式**：
   - 标题1（Heading 1）：用于一级标题
   - 标题2（Heading 2）：用于二级标题
   - 标题3（Heading 3）：用于三级标题

2. **正文样式**：
   - 正文（Normal）：用于正文段落
   - 列表样式：用于有序和无序列表

3. **表格样式**：
   - 表格样式：用于表格

#### 页面设置
- **页边距**：上下2.54cm，左右3.17cm（或根据需求调整）
- **页眉**：包含文档标题或公司名称
- **页脚**：包含页码和日期

#### 字体设置
- **中文字体**：微软雅黑或宋体
- **英文字体**：Times New Roman或Arial
- **字号**：标题根据级别设置，正文10.5pt或12pt

### 创建模板步骤
1. 在Word中创建一个新文档
2. 设置页面格式（页边距、页眉、页脚）
3. 定义样式（标题、正文、列表等）
4. 保存为`reference.docx`
5. 将文件放置在`capabilities/skills/local-tools/templates/`目录

---

## 工具使用记录

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
  - 支持多种格式转换
  - 可以自定义模板
  - 批量处理能力强
- **缺点**：
  - 需要安装额外工具
  - PDF转换需要LaTeX引擎
- **改进建议**：
  - 添加错误处理和日志记录
  - 支持更多输出格式选项

---

## 工具版本历史

| 版本 | 日期 | 更新内容 | 更新人 |
|------|------|---------|--------|
| v1.0 | 2026-01-13 | 初始封装 | 系统 |

---

## 关联记录

### 相关注册表
- [能力注册表链接](../registry.md)

### 相关Skill定义
- [Skill定义链接](../SKILL-TEMPLATE.md)

### 相关使用记录
- [使用记录链接](../../usage/usage-history.md)

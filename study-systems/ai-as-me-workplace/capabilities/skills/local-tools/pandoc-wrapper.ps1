# Pandoc文档转换封装脚本
# 用于将Markdown文件转换为Word或PDF格式

param(
    [Parameter(Mandatory=$false)]
    [string]$Action = "word",
    
    [Parameter(Mandatory=$false)]
    [string]$InputFile,
    
    [Parameter(Mandatory=$false)]
    [string]$OutputFile,
    
    [Parameter(Mandatory=$false)]
    [string]$TemplateFile = "reference.docx"
)

# 获取脚本所在目录
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$TemplateDir = Join-Path $ScriptDir "templates"

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
        return @{
            Success = $false
            Error = "输入文件不存在"
        }
    }
    
    # 如果没有指定输出文件，自动生成
    if ([string]::IsNullOrEmpty($OutputFile)) {
        $OutputFile = [System.IO.Path]::ChangeExtension($InputFile, ".docx")
    }
    
    # 检查模板文件是否存在
    $templatePath = Join-Path $TemplateDir $TemplateFile
    if (-not (Test-Path $templatePath)) {
        Write-Warning "模板文件不存在，使用默认格式: $templatePath"
        $templatePath = $null
    }
    
    # 检查Pandoc是否安装
    $pandocPath = Get-Command pandoc -ErrorAction SilentlyContinue
    if (-not $pandocPath) {
        Write-Error "Pandoc未安装或不在PATH中。请先安装Pandoc: https://pandoc.org/installing.html"
        return @{
            Success = $false
            Error = "Pandoc未安装"
        }
    }
    
    # 构建Pandoc命令
    $pandocCmd = "pandoc `"$InputFile`" -o `"$OutputFile`" -f markdown -t docx"
    
    if ($templatePath) {
        $pandocCmd += " --reference-doc=`"$templatePath`""
    }
    
    # 执行转换
    try {
        Write-Host "正在转换: $InputFile -> $OutputFile"
        Invoke-Expression $pandocCmd
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "转换成功: $OutputFile" -ForegroundColor Green
            return @{
                Success = $true
                OutputFile = $OutputFile
            }
        } else {
            Write-Error "转换失败，退出码: $LASTEXITCODE"
            return @{
                Success = $false
                Error = "转换失败，退出码: $LASTEXITCODE"
            }
        }
    } catch {
        Write-Error "转换过程中发生错误: $_"
        return @{
            Success = $false
            Error = $_.Exception.Message
        }
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
        return @{
            Success = $false
            Error = "输入文件不存在"
        }
    }
    
    # 如果没有指定输出文件，自动生成
    if ([string]::IsNullOrEmpty($OutputFile)) {
        $OutputFile = [System.IO.Path]::ChangeExtension($InputFile, ".pdf")
    }
    
    # 检查Pandoc是否安装
    $pandocPath = Get-Command pandoc -ErrorAction SilentlyContinue
    if (-not $pandocPath) {
        Write-Error "Pandoc未安装或不在PATH中。请先安装Pandoc: https://pandoc.org/installing.html"
        return @{
            Success = $false
            Error = "Pandoc未安装"
        }
    }
    
    # 构建Pandoc命令
    # 对于PDF，使用LaTeX引擎
    $pandocCmd = "pandoc `"$InputFile`" -o `"$OutputFile`" -f markdown -t pdf --pdf-engine=xelatex"
    
    # 执行转换
    try {
        Write-Host "正在转换: $InputFile -> $OutputFile"
        Invoke-Expression $pandocCmd
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "转换成功: $OutputFile" -ForegroundColor Green
            return @{
                Success = $true
                OutputFile = $OutputFile
            }
        } else {
            Write-Error "转换失败，退出码: $LASTEXITCODE"
            return @{
                Success = $false
                Error = "转换失败，退出码: $LASTEXITCODE"
            }
        }
    } catch {
        Write-Error "转换过程中发生错误: $_"
        return @{
            Success = $false
            Error = $_.Exception.Message
        }
    }
}

# 主逻辑
if ($InputFile) {
    switch ($Action.ToLower()) {
        "word" {
            Convert-MarkdownToWord -InputFile $InputFile -OutputFile $OutputFile -TemplateFile $TemplateFile
        }
        "pdf" {
            Convert-MarkdownToPDF -InputFile $InputFile -OutputFile $OutputFile -TemplateFile $TemplateFile
        }
        default {
            Write-Error "不支持的操作: $Action。支持的操作: word, pdf"
        }
    }
} else {
    Write-Host "Pandoc文档转换工具" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "用法:" -ForegroundColor Yellow
    Write-Host "  .\pandoc-wrapper.ps1 -Action word -InputFile <输入文件> [-OutputFile <输出文件>] [-TemplateFile <模板文件>]"
    Write-Host "  .\pandoc-wrapper.ps1 -Action pdf -InputFile <输入文件> [-OutputFile <输出文件>]"
    Write-Host ""
    Write-Host "示例:" -ForegroundColor Yellow
    Write-Host "  .\pandoc-wrapper.ps1 -Action word -InputFile 'work/documents/documents/report.md'"
    Write-Host "  .\pandoc-wrapper.ps1 -Action pdf -InputFile 'work/documents/documents/report.md'"
}

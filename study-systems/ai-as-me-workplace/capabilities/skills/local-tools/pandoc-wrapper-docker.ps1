# Pandoc文档转换封装脚本（Docker版本）
# 使用Docker运行Pandoc，无需在本地安装LaTeX包

param(
    [Parameter(Mandatory=$false)]
    [string]$Action = "word",
    
    [Parameter(Mandatory=$false)]
    [string]$InputFile,
    
    [Parameter(Mandatory=$false)]
    [string]$OutputFile,
    
    [Parameter(Mandatory=$false)]
    [string]$TemplateFile = "reference.docx",
    
    [Parameter(Mandatory=$false)]
    [switch]$UseDocker = $true
)

# 获取脚本所在目录
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$TemplateDir = Join-Path $ScriptDir "templates"
$WorkDir = Split-Path -Parent $ScriptDir

# Docker镜像名称
$DockerImage = "pandoc/latex:3.8.3"

function Test-Docker {
    $dockerCmd = Get-Command docker -ErrorAction SilentlyContinue
    if (-not $dockerCmd) {
        Write-Error "Docker未安装或不在PATH中。请先安装Docker Desktop。"
        return $false
    }
    
    # 检查Docker是否运行
    $dockerInfo = docker info 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Docker未运行。请启动Docker Desktop。"
        return $false
    }
    
    return $true
}

function Convert-MarkdownToWord-Docker {
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
    
    # 获取文件的绝对路径
    $InputFileAbs = (Resolve-Path $InputFile).Path
    $OutputFileAbs = (Resolve-Path (Split-Path $InputFile) -ErrorAction SilentlyContinue).Path
    if (-not $OutputFileAbs) {
        $OutputFileAbs = Split-Path $InputFile
    }
    $OutputFileAbs = Join-Path $OutputFileAbs (Split-Path -Leaf $OutputFile)
    
    # 获取工作目录（ai-as-me-workplace目录）
    # 从输入文件路径向上查找，直到找到ai-as-me-workplace目录
    $currentPath = Split-Path -Parent $InputFileAbs
    $WorkDir = $null
    while ($currentPath) {
        if ((Split-Path -Leaf $currentPath) -eq "ai-as-me-workplace") {
            $WorkDir = $currentPath
            break
        }
        $parentPath = Split-Path -Parent $currentPath
        if ($parentPath -eq $currentPath) { break }
        $currentPath = $parentPath
    }
    
    # 如果找不到，使用输入文件所在目录
    if (-not $WorkDir) {
        $WorkDir = Split-Path -Parent $InputFileAbs
    }
    
    # 构建Docker命令
    $InputFileRel = $InputFileAbs.Replace($WorkDir + "\", "").Replace("\", "/")
    $OutputFileRel = $OutputFileAbs.Replace($WorkDir + "\", "").Replace("\", "/")
    
    $dockerCmd = "docker run --rm -v `"${WorkDir}:/data`" -w /data $DockerImage pandoc `"$InputFileRel`" -o `"$OutputFileRel`" -f markdown -t docx"
    
    # 检查模板文件
    $templatePath = Join-Path $TemplateDir $TemplateFile
    if (Test-Path $templatePath) {
        $TemplateDirAbs = (Resolve-Path $TemplateDir).Path
        $TemplateRel = $templatePath.Replace($TemplateDirAbs + "\", "").Replace("\", "/")
        $dockerCmd += " --reference-doc=`"templates/$TemplateRel`""
    }
    
    # 执行转换
    try {
        Write-Host "正在使用Docker转换: $InputFile -> $OutputFile" -ForegroundColor Cyan
        Write-Host "Docker命令: $dockerCmd" -ForegroundColor Gray
        
        Invoke-Expression $dockerCmd
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "转换成功: $OutputFileAbs" -ForegroundColor Green
            return @{
                Success = $true
                OutputFile = $OutputFileAbs
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

function Convert-MarkdownToPDF-Docker {
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
    
    # 获取文件的绝对路径
    $InputFileAbs = (Resolve-Path $InputFile).Path
    $OutputFileAbs = (Resolve-Path (Split-Path $InputFile) -ErrorAction SilentlyContinue).Path
    if (-not $OutputFileAbs) {
        $OutputFileAbs = Split-Path $InputFile
    }
    $OutputFileAbs = Join-Path $OutputFileAbs (Split-Path -Leaf $OutputFile)
    
    # 获取工作目录（ai-as-me-workplace目录）
    $currentPath = Split-Path -Parent $InputFileAbs
    $WorkDir = $null
    while ($currentPath) {
        if ((Split-Path -Leaf $currentPath) -eq "ai-as-me-workplace") {
            $WorkDir = $currentPath
            break
        }
        $parentPath = Split-Path -Parent $currentPath
        if ($parentPath -eq $currentPath) { break }
        $currentPath = $parentPath
    }
    
    # 如果找不到，使用输入文件所在目录
    if (-not $WorkDir) {
        $WorkDir = Split-Path -Parent $InputFileAbs
    }
    
    # 构建Docker命令
    $InputFileRel = $InputFileAbs.Replace($WorkDir + "\", "").Replace("\", "/")
    $OutputFileRel = $OutputFileAbs.Replace($WorkDir + "\", "").Replace("\", "/")
    
    # 对于PDF，使用XeLaTeX引擎以支持中文
    $dockerCmd = "docker run --rm -v `"${WorkDir}:/data`" -w /data $DockerImage pandoc `"$InputFileRel`" -o `"$OutputFileRel`" -f markdown -t pdf --pdf-engine=xelatex -V mainfont=`"Microsoft YaHei`" -V CJKmainfont=`"Microsoft YaHei`""
    
    # 执行转换
    try {
        Write-Host "正在使用Docker转换: $InputFile -> $OutputFile" -ForegroundColor Cyan
        Write-Host "Docker命令: $dockerCmd" -ForegroundColor Gray
        
        Invoke-Expression $dockerCmd
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "转换成功: $OutputFileAbs" -ForegroundColor Green
            return @{
                Success = $true
                OutputFile = $OutputFileAbs
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
if ($UseDocker) {
    if (-not (Test-Docker)) {
        Write-Warning "Docker不可用，尝试使用本地Pandoc..."
        $UseDocker = $false
    }
}

if ($InputFile) {
    if ($UseDocker) {
        switch ($Action.ToLower()) {
            "word" {
                Convert-MarkdownToWord-Docker -InputFile $InputFile -OutputFile $OutputFile -TemplateFile $TemplateFile
            }
            "pdf" {
                Convert-MarkdownToPDF-Docker -InputFile $InputFile -OutputFile $OutputFile -TemplateFile $TemplateFile
            }
            default {
                Write-Error "不支持的操作: $Action。支持的操作: word, pdf"
            }
        }
    } else {
        # 回退到本地Pandoc（如果可用）
        Write-Host "使用本地Pandoc..." -ForegroundColor Yellow
        & "$ScriptDir\pandoc-wrapper.ps1" -Action $Action -InputFile $InputFile -OutputFile $OutputFile -TemplateFile $TemplateFile
    }
} else {
    Write-Host "Pandoc文档转换工具（Docker版本）" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "用法:" -ForegroundColor Yellow
    Write-Host "  .\pandoc-wrapper-docker.ps1 -Action word -InputFile <输入文件> [-OutputFile <输出文件>] [-TemplateFile <模板文件>]"
    Write-Host "  .\pandoc-wrapper-docker.ps1 -Action pdf -InputFile <输入文件> [-OutputFile <输出文件>]"
    Write-Host ""
    Write-Host "示例:" -ForegroundColor Yellow
    Write-Host "  .\pandoc-wrapper-docker.ps1 -Action word -InputFile 'work/documents/documents/report.md'"
    Write-Host "  .\pandoc-wrapper-docker.ps1 -Action pdf -InputFile 'work/documents/documents/report.md'"
    Write-Host ""
    Write-Host "Docker镜像:" -ForegroundColor Yellow
    Write-Host "  使用官方镜像: pandoc/latex:3.8.3"
    Write-Host "  包含完整的LaTeX环境，无需本地安装"
}

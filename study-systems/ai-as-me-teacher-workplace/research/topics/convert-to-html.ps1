# 将课题申报书转换为HTML和PDF的脚本

$ErrorActionPreference = "Continue"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# 获取当前目录
$currentDir = Get-Location
Write-Host "当前目录: $currentDir" -ForegroundColor Cyan

# 查找课题申报书文件
$inputFile = Get-ChildItem -Path $currentDir -Filter "*课题申报书*.md" | Select-Object -First 1

if (-not $inputFile) {
    Write-Host "未找到课题申报书文件！" -ForegroundColor Red
    exit 1
}

Write-Host "找到文件: $($inputFile.Name)" -ForegroundColor Green

# 输出文件路径（使用英文文件名避免编码问题）
$htmlFile = Join-Path $currentDir "课题申报书.html"
$pdfFile = Join-Path $currentDir "课题申报书.pdf"

# 转换为HTML
Write-Host "`n正在转换为HTML..." -ForegroundColor Yellow
$htmlCmd = "pandoc `"$($inputFile.FullName)`" -o `"$htmlFile`" -f markdown -t html --standalone --css=https://cdn.jsdelivr.net/npm/github-markdown-css@5/github-markdown.min.css --metadata title=`"基于多层次记忆架构的AI赋能教师工作空间构建及其教学改革实践研究`""

Invoke-Expression $htmlCmd

if ($LASTEXITCODE -eq 0) {
    Write-Host "HTML转换成功！文件: $htmlFile" -ForegroundColor Green
    
    # 尝试转换为PDF
    Write-Host "`n正在尝试转换为PDF..." -ForegroundColor Yellow
    $pdfCmd = "pandoc `"$($inputFile.FullName)`" -o `"$pdfFile`" -f markdown -t pdf --pdf-engine=xelatex -V mainfont=`"Microsoft YaHei`" -V geometry:margin=2cm"
    
    Invoke-Expression $pdfCmd
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "PDF转换成功！文件: $pdfFile" -ForegroundColor Green
    } else {
        Write-Host "PDF转换失败（可能需要安装LaTeX包）。" -ForegroundColor Yellow
        Write-Host "`n建议使用以下方法生成PDF：" -ForegroundColor Cyan
        Write-Host "1. 在浏览器中打开: $htmlFile"
        Write-Host "2. 按 Ctrl+P 打开打印对话框"
        Write-Host "3. 选择'另存为PDF'或'Microsoft Print to PDF'"
        Write-Host "4. 保存为PDF文件"
    }
    
    # 询问是否打开HTML文件
    Write-Host "`n是否现在打开HTML文件？(Y/N)" -ForegroundColor Cyan
    $response = Read-Host
    if ($response -eq "Y" -or $response -eq "y") {
        Start-Process $htmlFile
    }
} else {
    Write-Host "HTML转换失败！请检查pandoc是否正确安装。" -ForegroundColor Red
    exit 1
}

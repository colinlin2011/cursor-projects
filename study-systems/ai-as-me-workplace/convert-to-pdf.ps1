# 将README.md转换为PDF的脚本
# 由于MiKTeX需要安装额外包，这里提供两种方案

param(
    [string]$InputFile = "README.md",
    [string]$OutputFile = "README.pdf"
)

$ErrorActionPreference = "Continue"

Write-Host "正在将 $InputFile 转换为PDF..." -ForegroundColor Cyan

# 方案1：尝试使用pandoc直接转换为PDF（需要MiKTeX包完整）
Write-Host "`n方案1：尝试使用pandoc直接转换为PDF..." -ForegroundColor Yellow
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

# 尝试使用xelatex
$result = pandoc $InputFile -o $OutputFile -f markdown -t pdf --pdf-engine=xelatex -V mainfont="Microsoft YaHei" 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "转换成功！PDF文件已生成：$OutputFile" -ForegroundColor Green
    return
}

Write-Host "方案1失败，尝试方案2..." -ForegroundColor Yellow

# 方案2：先转换为HTML，然后使用浏览器打印为PDF
Write-Host "`n方案2：转换为HTML，然后使用浏览器打印为PDF..." -ForegroundColor Yellow

$htmlFile = [System.IO.Path]::ChangeExtension($InputFile, ".html")
pandoc $InputFile -o $htmlFile -f markdown -t html --standalone --css=https://cdn.jsdelivr.net/npm/github-markdown-css@5/github-markdown.min.css

if ($LASTEXITCODE -eq 0) {
    Write-Host "HTML文件已生成：$htmlFile" -ForegroundColor Green
    Write-Host "`n请按照以下步骤将HTML转换为PDF：" -ForegroundColor Cyan
    Write-Host "1. 在浏览器中打开 $htmlFile"
    Write-Host "2. 按 Ctrl+P 打开打印对话框"
    Write-Host "3. 选择'另存为PDF'或'Microsoft Print to PDF'"
    Write-Host "4. 保存为 $OutputFile"
    Write-Host "`n或者，您可以运行以下命令自动打开HTML文件：" -ForegroundColor Cyan
    Write-Host "Start-Process `"$htmlFile`""
    
    # 询问是否自动打开
    $response = Read-Host "`n是否现在打开HTML文件？(Y/N)"
    if ($response -eq "Y" -or $response -eq "y") {
        Start-Process $htmlFile
    }
} else {
    Write-Host "HTML转换也失败了。请检查pandoc是否正确安装。" -ForegroundColor Red
}

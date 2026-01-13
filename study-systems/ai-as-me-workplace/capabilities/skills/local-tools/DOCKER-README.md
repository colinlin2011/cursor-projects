# Pandoc Docker使用说明

## 概述

使用Docker运行Pandoc可以避免在本地安装LaTeX包，保持系统环境干净，并确保生成效果一致。

## Docker镜像

使用官方Pandoc镜像：`pandoc/latex:3.8.3`

该镜像包含：
- Pandoc 3.8.3
- 完整的LaTeX环境（TeX Live）
- 所有必要的LaTeX包
- 支持中文的XeLaTeX引擎

## 快速开始

### 1. 确保Docker Desktop运行

```powershell
docker info
```

如果Docker未运行，请启动Docker Desktop。

### 2. 拉取镜像（首次使用）

```powershell
docker pull pandoc/latex:3.8.3
```

### 3. 使用封装脚本

```powershell
# 转换为Word
.\pandoc-wrapper-docker.ps1 -Action word -InputFile "README.md"

# 转换为PDF
.\pandoc-wrapper-docker.ps1 -Action pdf -InputFile "README.md"
```

## 直接使用Docker命令

### 转换为Word

```powershell
docker run --rm `
  -v "${PWD}:/data" `
  -w /data `
  pandoc/latex:3.8.3 `
  pandoc README.md -o README.docx -f markdown -t docx
```

### 转换为PDF

```powershell
docker run --rm `
  -v "${PWD}:/data" `
  -w /data `
  pandoc/latex:3.8.3 `
  pandoc README.md -o README.pdf -f markdown -t pdf `
  --pdf-engine=xelatex `
  -V mainfont="Microsoft YaHei" `
  -V CJKmainfont="Microsoft YaHei"
```

### 使用模板

```powershell
docker run --rm `
  -v "${PWD}:/data" `
  -w /data `
  pandoc/latex:3.8.3 `
  pandoc README.md -o README.docx -f markdown -t docx `
  --reference-doc="templates/reference.docx"
```

## 优势

### 1. 环境隔离
- 不污染本地系统
- 不安装LaTeX包
- 不影响其他应用

### 2. 一致性
- 所有环境使用相同的镜像
- 生成效果完全一致
- 版本固定

### 3. 易于维护
- 更新只需拉取新镜像
- 无需管理LaTeX包
- 清理简单

### 4. 跨平台
- Windows、Linux、macOS使用相同方式
- 命令完全一致

## 注意事项

1. **首次使用**：需要下载镜像（约1-2GB），需要一些时间
2. **Docker运行**：确保Docker Desktop正在运行
3. **文件路径**：使用相对路径，脚本会自动处理
4. **模板文件**：模板文件需要在`templates/`目录下

## 故障排除

### Docker未运行
```
Error: Docker未运行。请启动Docker Desktop。
```
**解决**：启动Docker Desktop

### 镜像不存在
```
Error: Unable to find image 'pandoc/latex:3.8.3'
```
**解决**：运行 `docker pull pandoc/latex:3.8.3`

### 权限问题
```
Error: permission denied
```
**解决**：确保Docker Desktop有访问文件系统的权限

## 参考资源

- [Pandoc Docker镜像](https://hub.docker.com/r/pandoc/latex)
- [Docker Desktop文档](https://docs.docker.com/desktop/)
- [Pandoc官方文档](https://pandoc.org/MANUAL.html)

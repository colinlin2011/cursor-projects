# Docker设置说明

## Docker Desktop已安装

Docker Desktop已成功安装，但需要启动才能使用。

## 启动Docker Desktop

1. **从开始菜单启动**：
   - 搜索 "Docker Desktop"
   - 点击启动

2. **等待启动完成**：
   - Docker Desktop启动需要一些时间（首次启动可能需要1-2分钟）
   - 等待系统托盘中的Docker图标变为运行状态

3. **验证Docker运行**：
   ```powershell
   docker info
   ```
   如果显示Docker信息，说明已成功启动。

## 首次使用

### 1. 拉取Pandoc镜像

```powershell
docker pull pandoc/latex:3.8.3
```

这需要一些时间（镜像约1-2GB），但只需下载一次。

### 2. 使用Docker版本转换

```powershell
cd cursor-projects\study-systems\ai-as-me-workplace
.\capabilities\skills\local-tools\pandoc-wrapper-docker.ps1 -Action pdf -InputFile README.md
```

## 优势

使用Docker版本的优势：
- ✅ 无需安装LaTeX包
- ✅ 不污染系统环境
- ✅ 生成效果一致
- ✅ 包含完整的LaTeX环境
- ✅ 支持中文PDF生成

## 故障排除

### Docker未启动
如果看到错误：`failed to connect to the docker API`
**解决**：启动Docker Desktop并等待其完全启动

### 镜像下载慢
如果镜像下载很慢，可以：
- 使用国内镜像源（配置Docker Desktop）
- 或等待下载完成（只需一次）

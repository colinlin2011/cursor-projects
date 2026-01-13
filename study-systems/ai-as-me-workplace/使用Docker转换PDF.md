# 使用Docker转换PDF指南

## 当前状态

- ✅ **Docker Desktop 4.56.0** 已安装
- ✅ **Pandoc Docker脚本** 已创建
- ⏳ **Docker Desktop** 需要启动

## 快速开始

### 步骤1：启动Docker Desktop

1. 从开始菜单搜索并启动 **"Docker Desktop"**
2. 等待Docker Desktop完全启动（系统托盘图标变为运行状态）
3. 首次启动可能需要1-2分钟

### 步骤2：验证Docker运行

```powershell
docker info
```

如果显示Docker信息，说明已成功启动。

### 步骤3：拉取Pandoc镜像（首次使用）

```powershell
docker pull pandoc/latex:3.8.3
```

这需要一些时间（镜像约1-2GB），但只需下载一次。

### 步骤4：转换README.md为PDF

```powershell
cd cursor-projects\study-systems\ai-as-me-workplace
.\capabilities\skills\local-tools\pandoc-wrapper-docker.ps1 -Action pdf -InputFile README.md
```

## 优势

使用Docker版本的优势：
- ✅ **无需安装LaTeX包** - 所有依赖都在Docker镜像中
- ✅ **不污染系统** - 完全隔离的环境
- ✅ **生成效果一致** - 所有环境使用相同的镜像
- ✅ **支持中文** - 包含完整的中文字体支持
- ✅ **易于维护** - 更新只需拉取新镜像

## 文件说明

- `pandoc-wrapper-docker.ps1` - Docker版本的转换脚本（推荐）
- `pandoc-wrapper.ps1` - 本地版本的转换脚本
- `Dockerfile` - Docker镜像定义（可选，使用官方镜像）
- `docker-compose.yml` - Docker Compose配置（可选）
- `DOCKER-README.md` - 详细的Docker使用说明

## 故障排除

### Docker未启动
**错误**：`failed to connect to the docker API`  
**解决**：启动Docker Desktop并等待其完全启动

### 镜像下载慢
**解决**：首次下载需要时间，可以配置Docker镜像加速器

### 权限问题
**解决**：确保Docker Desktop有访问文件系统的权限

## 下一步

启动Docker Desktop后，运行转换命令即可生成PDF文件。

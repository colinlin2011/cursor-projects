# Node.js 安装指导

## 问题诊断

您的系统未检测到 Node.js 和 npm，需要先安装才能运行 Light-Cone-2025 项目。

## 安装方法

### 方法一：直接安装 Node.js（推荐）

1. **下载 Node.js**
   - 访问：https://nodejs.org/
   - 下载 LTS（长期支持）版本
   - 推荐版本：v20.x 或 v18.x

2. **安装步骤**
   - 运行下载的安装程序
   - 按照向导完成安装（保持默认设置即可）
   - **重要**：确保勾选 "Add to PATH" 选项

3. **验证安装**
   ```bash
   # 重新打开 PowerShell 或命令提示符
   node --version
   npm --version
   ```

### 方法二：使用 nvm-windows（适合需要多版本管理）

1. **下载 nvm-windows**
   - 访问：https://github.com/coreybutler/nvm-windows/releases
   - 下载 `nvm-setup.exe`

2. **安装步骤**
   - 运行安装程序
   - 完成后重新打开 PowerShell

3. **安装 Node.js**
   ```bash
   nvm install lts
   nvm use lts
   ```

## 安装后操作

1. **重新打开终端**
   - 关闭当前的 PowerShell/命令提示符
   - 重新打开新的终端窗口

2. **验证安装**
   ```bash
   node --version
   npm --version
   ```

3. **安装项目依赖**
   ```bash
   cd web-apps\Light-Cone-2025
   npm install
   ```

4. **启动开发服务器**
   ```bash
   npm run dev
   ```

## 常见问题

### 问题：安装后仍然提示找不到 npm

**解决方案：**
1. 检查 PATH 环境变量是否包含 Node.js 安装路径
2. 重新打开终端（环境变量更改需要重启终端）
3. 如果仍不行，手动添加到 PATH：
   - 通常路径：`C:\Program Files\nodejs\`
   - 或：`%LOCALAPPDATA%\Programs\nodejs\`

### 问题：权限错误

**解决方案：**
- 以管理员身份运行 PowerShell
- 或使用 `npm install --global` 时可能需要管理员权限

## 快速检查脚本

运行 `检查Node环境.bat` 可以快速诊断 Node.js 环境。

# PDF转换说明

## 当前状态

- ✅ **Pandoc 3.8.3** 已安装
- ✅ **MiKTeX 24.1** 已安装
- ✅ **README.html** 已生成（27.8 KB）

## PDF转换方案

由于MiKTeX需要安装额外的LaTeX包才能直接生成PDF，目前有以下方案：

### 方案1：使用浏览器打印为PDF（推荐，最简单）

1. **打开HTML文件**：
   - 双击 `README.html` 文件
   - 或在浏览器中打开：`README.html`

2. **打印为PDF**：
   - 按 `Ctrl+P` 打开打印对话框
   - 选择打印机：**"Microsoft Print to PDF"** 或 **"另存为PDF"**
   - 点击 **"打印"** 或 **"保存"**
   - 保存为 `README.pdf`

**优点**：简单快速，无需安装额外包  
**缺点**：需要手动操作

### 方案2：安装MiKTeX包后使用pandoc直接转换

1. **打开MiKTeX Console**：
   - 在开始菜单搜索 "MiKTeX Console"
   - 或运行：`miktex-console`

2. **安装必要的包**：
   - 在MiKTeX Console中，点击 **"Packages"**
   - 搜索并安装以下包：
     - `geometry`
     - `fancyvrb`
     - `xeCJK`（如果使用中文）
     - `infwarerr`
     - `etoolbox`
     - `hyperref`

3. **使用pandoc转换**：
   ```powershell
   cd cursor-projects\study-systems\ai-as-me-workplace
   pandoc README.md -o README.pdf -f markdown -t pdf --pdf-engine=xelatex -V mainfont="Microsoft YaHei"
   ```

**优点**：自动化，可批量处理  
**缺点**：需要安装额外包

### 方案3：使用转换脚本

运行提供的转换脚本：
```powershell
cd cursor-projects\study-systems\ai-as-me-workplace
.\convert-to-pdf.ps1
```

脚本会自动尝试方案2，如果失败则使用方案1。

## 当前可用文件

- `README.md` - 原始Markdown文件（21 KB）
- `README.html` - HTML格式文件（27.8 KB）
- `convert-to-pdf.ps1` - PDF转换脚本

## 建议

**立即使用**：使用方案1（浏览器打印），最快最简单。

**长期使用**：安装MiKTeX包后使用方案2，可以实现自动化转换。

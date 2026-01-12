# 项目集合

这是一个包含多个项目的集合，包括 Python 工具和网页应用等。

## 📁 项目结构

```
Cursor Project/
├── tools/                    # Python 工具项目目录
│   ├── excel-processor/      # Excel 处理工具
│   └── Access to Work Doc/  # 工作文档工具
├── web-apps/                 # 网页应用项目目录
│   └── Light-Cone-2025/      # Light-Cone-2025 项目
└── README_总项目.md          # 本文件
```

## 🛠️ 项目列表

### Python 工具 (`tools/`)

#### 1. Excel 处理工具 (`tools/excel-processor/`)

一个功能强大的 Excel 表格处理工具，支持：
- 📤 文件导入导出（Excel, CSV, JSON）
- 🧹 数据清洗（删除空行、去重、填充缺失值）
- 🔍 数据筛选和排序
- 📝 列操作（重命名、删除、添加、类型转换）
- 🔤 文本处理（去除空格、大小写转换、文本替换）
- 🧮 数值计算（计算列、分组统计）
- 📈 数据统计

**使用方式：**
```bash
cd tools/excel-processor
streamlit run main.py
```

**打包：**
```bash
cd tools/excel-processor
build_exe.bat
```

### 网页应用 (`web-apps/`)

#### 1. Light-Cone-2025 (`web-apps/Light-Cone-2025/`)

从 GitHub 导入的 Next.js 网页应用项目。

**项目信息：**
- 技术栈：Next.js + TypeScript + Tailwind CSS
- 数据库：Supabase
- 状态：已导入

**前置要求：**
- 需要安装 Node.js（v18+ 或 v20+）
- 如果未安装，请先运行 `check_node.bat` 检查环境
- 安装指导请查看 `安装Node指导.md`

**使用方式：**
```bash
cd web-apps/Light-Cone-2025
npm install          # 安装依赖（需要先安装 Node.js）
npm run dev          # 启动开发服务器
```

**导入方式：**
- 运行 `导入Light-Cone项目.bat` 自动导入
- 或手动运行：`git clone https://github.com/colinlin2011/Light-Cone-2025.git web-apps/Light-Cone-2025`

## 🚀 添加新项目

### 添加 Python 工具

1. 运行 `创建新工具.bat` 创建新工具
2. 或手动在 `tools/` 目录下创建新目录

### 从 GitHub 导入项目

1. **快速导入指定项目**：
   - 运行 `导入Light-Cone项目.bat`（针对 Light-Cone-2025）
   - 或运行 `导入GitHub项目.bat`（通用导入脚本）

2. **手动导入**：
   ```bash
   # 创建分类目录（如 web-apps, tools, other）
   mkdir web-apps
   
   # 克隆项目
   git clone https://github.com/username/repository.git web-apps/repository-name
   ```

## 📝 注意事项

- 每个工具都是独立的项目
- 每个工具有自己的 `requirements.txt`
- 建议每个工具有自己的 README.md
- 打包文件（build/, dist/）建议保留在各自工具目录中

# 专利申请文档转Word工具

## 快速开始

### 方法1：一键转换（Windows）

双击运行 `快速转换.bat`，脚本会自动：
1. 检查Python和pandoc是否安装
2. 安装必要的依赖
3. 转换所有核心申请文件
4. 打开输出目录

### 方法2：Python脚本

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 运行转换脚本
python convert_to_word.py
```

### 方法3：VSCode/Cursor插件

1. 安装插件 "Markdown PDF" (yzane)
2. 打开Markdown文件
3. 按 `F1`，输入 "Markdown PDF: Export (docx)"
4. 选择命令即可转换

## 文件说明

- `convert_to_word.py` - Python转换脚本
- `requirements.txt` - Python依赖列表
- `快速转换.bat` - Windows一键转换脚本
- `使用说明-转换Word.md` - 详细使用说明
- `.vscode/settings.json` - VSCode插件配置

## 输出文件

转换后的Word文档保存在 `word-output/` 目录：
- 权利要求书.docx
- 说明书.docx
- 说明书摘要.docx
- 附图说明.docx

## 详细说明

查看 `使用说明-转换Word.md` 了解详细使用方法、配置选项和常见问题。

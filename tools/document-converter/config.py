"""
文档转换工具 - 配置文件
"""

# 页面配置
PAGE_TITLE = "文档转换工具"
PAGE_ICON = "📄"

# 支持的文件类型
SUPPORTED_FILE_TYPES = {
    "PDF": [".pdf"],
    "Word": [".docx", ".doc"],
    "Excel": [".xlsx", ".xls"],
    "PowerPoint": [".pptx", ".ppt"]
}

# 输出格式
OUTPUT_FORMAT = "Markdown"  # 目前只支持Markdown

# 转换选项
CONVERSION_OPTIONS = {
    "preserve_formatting": True,  # 保留格式
    "extract_images": False,  # 是否提取图片（暂不支持）
    "extract_tables": True,  # 是否提取表格
}

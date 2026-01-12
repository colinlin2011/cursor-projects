"""
快速转换脚本 - 直接转换标准文档
无需启动UI，直接运行此脚本即可转换
"""

import sys
import io

# 修复Windows控制台编码问题
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from utils.document_converter import DocumentConverter
from pathlib import Path

def convert_standard_document():
    """转换标准文档"""
    
    converter = DocumentConverter()
    
    # 标准文档路径
    base_path = Path(r"p:\Cursor Project\study-systems\autonomous-safety-study\materials\01_Standards")
    
    # 查找PDF和Word文件
    pdf_file = base_path / "01. [新评估基准]GB 智能网联汽车 组合驾驶辅助系统安全要求_工信部官方公开征求意见版本_2509.pdf"
    word_file = base_path / "01. [新评估基准]GB 智能网联汽车 组合驾驶辅助系统安全要求_工信部官方公开征求意见版本_2509.docx"
    
    # 优先转换Word（如果存在）
    if word_file.exists():
        print(f"找到Word文档: {word_file.name}")
        output_path = base_path / "标准内容.md"
        print(f"开始转换Word文档...")
        result, success = converter.convert_word_to_markdown(str(word_file), str(output_path))
        
        if success:
            print(f"[成功] 转换成功！")
            print(f"文件已保存到: {output_path}")
            print(f"内容长度: {len(result)} 字符")
            return True
        else:
            print(f"[失败] Word转换失败: {result}")
            if "未安装" in result:
                print("提示: 请先安装依赖库: pip install python-docx")
            print(f"尝试转换PDF...")
    
    # 如果Word不存在或转换失败，尝试PDF
    if pdf_file.exists():
        print(f"找到PDF文档: {pdf_file.name}")
        output_path = base_path / "标准内容.md"
        print(f"开始转换PDF文档...")
        result, success = converter.convert_pdf_to_markdown(str(pdf_file), str(output_path))
        
        if success:
            print(f"[成功] 转换成功！")
            print(f"文件已保存到: {output_path}")
            print(f"内容长度: {len(result)} 字符")
            return True
        else:
            print(f"[失败] PDF转换失败: {result}")
            if "未安装" in result:
                print("提示: 请先安装依赖库: pip install pymupdf")
            return False
    
    print("[错误] 未找到标准文档文件")
    return False


if __name__ == "__main__":
    print("=" * 60)
    print("文档转换工具 - 快速转换脚本")
    print("=" * 60)
    print()
    
    success = convert_standard_document()
    
    if success:
        print()
        print("=" * 60)
        print("[成功] 转换完成！现在AI助手可以读取标准内容了")
        print("=" * 60)
    else:
        print()
        print("=" * 60)
        print("[失败] 转换失败，请检查文件路径和依赖库")
        print("=" * 60)
        print("\n安装依赖库:")
        print("  pip install python-docx  # Word支持")
        print("  pip install pymupdf     # PDF支持")
        print("  pip install pandas openpyxl  # Excel支持")

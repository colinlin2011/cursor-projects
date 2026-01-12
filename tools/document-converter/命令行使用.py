"""
文档转换工具 - 命令行使用示例
可以直接在Python中调用，无需启动Streamlit
"""

from utils.document_converter import DocumentConverter
from pathlib import Path

def convert_standard_document():
    """转换标准文档的示例"""
    
    converter = DocumentConverter()
    
    # 标准PDF路径
    pdf_path = r"p:\Cursor Project\study-systems\autonomous-safety-study\materials\01_Standards\01. [新评估基准]GB 智能网联汽车 组合驾驶辅助系统安全要求_工信部官方公开征求意见版本_2509.pdf"
    
    # 输出Markdown路径
    output_path = r"p:\Cursor Project\study-systems\autonomous-safety-study\materials\01_Standards\01. [新评估基准]GB 智能网联汽车 组合驾驶辅助系统安全要求_工信部官方公开征求意见版本_2509.md"
    
    print("开始转换标准PDF...")
    result, success = converter.convert_pdf_to_markdown(pdf_path, output_path)
    
    if success:
        print(f"✅ 转换成功！")
        print(f"文件已保存到: {output_path}")
        print(f"内容长度: {len(result)} 字符")
    else:
        print(f"❌ 转换失败: {result}")


def convert_word_document():
    """转换Word文档的示例"""
    
    converter = DocumentConverter()
    
    # Word文档路径
    word_path = r"p:\Cursor Project\study-systems\autonomous-safety-study\materials\01_Standards\01. [新评估基准]GB 智能网联汽车 组合驾驶辅助系统安全要求_工信部官方公开征求意见版本_2509.docx"
    
    # 输出Markdown路径
    output_path = r"p:\Cursor Project\study-systems\autonomous-safety-study\materials\01_Standards\标准内容.md"
    
    print("开始转换Word文档...")
    result, success = converter.convert_word_to_markdown(word_path, output_path)
    
    if success:
        print(f"✅ 转换成功！")
        print(f"文件已保存到: {output_path}")
    else:
        print(f"❌ 转换失败: {result}")


def batch_convert(directory_path: str):
    """批量转换目录下的所有文档"""
    
    converter = DocumentConverter()
    directory = Path(directory_path)
    
    # 支持的文件扩展名
    supported_extensions = ['.pdf', '.docx', '.doc', '.xlsx', '.xls']
    
    files_to_convert = []
    for ext in supported_extensions:
        files_to_convert.extend(directory.glob(f"*{ext}"))
    
    print(f"找到 {len(files_to_convert)} 个文件需要转换")
    
    for file_path in files_to_convert:
        output_path = file_path.parent / f"{file_path.stem}.md"
        
        print(f"\n正在转换: {file_path.name}")
        result, success = converter.convert(str(file_path), str(output_path))
        
        if success:
            print(f"✅ 成功: {output_path.name}")
        else:
            print(f"❌ 失败: {result}")


if __name__ == "__main__":
    # 示例1：转换标准PDF
    # convert_standard_document()
    
    # 示例2：转换Word文档
    # convert_word_document()
    
    # 示例3：批量转换
    # batch_convert(r"p:\Cursor Project\study-systems\autonomous-safety-study\materials\01_Standards")
    
    print("请取消注释上面的函数调用来使用")

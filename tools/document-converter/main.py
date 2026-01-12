"""
文档转换工具 - 主程序
提供友好的UI界面，将PDF、Word、Excel转换为Markdown格式
"""

import streamlit as st
from pathlib import Path
import os
from utils.document_converter import DocumentConverter
import config

# 页面配置
st.set_page_config(
    page_title=config.PAGE_TITLE,
    page_icon=config.PAGE_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

# 初始化转换器
if 'converter' not in st.session_state:
    st.session_state.converter = DocumentConverter()

converter = st.session_state.converter


def main():
    """主函数"""
    
    st.title("📄 文档转换工具")
    st.markdown("将PDF、Word、Excel文档转换为Markdown格式，方便AI助手读取和分析")
    
    # 侧边栏
    with st.sidebar:
        st.header("📋 使用说明")
        st.markdown("""
        ### 支持的文件类型
        - **PDF** (.pdf)
        - **Word** (.docx, .doc)
        - **Excel** (.xlsx, .xls)
        
        ### 使用步骤
        1. 上传要转换的文档
        2. 选择输出位置（可选）
        3. 点击转换按钮
        4. 下载转换后的Markdown文件
        
        ### 注意事项
        - PDF转换需要安装: `pip install pymupdf`
        - Word转换需要安装: `pip install python-docx`
        - Excel转换需要安装: `pip install pandas openpyxl`
        """)
        
        st.header("🔧 依赖检查")
        from utils.document_converter import PDF_AVAILABLE, WORD_AVAILABLE, EXCEL_AVAILABLE
        
        if PDF_AVAILABLE:
            st.success("✓ PDF支持已安装")
        else:
            st.error("✗ PDF支持未安装")
            st.code("pip install pymupdf", language="bash")
        
        if WORD_AVAILABLE:
            st.success("✓ Word支持已安装")
        else:
            st.error("✗ Word支持未安装")
            st.code("pip install python-docx", language="bash")
        
        if EXCEL_AVAILABLE:
            st.success("✓ Excel支持已安装")
        else:
            st.error("✗ Excel支持未安装")
            st.code("pip install pandas openpyxl", language="bash")
    
    # 主界面
    st.header("📤 上传文档")
    
    uploaded_file = st.file_uploader(
        "选择要转换的文档",
        type=['pdf', 'docx', 'doc', 'xlsx', 'xls'],
        help="支持PDF、Word、Excel格式"
    )
    
    if uploaded_file is not None:
        # 显示文件信息
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"**文件名**: {uploaded_file.name}")
        with col2:
            st.info(f"**文件大小**: {uploaded_file.size / 1024:.2f} KB")
        
        # 保存上传的文件到临时目录
        temp_dir = Path("temp_uploads")
        temp_dir.mkdir(exist_ok=True)
        temp_file_path = temp_dir / uploaded_file.name
        
        with open(temp_file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        st.success(f"文件已上传: {temp_file_path}")
        
        # 转换选项
        st.header("⚙️ 转换选项")
        
        col1, col2 = st.columns(2)
        with col1:
            output_dir = st.text_input(
                "输出目录（可选）",
                value="output",
                help="如果不指定，将在文件同目录下生成Markdown文件"
            )
        
        with col2:
            auto_open = st.checkbox("转换后自动预览", value=True)
        
        # 转换按钮
        if st.button("🔄 开始转换", type="primary", use_container_width=True):
            with st.spinner("正在转换..."):
                # 确定输出路径
                if output_dir:
                    output_path = Path(output_dir) / f"{Path(uploaded_file.name).stem}.md"
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                else:
                    output_path = temp_file_path.parent / f"{temp_file_path.stem}.md"
                
                # 执行转换
                result, success = converter.convert(str(temp_file_path), str(output_path))
                
                if success:
                    st.success("✅ 转换成功！")
                    
                    # 显示转换结果
                    st.header("📄 转换结果预览")
                    st.markdown("---")
                    
                    # 显示前1000个字符的预览
                    preview = result[:1000] if len(result) > 1000 else result
                    st.code(preview, language="markdown")
                    
                    if len(result) > 1000:
                        st.info(f"（预览前1000字符，完整内容共{len(result)}字符）")
                    
                    # 下载按钮
                    st.download_button(
                        label="📥 下载Markdown文件",
                        data=result,
                        file_name=output_path.name,
                        mime="text/markdown",
                        use_container_width=True
                    )
                    
                    # 显示完整路径
                    st.info(f"**文件已保存到**: `{output_path.absolute()}`")
                    
                    # 如果是在学习系统目录下，提供快捷操作
                    if "study-systems" in str(output_path.absolute()):
                        st.success("💡 提示：文件已保存到学习系统目录，AI助手可以直接读取！")
                
                else:
                    st.error("❌ 转换失败")
                    st.error(result)
        
        # 清理临时文件（可选）
        if st.button("🗑️ 清理临时文件"):
            if temp_file_path.exists():
                temp_file_path.unlink()
                st.success("临时文件已清理")


if __name__ == "__main__":
    main()

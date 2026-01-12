"""
Excel 处理工具 - 主程序
提供友好的导入导出 UI 界面
"""

import streamlit as st
import pandas as pd
from utils.excel_handler import ExcelHandler
import config

# 页面配置
st.set_page_config(
    page_title=config.PAGE_TITLE,
    page_icon=config.PAGE_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

# 初始化 session state
if 'excel_handler' not in st.session_state:
    st.session_state.excel_handler = ExcelHandler()

if 'file_loaded' not in st.session_state:
    st.session_state.file_loaded = False

# 获取 Excel 处理器实例
handler = st.session_state.excel_handler


def main():
    """主函数"""
    
    # 标题和说明
    st.title("📊 Excel 处理工具")
    st.markdown("---")
    st.markdown("""
    欢迎使用 Excel 处理工具！这是一个通用友好的表格处理工具。
    
    **使用步骤：**
    1. 📤 在左侧上传您的 Excel 文件
    2. 👀 查看文件信息和数据预览
    3. 🛠️ 使用处理功能（功能将逐步添加）
    4. 💾 下载处理后的文件
    """)
    
    # 侧边栏 - 文件上传
    with st.sidebar:
        st.header("📁 文件操作")
        
        # 文件上传
        uploaded_file = st.file_uploader(
            "选择 Excel 文件",
            type=['xlsx', 'xls', 'xlsm'],
            help="支持 .xlsx, .xls, .xlsm 格式"
        )
        
        if uploaded_file is not None:
            # 检查是否是新文件
            if not st.session_state.file_loaded or st.session_state.last_file_name != uploaded_file.name:
                with st.spinner("正在加载文件..."):
                    result = handler.load_file(uploaded_file)
                    
                    if result['success']:
                        st.session_state.file_loaded = True
                        st.session_state.last_file_name = uploaded_file.name
                        st.success(result['message'])
                        st.info(f"📊 数据规模: {result['rows']} 行 × {result['columns']} 列")
                    else:
                        st.error(result['error'])
                        st.session_state.file_loaded = False
        
        st.markdown("---")
        
        # 清空数据按钮
        if st.button("🗑️ 清空数据", use_container_width=True):
            handler.clear_data()
            st.session_state.file_loaded = False
            if 'last_file_name' in st.session_state:
                del st.session_state.last_file_name
            st.rerun()
    
    # 主内容区
    if st.session_state.file_loaded:
        # 获取数据信息
        info = handler.get_info()
        
        # 信息展示区域
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("文件名", info['file_name'])
        with col2:
            st.metric("总行数", f"{info['rows']:,}")
        with col3:
            st.metric("总列数", info['columns'])
        with col4:
            st.metric("内存占用", info['memory_usage'])
        
        st.markdown("---")
        
        # 标签页
        tab1, tab2, tab3 = st.tabs(["📋 数据预览", "📊 数据信息", "🛠️ 处理功能"])
        
        with tab1:
            st.subheader("数据预览")
            
            # 预览行数选择
            preview_rows = st.slider(
                "预览行数",
                min_value=5,
                max_value=min(100, info['rows']),
                value=min(config.PREVIEW_ROWS, info['rows']),
                step=5
            )
            
            # 显示预览数据
            preview_data = handler.get_preview(preview_rows)
            if preview_data is not None:
                st.dataframe(
                    preview_data,
                    use_container_width=True,
                    height=400
                )
        
        with tab2:
            st.subheader("数据详细信息")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**列名列表：**")
                for i, col_name in enumerate(info['column_names'], 1):
                    st.write(f"{i}. {col_name}")
            
            with col2:
                st.write("**数据类型：**")
                for col_name, dtype in info['data_types'].items():
                    st.write(f"`{col_name}`: {dtype}")
        
        with tab3:
            st.subheader("处理功能")
            
            # 功能分类
            function_category = st.radio(
                "选择功能类别",
                ["🧹 数据清洗", "🔍 数据筛选", "📊 数据排序", "📈 数据统计", "📝 列操作", "🔤 文本处理", "🧮 数值计算"],
                horizontal=True
            )
            
            st.markdown("---")
            
            # 数据清洗功能
            if function_category == "🧹 数据清洗":
                st.write("**数据清洗工具**")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**删除空行**")
                    if st.button("🗑️ 删除空行", use_container_width=True):
                        result = handler.remove_empty_rows()
                        if result['success']:
                            st.success(result['message'])
                            st.rerun()
                        else:
                            st.error(result['error'])
                    
                    st.markdown("---")
                    st.write("**删除重复行**")
                    # 选择用于判断重复的列
                    dup_columns = st.multiselect(
                        "选择用于判断重复的列（留空表示所有列）",
                        info['column_names'],
                        key="dup_columns"
                    )
                    dup_keep = st.selectbox(
                        "保留方式",
                        ["first", "last"],
                        key="dup_keep",
                        help="first: 保留第一个重复项，last: 保留最后一个重复项"
                    )
                    
                    if st.button("🔄 删除重复行", use_container_width=True):
                        result = handler.remove_duplicates(
                            columns=dup_columns if dup_columns else None,
                            keep=dup_keep
                        )
                        if result['success']:
                            st.success(result['message'])
                            st.rerun()
                        else:
                            st.error(result['error'])
                
                with col2:
                    st.write("**填充缺失值**")
                    fill_column = st.selectbox("选择要填充的列", info['column_names'], key="fill_col")
                    fill_method = st.selectbox(
                        "填充方法",
                        ["value", "mean", "median", "mode", "forward", "backward"],
                        key="fill_method"
                    )
                    
                    fill_value = None
                    if fill_method == "value":
                        fill_value = st.text_input("填充值", key="fill_val")
                        if fill_value:
                            try:
                                # 尝试转换为数字
                                if '.' in fill_value:
                                    fill_value = float(fill_value)
                                else:
                                    fill_value = int(fill_value)
                            except:
                                pass  # 保持为字符串
                        else:
                            st.warning("请输入填充值")
                    
                    if st.button("✨ 填充缺失值", use_container_width=True):
                        if fill_method == "value" and fill_value is None:
                            st.error("请先输入填充值")
                        else:
                            result = handler.fill_missing_values(
                                column=fill_column,
                                method=fill_method,
                                value=fill_value
                            )
                            if result['success']:
                                st.success(result['message'])
                                st.rerun()
                            else:
                                st.error(result['error'])
            
            # 数据筛选功能
            elif function_category == "🔍 数据筛选":
                st.write("**数据筛选工具**")
                
                filter_column = st.selectbox("选择筛选列", info['column_names'], key="filter_col")
                filter_condition = st.selectbox(
                    "选择条件",
                    ["==", "!=", ">", "<", ">=", "<=", "contains", "not_contains"],
                    key="filter_cond"
                )
                
                filter_value = st.text_input("输入比较值", key="filter_val")
                
                if st.button("🔍 应用筛选", use_container_width=True, type="primary"):
                    # 尝试转换数值
                    try:
                        if filter_condition in ['>', '<', '>=', '<=']:
                            if '.' in filter_value:
                                filter_value = float(filter_value)
                            else:
                                filter_value = int(filter_value)
                        elif filter_condition == "==":
                            # 尝试转换为数字
                            try:
                                if '.' in filter_value:
                                    filter_value = float(filter_value)
                                else:
                                    filter_value = int(filter_value)
                            except:
                                pass  # 保持为字符串
                    except:
                        pass
                    
                    result = handler.filter_data(
                        column=filter_column,
                        condition=filter_condition,
                        value=filter_value
                    )
                    if result['success']:
                        st.success(result['message'])
                        st.info(f"原始行数: {result['original_rows']} → 当前行数: {result['current_rows']}")
                        st.rerun()
                    else:
                        st.error(result['error'])
            
            # 数据排序功能
            elif function_category == "📊 数据排序":
                st.write("**数据排序工具**")
                
                sort_columns = st.multiselect(
                    "选择排序列（可多选，按顺序排序）",
                    info['column_names'],
                    key="sort_cols"
                )
                
                if sort_columns:
                    st.write("**排序方向（升序/降序）**")
                    sort_ascending = []
                    for i, col in enumerate(sort_columns):
                        asc = st.checkbox(f"{col} 升序", value=True, key=f"sort_asc_{i}")
                        sort_ascending.append(asc)
                    
                    if st.button("📊 应用排序", use_container_width=True, type="primary"):
                        result = handler.sort_data(
                            columns=sort_columns,
                            ascending=sort_ascending
                        )
                        if result['success']:
                            st.success(result['message'])
                            st.rerun()
                        else:
                            st.error(result['error'])
                else:
                    st.info("请先选择要排序的列")
            
            # 数据统计功能
            elif function_category == "📈 数据统计":
                st.write("**数据统计信息**")
                
                if st.button("📈 生成统计报告", use_container_width=True, type="primary"):
                    result = handler.get_statistics()
                    if result['success']:
                        stats = result['statistics']
                        
                        # 显示缺失值统计
                        st.subheader("缺失值统计")
                        missing_df = pd.DataFrame({
                            '列名': list(stats['missing_values'].keys()),
                            '缺失数量': list(stats['missing_values'].values())
                        })
                        st.dataframe(missing_df, use_container_width=True)
                        
                        # 显示数值列统计
                        if result['numeric_columns']:
                            st.subheader("数值列统计")
                            numeric_stats = pd.DataFrame(stats['numeric'])
                            st.dataframe(numeric_stats, use_container_width=True)
                        else:
                            st.info("当前数据中没有数值类型的列")
                    else:
                        st.error(result['error'])
            
            # 列操作功能
            elif function_category == "📝 列操作":
                st.write("**列操作工具**")
                
                col_op = st.selectbox(
                    "选择操作",
                    ["重命名列", "删除列", "删除多列", "添加列", "转换数据类型"],
                    key="col_operation"
                )
                
                st.markdown("---")
                
                if col_op == "重命名列":
                    old_name = st.selectbox("选择要重命名的列", info['column_names'], key="rename_old")
                    new_name = st.text_input("输入新列名", key="rename_new")
                    
                    if st.button("✏️ 重命名", use_container_width=True):
                        if new_name:
                            result = handler.rename_column(old_name, new_name)
                            if result['success']:
                                st.success(result['message'])
                                st.rerun()
                            else:
                                st.error(result['error'])
                        else:
                            st.warning("请输入新列名")
                
                elif col_op == "删除列":
                    del_col = st.selectbox("选择要删除的列", info['column_names'], key="del_col")
                    
                    if st.button("🗑️ 删除列", use_container_width=True, type="primary"):
                        result = handler.delete_column(del_col)
                        if result['success']:
                            st.success(result['message'])
                            st.rerun()
                        else:
                            st.error(result['error'])
                
                elif col_op == "删除多列":
                    del_cols = st.multiselect("选择要删除的列（可多选）", info['column_names'], key="del_cols")
                    
                    if st.button("🗑️ 删除多列", use_container_width=True, type="primary"):
                        if del_cols:
                            result = handler.delete_columns(del_cols)
                            if result['success']:
                                st.success(result['message'])
                                st.rerun()
                            else:
                                st.error(result['error'])
                        else:
                            st.warning("请至少选择一列")
                
                elif col_op == "添加列":
                    new_col_name = st.text_input("新列名", key="new_col_name")
                    new_col_value = st.text_input("初始值（留空表示空值）", key="new_col_value")
                    
                    if st.button("➕ 添加列", use_container_width=True):
                        if new_col_name:
                            value = new_col_value if new_col_value else None
                            result = handler.add_column(new_col_name, value)
                            if result['success']:
                                st.success(result['message'])
                                st.rerun()
                            else:
                                st.error(result['error'])
                        else:
                            st.warning("请输入列名")
                
                elif col_op == "转换数据类型":
                    conv_col = st.selectbox("选择要转换的列", info['column_names'], key="conv_col")
                    conv_type = st.selectbox(
                        "目标类型",
                        ["int", "float", "str", "datetime", "bool"],
                        key="conv_type"
                    )
                    
                    if st.button("🔄 转换类型", use_container_width=True):
                        result = handler.convert_data_type(conv_col, conv_type)
                        if result['success']:
                            st.success(result['message'])
                            st.rerun()
                        else:
                            st.error(result['error'])
            
            # 文本处理功能
            elif function_category == "🔤 文本处理":
                st.write("**文本处理工具**")
                
                text_op = st.selectbox(
                    "选择操作",
                    ["去除空格", "大小写转换", "文本替换"],
                    key="text_operation"
                )
                
                text_col = st.selectbox("选择要处理的列", info['column_names'], key="text_col")
                
                st.markdown("---")
                
                if text_op == "去除空格":
                    if st.button("✂️ 去除前后空格", use_container_width=True):
                        result = handler.text_trim(text_col)
                        if result['success']:
                            st.success(result['message'])
                            st.rerun()
                        else:
                            st.error(result['error'])
                
                elif text_op == "大小写转换":
                    case_type = st.selectbox(
                        "转换类型",
                        ["upper", "lower", "title", "capitalize"],
                        format_func=lambda x: {
                            "upper": "大写",
                            "lower": "小写",
                            "title": "标题格式",
                            "capitalize": "首字母大写"
                        }[x],
                        key="case_type"
                    )
                    
                    if st.button("🔄 转换大小写", use_container_width=True):
                        result = handler.text_case(text_col, case_type)
                        if result['success']:
                            st.success(result['message'])
                            st.rerun()
                        else:
                            st.error(result['error'])
                
                elif text_op == "文本替换":
                    old_text = st.text_input("要替换的文本", key="old_text")
                    new_text = st.text_input("替换为", key="new_text")
                    
                    if st.button("🔄 替换文本", use_container_width=True):
                        if old_text:
                            result = handler.text_replace(text_col, old_text, new_text)
                            if result['success']:
                                st.success(result['message'])
                                st.rerun()
                            else:
                                st.error(result['error'])
                        else:
                            st.warning("请输入要替换的文本")
            
            # 数值计算功能
            elif function_category == "🧮 数值计算":
                st.write("**数值计算工具**")
                
                calc_op = st.selectbox(
                    "选择操作",
                    ["添加计算列", "分组统计"],
                    key="calc_operation"
                )
                
                st.markdown("---")
                
                if calc_op == "添加计算列":
                    new_col = st.text_input("新列名", key="calc_new_col")
                    formula = st.text_input(
                        "计算公式（例如: col1 + col2 或 col1 * 2）",
                        key="calc_formula",
                        help="使用列名进行计算，支持 +, -, *, / 运算符"
                    )
                    calc_cols = st.multiselect(
                        "参与计算的列（选择后会在公式中可用）",
                        info['column_names'],
                        key="calc_cols"
                    )
                    
                    if st.button("➕ 添加计算列", use_container_width=True):
                        if new_col and formula and calc_cols:
                            result = handler.calculate_column(new_col, formula, calc_cols)
                            if result['success']:
                                st.success(result['message'])
                                st.rerun()
                            else:
                                st.error(result['error'])
                        else:
                            st.warning("请填写所有必填项")
                
                elif calc_op == "分组统计":
                    group_cols = st.multiselect(
                        "分组列（可多选）",
                        info['column_names'],
                        key="group_cols"
                    )
                    
                    st.write("**聚合函数设置**")
                    agg_col = st.selectbox("选择要聚合的列", info['column_names'], key="agg_col")
                    agg_funcs = st.multiselect(
                        "选择聚合函数",
                        ["sum", "mean", "count", "min", "max", "std"],
                        key="agg_funcs"
                    )
                    
                    if st.button("📊 执行分组统计", use_container_width=True):
                        if group_cols and agg_col and agg_funcs:
                            agg_dict = {agg_col: agg_funcs}
                            result = handler.group_by(group_cols, agg_dict)
                            if result['success']:
                                st.success(result['message'])
                                st.rerun()
                            else:
                                st.error(result['error'])
                        else:
                            st.warning("请填写所有必填项")
        
        st.markdown("---")
        
        # 下载区域
        st.subheader("💾 导出文件")
        
        export_format = st.radio(
            "导出格式",
            ["Excel (.xlsx)", "CSV (.csv)", "JSON (.json)"],
            horizontal=True,
            key="export_format"
        )
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # 使用更可靠的方法生成文件名
            import os
            base_name = os.path.splitext(info['file_name'])[0]
            
            if export_format == "Excel (.xlsx)":
                default_name = f"{base_name}_processed.xlsx"
                ext = '.xlsx'
            elif export_format == "CSV (.csv)":
                default_name = f"{base_name}_processed.csv"
                ext = '.csv'
            else:  # JSON
                default_name = f"{base_name}_processed.json"
                ext = '.json'
            
            download_filename = st.text_input(
                "下载文件名",
                value=default_name,
                help=f"输入导出文件的名称（包含 {ext} 扩展名）"
            )
        
        with col2:
            st.write("")  # 占位
            st.write("")  # 占位
            if st.button("📥 下载文件", use_container_width=True, type="primary"):
                try:
                    if export_format == "Excel (.xlsx)":
                        file_bytes = handler.export_to_excel()
                        mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    elif export_format == "CSV (.csv)":
                        file_bytes = handler.export_to_csv()
                        mime_type = "text/csv"
                    else:  # JSON
                        file_bytes = handler.export_to_json()
                        mime_type = "application/json"
                    
                    st.download_button(
                        label="⬇️ 点击下载",
                        data=file_bytes,
                        file_name=download_filename,
                        mime=mime_type,
                        use_container_width=True
                    )
                except Exception as e:
                    st.error(f"导出文件时出错: {str(e)}")
    
    else:
        # 未加载文件时的提示
        st.info("👈 请在左侧上传 Excel 文件开始使用")
        
        # 显示使用示例
        with st.expander("📖 使用说明", expanded=True):
            st.markdown("""
            ### 功能说明
            
            1. **文件上传**
               - 支持 .xlsx, .xls, .xlsm 格式
               - 文件大小限制: 50MB
            
            2. **数据预览**
               - 查看表格的前 N 行数据
               - 可调整预览行数
            
            3. **数据信息**
               - 查看列名和数据类型
               - 了解数据规模
            
            4. **文件导出**
               - 将处理后的数据导出为 Excel 文件
               - 支持自定义文件名
            
            ### 后续功能
            
            更多处理功能将逐步添加，包括：
            - 数据清洗和去重
            - 数据筛选和排序
            - 数据统计和分析
            - 多表合并
            - 格式转换
            - 等等...
            """)


if __name__ == "__main__":
    main()

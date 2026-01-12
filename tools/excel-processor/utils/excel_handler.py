"""
Excel 处理核心模块
提供基础的 Excel 读写功能，后续功能将在此模块中扩展
"""

import pandas as pd
import io
from typing import Optional, Dict, Any


class ExcelHandler:
    """Excel 文件处理类"""
    
    def __init__(self):
        """初始化 Excel 处理器"""
        self.data: Optional[pd.DataFrame] = None
        self.file_name: Optional[str] = None
    
    def load_file(self, uploaded_file) -> Dict[str, Any]:
        """
        加载 Excel 文件
        
        Args:
            uploaded_file: Streamlit 上传的文件对象
            
        Returns:
            dict: 包含加载结果和信息的字典
        """
        try:
            # 根据文件扩展名选择读取方式
            file_extension = uploaded_file.name.split('.')[-1].lower()
            
            if file_extension == 'xlsx' or file_extension == 'xlsm':
                self.data = pd.read_excel(uploaded_file, engine='openpyxl')
            elif file_extension == 'xls':
                self.data = pd.read_excel(uploaded_file, engine='xlrd')
            else:
                return {
                    'success': False,
                    'error': f'不支持的文件格式: .{file_extension}'
                }
            
            self.file_name = uploaded_file.name
            
            return {
                'success': True,
                'message': f'成功加载文件: {uploaded_file.name}',
                'rows': len(self.data),
                'columns': len(self.data.columns),
                'column_names': list(self.data.columns)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'加载文件时出错: {str(e)}'
            }
    
    def get_data(self) -> Optional[pd.DataFrame]:
        """
        获取当前加载的数据
        
        Returns:
            pd.DataFrame: 当前数据框，如果未加载则返回 None
        """
        return self.data
    
    def get_preview(self, n_rows: int = 10) -> Optional[pd.DataFrame]:
        """
        获取数据预览
        
        Args:
            n_rows: 预览行数
            
        Returns:
            pd.DataFrame: 预览数据
        """
        if self.data is not None:
            return self.data.head(n_rows)
        return None
    
    def get_info(self) -> Dict[str, Any]:
        """
        获取数据基本信息
        
        Returns:
            dict: 数据信息字典
        """
        if self.data is None:
            return {
                'loaded': False,
                'message': '尚未加载文件'
            }
        
        return {
            'loaded': True,
            'file_name': self.file_name,
            'rows': len(self.data),
            'columns': len(self.data.columns),
            'column_names': list(self.data.columns),
            'data_types': self.data.dtypes.astype(str).to_dict(),
            'memory_usage': f"{self.data.memory_usage(deep=True).sum() / 1024:.2f} KB"
        }
    
    def export_to_excel(self) -> bytes:
        """
        将数据导出为 Excel 文件（字节流）
        
        Returns:
            bytes: Excel 文件的字节流
        """
        if self.data is None:
            raise ValueError("没有可导出的数据")
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            self.data.to_excel(writer, index=False, sheet_name='Sheet1')
        
        output.seek(0)
        return output.getvalue()
    
    def clear_data(self):
        """清空当前数据"""
        self.data = None
        self.file_name = None
    
    # ========== 数据处理功能 ==========
    
    def remove_empty_rows(self) -> Dict[str, Any]:
        """
        删除完全空白的行
        
        Returns:
            dict: 处理结果
        """
        if self.data is None:
            return {'success': False, 'error': '请先加载文件'}
        
        original_rows = len(self.data)
        self.data = self.data.dropna(how='all')
        removed_rows = original_rows - len(self.data)
        
        return {
            'success': True,
            'message': f'已删除 {removed_rows} 行空行',
            'original_rows': original_rows,
            'current_rows': len(self.data),
            'removed_rows': removed_rows
        }
    
    def remove_duplicates(self, columns: list = None, keep: str = 'first') -> Dict[str, Any]:
        """
        删除重复行
        
        Args:
            columns: 用于判断重复的列（None 表示所有列）
            keep: 保留方式（'first' 保留第一个，'last' 保留最后一个，False 删除所有重复）
            
        Returns:
            dict: 处理结果
        """
        if self.data is None:
            return {'success': False, 'error': '请先加载文件'}
        
        original_rows = len(self.data)
        self.data = self.data.drop_duplicates(subset=columns, keep=keep)
        removed_rows = original_rows - len(self.data)
        
        return {
            'success': True,
            'message': f'已删除 {removed_rows} 行重复数据',
            'original_rows': original_rows,
            'current_rows': len(self.data),
            'removed_rows': removed_rows
        }
    
    def fill_missing_values(self, column: str, method: str = 'mean', value: Any = None) -> Dict[str, Any]:
        """
        填充缺失值
        
        Args:
            column: 要填充的列名
            method: 填充方法（'mean', 'median', 'mode', 'forward', 'backward', 'value'）
            value: 当 method='value' 时使用的填充值
            
        Returns:
            dict: 处理结果
        """
        if self.data is None:
            return {'success': False, 'error': '请先加载文件'}
        
        if column not in self.data.columns:
            return {'success': False, 'error': f'列 "{column}" 不存在'}
        
        original_missing = self.data[column].isna().sum()
        
        if method == 'mean':
            fill_value = self.data[column].mean()
        elif method == 'median':
            fill_value = self.data[column].median()
        elif method == 'mode':
            fill_value = self.data[column].mode()[0] if not self.data[column].mode().empty else None
        elif method == 'forward':
            self.data[column] = self.data[column].fillna(method='ffill')
            fill_value = None
        elif method == 'backward':
            self.data[column] = self.data[column].fillna(method='bfill')
            fill_value = None
        elif method == 'value':
            fill_value = value
        else:
            return {'success': False, 'error': f'不支持的填充方法: {method}'}
        
        if fill_value is not None:
            self.data[column] = self.data[column].fillna(fill_value)
        
        return {
            'success': True,
            'message': f'已填充 {original_missing} 个缺失值',
            'column': column,
            'method': method,
            'filled_count': original_missing
        }
    
    def filter_data(self, column: str, condition: str, value: Any) -> Dict[str, Any]:
        """
        按条件筛选数据
        
        Args:
            column: 筛选的列名
            condition: 条件（'==', '!=', '>', '<', '>=', '<=', 'contains', 'not_contains'）
            value: 比较值
            
        Returns:
            dict: 处理结果
        """
        if self.data is None:
            return {'success': False, 'error': '请先加载文件'}
        
        if column not in self.data.columns:
            return {'success': False, 'error': f'列 "{column}" 不存在'}
        
        original_rows = len(self.data)
        
        try:
            if condition == '==':
                self.data = self.data[self.data[column] == value]
            elif condition == '!=':
                self.data = self.data[self.data[column] != value]
            elif condition == '>':
                self.data = self.data[self.data[column] > value]
            elif condition == '<':
                self.data = self.data[self.data[column] < value]
            elif condition == '>=':
                self.data = self.data[self.data[column] >= value]
            elif condition == '<=':
                self.data = self.data[self.data[column] <= value]
            elif condition == 'contains':
                self.data = self.data[self.data[column].astype(str).str.contains(str(value), na=False)]
            elif condition == 'not_contains':
                self.data = self.data[~self.data[column].astype(str).str.contains(str(value), na=False)]
            else:
                return {'success': False, 'error': f'不支持的条件: {condition}'}
            
            filtered_rows = len(self.data)
            removed_rows = original_rows - filtered_rows
            
            return {
                'success': True,
                'message': f'筛选完成，保留 {filtered_rows} 行，删除 {removed_rows} 行',
                'original_rows': original_rows,
                'current_rows': filtered_rows,
                'removed_rows': removed_rows
            }
        except Exception as e:
            return {'success': False, 'error': f'筛选时出错: {str(e)}'}
    
    def sort_data(self, columns: list, ascending: list = None) -> Dict[str, Any]:
        """
        排序数据
        
        Args:
            columns: 要排序的列名列表
            ascending: 每列的排序方向列表（True 升序，False 降序），None 表示全部升序
            
        Returns:
            dict: 处理结果
        """
        if self.data is None:
            return {'success': False, 'error': '请先加载文件'}
        
        for col in columns:
            if col not in self.data.columns:
                return {'success': False, 'error': f'列 "{col}" 不存在'}
        
        if ascending is None:
            ascending = [True] * len(columns)
        
        self.data = self.data.sort_values(by=columns, ascending=ascending)
        
        return {
            'success': True,
            'message': f'已按 {", ".join(columns)} 排序',
            'sorted_columns': columns
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        获取数据统计信息
        
        Returns:
            dict: 统计信息
        """
        if self.data is None:
            return {'success': False, 'error': '请先加载文件'}
        
        numeric_cols = self.data.select_dtypes(include=['number']).columns.tolist()
        stats = {}
        
        if numeric_cols:
            stats['numeric'] = self.data[numeric_cols].describe().to_dict()
        
        stats['missing_values'] = self.data.isna().sum().to_dict()
        stats['data_types'] = self.data.dtypes.astype(str).to_dict()
        
        return {
            'success': True,
            'statistics': stats,
            'numeric_columns': numeric_cols
        }
    
    # ========== 列操作功能 ==========
    
    def rename_column(self, old_name: str, new_name: str) -> Dict[str, Any]:
        """
        重命名列
        
        Args:
            old_name: 原列名
            new_name: 新列名
            
        Returns:
            dict: 处理结果
        """
        if self.data is None:
            return {'success': False, 'error': '请先加载文件'}
        
        if old_name not in self.data.columns:
            return {'success': False, 'error': f'列 "{old_name}" 不存在'}
        
        if new_name in self.data.columns and new_name != old_name:
            return {'success': False, 'error': f'列 "{new_name}" 已存在'}
        
        self.data.rename(columns={old_name: new_name}, inplace=True)
        
        return {
            'success': True,
            'message': f'已将列 "{old_name}" 重命名为 "{new_name}"'
        }
    
    def delete_column(self, column: str) -> Dict[str, Any]:
        """
        删除列
        
        Args:
            column: 要删除的列名
            
        Returns:
            dict: 处理结果
        """
        if self.data is None:
            return {'success': False, 'error': '请先加载文件'}
        
        if column not in self.data.columns:
            return {'success': False, 'error': f'列 "{column}" 不存在'}
        
        original_cols = len(self.data.columns)
        self.data = self.data.drop(columns=[column])
        
        return {
            'success': True,
            'message': f'已删除列 "{column}"',
            'original_columns': original_cols,
            'current_columns': len(self.data.columns)
        }
    
    def delete_columns(self, columns: list) -> Dict[str, Any]:
        """
        删除多列
        
        Args:
            columns: 要删除的列名列表
            
        Returns:
            dict: 处理结果
        """
        if self.data is None:
            return {'success': False, 'error': '请先加载文件'}
        
        missing_cols = [col for col in columns if col not in self.data.columns]
        if missing_cols:
            return {'success': False, 'error': f'以下列不存在: {", ".join(missing_cols)}'}
        
        original_cols = len(self.data.columns)
        self.data = self.data.drop(columns=columns)
        
        return {
            'success': True,
            'message': f'已删除 {len(columns)} 列',
            'original_columns': original_cols,
            'current_columns': len(self.data.columns),
            'deleted_columns': columns
        }
    
    def add_column(self, column_name: str, value: Any = None, position: int = None) -> Dict[str, Any]:
        """
        添加新列
        
        Args:
            column_name: 新列名
            value: 列的初始值（可以是单个值或列表）
            position: 插入位置（None 表示添加到末尾）
            
        Returns:
            dict: 处理结果
        """
        if self.data is None:
            return {'success': False, 'error': '请先加载文件'}
        
        if column_name in self.data.columns:
            return {'success': False, 'error': f'列 "{column_name}" 已存在'}
        
        if value is None:
            value = ''
        
        # 添加列
        if position is None:
            self.data[column_name] = value
        else:
            cols = list(self.data.columns)
            cols.insert(position, column_name)
            self.data[column_name] = value
            self.data = self.data[cols]
        
        return {
            'success': True,
            'message': f'已添加列 "{column_name}"',
            'current_columns': len(self.data.columns)
        }
    
    def convert_data_type(self, column: str, target_type: str) -> Dict[str, Any]:
        """
        转换数据类型
        
        Args:
            column: 要转换的列名
            target_type: 目标类型（'int', 'float', 'str', 'datetime', 'bool'）
            
        Returns:
            dict: 处理结果
        """
        if self.data is None:
            return {'success': False, 'error': '请先加载文件'}
        
        if column not in self.data.columns:
            return {'success': False, 'error': f'列 "{column}" 不存在'}
        
        original_type = str(self.data[column].dtype)
        
        try:
            if target_type == 'int':
                self.data[column] = pd.to_numeric(self.data[column], errors='coerce').astype('Int64')
            elif target_type == 'float':
                self.data[column] = pd.to_numeric(self.data[column], errors='coerce')
            elif target_type == 'str':
                self.data[column] = self.data[column].astype(str)
            elif target_type == 'datetime':
                self.data[column] = pd.to_datetime(self.data[column], errors='coerce')
            elif target_type == 'bool':
                self.data[column] = self.data[column].astype(bool)
            else:
                return {'success': False, 'error': f'不支持的类型: {target_type}'}
            
            return {
                'success': True,
                'message': f'已将列 "{column}" 从 {original_type} 转换为 {target_type}',
                'original_type': original_type,
                'new_type': target_type
            }
        except Exception as e:
            return {'success': False, 'error': f'转换类型时出错: {str(e)}'}
    
    # ========== 文本处理功能 ==========
    
    def text_trim(self, column: str) -> Dict[str, Any]:
        """
        去除文本列的前后空格
        
        Args:
            column: 要处理的列名
            
        Returns:
            dict: 处理结果
        """
        if self.data is None:
            return {'success': False, 'error': '请先加载文件'}
        
        if column not in self.data.columns:
            return {'success': False, 'error': f'列 "{column}" 不存在'}
        
        self.data[column] = self.data[column].astype(str).str.strip()
        
        return {
            'success': True,
            'message': f'已去除列 "{column}" 的前后空格'
        }
    
    def text_case(self, column: str, case_type: str) -> Dict[str, Any]:
        """
        转换文本大小写
        
        Args:
            column: 要处理的列名
            case_type: 转换类型（'upper' 大写, 'lower' 小写, 'title' 标题, 'capitalize' 首字母大写）
            
        Returns:
            dict: 处理结果
        """
        if self.data is None:
            return {'success': False, 'error': '请先加载文件'}
        
        if column not in self.data.columns:
            return {'success': False, 'error': f'列 "{column}" 不存在'}
        
        case_map = {
            'upper': 'upper',
            'lower': 'lower',
            'title': 'title',
            'capitalize': 'capitalize'
        }
        
        if case_type not in case_map:
            return {'success': False, 'error': f'不支持的转换类型: {case_type}'}
        
        method = getattr(self.data[column].astype(str).str, case_map[case_type])
        self.data[column] = method()
        
        return {
            'success': True,
            'message': f'已将列 "{column}" 转换为{case_type}'
        }
    
    def text_replace(self, column: str, old_text: str, new_text: str) -> Dict[str, Any]:
        """
        替换文本
        
        Args:
            column: 要处理的列名
            old_text: 要替换的文本
            new_text: 替换后的文本
            
        Returns:
            dict: 处理结果
        """
        if self.data is None:
            return {'success': False, 'error': '请先加载文件'}
        
        if column not in self.data.columns:
            return {'success': False, 'error': f'列 "{column}" 不存在'}
        
        self.data[column] = self.data[column].astype(str).str.replace(old_text, new_text, regex=False)
        
        return {
            'success': True,
            'message': f'已在列 "{column}" 中将 "{old_text}" 替换为 "{new_text}"'
        }
    
    # ========== 数值计算功能 ==========
    
    def calculate_column(self, new_column: str, formula: str, columns: list) -> Dict[str, Any]:
        """
        添加计算列
        
        Args:
            new_column: 新列名
            formula: 计算公式（支持 +, -, *, /, 例如: 'col1 + col2', 'col1 * 2'）
            columns: 参与计算的列名列表
            
        Returns:
            dict: 处理结果
        """
        if self.data is None:
            return {'success': False, 'error': '请先加载文件'}
        
        if new_column in self.data.columns:
            return {'success': False, 'error': f'列 "{new_column}" 已存在'}
        
        missing_cols = [col for col in columns if col not in self.data.columns]
        if missing_cols:
            return {'success': False, 'error': f'以下列不存在: {", ".join(missing_cols)}'}
        
        try:
            # 安全地构建计算表达式
            # 将列名替换为数据框引用
            expr = formula
            for col in columns:
                # 使用更安全的替换方式，避免部分匹配
                import re
                pattern = r'\b' + re.escape(col) + r'\b'
                expr = re.sub(pattern, f'self.data["{col}"]', expr)
            
            # 限制可用的内置函数，提高安全性
            safe_dict = {
                '__builtins__': {},
                'self': self,
                'pd': pd,
                'abs': abs,
                'round': round,
                'min': min,
                'max': max,
                'sum': sum
            }
            
            # 执行计算
            result = eval(expr, safe_dict)
            self.data[new_column] = result
            
            return {
                'success': True,
                'message': f'已添加计算列 "{new_column}"',
                'formula': formula
            }
        except Exception as e:
            return {'success': False, 'error': f'计算时出错: {str(e)}'}
    
    def group_by(self, group_columns: list, agg_functions: Dict[str, list]) -> Dict[str, Any]:
        """
        分组统计
        
        Args:
            group_columns: 分组列名列表
            agg_functions: 聚合函数字典，格式: {'列名': ['sum', 'mean', 'count', ...]}
            
        Returns:
            dict: 处理结果
        """
        if self.data is None:
            return {'success': False, 'error': '请先加载文件'}
        
        missing_cols = [col for col in group_columns if col not in self.data.columns]
        if missing_cols:
            return {'success': False, 'error': f'以下分组列不存在: {", ".join(missing_cols)}'}
        
        try:
            # 执行分组聚合
            grouped = self.data.groupby(group_columns).agg(agg_functions)
            # 重置索引
            grouped = grouped.reset_index()
            # 扁平化列名
            grouped.columns = ['_'.join(col).strip() if col[1] else col[0] for col in grouped.columns.values]
            
            original_rows = len(self.data)
            self.data = grouped
            new_rows = len(self.data)
            
            return {
                'success': True,
                'message': f'分组统计完成，从 {original_rows} 行聚合为 {new_rows} 行',
                'original_rows': original_rows,
                'new_rows': new_rows
            }
        except Exception as e:
            return {'success': False, 'error': f'分组统计时出错: {str(e)}'}
    
    # ========== 导出功能 ==========
    
    def export_to_csv(self) -> bytes:
        """
        将数据导出为 CSV 文件（字节流）
        
        Returns:
            bytes: CSV 文件的字节流
        """
        if self.data is None:
            raise ValueError("没有可导出的数据")
        
        output = io.BytesIO()
        self.data.to_csv(output, index=False, encoding='utf-8-sig')
        output.seek(0)
        return output.getvalue()
    
    def export_to_json(self) -> bytes:
        """
        将数据导出为 JSON 文件（字节流）
        
        Returns:
            bytes: JSON 文件的字节流
        """
        if self.data is None:
            raise ValueError("没有可导出的数据")
        
        import json
        output = io.BytesIO()
        json_str = self.data.to_json(orient='records', force_ascii=False, indent=2)
        output.write(json_str.encode('utf-8'))
        output.seek(0)
        return output.getvalue()
    
    def process_data(self, operation: str, **kwargs) -> Dict[str, Any]:
        """
        数据处理入口（统一接口）
        
        Args:
            operation: 操作类型
            **kwargs: 操作参数
            
        Returns:
            dict: 处理结果
        """
        if self.data is None:
            return {'success': False, 'error': '请先加载文件'}
        
        operations = {
            'remove_empty_rows': self.remove_empty_rows,
            'remove_duplicates': self.remove_duplicates,
            'fill_missing': self.fill_missing_values,
            'filter': self.filter_data,
            'sort': self.sort_data,
            'statistics': self.get_statistics,
            'rename_column': self.rename_column,
            'delete_column': self.delete_column,
            'delete_columns': self.delete_columns,
            'add_column': self.add_column,
            'convert_data_type': self.convert_data_type,
            'text_trim': self.text_trim,
            'text_case': self.text_case,
            'text_replace': self.text_replace,
            'calculate_column': self.calculate_column,
            'group_by': self.group_by
        }
        
        if operation not in operations:
            return {'success': False, 'error': f'不支持的操作: {operation}'}
        
        try:
            return operations[operation](**kwargs)
        except Exception as e:
            return {'success': False, 'error': f'处理时出错: {str(e)}'}

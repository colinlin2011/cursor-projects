# -*- coding: utf-8 -*-
"""
飞书多维表格协作器 - 通用多维表格协作能力

提供简洁的API，支持：
- 创建/访问多维表格
- 数据表的CRUD操作
- 获取表格结构（字段、视图等）
- 数据分析和总结
"""

import sys
import os
import re
from typing import Optional, Dict, List, Any
from datetime import datetime
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from feishu_api_wrapper import FeishuAPI


class FeishuBitableCollaborator:
    """
    飞书多维表格协作器
    
    提供统一的接口进行多维表格协作，支持数据分析和总结
    """
    
    def __init__(
        self,
        app_id: str,
        app_secret: str,
        user_access_token: Optional[str] = None,
        tenant_access_token: Optional[str] = None
    ):
        """
        初始化多维表格协作器
        
        Args:
            app_id: 飞书应用ID
            app_secret: 飞书应用密钥
            user_access_token: 用户身份凭证（优先使用）
            tenant_access_token: 租户身份凭证（备选）
        """
        self.app_id = app_id
        self.app_secret = app_secret
        
        # 初始化API
        self.api = FeishuAPI(
            plugin_id="",
            plugin_secret="",
            app_id=app_id,
            app_secret=app_secret
        )
        
        if user_access_token:
            self.api.set_user_access_token(user_access_token)
        elif tenant_access_token:
            # 如果提供了tenant_access_token，需要手动设置
            pass
    
    def get_app_info(self, app_token: str) -> Optional[Dict]:
        """
        获取多维表格信息
        
        Args:
            app_token: 多维表格app_token
            
        Returns:
            表格信息或None
        """
        has_user_token = hasattr(self.api, '_user_access_token') and self.api._user_access_token is not None
        return self.api.get_bitable(app_token, use_user_token=has_user_token)
    
    def list_tables(self, app_token: str) -> List[Dict]:
        """
        列出所有数据表
        
        Args:
            app_token: 多维表格app_token
            
        Returns:
            数据表列表
        """
        has_user_token = hasattr(self.api, '_user_access_token') and self.api._user_access_token is not None
        result = self.api.list_bitable_tables(app_token, use_user_token=has_user_token)
        if result:
            # 处理不同的返回格式
            if 'code' in result:
                # 标准格式：有code字段
                if result.get('code') == 0:
                    return result.get('data', {}).get('items', [])
            else:
                # 直接返回data格式
                if 'items' in result:
                    return result.get('items', [])
        return []
    
    def get_table_structure(
        self,
        app_token: str,
        table_id: str
    ) -> Dict[str, Any]:
        """
        获取数据表结构（字段、视图等）
        
        Args:
            app_token: 多维表格app_token
            table_id: 数据表ID
            
        Returns:
            包含字段和视图信息的字典
        """
        structure = {
            'table_id': table_id,
            'fields': [],
            'views': []
        }
        
        has_user_token = hasattr(self.api, '_user_access_token') and self.api._user_access_token is not None
        
        # 获取字段
        fields_result = self.api.list_bitable_fields(
            app_token,
            table_id,
            use_user_token=has_user_token
        )
        if fields_result:
            # 处理不同的返回格式
            if 'code' in fields_result:
                # 标准格式：有code字段
                if fields_result.get('code') == 0:
                    structure['fields'] = fields_result.get('data', {}).get('items', [])
            else:
                # 直接返回data格式
                if 'items' in fields_result:
                    structure['fields'] = fields_result.get('items', [])
        
        # 获取视图
        views_result = self.api.list_bitable_views(
            app_token,
            table_id,
            use_user_token=has_user_token
        )
        if views_result:
            # 处理不同的返回格式
            if 'code' in views_result:
                # 标准格式：有code字段
                if views_result.get('code') == 0:
                    structure['views'] = views_result.get('data', {}).get('items', [])
            else:
                # 直接返回data格式
                if 'items' in views_result:
                    structure['views'] = views_result.get('items', [])
        
        return structure
    
    def get_all_records(
        self,
        app_token: str,
        table_id: str,
        page_size: int = 500
    ) -> List[Dict]:
        """
        获取所有记录（自动分页）
        
        Args:
            app_token: 多维表格app_token
            table_id: 数据表ID
            page_size: 分页大小（最大500）
            
        Returns:
            所有记录的列表
        """
        all_records = []
        page_token = None
        
        while True:
            result = self.api.get_bitable_records(
                app_token,
                table_id,
                page_size=min(page_size, 500),
                page_token=page_token
            )
            # 注意：get_bitable_records目前不支持use_user_token参数
            
            if not result:
                break
            
            # 处理不同的返回格式
            if 'code' in result:
                # 标准格式：有code字段
                if result.get('code') != 0:
                    break
                data = result.get('data', {})
                records = data.get('items', [])
                has_more = data.get('has_more', False)
                page_token = data.get('page_token')
            else:
                # 直接返回data格式
                records = result.get('items', [])
                has_more = result.get('has_more', False)
                page_token = result.get('page_token')
            
            all_records.extend(records)
            
            if not has_more:
                break
        
        return all_records
    
    def create_record(
        self,
        app_token: str,
        table_id: str,
        fields: Dict[str, Any]
    ) -> Optional[Dict]:
        """
        创建记录
        
        Args:
            app_token: 多维表格app_token
            table_id: 数据表ID
            fields: 字段数据
            
        Returns:
            创建的记录或None
        """
        return self.api.create_bitable_record(
            app_token,
            table_id,
            fields
        )
        # 注意：create_bitable_record目前不支持use_user_token参数
    
    def update_record(
        self,
        app_token: str,
        table_id: str,
        record_id: str,
        fields: Dict[str, Any]
    ) -> Optional[Dict]:
        """
        更新记录
        
        Args:
            app_token: 多维表格app_token
            table_id: 数据表ID
            record_id: 记录ID
            fields: 要更新的字段数据
            
        Returns:
            更新后的记录或None
        """
        has_user_token = hasattr(self.api, '_user_access_token') and self.api._user_access_token is not None
        return self.api.update_bitable_record(
            app_token,
            table_id,
            record_id,
            fields,
            use_user_token=has_user_token
        )
    
    def delete_record(
        self,
        app_token: str,
        table_id: str,
        record_id: str
    ) -> bool:
        """
        删除记录
        
        Args:
            app_token: 多维表格app_token
            table_id: 数据表ID
            record_id: 记录ID
            
        Returns:
            是否成功
        """
        has_user_token = hasattr(self.api, '_user_access_token') and self.api._user_access_token is not None
        result = self.api.delete_bitable_record(
            app_token,
            table_id,
            record_id,
            use_user_token=has_user_token
        )
        return result is not None and result.get('code') == 0
    
    def analyze_table(
        self,
        app_token: str,
        table_id: str
    ) -> Dict[str, Any]:
        """
        分析数据表，提供统计信息和洞察
        
        Args:
            app_token: 多维表格app_token
            table_id: 数据表ID
            
        Returns:
            分析结果字典，包含：
            - structure: 表格结构
            - statistics: 统计信息
            - insights: 数据洞察
        """
        # 获取表格结构
        structure = self.get_table_structure(app_token, table_id)
        
        # 获取所有记录
        records = self.get_all_records(app_token, table_id)
        
        # 统计信息
        statistics = {
            'total_records': len(records),
            'total_fields': len(structure['fields']),
            'total_views': len(structure['views']),
            'field_types': {},
            'field_names': [f.get('field_name', '') for f in structure['fields']]
        }
        
        # 统计字段类型
        for field in structure['fields']:
            field_type = field.get('type', 'unknown')
            statistics['field_types'][field_type] = statistics['field_types'].get(field_type, 0) + 1
        
        # 数据洞察
        insights = self._generate_insights(structure, records)
        
        return {
            'structure': structure,
            'statistics': statistics,
            'insights': insights
        }
    
    def _generate_insights(
        self,
        structure: Dict[str, Any],
        records: List[Dict]
    ) -> List[Dict[str, Any]]:
        """
        生成数据洞察
        
        Args:
            structure: 表格结构
            records: 记录列表
            
        Returns:
            洞察列表
        """
        insights = []
        
        if not records:
            insights.append({
                'type': 'info',
                'title': '数据表为空',
                'content': '当前数据表中没有记录'
            })
            return insights
        
        # 分析字段
        fields = structure.get('fields', [])
        field_map = {f.get('field_id'): f for f in fields}
        
        # 统计各字段的值分布
        field_value_counts = defaultdict(Counter)
        field_non_empty_counts = defaultdict(int)
        
        for record in records:
            fields_data = record.get('fields', {})
            for field_id, value in fields_data.items():
                field_info = field_map.get(field_id, {})
                field_name = field_info.get('field_name', field_id)
                field_type = field_info.get('type', '')
                
                if value is not None and value != '':
                    field_non_empty_counts[field_name] += 1
                    
                    # 根据字段类型进行统计
                    if field_type in ['1', '2', '3']:  # 文本类型
                        if isinstance(value, str):
                            field_value_counts[field_name][value] += 1
                    elif field_type == '4':  # 单选
                        if isinstance(value, list) and len(value) > 0:
                            field_value_counts[field_name][value[0].get('text', '')] += 1
                    elif field_type == '5':  # 多选
                        if isinstance(value, list):
                            for item in value:
                                field_value_counts[field_name][item.get('text', '')] += 1
        
        # 生成洞察
        total_records = len(records)
        
        # 完整性分析
        for field_name, count in field_non_empty_counts.items():
            completion_rate = (count / total_records) * 100
            if completion_rate < 50:
                insights.append({
                    'type': 'warning',
                    'title': f'字段"{field_name}"完整性较低',
                    'content': f'该字段的填充率为{completion_rate:.1f}%，建议检查数据质量'
                })
        
        # 值分布分析
        for field_name, value_counts in field_value_counts.items():
            if len(value_counts) > 0:
                most_common = value_counts.most_common(3)
                if len(most_common) > 0:
                    top_value, top_count = most_common[0]
                    top_percentage = (top_count / total_records) * 100
                    
                    if top_percentage > 80:
                        insights.append({
                            'type': 'info',
                            'title': f'字段"{field_name}"值分布集中',
                            'content': f'最常见的值为"{top_value}"，占比{top_percentage:.1f}%'
                        })
        
        # 数据量分析
        if total_records > 1000:
            insights.append({
                'type': 'info',
                'title': '数据量较大',
                'content': f'当前数据表包含{total_records}条记录，建议考虑数据归档或分表'
            })
        elif total_records < 10:
            insights.append({
                'type': 'info',
                'title': '数据量较少',
                'content': f'当前数据表仅包含{total_records}条记录，可能需要补充数据'
            })
        
        return insights
    
    def summarize_table(
        self,
        app_token: str,
        table_id: str,
        include_structure: bool = True,
        include_statistics: bool = True,
        include_insights: bool = True
    ) -> str:
        """
        生成数据表总结报告
        
        Args:
            app_token: 多维表格app_token
            table_id: 数据表ID
            include_structure: 是否包含结构信息
            include_statistics: 是否包含统计信息
            include_insights: 是否包含数据洞察
            
        Returns:
            总结报告文本
        """
        analysis = self.analyze_table(app_token, table_id)
        
        lines = []
        lines.append("=" * 60)
        lines.append("多维表格数据总结报告")
        lines.append("=" * 60)
        lines.append("")
        
        # 表格结构
        if include_structure:
            structure = analysis['structure']
            lines.append("## 表格结构")
            lines.append("")
            
            # 字段信息
            fields = structure.get('fields', [])
            if fields:
                lines.append(f"### 字段列表（共{len(fields)}个）")
                for i, field in enumerate(fields, 1):
                    field_name = field.get('field_name', '未知')
                    field_type = field.get('type', '未知')
                    field_type_name = self._get_field_type_name(field_type)
                    lines.append(f"{i}. **{field_name}** ({field_type_name})")
                lines.append("")
            
            # 视图信息
            views = structure.get('views', [])
            if views:
                lines.append(f"### 视图列表（共{len(views)}个）")
                for i, view in enumerate(views, 1):
                    view_name = view.get('view_name', '未知')
                    view_type = view.get('view_type', '未知')
                    lines.append(f"{i}. **{view_name}** ({view_type})")
                lines.append("")
        
        # 统计信息
        if include_statistics:
            stats = analysis['statistics']
            lines.append("## 统计信息")
            lines.append("")
            lines.append(f"- **总记录数**：{stats['total_records']}")
            lines.append(f"- **总字段数**：{stats['total_fields']}")
            lines.append(f"- **总视图数**：{stats['total_views']}")
            lines.append("")
            
            # 字段类型分布
            if stats['field_types']:
                lines.append("### 字段类型分布")
                for field_type, count in stats['field_types'].items():
                    type_name = self._get_field_type_name(field_type)
                    lines.append(f"- {type_name}：{count}个")
                lines.append("")
        
        # 数据洞察
        if include_insights:
            insights = analysis['insights']
            if insights:
                lines.append("## 数据洞察")
                lines.append("")
                for i, insight in enumerate(insights, 1):
                    insight_type = insight.get('type', 'info')
                    title = insight.get('title', '')
                    content = insight.get('content', '')
                    
                    icon = {
                        'info': 'ℹ️',
                        'warning': '⚠️',
                        'error': '❌',
                        'success': '✅'
                    }.get(insight_type, '•')
                    
                    lines.append(f"{i}. {icon} **{title}**")
                    lines.append(f"   {content}")
                    lines.append("")
        
        lines.append("=" * 60)
        
        return '\n'.join(lines)
    
    def _get_field_type_name(self, field_type: str) -> str:
        """获取字段类型名称"""
        # 支持字符串和数字类型的字段类型
        field_type_str = str(field_type)
        type_map = {
            '1': '文本',
            '2': '数字',
            '3': '单选',
            '4': '多选',
            '5': '日期',
            '7': '复选框',
            '11': '人员',
            '13': '电话号码',
            '15': '超链接',
            '17': '附件',
            '18': '关联',
            '19': '公式',
            '20': '公式',
            '21': '双向关联',
            '22': '创建人',
            '23': '修改人',
            '1001': '自动编号',
            '1002': '地理位置',
            '1003': '群组',
            '1004': '双向关联',
            '1005': '自动编号'
        }
        return type_map.get(field_type_str, f'未知类型({field_type})')
    
    def export_to_markdown(
        self,
        app_token: str,
        table_id: str,
        output_file: Optional[str] = None
    ) -> str:
        """
        将数据表导出为Markdown格式
        
        Args:
            app_token: 多维表格app_token
            table_id: 数据表ID
            output_file: 输出文件路径（可选）
            
        Returns:
            Markdown内容
        """
        # 获取表格结构
        structure = self.get_table_structure(app_token, table_id)
        fields = structure.get('fields', [])
        field_map = {f.get('field_id'): f for f in fields}
        
        # 获取所有记录
        records = self.get_all_records(app_token, table_id)
        
        # 生成Markdown
        lines = []
        lines.append("# 数据表导出")
        lines.append("")
        lines.append(f"**导出时间**：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"**记录数量**：{len(records)}")
        lines.append("")
        
        if not records:
            lines.append("数据表为空")
            content = '\n'.join(lines)
            if output_file:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(content)
            return content
        
        # 表头
        field_names = [f.get('field_name', '') for f in fields]
        lines.append("| " + " | ".join(field_names) + " |")
        lines.append("| " + " | ".join(['---'] * len(field_names)) + " |")
        
        # 数据行
        for record in records:
            fields_data = record.get('fields', {})
            row = []
            for field in fields:
                field_id = field.get('field_id')
                value = fields_data.get(field_id, '')
                row.append(self._format_field_value(value, field.get('type', '')))
            lines.append("| " + " | ".join(row) + " |")
        
        content = '\n'.join(lines)
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(content)
        
        return content
    
    def _format_field_value(self, value: Any, field_type: str) -> str:
        """格式化字段值为字符串"""
        if value is None or value == '':
            return ''
        
        if field_type == '4':  # 单选
            if isinstance(value, list) and len(value) > 0:
                return value[0].get('text', '')
        elif field_type == '5':  # 多选
            if isinstance(value, list):
                return ', '.join([item.get('text', '') for item in value])
        elif field_type == '11':  # 人员
            if isinstance(value, list):
                return ', '.join([item.get('name', '') for item in value])
        elif field_type == '5':  # 日期
            if isinstance(value, int):
                return datetime.fromtimestamp(value / 1000).strftime('%Y-%m-%d')
        
        return str(value)


# 便捷函数
def create_bitable_collaborator(
    app_id: str,
    app_secret: str,
    user_access_token: Optional[str] = None,
    tenant_access_token: Optional[str] = None
) -> FeishuBitableCollaborator:
    """
    创建多维表格协作器实例（便捷函数）
    
    Args:
        app_id: 飞书应用ID
        app_secret: 飞书应用密钥
        user_access_token: 用户身份凭证（优先使用）
        tenant_access_token: 租户身份凭证（备选）
        
    Returns:
        FeishuBitableCollaborator实例
    """
    return FeishuBitableCollaborator(
        app_id=app_id,
        app_secret=app_secret,
        user_access_token=user_access_token,
        tenant_access_token=tenant_access_token
    )

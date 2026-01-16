# -*- coding: utf-8 -*-
"""
飞书在线表格协作器

提供简洁的API，支持：
- 读取在线表格数据
- 获取表格结构（工作表、行列信息等）
- 数据分析和总结
- 缓存管理
"""

import sys
import os
from typing import Optional, Dict, List, Any
from datetime import datetime
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from feishu_api_wrapper import FeishuAPI


class FeishuSpreadsheetCollaborator:
    """
    飞书在线表格协作器
    
    提供统一的接口进行在线表格协作，支持数据分析和总结
    """
    
    def __init__(
        self,
        app_id: str,
        app_secret: str,
        user_access_token: Optional[str] = None,
        tenant_access_token: Optional[str] = None
    ):
        """
        初始化在线表格协作器
        
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
    
    def get_spreadsheet_info(
        self,
        spreadsheet_token: str,
        use_user_token: bool = True
    ) -> Optional[Dict]:
        """
        获取在线表格基本信息
        
        Args:
            spreadsheet_token: 表格token
            use_user_token: 是否使用用户身份凭证
            
        Returns:
            表格信息或None
        """
        return self.api.get_spreadsheet(spreadsheet_token)
    
    def get_spreadsheet_metainfo(
        self,
        spreadsheet_token: str,
        use_user_token: bool = True
    ) -> Optional[Dict]:
        """
        获取在线表格元信息（工作表列表等）
        
        Args:
            spreadsheet_token: 表格token
            use_user_token: 是否使用用户身份凭证
            
        Returns:
            表格元信息或None
        """
        # 使用v2 API获取元信息（包含工作表列表）
        endpoint = f"open-apis/sheets/v2/spreadsheets/{spreadsheet_token}/metainfo"
        result = self.api._open_platform_request('GET', endpoint, use_user_token=use_user_token)
        
        if result:
            # 处理不同的返回格式
            if 'code' in result and result.get('code') == 0:
                return result.get('data', {})
            elif 'data' in result:
                return result.get('data', {})
            else:
                return result
        
        return None
    
    def get_sheet_list(
        self,
        spreadsheet_token: str,
        use_user_token: bool = True
    ) -> List[Dict]:
        """
        获取工作表列表
        
        Args:
            spreadsheet_token: 表格token
            use_user_token: 是否使用用户身份凭证
            
        Returns:
            工作表列表
        """
        metainfo = self.get_spreadsheet_metainfo(spreadsheet_token, use_user_token)
        if metainfo:
            # 处理不同的返回格式
            if 'code' in metainfo and metainfo.get('code') == 0:
                return metainfo.get('data', {}).get('sheets', [])
            elif 'sheets' in metainfo:
                return metainfo.get('sheets', [])
            elif 'data' in metainfo:
                data = metainfo.get('data', {})
                if 'sheets' in data:
                    return data.get('sheets', [])
                spreadsheet = data.get('spreadsheet', {})
                if spreadsheet and 'sheets' in spreadsheet:
                    return spreadsheet.get('sheets', [])
        
        return []
    
    def get_sheet_data(
        self,
        spreadsheet_token: str,
        sheet_id: str,
        range: Optional[str] = None,
        use_user_token: bool = True
    ) -> Optional[Dict]:
        """
        获取工作表数据
        
        Args:
            spreadsheet_token: 表格token
            sheet_id: 工作表ID或工作表名称
            range: 范围（如"A1:Z100"，可选，不指定则获取整个工作表）
            use_user_token: 是否使用用户身份凭证
            
        Returns:
            工作表数据或None
        """
        # 获取工作表列表，找到实际的sheet_id
        sheets = self.get_sheet_list(spreadsheet_token, use_user_token)
        actual_sheet_id = None
        
        for sheet in sheets:
            # 匹配sheet_id或title
            if sheet.get('sheet_id') == sheet_id or sheet.get('title') == sheet_id:
                # 优先使用sheet_id，如果没有则使用title
                actual_sheet_id = sheet.get('sheet_id') or sheet.get('title', '')
                break
        
        if not actual_sheet_id:
            # 如果找不到，尝试直接使用传入的sheet_id
            actual_sheet_id = sheet_id
        
        # 构建API endpoint
        if range:
            endpoint = f"open-apis/sheets/v2/spreadsheets/{spreadsheet_token}/values/{actual_sheet_id}!{range}"
        else:
            # 获取整个工作表数据
            endpoint = f"open-apis/sheets/v2/spreadsheets/{spreadsheet_token}/values/{actual_sheet_id}"
        
        return self.api._open_platform_request('GET', endpoint, use_user_token=use_user_token)
    
    def get_all_sheets_data(
        self,
        spreadsheet_token: str,
        use_user_token: bool = True
    ) -> Dict[str, Any]:
        """
        获取所有工作表的数据
        
        Args:
            spreadsheet_token: 表格token
            use_user_token: 是否使用用户身份凭证
            
        Returns:
            所有工作表数据的字典，key为sheet_id
        """
        sheets = self.get_sheet_list(spreadsheet_token, use_user_token)
        all_data = {}
        
        for sheet in sheets:
            # sheet_id可能在sheet_id字段，也可能在sheetId字段
            sheet_id = sheet.get('sheet_id') or sheet.get('sheetId', '')
            sheet_title = sheet.get('title', '')
            
            if sheet_id:
                sheet_data = self.get_sheet_data(spreadsheet_token, sheet_id, use_user_token=use_user_token)
                if sheet_data:
                    all_data[sheet_id] = {
                        'sheet_id': sheet_id,
                        'title': sheet_title,
                        'data': sheet_data
                    }
        
        return all_data
    
    def analyze_spreadsheet(
        self,
        spreadsheet_token: str,
        use_user_token: bool = True
    ) -> Dict[str, Any]:
        """
        分析在线表格结构
        
        Args:
            spreadsheet_token: 表格token
            use_user_token: 是否使用用户身份凭证
            
        Returns:
            分析结果字典
        """
        metainfo = self.get_spreadsheet_metainfo(spreadsheet_token, use_user_token)
        sheets = self.get_sheet_list(spreadsheet_token, use_user_token)
        
        analysis = {
            'spreadsheet_token': spreadsheet_token,
            'sheets_count': len(sheets),
            'sheets': []
        }
        
        for sheet in sheets:
            sheet_id = sheet.get('sheet_id') or sheet.get('sheetId', '')
            sheet_title = sheet.get('title', '')
            row_count = sheet.get('row_count', 0)
            column_count = sheet.get('column_count', 0)
            
            sheet_info = {
                'sheet_id': sheet_id,
                'title': sheet_title,
                'row_count': row_count,
                'column_count': column_count
            }
            
            # 获取实际数据以分析
            if not sheet_id:
                analysis['sheets'].append(sheet_info)
                continue

            sheet_data = self.get_sheet_data(spreadsheet_token, sheet_id, use_user_token=use_user_token)
            if sheet_data:
                values = []
                if 'code' in sheet_data and sheet_data.get('code') == 0:
                    value_range = sheet_data.get('data', {}).get('valueRange', {})
                    values = value_range.get('values', [])
                elif 'valueRange' in sheet_data:
                    values = sheet_data.get('valueRange', {}).get('values', [])
                elif 'data' in sheet_data:
                    value_range = sheet_data.get('data', {}).get('valueRange', {})
                    values = value_range.get('values', [])
                
                sheet_info['actual_row_count'] = len(values)
                if values:
                    sheet_info['actual_column_count'] = len(values[0]) if values[0] else 0
                    # 第一行作为表头
                    if len(values) > 0:
                        sheet_info['headers'] = values[0]
            
            analysis['sheets'].append(sheet_info)
        
        return analysis
    
    def summarize_spreadsheet(
        self,
        spreadsheet_token: str,
        use_user_token: bool = True
    ) -> str:
        """
        总结在线表格内容
        
        Args:
            spreadsheet_token: 表格token
            use_user_token: 是否使用用户身份凭证
            
        Returns:
            总结文本
        """
        analysis = self.analyze_spreadsheet(spreadsheet_token, use_user_token)
        
        summary_lines = []
        summary_lines.append("=" * 80)
        summary_lines.append("在线表格分析总结")
        summary_lines.append("=" * 80)
        summary_lines.append("")
        summary_lines.append(f"表格Token: {spreadsheet_token}")
        summary_lines.append(f"工作表数量: {analysis['sheets_count']}")
        summary_lines.append("")
        
        for sheet in analysis['sheets']:
            summary_lines.append(f"## 工作表: {sheet['title']}")
            summary_lines.append("")
            summary_lines.append(f"- 工作表ID: {sheet['sheet_id']}")
            summary_lines.append(f"- 行数: {sheet.get('actual_row_count', sheet.get('row_count', 0))}")
            summary_lines.append(f"- 列数: {sheet.get('actual_column_count', sheet.get('column_count', 0))}")
            
            if sheet.get('headers'):
                summary_lines.append(f"- 表头: {', '.join(sheet['headers'])}")
            
            summary_lines.append("")
        
        return '\n'.join(summary_lines)


def create_spreadsheet_collaborator(
    app_id: str,
    app_secret: str,
    user_access_token: Optional[str] = None,
    tenant_access_token: Optional[str] = None
) -> FeishuSpreadsheetCollaborator:
    """
    创建在线表格协作器实例
    
    Args:
        app_id: 飞书应用ID
        app_secret: 飞书应用密钥
        user_access_token: 用户身份凭证（优先使用）
        tenant_access_token: 租户身份凭证（备选）
        
    Returns:
        FeishuSpreadsheetCollaborator实例
    """
    return FeishuSpreadsheetCollaborator(
        app_id=app_id,
        app_secret=app_secret,
        user_access_token=user_access_token,
        tenant_access_token=tenant_access_token
    )

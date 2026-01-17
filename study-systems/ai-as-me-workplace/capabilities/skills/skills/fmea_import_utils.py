# -*- coding: utf-8 -*-
"""
FMEA导入通用工具函数

提供查找记录、创建关联、数据去重等通用功能
"""

import sys
import os
from typing import Dict, List, Any, Optional

# 修复Windows控制台编码问题
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from feishu_bitable_collaborator import create_bitable_collaborator
from feishu_api_wrapper import FeishuAPI
from bitable_cache_manager import APP_ID, APP_SECRET


class FMEAImportUtils:
    """FMEA导入通用工具类"""
    
    def __init__(self, app_token: str, user_access_token: str = None):
        """
        初始化工具类
        
        Args:
            app_token: 多维表格app_token
            user_access_token: 用户访问令牌
        """
        self.app_token = app_token
        self.user_access_token = user_access_token or os.getenv("FEISHU_USER_ACCESS_TOKEN")
        
        # 创建API和协作器
        self.api = FeishuAPI("", "", APP_ID, APP_SECRET)
        self.api.set_user_access_token(self.user_access_token)
        
        self.collaborator = create_bitable_collaborator(
            app_id=APP_ID,
            app_secret=APP_SECRET,
            user_access_token=self.user_access_token
        )
    
    def find_record_by_field_value(
        self,
        table_id: str,
        field_name: str,
        field_value: Any,
        exact_match: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        根据字段值查找记录
        
        Args:
            table_id: 表ID
            field_name: 字段名
            field_value: 字段值
            exact_match: 是否精确匹配（默认True）
            
        Returns:
            找到的记录字典（包含record_id和fields），如果未找到则返回None
        """
        # 获取所有记录
        records = self.collaborator.get_all_records(self.app_token, table_id)
        
        if not records:
            return None
        
        # 注意：get_all_records返回的记录中，字段是用字段名作为key的，不是字段ID
        # 所以我们可以直接使用字段名来查找
        for record in records:
            record_fields = record.get('fields', {})
            value = record_fields.get(field_name)
            
            if value is None:
                continue
            
            # 处理不同类型的值
            if isinstance(value, list):
                # 列表类型（多选、关联等）
                for item in value:
                    if isinstance(item, dict):
                        item_value = item.get('text') or item.get('name') or str(item)
                    else:
                        item_value = str(item)
                    
                    if exact_match:
                        if str(item_value).strip() == str(field_value).strip():
                            return record
                    else:
                        if str(field_value).strip().lower() in str(item_value).strip().lower():
                            return record
            else:
                # 简单类型
                if exact_match:
                    if str(value).strip() == str(field_value).strip():
                        return record
                else:
                    if str(field_value).strip().lower() in str(value).strip().lower():
                        return record
        
        return None
    
    def find_or_create_record(
        self,
        table_id: str,
        fields: Dict[str, Any],
        search_field: str = None,
        search_value: Any = None
    ) -> Dict[str, Any]:
        """
        查找或创建记录
        
        Args:
            table_id: 表ID
            fields: 要创建的字段数据（字典，key为字段名）
            search_field: 用于搜索的字段名（如果提供，会先搜索是否存在）
            search_value: 用于搜索的字段值
            
        Returns:
            记录字典，包含：
            - record_id: 记录ID
            - created: 是否新创建（True）还是已存在（False）
            - record: 完整记录数据
        """
        # 如果提供了搜索字段，先尝试查找
        if search_field and search_value is not None:
            existing = self.find_record_by_field_value(
                table_id,
                search_field,
                search_value,
                exact_match=True
            )
            
            if existing:
                return {
                    'record_id': existing.get('record_id'),
                    'created': False,
                    'record': existing
                }
        
        # 如果不存在，创建新记录
        # 直接调用API，确保使用user_access_token
        result = self.api.create_bitable_record(
            self.app_token,
            table_id,
            fields,
            use_user_token=True
        )
        
        if not result:
            raise Exception("创建记录失败")
        
        # 处理不同的返回格式
        if 'code' in result:
            if result.get('code') == 0:
                data = result.get('data', {})
                record = data.get('record', {})
            else:
                raise Exception(f"创建记录失败: {result.get('msg')}")
        else:
            record = result.get('record', result)
        
        record_id = record.get('record_id') or record.get('id')
        
        return {
            'record_id': record_id,
            'created': True,
            'record': record
        }
    
    def create_relation_value(self, record_ids: List[str]) -> List[str]:
        """
        创建关联字段的值（记录ID数组）
        
        Args:
            record_ids: 记录ID列表
            
        Returns:
            关联字段值（记录ID数组）
        """
        return record_ids
    
    def extract_unique_values(
        self,
        fmea_rows: List[Dict[str, Any]],
        column_name: str
    ) -> List[str]:
        """
        从FMEA数据中提取唯一值
        
        Args:
            fmea_rows: FMEA行数据列表
            column_name: 列名
            
        Returns:
            唯一值列表（去重后）
        """
        values = set()
        
        for row in fmea_rows:
            value = row.get(column_name, '')
            if value:
                value_str = str(value).strip()
                if value_str:
                    values.add(value_str)
        
        return sorted(list(values))
    
    def extract_column_pairs(
        self,
        fmea_rows: List[Dict[str, Any]],
        column1: str,
        column2: str
    ) -> List[Dict[str, str]]:
        """
        从FMEA数据中提取两列的对应关系（去重）
        
        Args:
            fmea_rows: FMEA行数据列表
            column1: 第一列名
            column2: 第二列名
            
        Returns:
            对应关系列表，每个元素是 {column1: value1, column2: value2}
        """
        pairs = {}
        
        for row in fmea_rows:
            value1 = row.get(column1, '')
            value2 = row.get(column2, '')
            
            if value1 and value2:
                value1 = str(value1).strip()
                value2 = str(value2).strip()
                
                if value1 and value2:
                    # 使用(value1, value2)作为key去重
                    key = (value1, value2)
                    if key not in pairs:
                        pairs[key] = {
                            column1: value1,
                            column2: value2
                        }
        
        return list(pairs.values())
    
    def get_table_structure_info(
        self,
        table_id: str
    ) -> Dict[str, Any]:
        """
        获取表格结构信息（字段名、字段ID、字段类型等）
        
        Args:
            table_id: 表ID
            
        Returns:
            结构信息字典：
            - fields: 字段列表
            - field_name_to_id: 字段名到字段ID的映射
            - field_id_to_name: 字段ID到字段名的映射
        """
        structure = self.collaborator.get_table_structure(self.app_token, table_id)
        fields = structure.get('fields', [])
        
        field_name_to_id = {}
        field_id_to_name = {}
        
        for field in fields:
            field_name = field.get('field_name', '')
            field_id = field.get('field_id', '')
            field_type = field.get('type', '')
            
            field_name_to_id[field_name] = field_id
            field_id_to_name[field_id] = {
                'name': field_name,
                'type': field_type
            }
        
        return {
            'fields': fields,
            'field_name_to_id': field_name_to_id,
            'field_id_to_name': field_id_to_name
        }


def main():
    """测试函数"""
    # 这里需要实际的app_token和table_id
    app_token = "test_app_token"
    utils = FMEAImportUtils(app_token)
    
    # 测试提取唯一值
    test_rows = [
        {'Element Name': 'Element1', 'Function Description': 'Func1'},
        {'Element Name': 'Element2', 'Function Description': 'Func2'},
        {'Element Name': 'Element1', 'Function Description': 'Func3'},
    ]
    
    unique_elements = utils.extract_unique_values(test_rows, 'Element Name')
    print(f"唯一元素: {unique_elements}")
    
    pairs = utils.extract_column_pairs(test_rows, 'Element Name', 'Function Description')
    print(f"对应关系: {pairs}")


if __name__ == "__main__":
    main()

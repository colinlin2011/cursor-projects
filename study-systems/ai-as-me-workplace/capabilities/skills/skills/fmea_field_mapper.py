# -*- coding: utf-8 -*-
"""
FMEA字段映射器

处理FMEA在线表格字段到多维表格字段的映射、类型转换、选项值匹配等
"""

import sys
import os
import re
from typing import Dict, List, Any, Optional
from datetime import datetime

# 修复Windows控制台编码问题
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fmea_import_config import (
    FIELD_MAPPING,
    GUIDE_WORD_MAPPING,
    ANALYSIS_STATUS_MAPPING,
    FREQUENCY_MAPPING,
    MSR_EFFECTIVENESS_MAPPING,
    ASIL_LEVEL_MAPPING,
    SKIP_FIELDS,
    DATE_FORMATS
)


class FMEAFieldMapper:
    """FMEA字段映射器"""
    
    def __init__(self, bitable_fields: List[Dict[str, Any]]):
        """
        初始化字段映射器
        
        Args:
            bitable_fields: 多维表格字段列表（从get_table_structure获取）
        """
        self.bitable_fields = bitable_fields
        self.field_map = self._build_field_map()
        self.field_type_map = self._build_field_type_map()
    
    def _build_field_map(self) -> Dict[str, Dict[str, Any]]:
        """
        构建字段映射表（字段名 -> 字段信息）
        
        Returns:
            字段映射字典
        """
        field_map = {}
        for field in self.bitable_fields:
            field_name = field.get('field_name', '')
            field_id = field.get('field_id', '')
            field_type = field.get('type', '')
            field_map[field_name] = {
                'field_id': field_id,
                'field_type': field_type,
                'field_info': field
            }
        return field_map
    
    def _build_field_type_map(self) -> Dict[str, str]:
        """
        构建字段类型映射表（字段名 -> 字段类型）
        
        Returns:
            字段类型映射字典
        """
        type_map = {}
        for field_name, field_info in self.field_map.items():
            type_map[field_name] = str(field_info['field_type'])
        return type_map
    
    def find_target_field(self, fmea_field_name: str) -> Optional[str]:
        """
        查找目标字段名（支持模糊匹配）
        
        Args:
            fmea_field_name: FMEA表格中的字段名
            
        Returns:
            多维表格中的字段名，如果未找到则返回None
        """
        # 精确匹配
        if fmea_field_name in FIELD_MAPPING:
            target_field = FIELD_MAPPING[fmea_field_name]
            if target_field in self.field_map:
                return target_field
        
        # 模糊匹配（字段名包含关键词）
        fmea_field_lower = fmea_field_name.lower()
        for fmea_key, target_field in FIELD_MAPPING.items():
            if fmea_key.lower() in fmea_field_lower or fmea_field_lower in fmea_key.lower():
                if target_field in self.field_map:
                    return target_field
        
        # 直接匹配（如果FMEA字段名在多维表格中存在）
        if fmea_field_name in self.field_map:
            return fmea_field_name
        
        return None
    
    def convert_field_value(
        self,
        field_name: str,
        field_value: Any,
        fmea_row: Dict[str, Any] = None
    ) -> Any:
        """
        转换字段值（根据字段类型进行转换）
        
        Args:
            field_name: 多维表格字段名
            field_value: 原始字段值
            fmea_row: 完整的FMEA行数据（用于推导其他字段值）
            
        Returns:
            转换后的字段值
        """
        if field_name not in self.field_map:
            return None
        
        field_info = self.field_map[field_name]
        field_type = str(field_info['field_type'])
        
        # 处理空值
        if field_value is None or (isinstance(field_value, str) and not field_value.strip()):
            return None
        
        # 根据字段类型转换
        if field_type == '1':  # 文本
            return str(field_value).strip()
        
        elif field_type == '2':  # 数字
            try:
                return float(field_value)
            except:
                return None
        
        elif field_type == '3':  # 单选
            return self._convert_select_option(field_name, field_value, field_info)
        
        elif field_type == '4':  # 多选
            return self._convert_multi_select(field_name, field_value, field_info)
        
        elif field_type == '5':  # 日期
            return self._convert_date(field_value)
        
        elif field_type == '11':  # 人员
            return self._convert_person(field_value)
        
        elif field_type in ['18', '21', '1004']:  # 关联字段
            # 关联字段需要特殊处理，这里先返回None，由导入器处理
            return None
        
        elif field_type in ['19', '20']:  # 公式字段
            # 公式字段不需要导入
            return None
        
        else:
            # 其他类型，直接返回字符串
            return str(field_value).strip()
    
    def _convert_select_option(
        self,
        field_name: str,
        field_value: Any,
        field_info: Dict[str, Any]
    ) -> Optional[str]:
        """
        转换单选选项值
        
        Args:
            field_name: 字段名
            field_value: 原始值
            field_info: 字段信息
            
        Returns:
            选项值（字符串），如果未找到匹配则返回None
        """
        value_str = str(field_value).strip()
        
        # 根据字段名选择对应的映射表
        mapping = {}
        if "引导词" in field_name:
            mapping = GUIDE_WORD_MAPPING
        elif "分析状态" in field_name or "状态" in field_name:
            mapping = ANALYSIS_STATUS_MAPPING
        elif "频度" in field_name or field_name.endswith("(F)"):
            mapping = FREQUENCY_MAPPING
        elif "MSR有效性" in field_name or field_name.endswith("(M)"):
            mapping = MSR_EFFECTIVENESS_MAPPING
        elif "ASIL" in field_name:
            mapping = ASIL_LEVEL_MAPPING
        
        # 查找映射
        if value_str in mapping:
            return mapping[value_str]
        
        # 模糊匹配
        value_lower = value_str.lower()
        for key, mapped_value in mapping.items():
            if key.lower() in value_lower or value_lower in key.lower():
                return mapped_value
        
        # 如果字段信息中包含选项列表，尝试匹配
        field_property = field_info.get('field_info', {}).get('property', {})
        options = field_property.get('options', [])
        if options:
            for option in options:
                option_name = option.get('name', '')
                if value_str == option_name or value_lower == option_name.lower():
                    return option_name
        
        # 如果找不到匹配，返回原始值（让API决定是否接受）
        return value_str
    
    def _convert_multi_select(
        self,
        field_name: str,
        field_value: Any,
        field_info: Dict[str, Any]
    ) -> Optional[List[str]]:
        """
        转换多选选项值
        
        Args:
            field_name: 字段名
            field_value: 原始值（可能是字符串或列表）
            field_info: 字段信息
            
        Returns:
            选项值列表
        """
        if isinstance(field_value, list):
            values = field_value
        else:
            # 尝试分割字符串
            value_str = str(field_value).strip()
            if not value_str:
                return None
            # 尝试多种分隔符
            for sep in [',', ';', '、', '|']:
                if sep in value_str:
                    values = [v.strip() for v in value_str.split(sep)]
                    break
            else:
                values = [value_str]
        
        # 转换每个值
        converted_values = []
        for value in values:
            converted = self._convert_select_option(field_name, value, field_info)
            if converted:
                converted_values.append(converted)
        
        return converted_values if converted_values else None
    
    def _convert_date(self, field_value: Any) -> Optional[int]:
        """
        转换日期值（返回时间戳，单位：毫秒）
        
        Args:
            field_value: 原始值
            
        Returns:
            时间戳（毫秒），如果转换失败则返回None
        """
        if isinstance(field_value, (int, float)):
            # 如果已经是时间戳
            if field_value > 1000000000000:  # 毫秒时间戳
                return int(field_value)
            elif field_value > 1000000000:  # 秒时间戳
                return int(field_value * 1000)
            return None
        
        value_str = str(field_value).strip()
        if not value_str:
            return None
        
        # 尝试各种日期格式
        for date_format in DATE_FORMATS:
            try:
                dt = datetime.strptime(value_str, date_format)
                # 转换为毫秒时间戳
                return int(dt.timestamp() * 1000)
            except:
                continue
        
        return None
    
    def _convert_person(self, field_value: Any) -> Optional[Dict[str, str]]:
        """
        转换人员值
        
        Args:
            field_value: 原始值（可能是姓名或人员ID）
            
        Returns:
            人员字典，格式：{"id": "user_id"}，如果转换失败则返回None
        """
        # 注意：人员字段需要人员ID，不能直接用姓名
        # 这里先返回None，由导入器通过查找人员表来处理
        return None
    
    def map_row(
        self,
        fmea_row: Dict[str, Any],
        skip_relations: bool = False
    ) -> Dict[str, Any]:
        """
        映射一行FMEA数据到多维表格格式
        
        Args:
            fmea_row: FMEA行数据（字典，key为FMEA字段名）
            skip_relations: 是否跳过关联字段（用于预览）
            
        Returns:
            映射后的字段字典（key为多维表格字段名，value为转换后的值）
        """
        mapped_fields = {}
        relation_fields = {}  # 关联字段单独处理
        
        for fmea_field_name, fmea_value in fmea_row.items():
            # 跳过空值
            if fmea_value is None or (isinstance(fmea_value, str) and not fmea_value.strip()):
                continue
            
            # 查找目标字段
            target_field = self.find_target_field(fmea_field_name)
            if not target_field:
                continue
            
            # 检查是否需要跳过
            if target_field in SKIP_FIELDS:
                continue
            
            # 检查字段类型
            field_type = self.field_type_map.get(target_field, '')
            
            # 关联字段单独处理
            if field_type in ['18', '21', '1004']:
                if not skip_relations:
                    relation_fields[target_field] = {
                        'fmea_field': fmea_field_name,
                        'value': fmea_value,
                        'field_info': self.field_map[target_field]
                    }
                continue
            
            # 转换字段值
            converted_value = self.convert_field_value(target_field, fmea_value, fmea_row)
            if converted_value is not None:
                # 注意：飞书API要求使用字段名（field_name）作为key，而不是字段ID
                mapped_fields[target_field] = converted_value
        
        return {
            'fields': mapped_fields,
            'relation_fields': relation_fields
        }


def main():
    """测试函数"""
    # 模拟字段列表
    test_fields = [
        {'field_name': '实际识别的失效模式', 'field_id': 'fld001', 'type': '1'},
        {'field_name': '潜在失效影响', 'field_id': 'fld002', 'type': '1'},
        {'field_name': '引导词', 'field_id': 'fld003', 'type': '3'},
        {'field_name': '分析日期', 'field_id': 'fld004', 'type': '5'},
    ]
    
    mapper = FMEAFieldMapper(test_fields)
    
    # 测试映射
    test_row = {
        '失效模式': '功能输出错误',
        '失效影响': '系统无法正常工作',
        '引导词': '错误',
        '分析日期': '2024-01-15'
    }
    
    result = mapper.map_row(test_row)
    print("映射结果:")
    print(result)


if __name__ == "__main__":
    main()

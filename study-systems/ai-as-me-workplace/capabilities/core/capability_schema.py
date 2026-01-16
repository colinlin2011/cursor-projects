# -*- coding: utf-8 -*-
"""
能力Schema定义

定义能力的输入输出数据格式规范
"""

from typing import Dict, Any, Optional, List
import json


class CapabilitySchema:
    """能力Schema管理器"""
    
    @staticmethod
    def create_input_schema(
        properties: Dict[str, Any],
        required: Optional[List[str]] = None,
        additional_properties: bool = False
    ) -> Dict[str, Any]:
        """
        创建输入数据Schema
        
        Args:
            properties: 属性定义字典
            required: 必需属性列表
            additional_properties: 是否允许额外属性
            
        Returns:
            JSON Schema格式的输入数据定义
        """
        schema = {
            "type": "object",
            "properties": properties,
            "additionalProperties": additional_properties
        }
        if required:
            schema["required"] = required
        return schema
    
    @staticmethod
    def create_output_schema(
        properties: Dict[str, Any],
        required: Optional[List[str]] = None,
        additional_properties: bool = False
    ) -> Dict[str, Any]:
        """
        创建输出数据Schema
        
        Args:
            properties: 属性定义字典
            required: 必需属性列表
            additional_properties: 是否允许额外属性
            
        Returns:
            JSON Schema格式的输出数据定义
        """
        return CapabilitySchema.create_input_schema(
            properties, required, additional_properties
        )
    
    @staticmethod
    def validate_against_schema(
        data: Dict[str, Any],
        schema: Dict[str, Any]
    ) -> tuple:
        """
        根据Schema验证数据
        
        Args:
            data: 待验证的数据
            schema: JSON Schema定义
            
        Returns:
            (是否有效, 错误信息)
        """
        # 基本类型检查
        if schema.get("type") == "object":
            if not isinstance(data, dict):
                return False, "数据必须是对象类型"
            
            # 检查必需属性
            required = schema.get("required", [])
            for prop in required:
                if prop not in data:
                    return False, f"缺少必需属性: {prop}"
            
            # 检查属性类型
            properties = schema.get("properties", {})
            for key, value in data.items():
                if key in properties:
                    prop_schema = properties[key]
                    prop_type = prop_schema.get("type")
                    
                    if prop_type == "string" and not isinstance(value, str):
                        return False, f"属性 {key} 必须是字符串类型"
                    elif prop_type == "integer" and not isinstance(value, int):
                        return False, f"属性 {key} 必须是整数类型"
                    elif prop_type == "number" and not isinstance(value, (int, float)):
                        return False, f"属性 {key} 必须是数字类型"
                    elif prop_type == "boolean" and not isinstance(value, bool):
                        return False, f"属性 {key} 必须是布尔类型"
                    elif prop_type == "array" and not isinstance(value, list):
                        return False, f"属性 {key} 必须是数组类型"
                    elif prop_type == "object" and not isinstance(value, dict):
                        return False, f"属性 {key} 必须是对象类型"
            
            # 检查是否允许额外属性
            if not schema.get("additionalProperties", False):
                for key in data:
                    if key not in properties:
                        return False, f"不允许的属性: {key}"
        
        return True, None
    
    @staticmethod
    def get_common_schemas() -> Dict[str, Dict[str, Any]]:
        """
        获取通用Schema定义
        
        Returns:
            通用Schema字典
        """
        return {
            "ticket_id": {
                "type": "string",
                "description": "问题单ID（支持工作项ID、记录ID、问题单号）"
            },
            "table_name": {
                "type": "string",
                "description": "表格名称"
            },
            "node_token": {
                "type": "string",
                "description": "飞书节点Token"
            },
            "cache_file": {
                "type": "string",
                "description": "缓存文件名"
            },
            "force_refresh": {
                "type": "boolean",
                "description": "是否强制刷新缓存",
                "default": False
            }
        }

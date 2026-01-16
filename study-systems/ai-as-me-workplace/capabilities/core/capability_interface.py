# -*- coding: utf-8 -*-
"""
能力接口定义

定义所有原子能力必须遵循的标准接口
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from enum import Enum


class CapabilityStatus(Enum):
    """能力状态枚举"""
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    MAINTENANCE = "maintenance"
    DEPRECATED = "deprecated"


class CapabilityResult:
    """能力执行结果"""
    
    def __init__(
        self,
        success: bool,
        data: Any = None,
        error: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.success = success
        self.data = data
        self.error = error
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'success': self.success,
            'data': self.data,
            'error': self.error,
            'metadata': self.metadata
        }


class ICapability(ABC):
    """能力接口基类"""
    
    @abstractmethod
    def get_metadata(self) -> Dict[str, Any]:
        """
        获取能力元数据
        
        Returns:
            包含能力ID、名称、版本、描述等信息的字典
        """
        pass
    
    @abstractmethod
    def validate(self, input_data: Dict[str, Any]) -> tuple:
        """
        验证输入数据
        
        Args:
            input_data: 输入数据字典
            
        Returns:
            (是否有效, 错误信息)
        """
        pass
    
    @abstractmethod
    def execute(self, input_data: Dict[str, Any]) -> CapabilityResult:
        """
        执行能力
        
        Args:
            input_data: 输入数据字典
            
        Returns:
            能力执行结果
        """
        pass
    
    def get_status(self) -> CapabilityStatus:
        """
        获取能力状态
        
        Returns:
            能力状态
        """
        return CapabilityStatus.AVAILABLE
    
    def get_dependencies(self) -> List[str]:
        """
        获取能力依赖
        
        Returns:
            依赖的能力ID列表
        """
        return []
    
    def get_output_schema(self) -> Optional[Dict[str, Any]]:
        """
        获取输出数据Schema
        
        Returns:
            JSON Schema格式的输出数据定义
        """
        return None
    
    def get_input_schema(self) -> Optional[Dict[str, Any]]:
        """
        获取输入数据Schema
        
        Returns:
            JSON Schema格式的输入数据定义
        """
        return None

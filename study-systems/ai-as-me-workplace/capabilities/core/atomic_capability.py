# -*- coding: utf-8 -*-
"""
原子能力基础抽象类

提供所有原子能力的标准实现基类
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from .capability_interface import (
    ICapability, CapabilityResult, CapabilityStatus
)
from .capability_schema import CapabilitySchema


# 配置日志
logger = logging.getLogger(__name__)


class AtomicCapability(ICapability):
    """原子能力基类"""
    
    def __init__(
        self,
        capability_id: str,
        name: str,
        version: str = "1.0.0",
        description: str = "",
        author: str = "",
        status: CapabilityStatus = CapabilityStatus.AVAILABLE
    ):
        """
        初始化原子能力
        
        Args:
            capability_id: 能力ID
            name: 能力名称
            version: 版本号
            description: 能力描述
            author: 作者
            status: 能力状态
        """
        self.capability_id = capability_id
        self.name = name
        self.version = version
        self.description = description
        self.author = author
        self._status = status
        self._dependencies: list[str] = []
        self._input_schema: Optional[Dict[str, Any]] = None
        self._output_schema: Optional[Dict[str, Any]] = None
        
        # 执行统计
        self._execution_count = 0
        self._success_count = 0
        self._error_count = 0
        self._last_execution_time: Optional[datetime] = None
    
    def get_metadata(self) -> Dict[str, Any]:
        """获取能力元数据"""
        return {
            'capability_id': self.capability_id,
            'name': self.name,
            'version': self.version,
            'description': self.description,
            'author': self.author,
            'status': self._status.value,
            'dependencies': self._dependencies,
            'statistics': {
                'execution_count': self._execution_count,
                'success_count': self._success_count,
                'error_count': self._error_count,
                'last_execution_time': self._last_execution_time.isoformat() if self._last_execution_time else None
            }
        }
    
    def validate(self, input_data: Dict[str, Any]) -> tuple:
        """
        验证输入数据
        
        子类可以重写此方法实现自定义验证逻辑
        """
        if self._input_schema:
            return CapabilitySchema.validate_against_schema(
                input_data, self._input_schema
            )
        return True, None
    
    def execute(self, input_data: Dict[str, Any]) -> CapabilityResult:
        """
        执行能力
        
        子类必须实现 _execute_impl 方法
        """
        # 更新执行统计
        self._execution_count += 1
        self._last_execution_time = datetime.now()
        
        # 验证输入
        is_valid, error_msg = self.validate(input_data)
        if not is_valid:
            self._error_count += 1
            logger.error(f"[{self.capability_id}] 输入验证失败: {error_msg}")
            return CapabilityResult(
                success=False,
                error=f"输入验证失败: {error_msg}",
                metadata={'capability_id': self.capability_id}
            )
        
        # 执行能力
        try:
            logger.info(f"[{self.capability_id}] 开始执行: {self.name}")
            result = self._execute_impl(input_data)
            
            if result.success:
                self._success_count += 1
                logger.info(f"[{self.capability_id}] 执行成功")
            else:
                self._error_count += 1
                logger.warning(f"[{self.capability_id}] 执行失败: {result.error}")
            
            # 添加能力元数据
            result.metadata.update({
                'capability_id': self.capability_id,
                'execution_time': self._last_execution_time.isoformat()
            })
            
            return result
            
        except Exception as e:
            self._error_count += 1
            error_msg = f"执行异常: {str(e)}"
            logger.error(f"[{self.capability_id}] {error_msg}", exc_info=True)
            return CapabilityResult(
                success=False,
                error=error_msg,
                metadata={'capability_id': self.capability_id}
            )
    
    def _execute_impl(self, input_data: Dict[str, Any]) -> CapabilityResult:
        """
        执行能力的具体实现
        
        子类必须实现此方法
        """
        raise NotImplementedError("子类必须实现 _execute_impl 方法")
    
    def get_status(self) -> CapabilityStatus:
        """获取能力状态"""
        return self._status
    
    def set_status(self, status: CapabilityStatus):
        """设置能力状态"""
        self._status = status
    
    def get_dependencies(self) -> list[str]:
        """获取能力依赖"""
        return self._dependencies.copy()
    
    def add_dependency(self, capability_id: str):
        """添加能力依赖"""
        if capability_id not in self._dependencies:
            self._dependencies.append(capability_id)
    
    def get_input_schema(self) -> Optional[Dict[str, Any]]:
        """获取输入数据Schema"""
        return self._input_schema
    
    def set_input_schema(self, schema: Dict[str, Any]):
        """设置输入数据Schema"""
        self._input_schema = schema
    
    def get_output_schema(self) -> Optional[Dict[str, Any]]:
        """获取输出数据Schema"""
        return self._output_schema
    
    def set_output_schema(self, schema: Dict[str, Any]):
        """设置输出数据Schema"""
        self._output_schema = schema
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取执行统计"""
        return {
            'execution_count': self._execution_count,
            'success_count': self._success_count,
            'error_count': self._error_count,
            'success_rate': self._success_count / self._execution_count if self._execution_count > 0 else 0,
            'last_execution_time': self._last_execution_time.isoformat() if self._last_execution_time else None
        }

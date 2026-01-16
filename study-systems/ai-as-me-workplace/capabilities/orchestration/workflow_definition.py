# -*- coding: utf-8 -*-
"""
工作流定义格式

定义工作流的JSON/YAML格式规范
"""

from typing import Dict, Any, List, Optional
from enum import Enum


class StepType(Enum):
    """步骤类型"""
    SEQUENTIAL = "sequential"  # 顺序执行
    PARALLEL = "parallel"  # 并行执行
    CONDITIONAL = "conditional"  # 条件分支
    LOOP = "loop"  # 循环执行


class WorkflowDefinition:
    """工作流定义"""
    
    def __init__(
        self,
        name: str,
        version: str = "1.0.0",
        description: str = "",
        steps: Optional[List[Dict[str, Any]]] = None
    ):
        """
        初始化工作流定义
        
        Args:
            name: 工作流名称
            version: 版本号
            description: 描述
            steps: 步骤列表
        """
        self.name = name
        self.version = version
        self.description = description
        self.steps = steps or []
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WorkflowDefinition':
        """
        从字典创建工作流定义
        
        Args:
            data: 工作流定义字典
            
        Returns:
            工作流定义对象
        """
        return cls(
            name=data.get('name', ''),
            version=data.get('version', '1.0.0'),
            description=data.get('description', ''),
            steps=data.get('steps', [])
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典
        
        Returns:
            工作流定义字典
        """
        return {
            'name': self.name,
            'version': self.version,
            'description': self.description,
            'steps': self.steps
        }
    
    def validate(self) -> tuple[bool, Optional[str]]:
        """
        验证工作流定义
        
        Returns:
            (是否有效, 错误信息)
        """
        if not self.name:
            return False, "工作流名称不能为空"
        
        if not self.steps:
            return False, "工作流步骤不能为空"
        
        for i, step in enumerate(self.steps):
            if 'capability' not in step:
                return False, f"步骤 {i+1} 缺少 capability 字段"
            
            if 'action' not in step:
                return False, f"步骤 {i+1} 缺少 action 字段"
        
        return True, None


def create_workflow_template(name: str, steps: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    创建工作流模板
    
    Args:
        name: 工作流名称
        steps: 步骤列表
        
    Returns:
        工作流定义字典
    """
    return {
        'workflow': {
            'name': name,
            'version': '1.0.0',
            'description': '',
            'steps': steps
        }
    }


def create_step(
    capability: str,
    action: str,
    input_data: Dict[str, Any],
    output: str,
    condition: Optional[str] = None,
    retry: Optional[int] = None,
    timeout: Optional[int] = None
) -> Dict[str, Any]:
    """
    创建工作流步骤
    
    Args:
        capability: 能力ID
        action: 动作名称
        input_data: 输入数据（支持模板变量）
        output: 输出变量名
        condition: 执行条件（可选）
        retry: 重试次数（可选）
        timeout: 超时时间（秒，可选）
        
    Returns:
        步骤定义字典
    """
    step = {
        'capability': capability,
        'action': action,
        'input': input_data,
        'output': output
    }
    
    if condition:
        step['condition'] = condition
    
    if retry:
        step['retry'] = retry
    
    if timeout:
        step['timeout'] = timeout
    
    return step

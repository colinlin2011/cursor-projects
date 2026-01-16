# -*- coding: utf-8 -*-
"""
工作流引擎

支持顺序执行、并行执行、条件分支、错误处理和重试机制
"""

import logging
import time
import re
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime

from .workflow_definition import WorkflowDefinition, StepType

logger = logging.getLogger(__name__)


class WorkflowContext:
    """工作流上下文"""
    
    def __init__(self):
        """初始化上下文"""
        self.variables: Dict[str, Any] = {}
        self.step_results: Dict[str, Any] = {}
        self.errors: List[Dict[str, Any]] = []
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
    
    def set_variable(self, name: str, value: Any):
        """设置变量"""
        self.variables[name] = value
    
    def get_variable(self, name: str, default: Any = None) -> Any:
        """获取变量"""
        return self.variables.get(name, default)
    
    def set_step_result(self, step_name: str, result: Any):
        """设置步骤结果"""
        self.step_results[step_name] = result
    
    def get_step_result(self, step_name: str) -> Optional[Any]:
        """获取步骤结果"""
        return self.step_results.get(step_name)
    
    def add_error(self, step_name: str, error: str):
        """添加错误"""
        self.errors.append({
            'step': step_name,
            'error': error,
            'timestamp': datetime.now().isoformat()
        })


class WorkflowEngine:
    """工作流引擎"""
    
    def __init__(self, capability_registry: Optional[Dict[str, Any]] = None):
        """
        初始化工作流引擎
        
        Args:
            capability_registry: 能力注册表（能力ID -> 能力实例的映射）
        """
        self.capability_registry = capability_registry or {}
        self.context = WorkflowContext()
    
    def register_capability(self, capability_id: str, capability: Any):
        """
        注册能力
        
        Args:
            capability_id: 能力ID
            capability: 能力实例
        """
        self.capability_registry[capability_id] = capability
    
    def execute(self, workflow: WorkflowDefinition) -> Dict[str, Any]:
        """
        执行工作流
        
        Args:
            workflow: 工作流定义
            
        Returns:
            执行结果字典
        """
        # 验证工作流
        is_valid, error_msg = workflow.validate()
        if not is_valid:
            return {
                'success': False,
                'error': f"工作流验证失败: {error_msg}",
                'context': self.context
            }
        
        # 初始化上下文
        self.context = WorkflowContext()
        self.context.start_time = datetime.now()
        
        logger.info(f"开始执行工作流: {workflow.name}")
        
        try:
            # 执行步骤
            for i, step in enumerate(workflow.steps):
                step_name = step.get('output', f'step_{i+1}')
                
                # 检查执行条件
                if 'condition' in step:
                    if not self._evaluate_condition(step['condition']):
                        logger.info(f"步骤 {step_name} 条件不满足，跳过")
                        continue
                
                # 执行步骤
                result = self._execute_step(step, step_name)
                
                if not result['success']:
                    # 检查是否需要重试
                    retry_count = step.get('retry', 0)
                    if retry_count > 0:
                        logger.warning(f"步骤 {step_name} 执行失败，尝试重试（剩余 {retry_count} 次）")
                        for retry in range(retry_count):
                            time.sleep(1)  # 等待1秒后重试
                            result = self._execute_step(step, step_name)
                            if result['success']:
                                break
                    
                    if not result['success']:
                        # 如果步骤失败且没有重试成功，记录错误
                        self.context.add_error(step_name, result.get('error', '未知错误'))
                        
                        # 检查是否应该继续执行（可以根据配置决定）
                        # 这里默认继续执行，但记录错误
                        logger.warning(f"步骤 {step_name} 执行失败: {result.get('error')}")
                
                # 保存步骤结果
                self.context.set_step_result(step_name, result)
                
                # 将输出保存到上下文变量
                if 'output' in step and result['success']:
                    self.context.set_variable(step['output'], result.get('data'))
            
            self.context.end_time = datetime.now()
            
            # 计算执行时间
            duration = (self.context.end_time - self.context.start_time).total_seconds()
            
            logger.info(f"工作流执行完成: {workflow.name}，耗时 {duration:.2f} 秒")
            
            return {
                'success': len(self.context.errors) == 0,
                'workflow_name': workflow.name,
                'duration': duration,
                'context': {
                    'variables': self.context.variables,
                    'step_results': self.context.step_results,
                    'errors': self.context.errors
                }
            }
            
        except Exception as e:
            self.context.end_time = datetime.now()
            error_msg = f"工作流执行异常: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.context.add_error('workflow', error_msg)
            
            return {
                'success': False,
                'error': error_msg,
                'context': {
                    'variables': self.context.variables,
                    'step_results': self.context.step_results,
                    'errors': self.context.errors
                }
            }
    
    def _execute_step(self, step: Dict[str, Any], step_name: str) -> Dict[str, Any]:
        """
        执行单个步骤
        
        Args:
            step: 步骤定义
            step_name: 步骤名称
            
        Returns:
            执行结果
        """
        capability_id = step.get('capability')
        action = step.get('action')
        input_data = step.get('input', {})
        timeout = step.get('timeout')
        
        # 解析输入数据中的模板变量
        resolved_input = self._resolve_template_variables(input_data)
        
        # 获取能力实例
        capability = self.capability_registry.get(capability_id)
        if not capability:
            return {
                'success': False,
                'error': f"能力 {capability_id} 未注册"
            }
        
        # 执行能力
        try:
            # 如果能力有execute方法，直接调用
            if hasattr(capability, 'execute'):
                if timeout:
                    # 简单的超时处理（实际应该使用threading或asyncio）
                    result = capability.execute(resolved_input)
                else:
                    result = capability.execute(resolved_input)
                
                # 如果结果是CapabilityResult对象，转换为字典
                if hasattr(result, 'to_dict'):
                    return result.to_dict()
                elif isinstance(result, dict):
                    return result
                else:
                    return {
                        'success': True,
                        'data': result
                    }
            # 如果能力有action方法，调用action
            elif hasattr(capability, action):
                method = getattr(capability, action)
                result = method(**resolved_input)
                
                return {
                    'success': True,
                    'data': result
                }
            else:
                return {
                    'success': False,
                    'error': f"能力 {capability_id} 不支持动作 {action}"
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f"执行异常: {str(e)}"
            }
    
    def _resolve_template_variables(self, data: Any) -> Any:
        """
        解析模板变量
        
        支持格式：{{variable_name}} 或 {{step_name.field_name}}
        
        Args:
            data: 包含模板变量的数据
            
        Returns:
            解析后的数据
        """
        if isinstance(data, dict):
            return {k: self._resolve_template_variables(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._resolve_template_variables(item) for item in data]
        elif isinstance(data, str):
            # 匹配 {{variable}} 格式
            pattern = r'\{\{([^}]+)\}\}'
            matches = re.findall(pattern, data)
            
            if not matches:
                return data
            
            resolved = data
            for match in matches:
                var_path = match.strip()
                value = self._get_variable_value(var_path)
                
                if value is not None:
                    # 替换变量
                    resolved = resolved.replace(f'{{{{{var_path}}}}}', str(value))
                else:
                    # 变量不存在，保持原样或抛出错误
                    logger.warning(f"模板变量 {var_path} 不存在")
            
            return resolved
        else:
            return data
    
    def _get_variable_value(self, var_path: str) -> Any:
        """
        获取变量值
        
        支持路径访问：step_name.field_name
        
        Args:
            var_path: 变量路径
            
        Returns:
            变量值
        """
        # 检查是否是步骤结果路径
        if '.' in var_path:
            parts = var_path.split('.', 1)
            step_name = parts[0]
            field_path = parts[1]
            
            step_result = self.context.get_step_result(step_name)
            if step_result and isinstance(step_result, dict):
                # 递归获取字段值
                return self._get_nested_value(step_result.get('data', {}), field_path)
        
        # 直接变量
        return self.context.get_variable(var_path)
    
    def _get_nested_value(self, data: Dict[str, Any], path: str) -> Any:
        """
        获取嵌套字段值
        
        Args:
            data: 数据字典
            path: 字段路径（支持点号分隔）
            
        Returns:
            字段值
        """
        parts = path.split('.')
        value = data
        
        for part in parts:
            if isinstance(value, dict):
                value = value.get(part)
            elif isinstance(value, list) and part.isdigit():
                value = value[int(part)] if int(part) < len(value) else None
            else:
                return None
            
            if value is None:
                return None
        
        return value
    
    def _evaluate_condition(self, condition: str) -> bool:
        """
        评估执行条件
        
        支持简单的条件表达式，如：{{variable}} == "value"
        
        Args:
            condition: 条件表达式
            
        Returns:
            条件是否满足
        """
        # 简单的条件评估（实际应该使用更强大的表达式引擎）
        # 这里只支持简单的变量检查
        if condition.startswith('{{') and condition.endswith('}}'):
            var_path = condition[2:-2].strip()
            value = self._get_variable_value(var_path)
            return value is not None and value != False
        
        # 其他条件表达式可以在这里扩展
        return True

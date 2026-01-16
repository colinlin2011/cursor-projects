# -*- coding: utf-8 -*-
"""
模板引擎

支持业务流程模板的加载、参数化和执行
"""

import yaml
import json
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path

from ..orchestration.workflow_definition import WorkflowDefinition
from ..orchestration.workflow_engine import WorkflowEngine

logger = logging.getLogger(__name__)


class TemplateEngine:
    """模板引擎"""
    
    def __init__(self, template_dir: Optional[Path] = None):
        """
        初始化模板引擎
        
        Args:
            template_dir: 模板目录路径
        """
        if template_dir is None:
            template_dir = Path(__file__).parent / "business_processes"
        
        self.template_dir = Path(template_dir)
        self.templates: Dict[str, Dict[str, Any]] = {}
        self._load_templates()
    
    def _load_templates(self):
        """加载所有模板"""
        if not self.template_dir.exists():
            logger.warning(f"模板目录不存在: {self.template_dir}")
            return
        
        # 加载YAML模板
        for yaml_file in self.template_dir.glob("*.yaml"):
            try:
                with open(yaml_file, 'r', encoding='utf-8') as f:
                    template_data = yaml.safe_load(f)
                    template_name = yaml_file.stem
                    self.templates[template_name] = template_data
                    logger.info(f"加载模板: {template_name}")
            except Exception as e:
                logger.error(f"加载模板失败 {yaml_file}: {e}")
        
        # 加载JSON模板
        for json_file in self.template_dir.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    template_data = json.load(f)
                    template_name = json_file.stem
                    self.templates[template_name] = template_data
                    logger.info(f"加载模板: {template_name}")
            except Exception as e:
                logger.error(f"加载模板失败 {json_file}: {e}")
    
    def get_template(self, template_name: str) -> Optional[Dict[str, Any]]:
        """
        获取模板
        
        Args:
            template_name: 模板名称
            
        Returns:
            模板数据字典
        """
        return self.templates.get(template_name)
    
    def list_templates(self) -> List[str]:
        """
        列出所有模板
        
        Returns:
            模板名称列表
        """
        return list(self.templates.keys())
    
    def instantiate_template(
        self,
        template_name: str,
        parameters: Dict[str, Any]
    ) -> Optional[WorkflowDefinition]:
        """
        实例化模板（参数化）
        
        Args:
            template_name: 模板名称
            parameters: 参数字典
            
        Returns:
            工作流定义对象
        """
        template = self.get_template(template_name)
        if not template:
            logger.error(f"模板不存在: {template_name}")
            return None
        
        # 提取工作流定义
        workflow_data = template.get('workflow')
        if not workflow_data:
            logger.error(f"模板格式错误: {template_name}")
            return None
        
        # 参数化处理
        instantiated_workflow = self._apply_parameters(workflow_data, parameters)
        
        # 创建工作流定义
        return WorkflowDefinition.from_dict(instantiated_workflow)
    
    def _apply_parameters(
        self,
        workflow_data: Dict[str, Any],
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        应用参数到工作流定义
        
        Args:
            workflow_data: 工作流数据
            parameters: 参数字典
            
        Returns:
            参数化后的工作流数据
        """
        import copy
        import re
        
        result = copy.deepcopy(workflow_data)
        
        # 递归替换参数
        def replace_params(obj):
            if isinstance(obj, dict):
                return {k: replace_params(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [replace_params(item) for item in obj]
            elif isinstance(obj, str):
                # 替换 {{param_name}} 格式的参数
                pattern = r'\{\{([^}]+)\}\}'
                matches = re.findall(pattern, obj)
                
                if not matches:
                    return obj
                
                resolved = obj
                for match in matches:
                    param_name = match.strip()
                    if param_name in parameters:
                        value = parameters[param_name]
                        resolved = resolved.replace(f'{{{{{param_name}}}}}', str(value))
                
                return resolved
            else:
                return obj
        
        return replace_params(result)
    
    def execute_template(
        self,
        template_name: str,
        parameters: Dict[str, Any],
        workflow_engine: Optional[WorkflowEngine] = None
    ) -> Dict[str, Any]:
        """
        执行模板
        
        Args:
            template_name: 模板名称
            parameters: 参数字典
            workflow_engine: 工作流引擎（可选）
            
        Returns:
            执行结果
        """
        # 实例化模板
        workflow = self.instantiate_template(template_name, parameters)
        if not workflow:
            return {
                'success': False,
                'error': f"无法实例化模板: {template_name}"
            }
        
        # 创建工作流引擎（如果未提供）
        if workflow_engine is None:
            workflow_engine = WorkflowEngine()
        
        # 执行工作流
        return workflow_engine.execute(workflow)

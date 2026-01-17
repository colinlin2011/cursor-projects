# -*- coding: utf-8 -*-
"""
SSH日志查询配置

提供SSH日志查询的默认配置和配置管理功能
"""

import os
from typing import Dict, Optional
from pathlib import Path

# 从fault_diagnosis_config复用SSH配置
from fault_diagnosis_config import SSH_CONFIG, get_ssh_config, LOG_CACHE_DIR

# 默认查询参数
DEFAULT_QUERY_PARAMS = {
    'logic': 'OR',  # 默认OR逻辑
    'fuzzy_match': True,  # 默认启用模糊匹配
    'max_results': 100,  # 默认最大结果数
    'context_lines': 0,  # 默认不提取上下文
    'output_format': 'both',  # 默认同时返回JSON和文本
    'query_method': None  # 默认自动选择查询方式
}

# 文件大小阈值（字节）
# 超过此大小的文件使用远程grep，小于此大小的文件下载到本地后搜索
FILE_SIZE_THRESHOLD = 10 * 1024 * 1024  # 10MB

# 支持的日志文件扩展名
SUPPORTED_LOG_EXTENSIONS = ['.log', '.txt', '.gz', '.log.gz']

# 默认grep命令超时时间（秒）
GREP_TIMEOUT = 60

# 上下文提取的最大行数限制
MAX_CONTEXT_LINES = 50

# 最大结果数限制
MAX_RESULTS_LIMIT = 10000


def get_ssh_config_for_query() -> Dict:
    """
    获取SSH配置（用于查询）
    
    Returns:
        SSH配置字典
    """
    return get_ssh_config()


def get_default_query_params() -> Dict:
    """
    获取默认查询参数
    
    Returns:
        默认查询参数字典
    """
    return DEFAULT_QUERY_PARAMS.copy()


def get_file_size_threshold() -> int:
    """
    获取文件大小阈值
    
    Returns:
        文件大小阈值（字节）
    """
    return FILE_SIZE_THRESHOLD


def get_supported_extensions() -> list:
    """
    获取支持的日志文件扩展名
    
    Returns:
        扩展名列表
    """
    return SUPPORTED_LOG_EXTENSIONS.copy()


def get_cache_dir() -> Path:
    """
    获取日志缓存目录
    
    Returns:
        缓存目录路径
    """
    return LOG_CACHE_DIR


def validate_query_params(params: Dict) -> tuple[bool, Optional[str]]:
    """
    验证查询参数
    
    Args:
        params: 查询参数字典
        
    Returns:
        (是否有效, 错误信息)
    """
    # 检查必需参数
    if 'remote_path' not in params:
        return False, "缺少必需参数: remote_path"
    
    if 'keywords' not in params:
        return False, "缺少必需参数: keywords"
    
    # 检查逻辑运算符
    if 'logic' in params:
        if params['logic'].upper() not in ['AND', 'OR']:
            return False, f"无效的逻辑运算符: {params['logic']}，必须是AND或OR"
    
    # 检查输出格式
    if 'output_format' in params:
        if params['output_format'] not in ['json', 'text', 'both']:
            return False, f"无效的输出格式: {params['output_format']}，必须是json、text或both"
    
    # 检查最大结果数
    if 'max_results' in params:
        if not isinstance(params['max_results'], int) or params['max_results'] < 1:
            return False, f"无效的最大结果数: {params['max_results']}，必须是正整数"
        if params['max_results'] > MAX_RESULTS_LIMIT:
            return False, f"最大结果数超过限制: {params['max_results']}，最大允许{MAX_RESULTS_LIMIT}"
    
    # 检查上下文行数
    if 'context_lines' in params:
        if not isinstance(params['context_lines'], int) or params['context_lines'] < 0:
            return False, f"无效的上下文行数: {params['context_lines']}，必须是非负整数"
        if params['context_lines'] > MAX_CONTEXT_LINES:
            return False, f"上下文行数超过限制: {params['context_lines']}，最大允许{MAX_CONTEXT_LINES}"
    
    return True, None

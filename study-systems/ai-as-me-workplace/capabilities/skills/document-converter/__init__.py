"""
文档转换Skill模块
提供Markdown到Word的文档转换功能
"""

from .converter import (
    convert_markdown_to_word,
    batch_convert_to_word,
    check_dependencies,
    install_dependencies
)

__all__ = [
    'convert_markdown_to_word',
    'batch_convert_to_word',
    'check_dependencies',
    'install_dependencies'
]

__version__ = '1.0.0'

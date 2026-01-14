# -*- coding: utf-8 -*-
"""
飞书Wiki/多维表格今日更新记录总结工具

重要说明：
1. 用户提供的链接是Wiki链接
2. 当前reference文档主要是飞书项目的API，不包含Wiki或多维表格（Bitable）的API
3. 如果目标是飞书多维表格（Bitable），需要飞书开放平台的多维表格API
4. 如果目标是飞书项目中的表格视图，可以使用reference中的工作项API
"""

import requests
import json
import os
from datetime import datetime
from typing import Dict, Optional
from urllib.parse import urlparse

# Reference文档位置
REFERENCE_PATH = os.path.join(os.path.expanduser("~"), ".cursor", "cursor-projects", "tools", "feishu interaction", "reference")
API_DOCS_PATH = os.path.join(REFERENCE_PATH, "api_docs")

# API基础URL
BASE_URL = "https://project.feishu.cn"


def parse_wiki_link(wiki_url: str) -> Dict[str, str]:
    """
    解析飞书Wiki链接
    
    Args:
        wiki_url: Wiki链接
    
    Returns:
        dict: 包含wiki_id等信息
    """
    parsed = urlparse(wiki_url)
    path_parts = parsed.path.strip('/').split('/')
    
    result = {
        "type": "wiki",
        "domain": parsed.netloc,
        "wiki_id": None
    }
    
    # Wiki链接格式：https://domain.feishu.cn/wiki/WikiID
    if 'wiki' in path_parts:
        idx = path_parts.index('wiki')
        if idx + 1 < len(path_parts):
            result["wiki_id"] = path_parts[idx + 1]
    
    return result


def get_wiki_bitable_summary(
    wiki_url: str,
    plugin_id: str = None,
    plugin_secret: str = None,
    user_key: str = None
) -> Dict:
    """
    获取飞书Wiki或多维表格的今日更新记录总结
    
    重要说明：
    - 当前reference文档主要是飞书项目的API
    - Wiki和多维表格（Bitable）需要使用飞书开放平台的API
    - 如果Wiki中嵌入了飞书项目视图，可能需要先解析项目信息
    
    Args:
        wiki_url: Wiki链接
        plugin_id: 插件ID（如果使用项目API）
        plugin_secret: 插件密钥（如果使用项目API）
        user_key: 用户密钥（如果使用项目API）
    
    Returns:
        dict: 更新记录总结或错误信息
    """
    # 解析链接
    parsed = parse_wiki_link(wiki_url)
    
    if not parsed.get("wiki_id"):
        return {
            "error": "无法识别Wiki ID，请提供有效的Wiki链接",
            "parsed_info": parsed
        }
    
    # 说明情况
    result = {
        "wiki_url": wiki_url,
        "wiki_id": parsed["wiki_id"],
        "domain": parsed["domain"],
        "type": "wiki",
        "status": "需要额外API",
        "message": "当前reference文档主要是飞书项目的API，不包含Wiki或多维表格（Bitable）的API",
        "suggestions": [
            "如果这是飞书多维表格（Bitable），需要使用飞书开放平台的多维表格API",
            "如果Wiki中嵌入了飞书项目视图，可以尝试提取项目信息后使用项目API",
            "需要飞书开放平台的Wiki API文档来获取Wiki更新记录",
            "需要飞书开放平台的多维表格API文档来获取Bitable更新记录"
        ],
        "reference_docs": {
            "current": "飞书项目API（project.feishu.cn）",
            "needed": "飞书开放平台API（open.feishu.cn）- Wiki和Bitable API"
        }
    }
    
    # 如果提供了项目API凭证，可以尝试查找关联的项目
    if plugin_id and plugin_secret and user_key:
        result["note"] = "已提供项目API凭证，但Wiki链接需要飞书开放平台的API"
    
    return result


if __name__ == "__main__":
    # 测试解析
    wiki_url = "https://zyt.feishu.cn/wiki/CGMnwhxzLixWhGk87jYcDRfonsh"
    result = get_wiki_bitable_summary(wiki_url)
    
    print("解析结果：")
    print(json.dumps(result, indent=2, ensure_ascii=False))

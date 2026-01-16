# -*- coding: utf-8 -*-
"""
故障定位系统配置管理模块
"""

import os
import json
from typing import Dict, List, Optional
from pathlib import Path

# 飞书配置
APP_ID = "cli_a9c92ca516f99bd9"
APP_SECRET = "zlOKnyZkSuSUSr0WlAl6qbh5Qw4eM6wC"
USER_ACCESS_TOKEN = os.getenv("FEISHU_USER_ACCESS_TOKEN", "u-eIUWr84upbgokMMGU78cvQk1npEg4kOXryayFxa020ku")
SPACE_ID = "7353073903872868356"  # Wiki知识库ID

# 缺陷问题闭环表配置
DEFECT_TABLE_NAME = "10. 缺陷问题闭环表"
DEFECT_TABLE_CACHE_FILE = "new_bitable.json"

# 字段映射配置
FIELD_MAPPING = {
    "描述": "描述",
    "Ticket元信息": "Ticket 元信息",
    "工作项id": "工作项id",
    "工具回传": "工具回传",  # 用于回填分析结果
    "Fault_ID": "Fault_ID",
    "Fault ID": "Fault ID"
}

# 故障定位指引文档配置（默认配置）
FAULT_GUIDE_DOCS = [
    {
        "name": "故障定位指引文档1",
        "node_token": "UBS2wO9aai7jB7kaw4QcQGNbngc",
        "url": "https://zyt.feishu.cn/wiki/UBS2wO9aai7jB7kaw4QcQGNbngc"
    },
    {
        "name": "故障定位指引文档2",
        "node_token": "H7a5w5tqBidVHMkCqxHc6AmEn5c",
        "url": "https://zyt.feishu.cn/wiki/H7a5w5tqBidVHMkCqxHc6AmEn5c"
    },
    {
        "name": "故障定位指引文档3",
        "node_token": "NUgTwgJWpikCV7k8OFqcH8kYn7e",
        "url": "https://zyt.feishu.cn/wiki/NUgTwgJWpikCV7k8OFqcH8kYn7e"
    }
]

# 故障定位指引文档配置文件路径
# 从当前文件位置计算到项目根目录的work目录
_current_file = Path(__file__)
_project_root = _current_file.parent.parent.parent.parent  # 从capabilities/skills/skills/到项目根目录
GUIDE_DOCS_CONFIG_FILE = _project_root / "work" / "fault_diagnosis_guides_config.json"

# SSH服务器配置
SSH_CONFIG = {
    "host": os.getenv("LOG_SERVER_HOST", "10.241.120.100"),
    "port": int(os.getenv("LOG_SERVER_PORT", "22")),
    "username": os.getenv("LOG_SERVER_USER", "dji"),
    "password": os.getenv("LOG_SERVER_PASSWORD", "AutoXPC.246!"),
    "timeout": int(os.getenv("SSH_TIMEOUT", "30"))
}

# 日志路径关键字
LOG_PATH_KEYWORDS = ["/rawdata/", "roadtest", "/bench-log/"]

# 监控配置
MONITOR_CONFIG = {
    "interval_seconds": 3 * 3600,  # 3小时
    "check_new_work_item_id": True,  # 检查新增的"工作项id"
    "deduplicate": True,  # 去重处理
    "processed_items_file": "work/fault_diagnosis_processed_items.json"  # 已处理记录文件
}

# 报告文档配置
REPORT_PARENT_NODE_TOKEN = "GCrNwnjWFiNw1UkLOraclXVynO1"  # 报告文档父节点

# 本地缓存目录
# 从当前文件位置计算到项目根目录的work目录
CACHE_DIR = _project_root / "work" / "fault_diagnosis_cache"
LOG_CACHE_DIR = CACHE_DIR / "logs"
GUIDE_CACHE_DIR = CACHE_DIR / "guides"

# 确保缓存目录存在
CACHE_DIR.mkdir(parents=True, exist_ok=True)
LOG_CACHE_DIR.mkdir(parents=True, exist_ok=True)
GUIDE_CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Fault ID格式支持
FAULT_ID_PATTERNS = [
    r"0x[0-9A-Fa-f]+",  # 0x0165
    r"[0-9]+",  # 165
    r"0x[0-9]+",  # 0x165
]

def get_field_name(field_key: str) -> str:
    """获取字段名称"""
    return FIELD_MAPPING.get(field_key, field_key)

def get_ssh_config() -> Dict:
    """获取SSH配置"""
    return SSH_CONFIG.copy()

def get_monitor_config() -> Dict:
    """获取监控配置"""
    return MONITOR_CONFIG.copy()

def load_guide_docs_from_file() -> List[Dict]:
    """从配置文件加载指引文档列表"""
    if GUIDE_DOCS_CONFIG_FILE.exists():
        try:
            with open(GUIDE_DOCS_CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                file_docs = config.get('guide_docs', [])
                if file_docs:
                    return file_docs
        except Exception as e:
            print(f"[!] 读取指引文档配置失败: {e}")
    return FAULT_GUIDE_DOCS

def get_guide_docs() -> List[Dict]:
    """获取故障定位指引文档列表（优先从文件加载）"""
    return load_guide_docs_from_file()

# Token管理（延迟导入避免循环依赖）
def get_user_access_token_config() -> str:
    """获取user_access_token（自动刷新）"""
    try:
        from token_manager import get_user_access_token
        token = get_user_access_token()
        if token:
            return token
    except ImportError:
        pass
    except Exception as e:
        print(f"[!] Token自动刷新失败: {e}")
    
    # 如果自动刷新失败，使用环境变量或默认值
    return os.getenv("FEISHU_USER_ACCESS_TOKEN", "u-eIUWr84upbgokMMGU78cvQk1npEg4kOXryayFxa020ku")

# 动态获取USER_ACCESS_TOKEN（每次调用时获取最新token）
def get_dynamic_user_access_token() -> str:
    """动态获取user_access_token"""
    return get_user_access_token_config()

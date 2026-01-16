# -*- coding: utf-8 -*-
"""
Token管理模块 - 自动刷新user_access_token
"""

import sys
import os
import json
import time
import requests
from typing import Optional, Dict
from pathlib import Path
from datetime import datetime

# 修复Windows控制台编码问题
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

# 配置
APP_ID = "cli_a9c92ca516f99bd9"
APP_SECRET = "zlOKnyZkSuSUSr0WlAl6qbh5Qw4eM6wC"

# 从当前文件位置计算到项目根目录的work目录
_current_file = Path(__file__)
_project_root = _current_file.parent.parent.parent.parent  # 从capabilities/skills/skills/到项目根目录
TOKEN_CACHE_FILE = _project_root / "work" / "fault_diagnosis_token_cache.json"


class TokenManager:
    """Token管理器 - 自动刷新user_access_token"""
    
    def __init__(self):
        """初始化Token管理器"""
        self.app_id = APP_ID
        self.app_secret = APP_SECRET
        self.token_cache_file = TOKEN_CACHE_FILE
        self.token_cache_file.parent.mkdir(parents=True, exist_ok=True)
    
    def get_tenant_access_token(self) -> Optional[str]:
        """获取tenant_access_token"""
        url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
        headers = {'Content-Type': 'application/json'}
        data = {
            "app_id": self.app_id,
            "app_secret": self.app_secret
        }
        
        try:
            response = requests.post(url, headers=headers, json=data)
            if response.status_code == 200:
                result = response.json()
                if result.get('code') == 0:
                    return result.get('tenant_access_token')
        except Exception as e:
            print(f"[!] 获取tenant_access_token失败: {e}")
        return None
    
    def load_token_cache(self) -> Optional[Dict]:
        """加载token缓存"""
        if self.token_cache_file.exists():
            try:
                with open(self.token_cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return None
    
    def save_token_cache(self, token_data: Dict):
        """保存token缓存"""
        try:
            with open(self.token_cache_file, 'w', encoding='utf-8') as f:
                json.dump(token_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[!] 保存token缓存失败: {e}")
    
    def refresh_user_access_token(self, refresh_token: str) -> Optional[Dict]:
        """
        使用refresh_token刷新user_access_token
        
        Args:
            refresh_token: 刷新token
            
        Returns:
            token数据字典或None
        """
        tenant_token = self.get_tenant_access_token()
        if not tenant_token:
            return None
        
        url = "https://open.feishu.cn/open-apis/authen/v1/oidc/refresh_access_token"
        headers = {
            "Authorization": f"Bearer {tenant_token}",
            "Content-Type": "application/json"
        }
        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token
        }
        
        try:
            response = requests.post(url, headers=headers, json=data)
            if response.status_code == 200:
                result = response.json()
                if result.get('code') == 0:
                    return result.get('data', {})
        except Exception as e:
            print(f"[!] 刷新token失败: {e}")
        return None
    
    def get_valid_user_access_token(self) -> Optional[str]:
        """
        获取有效的user_access_token（自动刷新）
        
        Returns:
            user_access_token或None
        """
        cache = self.load_token_cache()
        
        if cache:
            access_token = cache.get('access_token')
            expires_at = cache.get('expires_at', 0)
            refresh_token = cache.get('refresh_token')
            
            # 检查token是否还有效（提前5分钟刷新）
            if access_token and time.time() < expires_at - 300:
                return access_token
            
            # 如果token即将过期，尝试刷新
            if refresh_token:
                print("[!] Token即将过期，尝试刷新...")
                new_token_data = self.refresh_user_access_token(refresh_token)
                if new_token_data:
                    access_token = new_token_data.get('access_token')
                    expires_in = new_token_data.get('expires_in', 7200)
                    new_refresh_token = new_token_data.get('refresh_token', refresh_token)
                    
                    # 保存新的token
                    self.save_token_cache({
                        'access_token': access_token,
                        'expires_at': time.time() + expires_in,
                        'refresh_token': new_refresh_token,
                        'last_refresh': datetime.now().isoformat()
                    })
                    
                    print("[OK] Token刷新成功")
                    return access_token
        
        # 如果没有缓存或刷新失败，返回None（需要重新授权）
        print("[!] 无法获取有效token，需要重新授权")
        return None
    
    def save_initial_token(self, access_token: str, expires_in: int, refresh_token: str):
        """
        保存初始token（首次授权后调用）
        
        Args:
            access_token: user_access_token
            expires_in: 有效期（秒）
            refresh_token: 刷新token
        """
        self.save_token_cache({
            'access_token': access_token,
            'expires_at': time.time() + expires_in,
            'refresh_token': refresh_token,
            'last_refresh': datetime.now().isoformat()
        })
        print("[OK] Token已保存到缓存")


# 全局实例
_token_manager = None

def get_token_manager() -> TokenManager:
    """获取Token管理器实例（单例）"""
    global _token_manager
    if _token_manager is None:
        _token_manager = TokenManager()
    return _token_manager

def get_user_access_token() -> Optional[str]:
    """
    获取有效的user_access_token（便捷函数）
    
    Returns:
        user_access_token或None
    """
    manager = get_token_manager()
    return manager.get_valid_user_access_token()

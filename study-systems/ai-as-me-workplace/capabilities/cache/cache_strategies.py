# -*- coding: utf-8 -*-
"""
缓存策略实现

支持多种缓存策略：内存缓存、文件缓存、TTL管理
"""

import json
import time
from abc import ABC, abstractmethod
from typing import Any, Optional, Dict
from pathlib import Path
from datetime import datetime, timedelta


class CacheStrategy(ABC):
    """缓存策略基类"""
    
    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        pass
    
    @abstractmethod
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """设置缓存值"""
        pass
    
    @abstractmethod
    def delete(self, key: str):
        """删除缓存值"""
        pass
    
    @abstractmethod
    def clear(self):
        """清空所有缓存"""
        pass
    
    @abstractmethod
    def exists(self, key: str) -> bool:
        """检查缓存是否存在"""
        pass


class MemoryCacheStrategy(CacheStrategy):
    """内存缓存策略"""
    
    def __init__(self):
        """初始化内存缓存"""
        self._cache: Dict[str, Dict[str, Any]] = {}
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        if key not in self._cache:
            return None
        
        entry = self._cache[key]
        
        # 检查TTL
        if 'expires_at' in entry:
            if time.time() > entry['expires_at']:
                del self._cache[key]
                return None
        
        return entry.get('value')
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """设置缓存值"""
        entry = {'value': value}
        if ttl:
            entry['expires_at'] = time.time() + ttl
        self._cache[key] = entry
    
    def delete(self, key: str):
        """删除缓存值"""
        if key in self._cache:
            del self._cache[key]
    
    def clear(self):
        """清空所有缓存"""
        self._cache.clear()
    
    def exists(self, key: str) -> bool:
        """检查缓存是否存在"""
        if key not in self._cache:
            return False
        
        # 检查TTL
        entry = self._cache[key]
        if 'expires_at' in entry:
            if time.time() > entry['expires_at']:
                del self._cache[key]
                return False
        
        return True


class FileCacheStrategy(CacheStrategy):
    """文件缓存策略"""
    
    def __init__(self, cache_dir: Path):
        """
        初始化文件缓存
        
        Args:
            cache_dir: 缓存目录路径
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_cache_path(self, key: str) -> Path:
        """获取缓存文件路径"""
        # 使用key的hash作为文件名，避免特殊字符问题
        import hashlib
        key_hash = hashlib.md5(key.encode('utf-8')).hexdigest()
        return self.cache_dir / f"{key_hash}.json"
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        cache_path = self._get_cache_path(key)
        
        if not cache_path.exists():
            return None
        
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                entry = json.load(f)
            
            # 检查TTL
            if 'expires_at' in entry:
                if time.time() > entry['expires_at']:
                    cache_path.unlink()
                    return None
            
            return entry.get('value')
        except Exception:
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """设置缓存值"""
        cache_path = self._get_cache_path(key)
        
        entry = {
            'key': key,
            'value': value,
            'cached_at': time.time()
        }
        
        if ttl:
            entry['expires_at'] = time.time() + ttl
        
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(entry, f, ensure_ascii=False, indent=2)
        except Exception as e:
            raise RuntimeError(f"写入缓存失败: {e}")
    
    def delete(self, key: str):
        """删除缓存值"""
        cache_path = self._get_cache_path(key)
        if cache_path.exists():
            cache_path.unlink()
    
    def clear(self):
        """清空所有缓存"""
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                cache_file.unlink()
            except Exception:
                pass
    
    def exists(self, key: str) -> bool:
        """检查缓存是否存在"""
        cache_path = self._get_cache_path(key)
        
        if not cache_path.exists():
            return False
        
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                entry = json.load(f)
            
            # 检查TTL
            if 'expires_at' in entry:
                if time.time() > entry['expires_at']:
                    cache_path.unlink()
                    return False
            
            return True
        except Exception:
            return False


class HybridCacheStrategy(CacheStrategy):
    """混合缓存策略（内存+文件）"""
    
    def __init__(self, cache_dir: Path):
        """
        初始化混合缓存
        
        Args:
            cache_dir: 缓存目录路径
        """
        self.memory_cache = MemoryCacheStrategy()
        self.file_cache = FileCacheStrategy(cache_dir)
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存值（优先从内存）"""
        # 先从内存获取
        value = self.memory_cache.get(key)
        if value is not None:
            return value
        
        # 从文件获取
        value = self.file_cache.get(key)
        if value is not None:
            # 回填到内存
            self.memory_cache.set(key, value)
            return value
        
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """设置缓存值（同时写入内存和文件）"""
        self.memory_cache.set(key, value, ttl)
        self.file_cache.set(key, value, ttl)
    
    def delete(self, key: str):
        """删除缓存值"""
        self.memory_cache.delete(key)
        self.file_cache.delete(key)
    
    def clear(self):
        """清空所有缓存"""
        self.memory_cache.clear()
        self.file_cache.clear()
    
    def exists(self, key: str) -> bool:
        """检查缓存是否存在"""
        return self.memory_cache.exists(key) or self.file_cache.exists(key)

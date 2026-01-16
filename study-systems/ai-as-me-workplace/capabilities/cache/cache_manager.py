# -*- coding: utf-8 -*-
"""
统一缓存管理器

提供统一的缓存接口和管理策略
"""

import json
import logging
from typing import Any, Optional, Dict
from pathlib import Path
from datetime import datetime

from .cache_strategies import (
    CacheStrategy, MemoryCacheStrategy, FileCacheStrategy, HybridCacheStrategy
)

logger = logging.getLogger(__name__)


class UnifiedCacheManager:
    """统一缓存管理器"""
    
    def __init__(self, config_file: Optional[Path] = None):
        """
        初始化统一缓存管理器
        
        Args:
            config_file: 配置文件路径（可选）
        """
        self.config_file = config_file or Path("capabilities/cache/cache_config.json")
        self.config = self._load_config()
        self._strategies: Dict[str, CacheStrategy] = {}
        self._statistics: Dict[str, Dict[str, int]] = {}
        
        # 初始化策略
        self._init_strategies()
    
    def _load_config(self) -> Dict[str, Any]:
        """加载缓存配置"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"加载缓存配置失败: {e}，使用默认配置")
        
        # 默认配置
        return {
            "cache_strategies": {
                "bitable": {
                    "type": "file",
                    "ttl": 3600,
                    "location": "work/bitable_cache/"
                },
                "spreadsheet": {
                    "type": "file",
                    "ttl": 3600,
                    "location": "work/spreadsheet_cache/"
                },
                "fault_guide": {
                    "type": "file",
                    "ttl": 86400,
                    "location": "work/fault_diagnosis_cache/guides/"
                },
                "default": {
                    "type": "memory",
                    "ttl": 3600
                }
            }
        }
    
    def _init_strategies(self):
        """初始化缓存策略"""
        strategies_config = self.config.get("cache_strategies", {})
        
        for strategy_name, strategy_config in strategies_config.items():
            strategy_type = strategy_config.get("type", "memory")
            ttl = strategy_config.get("ttl", 3600)
            
            if strategy_type == "memory":
                strategy = MemoryCacheStrategy()
            elif strategy_type == "file":
                location = strategy_config.get("location", "work/cache/")
                cache_dir = Path(location)
                strategy = FileCacheStrategy(cache_dir)
            elif strategy_type == "hybrid":
                location = strategy_config.get("location", "work/cache/")
                cache_dir = Path(location)
                strategy = HybridCacheStrategy(cache_dir)
            else:
                logger.warning(f"未知的缓存策略类型: {strategy_type}，使用内存缓存")
                strategy = MemoryCacheStrategy()
            
            self._strategies[strategy_name] = strategy
            self._statistics[strategy_name] = {
                'hits': 0,
                'misses': 0,
                'sets': 0,
                'deletes': 0
            }
    
    def get_strategy(self, strategy_name: str = "default") -> CacheStrategy:
        """
        获取缓存策略
        
        Args:
            strategy_name: 策略名称
            
        Returns:
            缓存策略实例
        """
        if strategy_name not in self._strategies:
            logger.warning(f"缓存策略 {strategy_name} 不存在，使用默认策略")
            strategy_name = "default"
        
        return self._strategies[strategy_name]
    
    def get(
        self,
        key: str,
        strategy_name: str = "default"
    ) -> Optional[Any]:
        """
        获取缓存值
        
        Args:
            key: 缓存键
            strategy_name: 策略名称
            
        Returns:
            缓存值，如果不存在或已过期则返回None
        """
        strategy = self.get_strategy(strategy_name)
        value = strategy.get(key)
        
        # 更新统计
        if value is not None:
            self._statistics[strategy_name]['hits'] += 1
        else:
            self._statistics[strategy_name]['misses'] += 1
        
        return value
    
    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        strategy_name: str = "default"
    ):
        """
        设置缓存值
        
        Args:
            key: 缓存键
            value: 缓存值
            ttl: 生存时间（秒），如果为None则使用策略默认值
            strategy_name: 策略名称
        """
        strategy = self.get_strategy(strategy_name)
        
        # 如果没有指定TTL，使用策略配置中的默认值
        if ttl is None:
            strategies_config = self.config.get("cache_strategies", {})
            strategy_config = strategies_config.get(strategy_name, {})
            ttl = strategy_config.get("ttl", 3600)
        
        strategy.set(key, value, ttl)
        
        # 更新统计
        self._statistics[strategy_name]['sets'] += 1
    
    def delete(self, key: str, strategy_name: str = "default"):
        """
        删除缓存值
        
        Args:
            key: 缓存键
            strategy_name: 策略名称
        """
        strategy = self.get_strategy(strategy_name)
        strategy.delete(key)
        
        # 更新统计
        self._statistics[strategy_name]['deletes'] += 1
    
    def clear(self, strategy_name: Optional[str] = None):
        """
        清空缓存
        
        Args:
            strategy_name: 策略名称，如果为None则清空所有策略
        """
        if strategy_name:
            strategy = self.get_strategy(strategy_name)
            strategy.clear()
        else:
            for strategy in self._strategies.values():
                strategy.clear()
    
    def exists(self, key: str, strategy_name: str = "default") -> bool:
        """
        检查缓存是否存在
        
        Args:
            key: 缓存键
            strategy_name: 策略名称
            
        Returns:
            缓存是否存在且未过期
        """
        strategy = self.get_strategy(strategy_name)
        return strategy.exists(key)
    
    def get_statistics(self, strategy_name: Optional[str] = None) -> Dict[str, Any]:
        """
        获取缓存统计信息
        
        Args:
            strategy_name: 策略名称，如果为None则返回所有策略的统计
            
        Returns:
            统计信息字典
        """
        if strategy_name:
            stats = self._statistics.get(strategy_name, {})
            total = stats.get('hits', 0) + stats.get('misses', 0)
            hit_rate = stats.get('hits', 0) / total if total > 0 else 0
            
            return {
                **stats,
                'hit_rate': hit_rate,
                'total_requests': total
            }
        else:
            result = {}
            for name, stats in self._statistics.items():
                total = stats.get('hits', 0) + stats.get('misses', 0)
                hit_rate = stats.get('hits', 0) / total if total > 0 else 0
                
                result[name] = {
                    **stats,
                    'hit_rate': hit_rate,
                    'total_requests': total
                }
            return result
    
    def refresh(
        self,
        key: str,
        refresh_func,
        ttl: Optional[int] = None,
        strategy_name: str = "default"
    ) -> Any:
        """
        刷新缓存（如果不存在或已过期则调用刷新函数）
        
        Args:
            key: 缓存键
            refresh_func: 刷新函数（无参数，返回缓存值）
            ttl: 生存时间（秒）
            strategy_name: 策略名称
            
        Returns:
            缓存值
        """
        value = self.get(key, strategy_name)
        
        if value is None:
            # 缓存不存在或已过期，调用刷新函数
            value = refresh_func()
            self.set(key, value, ttl, strategy_name)
        
        return value

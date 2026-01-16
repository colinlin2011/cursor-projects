# -*- coding: utf-8 -*-
"""
日志清理管理器

自动清理本地日志文件，在分析成功后约1天后删除
"""

import sys
import os
import json
import time
from typing import List, Optional
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fault_diagnosis_config import LOG_CACHE_DIR

# 修复Windows控制台编码问题
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass


class LogCleanupManager:
    """日志清理管理器"""
    
    def __init__(self, cleanup_after_hours: int = 24):
        """
        初始化清理管理器
        
        Args:
            cleanup_after_hours: 清理时间间隔（小时），默认24小时
        """
        self.cleanup_after_hours = cleanup_after_hours
        self.log_cache_dir = LOG_CACHE_DIR
        self.cleanup_record_file = self.log_cache_dir.parent / "log_cleanup_records.json"
        
        # 确保记录文件存在
        self.cleanup_record_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.cleanup_record_file.exists():
            self._save_cleanup_records({})
    
    def _load_cleanup_records(self) -> dict:
        """加载清理记录"""
        if self.cleanup_record_file.exists():
            try:
                with open(self.cleanup_record_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_cleanup_records(self, records: dict):
        """保存清理记录"""
        try:
            with open(self.cleanup_record_file, 'w', encoding='utf-8') as f:
                json.dump(records, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[!] 保存清理记录失败: {e}")
    
    def register_log_path(self, log_path: Path, analysis_time: Optional[datetime] = None):
        """
        注册日志路径，记录分析时间
        
        Args:
            log_path: 日志路径（文件或目录）
            analysis_time: 分析时间，默认为当前时间
        """
        if not log_path or not log_path.exists():
            return
        
        if analysis_time is None:
            analysis_time = datetime.now()
        
        records = self._load_cleanup_records()
        
        # 如果是目录，记录目录下所有文件
        if log_path.is_dir():
            for file_path in log_path.rglob("*"):
                if file_path.is_file():
                    file_str = str(file_path)
                    records[file_str] = {
                        'analysis_time': analysis_time.isoformat(),
                        'cleanup_time': (analysis_time + timedelta(hours=self.cleanup_after_hours)).isoformat(),
                        'status': 'pending'
                    }
        else:
            # 单个文件
            file_str = str(log_path)
            records[file_str] = {
                'analysis_time': analysis_time.isoformat(),
                'cleanup_time': (analysis_time + timedelta(hours=self.cleanup_after_hours)).isoformat(),
                'status': 'pending'
            }
        
        self._save_cleanup_records(records)
    
    def cleanup_expired_logs(self) -> int:
        """
        清理过期的日志文件
        
        Returns:
            清理的文件数量
        """
        records = self._load_cleanup_records()
        current_time = datetime.now()
        cleaned_count = 0
        
        files_to_remove = []
        
        for file_path_str, record in records.items():
            if record.get('status') == 'cleaned':
                continue
            
            cleanup_time_str = record.get('cleanup_time')
            if not cleanup_time_str:
                continue
            
            try:
                cleanup_time = datetime.fromisoformat(cleanup_time_str)
                if current_time >= cleanup_time:
                    file_path = Path(file_path_str)
                    if file_path.exists():
                        files_to_remove.append((file_path, record))
            except Exception as e:
                print(f"[!] 解析清理时间失败 {file_path_str}: {e}")
        
        # 删除文件
        for file_path, record in files_to_remove:
            try:
                if file_path.is_file():
                    file_path.unlink()
                    cleaned_count += 1
                    record['status'] = 'cleaned'
                    record['cleaned_at'] = datetime.now().isoformat()
                    print(f"[OK] 已清理日志文件: {file_path.name}")
                elif file_path.is_dir():
                    # 如果是目录，删除整个目录
                    import shutil
                    shutil.rmtree(file_path)
                    cleaned_count += 1
                    record['status'] = 'cleaned'
                    record['cleaned_at'] = datetime.now().isoformat()
                    print(f"[OK] 已清理日志目录: {file_path.name}")
            except Exception as e:
                print(f"[!] 清理文件失败 {file_path}: {e}")
                record['status'] = 'error'
                record['error'] = str(e)
        
        # 保存更新后的记录
        if files_to_remove:
            self._save_cleanup_records(records)
        
        return cleaned_count
    
    def cleanup_old_records(self, days: int = 7):
        """
        清理旧的清理记录（已清理超过指定天数的记录）
        
        Args:
            days: 保留天数，默认7天
        """
        records = self._load_cleanup_records()
        current_time = datetime.now()
        cutoff_time = current_time - timedelta(days=days)
        
        records_to_remove = []
        for file_path_str, record in records.items():
            if record.get('status') == 'cleaned':
                cleaned_at_str = record.get('cleaned_at')
                if cleaned_at_str:
                    try:
                        cleaned_at = datetime.fromisoformat(cleaned_at_str)
                        if cleaned_at < cutoff_time:
                            records_to_remove.append(file_path_str)
                    except:
                        pass
        
        for file_path_str in records_to_remove:
            del records[file_path_str]
        
        if records_to_remove:
            self._save_cleanup_records(records)
            print(f"[OK] 已清理 {len(records_to_remove)} 条旧记录")


def register_log_for_cleanup(log_path: Path, analysis_time: Optional[datetime] = None):
    """
    注册日志文件用于自动清理（便捷函数）
    
    Args:
        log_path: 日志路径
        analysis_time: 分析时间
    """
    manager = LogCleanupManager()
    manager.register_log_path(log_path, analysis_time)


def cleanup_expired_logs() -> int:
    """
    清理过期的日志文件（便捷函数）
    
    Returns:
        清理的文件数量
    """
    manager = LogCleanupManager()
    return manager.cleanup_expired_logs()

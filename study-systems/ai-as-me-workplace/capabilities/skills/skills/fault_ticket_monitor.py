# -*- coding: utf-8 -*-
"""
问题单监控与触发模块

监控"缺陷问题闭环表"的新增记录，支持自动监控和手动触发
"""

import sys
import os
import json
import time
from typing import List, Optional, Dict, Any, Set
from pathlib import Path
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bitable_query_interface import get_query_interface
from fault_diagnosis_config import (
    DEFECT_TABLE_NAME, DEFECT_TABLE_CACHE_FILE,
    MONITOR_CONFIG, get_field_name, get_monitor_config
)

# 修复Windows控制台编码问题
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass


class FaultTicketMonitor:
    """问题单监控器"""
    
    def __init__(self):
        """初始化监控器"""
        self.query_interface = get_query_interface()
        self.monitor_config = get_monitor_config()
        self.processed_items_file = Path(self.monitor_config['processed_items_file'])
        self.processed_items: Set[str] = self._load_processed_items()
    
    def _load_processed_items(self) -> Set[str]:
        """加载已处理的问题单ID"""
        if self.processed_items_file.exists():
            try:
                with open(self.processed_items_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return set(data.get('processed_items', []))
            except:
                pass
        return set()
    
    def _save_processed_items(self):
        """保存已处理的问题单ID"""
        self.processed_items_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.processed_items_file, 'w', encoding='utf-8') as f:
            json.dump({
                'processed_items': list(self.processed_items),
                'last_update': datetime.now().isoformat()
            }, f, ensure_ascii=False, indent=2)
    
    def get_ticket_info(self, ticket_id: str) -> Optional[Dict[str, Any]]:
        """
        获取问题单信息
        
        Args:
            ticket_id: 问题单记录ID或工作项ID
            
        Returns:
            问题单数据字典
        """
        # 从缓存中获取表数据
        table_data = self.query_interface.get_table_data(
            DEFECT_TABLE_NAME,
            DEFECT_TABLE_CACHE_FILE
        )
        
        if not table_data:
            print(f"[X] 无法获取表数据: {DEFECT_TABLE_NAME}")
            return None
        
        records = table_data.get('records', [])
        
        # 查找匹配的记录
        for record in records:
            fields = record.get('fields', {})
            record_id = record.get('record_id', '')
            work_item_id = fields.get(get_field_name("工作项id"), "")
            
            # 匹配记录ID或工作项ID
            if record_id == ticket_id or work_item_id == ticket_id:
                return {
                    'record_id': record_id,
                    'fields': fields,
                    'work_item_id': work_item_id
                }
        
        return None
    
    def get_new_tickets(self, last_check_time: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """
        获取新增的问题单
        
        Args:
            last_check_time: 上次检查时间（可选）
            
        Returns:
            新增问题单列表
        """
        table_data = self.query_interface.get_table_data(
            DEFECT_TABLE_NAME,
            DEFECT_TABLE_CACHE_FILE
        )
        
        if not table_data:
            return []
        
        records = table_data.get('records', [])
        new_tickets = []
        
        for record in records:
            fields = record.get('fields', {})
            work_item_id = fields.get(get_field_name("工作项id"), "")
            record_id = record.get('record_id', '')
            
            # 检查是否已处理
            if self.monitor_config['deduplicate']:
                if work_item_id in self.processed_items or record_id in self.processed_items:
                    continue
            
            # 检查是否有新的工作项ID
            if self.monitor_config['check_new_work_item_id']:
                if work_item_id:
                    new_tickets.append({
                        'record_id': record_id,
                        'fields': fields,
                        'work_item_id': work_item_id
                    })
        
        return new_tickets
    
    def mark_as_processed(self, ticket_id: str):
        """标记问题单为已处理"""
        self.processed_items.add(ticket_id)
        self._save_processed_items()
    
    def monitor_new_tickets(self, callback=None) -> List[Dict[str, Any]]:
        """
        监控新增问题单
        
        Args:
            callback: 回调函数，处理每个新问题单
            
        Returns:
            新增问题单列表
        """
        print("=" * 80)
        print("监控新增问题单")
        print("=" * 80)
        print()
        
        # 刷新缓存
        from bitable_cache_manager import BitableCacheManager, APP_ID, APP_SECRET, USER_ACCESS_TOKEN, SPACE_ID
        manager = BitableCacheManager(APP_ID, APP_SECRET, USER_ACCESS_TOKEN, SPACE_ID)
        config = None
        for cfg in manager.BITABLE_CONFIGS:
            if cfg.get('cache_file') == DEFECT_TABLE_CACHE_FILE:
                config = cfg
                break
        
        if config:
            print("刷新缓存...")
            manager.load_bitable_data(
                node_token=config['node_token'],
                cache_file=config['cache_file'],
                force_refresh=True
            )
            print()
        
        # 获取新问题单
        new_tickets = self.get_new_tickets()
        
        print(f"发现 {len(new_tickets)} 个新问题单")
        print()
        
        if new_tickets:
            for ticket in new_tickets:
                work_item_id = ticket.get('work_item_id', '')
                record_id = ticket.get('record_id', '')
                print(f"新问题单: {work_item_id} (记录ID: {record_id})")
                
                if callback:
                    try:
                        callback(ticket)
                        # 标记为已处理
                        if work_item_id:
                            self.mark_as_processed(work_item_id)
                        if record_id:
                            self.mark_as_processed(record_id)
                    except Exception as e:
                        print(f"[X] 处理问题单失败: {e}")
                        import traceback
                        traceback.print_exc()
                print()
        
        return new_tickets
    
    def run_auto_monitor(self, interval: Optional[int] = None, callback=None):
        """
        运行自动监控
        
        Args:
            interval: 监控间隔（秒），如果为None则使用配置中的值
            callback: 回调函数，处理每个新问题单
        """
        if interval is None:
            interval = self.monitor_config['interval_seconds']
        
        print("=" * 80)
        print("启动自动监控")
        print("=" * 80)
        print(f"监控间隔: {interval}秒 ({interval/3600:.1f}小时)")
        print(f"监控表: {DEFECT_TABLE_NAME}")
        print()
        
        try:
            while True:
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始检查...")
                self.monitor_new_tickets(callback)
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 等待 {interval}秒...")
                print()
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\n监控已停止")


def get_ticket_monitor() -> FaultTicketMonitor:
    """获取监控器实例（单例模式）"""
    if not hasattr(get_ticket_monitor, '_instance'):
        get_ticket_monitor._instance = FaultTicketMonitor()
    return get_ticket_monitor._instance

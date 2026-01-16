# -*- coding: utf-8 -*-
"""
多维表格缓存管理器

支持多个多维表格的缓存、自动同步和自然语言查询
"""

import sys
import os
import json
import time
from typing import Optional, Dict, List, Any
from datetime import datetime
from pathlib import Path

# 修复Windows控制台编码问题
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from feishu_bitable_collaborator import create_bitable_collaborator
from feishu_api_wrapper import FeishuAPI

# 配置信息
APP_ID = "cli_a9c92ca516f99bd9"
APP_SECRET = "zlOKnyZkSuSUSr0WlAl6qbh5Qw4eM6wC"
USER_ACCESS_TOKEN = os.getenv("FEISHU_USER_ACCESS_TOKEN", "u-fjEA3Zj5J4eGr.QY6KVnXg14hgJ04kgVOOwaFMy024ps")
SPACE_ID = "7353073903872868356"  # 默认space_id

# 缓存配置
CACHE_DIR = Path("work/bitable_cache")
CACHE_CONFIG_FILE = CACHE_DIR / "cache_config.json"
SYNC_INTERVAL = 3600  # 默认同步间隔：1小时

# 多维表格配置
BITABLE_CONFIGS = [
    {
        "name": "功能安全部人力盘点",
        "node_token": "CGMnwhxzLixWhGk87jYcDRfonsh",
        "url": "https://zyt.feishu.cn/wiki/CGMnwhxzLixWhGk87jYcDRfonsh",
        "cache_file": "hr_inventory.json"
    },
    {
        "name": "新多维表格",
        "node_token": "BPddwBxoRiPFSsk8jZJctCMmndg",
        "url": "https://zyt.feishu.cn/wiki/BPddwBxoRiPFSsk8jZJctCMmndg",
        "cache_file": "new_bitable.json"
    }
]


class BitableCacheManager:
    """多维表格缓存管理器"""
    
    def __init__(self, app_id: str, app_secret: str, user_access_token: str, space_id: str = None):
        """
        初始化缓存管理器
        
        Args:
            app_id: 应用ID
            app_secret: 应用密钥
            user_access_token: 用户访问令牌
            space_id: 知识库ID（可选，默认使用全局配置）
        """
        self.app_id = app_id
        self.app_secret = app_secret
        self.user_access_token = user_access_token
        self.space_id = space_id or SPACE_ID
        
        # 创建API和协作器
        self.api = FeishuAPI(
            plugin_id="",
            plugin_secret="",
            app_id=app_id,
            app_secret=app_secret
        )
        self.api.set_user_access_token(user_access_token)
        
        self.collaborator = create_bitable_collaborator(
            app_id=app_id,
            app_secret=app_secret,
            user_access_token=user_access_token
        )
        
        # 确保缓存目录存在
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        
        # 加载缓存配置
        self.cache_config = self._load_cache_config()
    
    def _load_cache_config(self) -> Dict:
        """加载缓存配置"""
        if CACHE_CONFIG_FILE.exists():
            try:
                with open(CACHE_CONFIG_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {}
    
    def _save_cache_config(self):
        """保存缓存配置"""
        with open(CACHE_CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.cache_config, f, ensure_ascii=False, indent=2)
    
    def get_app_token_from_wiki(self, node_token: str, space_id: str = None) -> Optional[str]:
        """
        通过Wiki节点获取app_token
        
        Args:
            node_token: Wiki节点token
            space_id: 知识库ID（可选）
            
        Returns:
            多维表格app_token或None
        """
        space_id = space_id or self.space_id
        result = self.api.get_wiki_node(space_id, node_token, use_user_token=True)
        
        if result:
            node = result.get('node', result) if 'node' in result else result
            if node.get('obj_type') == 'bitable':
                return node.get('obj_token')
        return None
    
    def load_bitable_data(
        self,
        node_token: str,
        cache_file: str,
        force_refresh: bool = False,
        space_id: str = None
    ) -> Dict[str, Any]:
        """
        加载多维表格数据（从缓存或API）
        
        Args:
            node_token: Wiki节点token
            cache_file: 缓存文件名
            force_refresh: 是否强制刷新
            space_id: 知识库ID（可选）
            
        Returns:
            缓存的数据字典
        """
        cache_path = CACHE_DIR / cache_file
        space_id = space_id or self.space_id
        
        # 检查缓存是否需要刷新
        if not force_refresh and cache_path.exists():
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                
                cache_time = cache_data.get('cache_time', 0)
                sync_interval = cache_data.get('sync_interval', SYNC_INTERVAL)
                
                # 检查缓存是否过期
                if time.time() - cache_time < sync_interval:
                    print(f"[OK] 从缓存加载数据（缓存时间: {datetime.fromtimestamp(cache_time).strftime('%Y-%m-%d %H:%M:%S')}）")
                    return cache_data
                else:
                    print(f"[!] 缓存已过期，需要刷新（缓存时间: {datetime.fromtimestamp(cache_time).strftime('%Y-%m-%d %H:%M:%S')}）")
            except Exception as e:
                print(f"[!] 读取缓存失败: {e}，将重新加载")
        
        # 从API加载数据
        print(f"从API加载数据: {node_token}...")
        
        # 获取app_token
        app_token = self.get_app_token_from_wiki(node_token, space_id)
        if not app_token:
            print(f"[X] 无法获取app_token for node_token: {node_token}")
            return {}
        
        # 列出所有数据表
        tables_result = self.api.list_bitable_tables(app_token, use_user_token=True)
        if not tables_result:
            print(f"[X] 无法列出数据表 for app_token: {app_token}")
            return {}
        
        tables = tables_result.get('items', []) if 'items' in tables_result else []
        
        # 加载所有数据
        cache_data = {
            'cache_time': time.time(),
            'sync_interval': SYNC_INTERVAL,
            'node_token': node_token,
            'app_token': app_token,
            'space_id': space_id,
            'tables': {},
            'indexes': {
                'people': {},  # 人员索引：姓名 -> 记录信息
                'work_packages': {},  # 工作包索引：任务ID -> 工作包信息
                'allocations': {},  # 投入分配索引：分配ID -> 分配信息
                'by_field': {}  # 按字段值索引
            }
        }
        
        for table in tables:
            table_id = table.get('table_id')
            table_name = table.get('name', '未知')
            
            print(f"  加载数据表: {table_name}...")
            
            # 获取表格结构
            structure = self.collaborator.get_table_structure(app_token, table_id)
            fields = structure.get('fields', [])
            
            # 获取所有记录
            records = self.collaborator.get_all_records(app_token, table_id)
            
            # 创建字段映射
            field_map = {}
            for field in fields:
                field_id = field.get('field_id', '')
                field_map[field_id] = {
                    'field_name': field.get('field_name', ''),
                    'field_type': field.get('type', ''),
                    'field_id': field_id
                }
            
            # 处理记录
            processed_records = []
            for record in records:
                record_id = record.get('record_id', '')
                record_fields = record.get('fields', {})
                
                # 转换为更易用的格式
                processed_record = {
                    'record_id': record_id,
                    'fields': {}
                }
                
                for field_id, value in record_fields.items():
                    field_info = field_map.get(field_id, {})
                    field_name = field_info.get('field_name', field_id)
                    processed_record['fields'][field_name] = value
                
                processed_records.append(processed_record)
                
                # 建立索引
                self._build_indexes(cache_data['indexes'], table_name, processed_record)
            
            cache_data['tables'][table_name] = {
                'table_id': table_id,
                'fields': [{'field_name': f.get('field_name', ''), 'field_type': f.get('type', '')} for f in fields],
                'records': processed_records,
                'record_count': len(processed_records)
            }
            
            print(f"    [OK] 加载 {len(processed_records)} 条记录")
        
        # 保存缓存
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)
        
        # 更新缓存配置
        cache_key = f"{node_token}_{cache_file}"
        self.cache_config[cache_key] = {
            'node_token': node_token,
            'cache_file': cache_file,
            'last_sync': time.time(),
            'app_token': app_token
        }
        self._save_cache_config()
        
        print(f"[OK] 数据已缓存到: {cache_path}")
        
        return cache_data
    
    def _build_indexes(self, indexes: Dict, table_name: str, record: Dict):
        """建立索引"""
        fields = record.get('fields', {})
        record_id = record.get('record_id', '')
        
        # 根据表名建立不同的索引
        if table_name == "资源池表_谁可用":
            name = fields.get('姓名', '')
            if name:
                indexes['people'][name] = record
        
        elif table_name == "业务规划表_做什么":
            task_id = fields.get('任务ID', '')
            if task_id:
                indexes['work_packages'][task_id] = record
        
        elif table_name == "投入分配表_怎么分":
            allocation_id = fields.get('分配ID', '')
            if allocation_id:
                indexes['allocations'][allocation_id] = record
        
        # 通用字段索引（按字段值索引）
        for field_name, value in fields.items():
            if value and isinstance(value, (str, int, float)):
                if field_name not in indexes['by_field']:
                    indexes['by_field'][field_name] = {}
                if value not in indexes['by_field'][field_name]:
                    indexes['by_field'][field_name][value] = []
                indexes['by_field'][field_name][value].append(record)
    
    def get_cached_data(self, cache_file: str) -> Optional[Dict]:
        """获取缓存数据"""
        cache_path = CACHE_DIR / cache_file
        if not cache_path.exists():
            return None
        
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return None
    
    def sync_all_bitables(self, force_refresh: bool = False):
        """同步所有配置的多维表格"""
        print("=" * 80)
        print("开始同步所有多维表格...")
        print("=" * 80)
        print()
        
        results = {}
        
        for config in BITABLE_CONFIGS:
            name = config['name']
            node_token = config['node_token']
            cache_file = config['cache_file']
            
            print(f"同步: {name}")
            print(f"  Node Token: {node_token}")
            print(f"  缓存文件: {cache_file}")
            print()
            
            try:
                data = self.load_bitable_data(
                    node_token=node_token,
                    cache_file=cache_file,
                    force_refresh=force_refresh
                )
                results[name] = {
                    'success': True,
                    'data': data,
                    'tables_count': len(data.get('tables', {})),
                    'total_records': sum(t.get('record_count', 0) for t in data.get('tables', {}).values())
                }
                print(f"  [OK] 同步成功")
            except Exception as e:
                results[name] = {
                    'success': False,
                    'error': str(e)
                }
                print(f"  [X] 同步失败: {e}")
            
            print()
        
        print("=" * 80)
        print("同步完成")
        print("=" * 80)
        print()
        
        # 打印汇总
        for name, result in results.items():
            if result.get('success'):
                print(f"{name}:")
                print(f"  - 数据表数: {result['tables_count']}")
                print(f"  - 总记录数: {result['total_records']}")
            else:
                print(f"{name}: 同步失败 - {result.get('error')}")
            print()
        
        return results
    
    def query_person(self, person_name: str, cache_file: str = None) -> Optional[Dict]:
        """
        查询人员信息
        
        Args:
            person_name: 人员姓名
            cache_file: 缓存文件名（如果为None，会在所有缓存中搜索）
            
        Returns:
            人员信息字典
        """
        if cache_file:
            # 从指定缓存查询
            data = self.get_cached_data(cache_file)
            if data:
                return data.get('indexes', {}).get('people', {}).get(person_name)
        else:
            # 从所有缓存查询
            for config in BITABLE_CONFIGS:
                data = self.get_cached_data(config['cache_file'])
                if data:
                    person = data.get('indexes', {}).get('people', {}).get(person_name)
                    if person:
                        return person
        return None
    
    def get_person_allocations(self, person_name: str, cache_file: str = None) -> List[Dict]:
        """获取人员的投入分配"""
        if cache_file:
            data = self.get_cached_data(cache_file)
            if not data:
                return []
        else:
            # 从所有缓存中查找
            for config in BITABLE_CONFIGS:
                data = self.get_cached_data(config['cache_file'])
                if data:
                    person = data.get('indexes', {}).get('people', {}).get(person_name)
                    if person:
                        cache_file = config['cache_file']
                        break
            else:
                return []
        
        person_info = data.get('indexes', {}).get('people', {}).get(person_name)
        if not person_info:
            return []
        
        # 从投入分配表中查找
        allocation_table = data.get('tables', {}).get('投入分配表_怎么分', {})
        allocations = []
        
        person_record_id = person_info.get('record_id')
        if not person_record_id:
            return []
        
        for record in allocation_table.get('records', []):
            fields = record.get('fields', {})
            person_field = fields.get('人员', [])
            
            if person_field and isinstance(person_field, list):
                for item in person_field:
                    if isinstance(item, dict):
                        record_ids = item.get('record_ids', [])
                        if person_record_id in record_ids:
                            allocations.append(record)
                            break
        
        return allocations


def main():
    """主函数：同步所有多维表格"""
    manager = BitableCacheManager(
        app_id=APP_ID,
        app_secret=APP_SECRET,
        user_access_token=USER_ACCESS_TOKEN,
        space_id=SPACE_ID
    )
    
    # 同步所有多维表格
    results = manager.sync_all_bitables(force_refresh=False)
    
    print()
    print("=" * 80)
    print("缓存数据概览")
    print("=" * 80)
    print()
    
    for name, result in results.items():
        if result.get('success'):
            data = result.get('data', {})
            print(f"## {name}")
            print()
            for table_name, table_data in data.get('tables', {}).items():
                print(f"- **{table_name}**: {table_data.get('record_count', 0)} 条记录")
            print()
            
            indexes = data.get('indexes', {})
            print(f"索引统计:")
            print(f"  - 人员索引: {len(indexes.get('people', {}))} 人")
            print(f"  - 工作包索引: {len(indexes.get('work_packages', {}))} 个")
            print(f"  - 投入分配索引: {len(indexes.get('allocations', {}))} 个")
            print()


if __name__ == "__main__":
    main()

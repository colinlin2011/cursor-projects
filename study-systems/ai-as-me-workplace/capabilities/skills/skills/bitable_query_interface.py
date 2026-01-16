# -*- coding: utf-8 -*-
"""
多维表格自然语言查询接口

基于缓存数据，提供自然语言查询能力
"""

import sys
import os
import json
from typing import Optional, Dict, List, Any
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bitable_cache_manager import BitableCacheManager, BITABLE_CONFIGS, CACHE_DIR

# 配置信息
APP_ID = "cli_a9c92ca516f99bd9"
APP_SECRET = "zlOKnyZkSuSUSr0WlAl6qbh5Qw4eM6wC"
USER_ACCESS_TOKEN = os.getenv("FEISHU_USER_ACCESS_TOKEN", "u-fjEA3Zj5J4eGr.QY6KVnXg14hgJ04kgVOOwaFMy024ps")
SPACE_ID = "7353073903872868356"


class BitableQueryInterface:
    """多维表格查询接口"""
    
    def __init__(self):
        """初始化查询接口"""
        self.manager = BitableCacheManager(
            app_id=APP_ID,
            app_secret=APP_SECRET,
            user_access_token=USER_ACCESS_TOKEN,
            space_id=SPACE_ID
        )
        self._cache_data = {}  # 内存缓存
    
    def _load_cache_data(self, cache_file: str) -> Optional[Dict]:
        """加载缓存数据（带内存缓存）"""
        if cache_file in self._cache_data:
            return self._cache_data[cache_file]
        
        data = self.manager.get_cached_data(cache_file)
        if data:
            self._cache_data[cache_file] = data
        return data
    
    def get_person_info(self, person_name: str, cache_file: str = None) -> Optional[Dict]:
        """
        获取人员信息
        
        Args:
            person_name: 人员姓名
            cache_file: 缓存文件名（可选，如果为None会在所有缓存中搜索）
            
        Returns:
            人员信息字典，包含：
            - record_id: 记录ID
            - fields: 字段信息（姓名、所属小组、人员属性、可投带宽、实际投入等）
        """
        if cache_file:
            data = self._load_cache_data(cache_file)
            if data:
                return data.get('indexes', {}).get('people', {}).get(person_name)
        else:
            # 从所有缓存中搜索
            for config in BITABLE_CONFIGS:
                data = self._load_cache_data(config['cache_file'])
                if data:
                    person = data.get('indexes', {}).get('people', {}).get(person_name)
                    if person:
                        return person
        return None
    
    def get_person_allocations(self, person_name: str, cache_file: str = None) -> List[Dict]:
        """
        获取人员的投入分配
        
        Args:
            person_name: 人员姓名
            cache_file: 缓存文件名（可选）
            
        Returns:
            投入分配记录列表
        """
        person_info = self.get_person_info(person_name, cache_file)
        if not person_info:
            return []
        
        # 找到包含该人员的缓存
        target_cache = None
        if cache_file:
            target_cache = cache_file
        else:
            for config in BITABLE_CONFIGS:
                data = self._load_cache_data(config['cache_file'])
                if data:
                    if person_name in data.get('indexes', {}).get('people', {}):
                        target_cache = config['cache_file']
                        break
        
        if not target_cache:
            return []
        
        data = self._load_cache_data(target_cache)
        if not data:
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
    
    def get_work_package_info(self, task_id: str, cache_file: str = None) -> Optional[Dict]:
        """
        获取工作包信息
        
        Args:
            task_id: 任务ID（如WP_001）
            cache_file: 缓存文件名（可选）
            
        Returns:
            工作包信息字典
        """
        if cache_file:
            data = self._load_cache_data(cache_file)
            if data:
                return data.get('indexes', {}).get('work_packages', {}).get(task_id)
        else:
            # 从所有缓存中搜索
            for config in BITABLE_CONFIGS:
                data = self._load_cache_data(config['cache_file'])
                if data:
                    wp = data.get('indexes', {}).get('work_packages', {}).get(task_id)
                    if wp:
                        return wp
        return None
    
    def search_by_field(self, field_name: str, field_value: Any, cache_file: str = None) -> List[Dict]:
        """
        按字段值搜索记录
        
        Args:
            field_name: 字段名
            field_value: 字段值
            cache_file: 缓存文件名（可选）
            
        Returns:
            匹配的记录列表
        """
        results = []
        
        if cache_file:
            data = self._load_cache_data(cache_file)
            if data:
                indexes = data.get('indexes', {}).get('by_field', {})
                if field_name in indexes and field_value in indexes[field_name]:
                    results.extend(indexes[field_name][field_value])
        else:
            # 从所有缓存中搜索
            for config in BITABLE_CONFIGS:
                data = self._load_cache_data(config['cache_file'])
                if data:
                    indexes = data.get('indexes', {}).get('by_field', {})
                    if field_name in indexes and field_value in indexes[field_name]:
                        results.extend(indexes[field_name][field_value])
        
        return results
    
    def get_table_data(self, table_name: str, cache_file: str = None) -> Optional[Dict]:
        """
        获取整个数据表的数据
        
        Args:
            table_name: 数据表名称
            cache_file: 缓存文件名（可选）
            
        Returns:
            数据表信息字典，包含：
            - table_id: 表ID
            - fields: 字段列表
            - records: 记录列表
            - record_count: 记录数
        """
        if cache_file:
            data = self._load_cache_data(cache_file)
            if data:
                return data.get('tables', {}).get(table_name)
        else:
            # 从所有缓存中搜索
            for config in BITABLE_CONFIGS:
                data = self._load_cache_data(config['cache_file'])
                if data:
                    table = data.get('tables', {}).get(table_name)
                    if table:
                        return table
        return None
    
    def get_all_people(self, cache_file: str = None) -> List[str]:
        """
        获取所有人员姓名列表
        
        Args:
            cache_file: 缓存文件名（可选）
            
        Returns:
            人员姓名列表
        """
        people = []
        
        if cache_file:
            data = self._load_cache_data(cache_file)
            if data:
                people = list(data.get('indexes', {}).get('people', {}).keys())
        else:
            # 从所有缓存中收集
            seen = set()
            for config in BITABLE_CONFIGS:
                data = self._load_cache_data(config['cache_file'])
                if data:
                    for name in data.get('indexes', {}).get('people', {}).keys():
                        if name not in seen:
                            people.append(name)
                            seen.add(name)
        
        return sorted(people)
    
    def get_cache_summary(self) -> Dict[str, Any]:
        """
        获取缓存数据摘要
        
        Returns:
            缓存摘要信息
        """
        summary = {}
        
        for config in BITABLE_CONFIGS:
            name = config['name']
            cache_file = config['cache_file']
            data = self._load_cache_data(cache_file)
            
            if data:
                summary[name] = {
                    'cache_file': cache_file,
                    'node_token': config['node_token'],
                    'cache_time': data.get('cache_time', 0),
                    'tables': {
                        table_name: table_data.get('record_count', 0)
                        for table_name, table_data in data.get('tables', {}).items()
                    },
                    'indexes': {
                        'people_count': len(data.get('indexes', {}).get('people', {})),
                        'work_packages_count': len(data.get('indexes', {}).get('work_packages', {})),
                        'allocations_count': len(data.get('indexes', {}).get('allocations', {}))
                    }
                }
        
        return summary


# 全局查询接口实例
_query_interface = None

def get_query_interface() -> BitableQueryInterface:
    """获取全局查询接口实例"""
    global _query_interface
    if _query_interface is None:
        _query_interface = BitableQueryInterface()
    return _query_interface


# 便捷函数
def query_person(person_name: str) -> Optional[Dict]:
    """查询人员信息（便捷函数）"""
    return get_query_interface().get_person_info(person_name)


def query_person_allocations(person_name: str) -> List[Dict]:
    """查询人员投入分配（便捷函数）"""
    return get_query_interface().get_person_allocations(person_name)


def query_work_package(task_id: str) -> Optional[Dict]:
    """查询工作包信息（便捷函数）"""
    return get_query_interface().get_work_package_info(task_id)


def get_all_people() -> List[str]:
    """获取所有人员列表（便捷函数）"""
    return get_query_interface().get_all_people()


if __name__ == "__main__":
    # 测试查询接口
    interface = BitableQueryInterface()
    
    print("=" * 80)
    print("多维表格查询接口测试")
    print("=" * 80)
    print()
    
    # 获取缓存摘要
    summary = interface.get_cache_summary()
    print("缓存数据摘要:")
    for name, info in summary.items():
        print(f"\n## {name}")
        print(f"  数据表数: {len(info['tables'])}")
        print(f"  总记录数: {sum(info['tables'].values())}")
        print(f"  人员索引: {info['indexes']['people_count']} 人")
        print(f"  工作包索引: {info['indexes']['work_packages_count']} 个")
    
    print()
    print("=" * 80)
    print("测试查询: 林广义")
    print("=" * 80)
    print()
    
    person = interface.get_person_info("林广义")
    if person:
        print("人员信息:")
        fields = person.get('fields', {})
        print(f"  姓名: {fields.get('姓名', '')}")
        print(f"  所属小组: {fields.get('所属小组', '')}")
        print(f"  人员属性: {fields.get('人员属性', '')}")
        print(f"  可投带宽: {fields.get('可投带宽', '')}")
        print(f"  实际投入: {fields.get('实际投入', '')}")
        
        allocations = interface.get_person_allocations("林广义")
        print(f"\n投入分配数: {len(allocations)} 个")
        for i, alloc in enumerate(allocations[:3], 1):
            fields = alloc.get('fields', {})
            print(f"  {i}. {fields.get('工作包', [{}])[0].get('text', '') if isinstance(fields.get('工作包'), list) else ''}")
            print(f"     全年投入: {fields.get('全年总投入', '')}")
    else:
        print("未找到该人员")

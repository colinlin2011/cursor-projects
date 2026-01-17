# -*- coding: utf-8 -*-
"""
飞书资源统一配置加载器

从统一配置文件加载资源配置，支持向后兼容
"""

import sys
import os
import json
from typing import Dict, List, Optional, Any
from pathlib import Path

# 修复Windows控制台编码问题
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

# 统一配置文件路径
UNIFIED_CONFIG_FILE = Path(__file__).parent.parent.parent.parent / "work" / "feishu_resources_config.json"

# 旧配置文件路径（向后兼容）
LEGACY_DOC_CONFIG_FILE = Path(__file__).parent.parent.parent.parent / "work" / "fault_diagnosis_guides_config.json"


class FeishuConfigLoader:
    """飞书资源配置加载器"""
    
    def __init__(self, config_file: Optional[Path] = None):
        """
        初始化配置加载器
        
        Args:
            config_file: 配置文件路径（可选，默认使用统一配置文件）
        """
        self.config_file = config_file or UNIFIED_CONFIG_FILE
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"[!] 加载统一配置文件失败: {e}")
                return {}
        return {}
    
    def get_documents(self) -> List[Dict[str, Any]]:
        """
        获取云文档配置列表
        
        Returns:
            文档配置列表
        """
        if self.config and 'documents' in self.config:
            items = self.config['documents'].get('items', [])
            # 过滤启用的文档
            return [item for item in items if item.get('enabled', True)]
        
        # 向后兼容：从旧配置文件加载
        return self._load_legacy_doc_config()
    
    def get_bitables(self) -> List[Dict[str, Any]]:
        """
        获取多维表格配置列表
        
        Returns:
            多维表格配置列表
        """
        if self.config and 'bitables' in self.config:
            items = self.config['bitables'].get('items', [])
            # 过滤启用的表格
            return [item for item in items if item.get('enabled', True)]
        
        # 向后兼容：从代码中加载
        return self._load_legacy_bitable_config()
    
    def get_spreadsheets(self) -> List[Dict[str, Any]]:
        """
        获取在线表格配置列表
        
        Returns:
            在线表格配置列表
        """
        if self.config and 'spreadsheets' in self.config:
            items = self.config['spreadsheets'].get('items', [])
            # 过滤启用的表格
            return [item for item in items if item.get('enabled', True)]
        
        # 向后兼容：从代码中加载
        return self._load_legacy_spreadsheet_config()
    
    def _load_legacy_doc_config(self) -> List[Dict[str, Any]]:
        """从旧配置文件加载文档配置（向后兼容）"""
        if LEGACY_DOC_CONFIG_FILE.exists():
            try:
                with open(LEGACY_DOC_CONFIG_FILE, 'r', encoding='utf-8') as f:
                    legacy_config = json.load(f)
                    guide_docs = legacy_config.get('guide_docs', [])
                    # 转换为新格式
                    return [
                        {
                            'id': f"doc_{i+1:03d}",
                            'name': doc.get('name', ''),
                            'node_token': doc.get('node_token', ''),
                            'url': doc.get('url', ''),
                            'cache_file': f"guide_{doc.get('node_token', '')}.json",
                            'category': '未分类',
                            'enabled': True,
                            'sync_interval_hours': 24,
                            'description': doc.get('name', '')
                        }
                        for i, doc in enumerate(guide_docs)
                    ]
            except Exception as e:
                print(f"[!] 加载旧文档配置失败: {e}")
        return []
    
    def _load_legacy_bitable_config(self) -> List[Dict[str, Any]]:
        """从代码中加载多维表格配置（向后兼容）"""
        try:
            from bitable_cache_manager import BITABLE_CONFIGS
            return [
                {
                    'id': f"bitable_{i+1:03d}",
                    'name': config.get('name', ''),
                    'node_token': config.get('node_token', ''),
                    'url': config.get('url', ''),
                    'cache_file': config.get('cache_file', ''),
                    'category': '未分类',
                    'enabled': True,
                    'sync_interval_hours': 24,
                    'description': config.get('name', '')
                }
                for i, config in enumerate(BITABLE_CONFIGS)
            ]
        except Exception as e:
            print(f"[!] 加载旧多维表格配置失败: {e}")
        return []
    
    def _load_legacy_spreadsheet_config(self) -> List[Dict[str, Any]]:
        """从代码中加载在线表格配置（向后兼容）"""
        try:
            from spreadsheet_cache_manager import SPREADSHEET_CONFIGS
            return [
                {
                    'id': f"spreadsheet_{i+1:03d}",
                    'name': config.get('name', ''),
                    'node_token': config.get('node_token', ''),
                    'url': config.get('url', ''),
                    'cache_file': config.get('cache_file', ''),
                    'category': '未分类',
                    'enabled': True,
                    'sync_interval_hours': 24,
                    'description': config.get('name', '')
                }
                for i, config in enumerate(SPREADSHEET_CONFIGS)
            ]
        except Exception as e:
            print(f"[!] 加载旧在线表格配置失败: {e}")
        return []
    
    def get_resource_by_id(self, resource_id: str) -> Optional[Dict[str, Any]]:
        """
        根据ID获取资源配置
        
        Args:
            resource_id: 资源ID（如 doc_001, bitable_001）
            
        Returns:
            资源配置字典，如果不存在返回None
        """
        # 检查所有资源类型
        for resource_type in ['documents', 'bitables', 'spreadsheets']:
            if resource_type in self.config:
                items = self.config[resource_type].get('items', [])
                for item in items:
                    if item.get('id') == resource_id:
                        return item
        return None
    
    def get_resources_by_category(self, category: str) -> List[Dict[str, Any]]:
        """
        根据分类获取资源列表
        
        Args:
            category: 分类标签
            
        Returns:
            资源配置列表
        """
        results = []
        for resource_type in ['documents', 'bitables', 'spreadsheets']:
            if resource_type in self.config:
                items = self.config[resource_type].get('items', [])
                for item in items:
                    if item.get('category') == category and item.get('enabled', True):
                        results.append(item)
        return results
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        获取元数据配置
        
        Returns:
            元数据字典
        """
        return self.config.get('metadata', {})
    
    def list_all_resources(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        列出所有资源
        
        Returns:
            包含所有资源类型的字典
        """
        return {
            'documents': self.get_documents(),
            'bitables': self.get_bitables(),
            'spreadsheets': self.get_spreadsheets()
        }
    
    def print_summary(self):
        """打印配置摘要"""
        print("=" * 80)
        print("飞书资源配置摘要")
        print("=" * 80)
        print()
        
        documents = self.get_documents()
        bitables = self.get_bitables()
        spreadsheets = self.get_spreadsheets()
        
        print(f"📄 云文档: {len(documents)} 个")
        for doc in documents:
            status = "✓" if doc.get('enabled', True) else "✗"
            print(f"  {status} [{doc.get('id', 'N/A')}] {doc.get('name', 'N/A')}")
        
        print()
        print(f"📊 多维表格: {len(bitables)} 个")
        for bitable in bitables:
            status = "✓" if bitable.get('enabled', True) else "✗"
            print(f"  {status} [{bitable.get('id', 'N/A')}] {bitable.get('name', 'N/A')}")
        
        print()
        print(f"📈 在线表格: {len(spreadsheets)} 个")
        for spreadsheet in spreadsheets:
            status = "✓" if spreadsheet.get('enabled', True) else "✗"
            print(f"  {status} [{spreadsheet.get('id', 'N/A')}] {spreadsheet.get('name', 'N/A')}")
        
        print()
        print("=" * 80)


def main():
    """主函数：打印配置摘要"""
    loader = FeishuConfigLoader()
    loader.print_summary()


if __name__ == "__main__":
    main()

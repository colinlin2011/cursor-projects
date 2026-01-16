# -*- coding: utf-8 -*-
"""
在线表格缓存管理器

支持多个在线表格的缓存、自动同步和自然语言查询
"""

import sys
import os
import json
import time
from typing import Optional, Dict, List, Any
from datetime import datetime
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from feishu_spreadsheet_collaborator import create_spreadsheet_collaborator
from feishu_api_wrapper import FeishuAPI

# 配置信息
APP_ID = "cli_a9c92ca516f99bd9"
APP_SECRET = "zlOKnyZkSuSUSr0WlAl6qbh5Qw4eM6wC"
USER_ACCESS_TOKEN = os.getenv("FEISHU_USER_ACCESS_TOKEN", "u-fjEA3Zj5J4eGr.QY6KVnXg14hgJ04kgVOOwaFMy024ps")
SPACE_ID = "7353073903872868356"  # 默认space_id

# 缓存配置
CACHE_DIR = Path("work/spreadsheet_cache")
CACHE_CONFIG_FILE = CACHE_DIR / "cache_config.json"
SYNC_INTERVAL = 3600  # 默认同步间隔：1小时

# 在线表格配置
SPREADSHEET_CONFIGS = [
    {
        "name": "在线表格示例",
        "node_token": "TDlnwRfpBikbUIk5guDcRyN5neh",
        "url": "https://zyt.feishu.cn/wiki/TDlnwRfpBikbUIk5guDcRyN5neh",
        "cache_file": "spreadsheet_example.json"
    }
]

# 修复Windows控制台编码问题
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass


class SpreadsheetCacheManager:
    """在线表格缓存管理器"""
    
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
        
        self.collaborator = create_spreadsheet_collaborator(
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
    
    def get_spreadsheet_token_from_wiki(self, node_token: str, space_id: str = None) -> Optional[str]:
        """
        通过Wiki节点获取spreadsheet_token
        
        Args:
            node_token: Wiki节点token
            space_id: 知识库ID（可选）
            
        Returns:
            在线表格spreadsheet_token或None
        """
        space_id = space_id or self.space_id
        result = self.api.get_wiki_node(space_id, node_token, use_user_token=True)
        
        if result:
            node = result.get('node', result) if 'node' in result else result
            obj_type = node.get('obj_type', '')
            obj_token = node.get('obj_token', '')
            
            # 在线表格的obj_type可能是'sheet'或'spreadsheet'
            if obj_type in ['sheet', 'spreadsheet']:
                return obj_token
        return None
    
    def load_spreadsheet_data(
        self,
        node_token: str,
        cache_file: str,
        force_refresh: bool = False,
        space_id: str = None
    ) -> Dict[str, Any]:
        """
        加载在线表格数据（从缓存或API）
        
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
        
        # 获取spreadsheet_token
        spreadsheet_token = self.get_spreadsheet_token_from_wiki(node_token, space_id)
        if not spreadsheet_token:
            print(f"[X] 无法获取spreadsheet_token for node_token: {node_token}")
            return {}
        
        print(f"[OK] 获取到spreadsheet_token: {spreadsheet_token}")
        
        # 分析表格结构
        analysis = self.collaborator.analyze_spreadsheet(spreadsheet_token, use_user_token=True)
        
        # 构建缓存数据
        cache_data = {
            'cache_time': time.time(),
            'sync_interval': SYNC_INTERVAL,
            'node_token': node_token,
            'spreadsheet_token': spreadsheet_token,
            'space_id': space_id,
            'sheets': {},
            'analysis': analysis
        }
        
        # 获取工作表列表
        sheets = self.collaborator.get_sheet_list(spreadsheet_token, use_user_token=True)
        
        print(f"  找到 {len(sheets)} 个工作表")
        
        # 处理每个工作表的数据
        for sheet in sheets:
            # sheet_id可能在sheet_id字段，也可能在sheetId字段（驼峰命名）
            sheet_id = sheet.get('sheet_id') or sheet.get('sheetId', '')
            sheet_title = sheet.get('title', '')
            
            print(f"    工作表: {sheet_title}, sheet_id: {sheet_id}")
            
            if not sheet_id:
                print(f"  [!] 工作表 '{sheet_title}' 没有sheet_id，跳过")
                print(f"      工作表对象: {sheet}")
                continue
            
            print(f"  加载工作表: {sheet_title} (ID: {sheet_id})...")
            
            # 获取工作表数据
            sheet_data = self.collaborator.get_sheet_data(spreadsheet_token, sheet_id, use_user_token=True)
            
            # 提取数据值
            values = []
            if sheet_data:
                # 处理不同的返回格式
                if 'code' in sheet_data and sheet_data.get('code') == 0:
                    value_range = sheet_data.get('data', {}).get('valueRange', {})
                    values = value_range.get('values', [])
                elif 'valueRange' in sheet_data:
                    # 直接返回valueRange格式
                    value_range = sheet_data.get('valueRange', {})
                    values = value_range.get('values', [])
                elif 'data' in sheet_data:
                    value_range = sheet_data.get('data', {}).get('valueRange', {})
                    values = value_range.get('values', [])
                elif 'values' in sheet_data:
                    values = sheet_data.get('values', [])
            
            # 转换为更易用的格式（第一行作为表头）
            # 处理headers，将None转换为空字符串
            headers = []
            if values:
                headers = [str(cell) if cell is not None else '' for cell in values[0]]
            
            processed_data = {
                'sheet_id': sheet_id,
                'title': sheet_title,
                'headers': headers,
                'rows': values[1:] if len(values) > 1 else [],
                'row_count': len(values) - 1 if len(values) > 1 else 0,
                'column_count': len(headers) if headers else 0
            }
            
            cache_data['sheets'][sheet_title] = processed_data
            
            print(f"    [OK] 加载 {processed_data['row_count']} 行, {processed_data['column_count']} 列")
        
        # 保存缓存
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)
        
        # 更新缓存配置
        cache_key = f"{node_token}_{cache_file}"
        self.cache_config[cache_key] = {
            'node_token': node_token,
            'cache_file': cache_file,
            'last_sync': time.time(),
            'spreadsheet_token': spreadsheet_token
        }
        self._save_cache_config()
        
        print(f"[OK] 数据已缓存到: {cache_path}")
        
        return cache_data
    
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
    
    def sync_all_spreadsheets(self, force_refresh: bool = False):
        """同步所有配置的在线表格"""
        print("=" * 80)
        print("开始同步所有在线表格...")
        print("=" * 80)
        print()
        
        results = {}
        
        for config in SPREADSHEET_CONFIGS:
            name = config['name']
            node_token = config['node_token']
            cache_file = config['cache_file']
            
            print(f"同步: {name}")
            print(f"  Node Token: {node_token}")
            print(f"  缓存文件: {cache_file}")
            print()
            
            try:
                data = self.load_spreadsheet_data(
                    node_token=node_token,
                    cache_file=cache_file,
                    force_refresh=force_refresh
                )
                results[name] = {
                    'success': True,
                    'data': data,
                    'sheets_count': len(data.get('sheets', {})),
                    'total_rows': sum(s.get('row_count', 0) for s in data.get('sheets', {}).values())
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
                print(f"  - 工作表数: {result['sheets_count']}")
                print(f"  - 总行数: {result['total_rows']}")
            else:
                print(f"{name}: 同步失败 - {result.get('error')}")
            print()
        
        return results


def main():
    """主函数：同步所有在线表格"""
    manager = SpreadsheetCacheManager(
        app_id=APP_ID,
        app_secret=APP_SECRET,
        user_access_token=USER_ACCESS_TOKEN,
        space_id=SPACE_ID
    )
    
    # 同步所有在线表格
    results = manager.sync_all_spreadsheets(force_refresh=False)
    
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
            for sheet_name, sheet_data in data.get('sheets', {}).items():
                print(f"- **{sheet_name}**: {sheet_data.get('row_count', 0)} 行, {sheet_data.get('column_count', 0)} 列")
            print()


if __name__ == "__main__":
    main()

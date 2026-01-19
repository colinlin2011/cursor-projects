#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
配置同步脚本

用于将团队配置同步到个人配置，支持继承、合并、冲突处理。

使用方法：
    python sync_config.py --source team_configs.json --target personal_config.json --merge
    python sync_config.py --source team_configs.json --target personal_config.json --inherit
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional

# 获取脚本所在目录
SCRIPT_DIR = Path(__file__).parent
TEAM_SHARED_DIR = SCRIPT_DIR.parent


class ConfigSyncer:
    """配置同步器"""
    
    def __init__(self):
        self.conflicts = []
        
    def load_config(self, config_path: Path) -> Dict:
        """加载配置文件"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"配置文件不存在: {config_path}")
            return {}
        except json.JSONDecodeError as e:
            print(f"配置文件格式错误: {e}")
            return {}
    
    def save_config(self, config: Dict, config_path: Path):
        """保存配置文件"""
        # 确保目录存在
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    
    def merge_configs(self, team_config: Dict, personal_config: Dict, 
                      merge_mode: str = "merge") -> Dict:
        """合并配置"""
        if merge_mode == "inherit":
            # 继承模式：个人配置继承团队配置，个人配置优先级更高
            merged = self._deep_merge(team_config.copy(), personal_config)
        elif merge_mode == "merge":
            # 合并模式：合并两个配置，个人配置优先级更高
            merged = self._deep_merge(personal_config.copy(), team_config)
        else:
            # 覆盖模式：团队配置覆盖个人配置
            merged = team_config.copy()
        
        return merged
    
    def _deep_merge(self, base: Dict, override: Dict) -> Dict:
        """深度合并字典"""
        result = base.copy()
        
        for key, value in override.items():
            if key in result:
                if isinstance(result[key], dict) and isinstance(value, dict):
                    result[key] = self._deep_merge(result[key], value)
                elif isinstance(result[key], list) and isinstance(value, list):
                    # 合并列表，检查ID冲突
                    result[key] = self._merge_lists(result[key], value, key)
                else:
                    # 个人配置优先级更高
                    result[key] = value
            else:
                result[key] = value
        
        return result
    
    def _merge_lists(self, base_list: List[Dict], override_list: List[Dict], 
                     list_name: str) -> List[Dict]:
        """合并列表，处理ID冲突"""
        merged = base_list.copy()
        base_ids = {item.get('id') for item in base_list if 'id' in item}
        
        for override_item in override_list:
            item_id = override_item.get('id')
            if item_id and item_id in base_ids:
                # 找到相同ID的项，检查冲突
                base_item = next(item for item in merged if item.get('id') == item_id)
                if self._has_conflict(base_item, override_item):
                    self.conflicts.append({
                        'list': list_name,
                        'id': item_id,
                        'base': base_item,
                        'override': override_item
                    })
                # 个人配置优先级更高，覆盖团队配置
                merged = [item if item.get('id') != item_id else override_item 
                         for item in merged]
            else:
                # 新项，直接添加
                merged.append(override_item)
        
        return merged
    
    def _has_conflict(self, base_item: Dict, override_item: Dict) -> bool:
        """检查配置项是否有冲突"""
        # 检查关键字段是否不同
        key_fields = ['name', 'url', 'node_token', 'app_token']
        for field in key_fields:
            if field in base_item and field in override_item:
                if base_item[field] != override_item[field]:
                    return True
        return False
    
    def sync(self, source_path: Path, target_path: Path, 
             merge_mode: str = "merge", dry_run: bool = False) -> bool:
        """同步配置"""
        print(f"开始同步配置...")
        print(f"源配置: {source_path}")
        print(f"目标配置: {target_path}")
        print(f"合并模式: {merge_mode}")
        
        # 加载配置
        team_config = self.load_config(source_path)
        if not team_config:
            print("加载团队配置失败!")
            return False
        
        personal_config = self.load_config(target_path)
        if not personal_config:
            print("加载个人配置失败，将创建新配置")
            personal_config = {}
        
        # 合并配置
        print("\n合并配置...")
        merged_config = self.merge_configs(team_config, personal_config, merge_mode)
        
        # 检查冲突
        if self.conflicts:
            print(f"\n发现 {len(self.conflicts)} 个配置冲突:")
            for conflict in self.conflicts:
                print(f"  - {conflict['list']}.{conflict['id']}:")
                print(f"    团队配置: {conflict['base'].get('name', 'N/A')}")
                print(f"    个人配置: {conflict['override'].get('name', 'N/A')}")
                print(f"    (个人配置将覆盖团队配置)")
        
        # 保存配置
        if not dry_run:
            print("\n保存配置...")
            self.save_config(merged_config, target_path)
            print(f"配置已保存到: {target_path}")
        else:
            print("\n(干运行模式，未实际保存)")
        
        print("\n同步完成!")
        return True
    
    def show_diff(self, source_path: Path, target_path: Path):
        """显示配置差异"""
        team_config = self.load_config(source_path)
        personal_config = self.load_config(target_path)
        
        if not team_config or not personal_config:
            print("无法加载配置进行比较")
            return
        
        print("配置差异:")
        print("=" * 50)
        
        # 比较共享资源
        for resource_type in ['documents', 'bitables', 'spreadsheets']:
            if resource_type in team_config.get('shared_resources', {}):
                team_items = team_config['shared_resources'][resource_type].get('items', [])
                personal_items = personal_config.get(resource_type, {}).get('items', [])
                
                team_ids = {item.get('id') for item in team_items if 'id' in item}
                personal_ids = {item.get('id') for item in personal_items if 'id' in item}
                
                only_team = team_ids - personal_ids
                only_personal = personal_ids - team_ids
                common = team_ids & personal_ids
                
                if only_team or only_personal or common:
                    print(f"\n{resource_type}:")
                    if only_team:
                        print(f"  仅在团队配置中: {only_team}")
                    if only_personal:
                        print(f"  仅在个人配置中: {only_personal}")
                    if common:
                        print(f"  共同配置: {common}")


def main():
    parser = argparse.ArgumentParser(description="同步团队配置到个人配置")
    parser.add_argument("--source", required=True, help="源配置文件（团队配置）")
    parser.add_argument("--target", required=True, help="目标配置文件（个人配置）")
    parser.add_argument("--merge", action="store_true", help="合并模式（默认）")
    parser.add_argument("--inherit", action="store_true", help="继承模式")
    parser.add_argument("--override", action="store_true", help="覆盖模式")
    parser.add_argument("--dry-run", action="store_true", help="干运行模式（不实际保存）")
    parser.add_argument("--diff", action="store_true", help="显示配置差异")
    
    args = parser.parse_args()
    
    # 解析路径
    source_path = Path(args.source)
    if not source_path.is_absolute():
        source_path = TEAM_SHARED_DIR / source_path
    
    target_path = Path(args.target)
    if not target_path.is_absolute():
        # 假设目标路径相对于个人工作空间
        target_path = TEAM_SHARED_DIR.parent / "ai-as-me-workplace" / target_path
    
    syncer = ConfigSyncer()
    
    if args.diff:
        # 显示差异
        syncer.show_diff(source_path, target_path)
    else:
        # 确定合并模式
        if args.inherit:
            merge_mode = "inherit"
        elif args.override:
            merge_mode = "override"
        else:
            merge_mode = "merge"
        
        # 同步配置
        success = syncer.sync(
            source_path=source_path,
            target_path=target_path,
            merge_mode=merge_mode,
            dry_run=args.dry_run
        )
        
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

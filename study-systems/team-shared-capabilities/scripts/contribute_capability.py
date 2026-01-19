#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
能力贡献脚本

用于将个人开发的能力贡献到团队共享能力库。

使用方法：
    python contribute_capability.py --capability-path [路径] --name [名称] --description [描述] --category [分类] --contributor [贡献者]
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# 获取脚本所在目录
SCRIPT_DIR = Path(__file__).parent
TEAM_SHARED_DIR = SCRIPT_DIR.parent
REGISTRY_FILE = TEAM_SHARED_DIR / "capabilities" / "registry.md"
CONTRIBUTORS_FILE = TEAM_SHARED_DIR / "contributors" / "contributors.md"
CONTRIBUTION_TEMPLATE = TEAM_SHARED_DIR / "CONTRIBUTION-TEMPLATE.md"


class CapabilityContributor:
    """能力贡献者"""
    
    def __init__(self):
        self.registry_file = REGISTRY_FILE
        self.contributors_file = CONTRIBUTORS_FILE
        self.template_file = CONTRIBUTION_TEMPLATE
        
    def check_capability(self, capability_path: Path) -> Dict[str, any]:
        """检查能力完整性"""
        checks = {
            "exists": False,
            "has_readme": False,
            "has_code": False,
            "has_examples": False,
            "errors": []
        }
        
        if not capability_path.exists():
            checks["errors"].append(f"能力路径不存在: {capability_path}")
            return checks
        
        checks["exists"] = True
        
        # 检查README.md
        readme_file = capability_path / "README.md"
        if readme_file.exists():
            checks["has_readme"] = True
        else:
            checks["errors"].append("缺少README.md文件")
        
        # 检查代码文件
        code_files = list(capability_path.glob("*.py"))
        if code_files:
            checks["has_code"] = True
        else:
            checks["errors"].append("缺少Python代码文件")
        
        # 检查示例目录
        examples_dir = capability_path / "examples"
        if examples_dir.exists() and list(examples_dir.glob("*.py")):
            checks["has_examples"] = True
        
        return checks
    
    def generate_capability_id(self, capability_type: str, registry_content: str) -> str:
        """生成能力ID"""
        # 提取现有ID的最大编号
        pattern = f"TEAM-{capability_type.upper()}-(\\d+)"
        matches = re.findall(pattern, registry_content)
        
        if matches:
            max_num = max(int(m) for m in matches)
            next_num = max_num + 1
        else:
            next_num = 1
        
        return f"TEAM-{capability_type.upper()}-{next_num:03d}"
    
    def update_registry(self, capability_info: Dict[str, any]) -> bool:
        """更新团队注册表"""
        try:
            # 读取注册表
            with open(self.registry_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 生成能力ID
            capability_id = self.generate_capability_id(
                capability_info['type'],
                content
            )
            capability_info['id'] = capability_id
            
            # 构建注册表条目
            registry_entry = self._build_registry_entry(capability_info)
            
            # 找到插入位置（在对应类型的表格后）
            type_section = f"## {capability_info['type'].title()}能力"
            if type_section in content:
                # 在表格后插入
                table_end_pattern = r"(\|.*\|\n\n###)"
                match = re.search(table_end_pattern, content)
                if match:
                    insert_pos = match.end() - 1
                    content = content[:insert_pos] + registry_entry + "\n" + content[insert_pos:]
                else:
                    # 如果找不到表格，在类型标题后插入
                    insert_pos = content.find(type_section) + len(type_section)
                    content = content[:insert_pos] + "\n\n" + registry_entry + "\n" + content[insert_pos:]
            
            # 添加能力详情
            detail_section = self._build_detail_section(capability_info)
            detail_section_title = f"### {capability_info['type'].title()}能力详情"
            if detail_section_title in content:
                # 在详情部分添加
                insert_pos = content.find(detail_section_title) + len(detail_section_title)
                content = content[:insert_pos] + "\n\n" + detail_section + "\n" + content[insert_pos:]
            
            # 写入注册表
            with open(self.registry_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return True
            
        except Exception as e:
            print(f"更新注册表失败: {e}")
            return False
    
    def _build_registry_entry(self, info: Dict[str, any]) -> str:
        """构建注册表条目"""
        today = datetime.now().strftime("%Y-%m-%d")
        entry = f"| {info['id']} | {info['name']} | {info['type']} | {info['description'][:50]}... | {info.get('interface', '-')} | {info.get('params', '-')} | 可用 | {info.get('version', 'v1.0.0')} | {today} | {today} | {info['contributor']} | 0 | 0 | - | - |"
        return entry
    
    def _build_detail_section(self, info: Dict[str, any]) -> str:
        """构建详情部分"""
        detail = f"""- **{info['id']} {info['name']}**：[{info['name']}.md](skills/{info['name']}/README.md)
  - 功能：{info['description']}
  - 贡献者：{info['contributor']}
  - 创建日期：{datetime.now().strftime('%Y-%m-%d')}
"""
        return detail
    
    def update_contributors(self, contributor_info: Dict[str, any]) -> bool:
        """更新贡献者列表"""
        try:
            # 读取贡献者文件
            if self.contributors_file.exists():
                with open(self.contributors_file, 'r', encoding='utf-8') as f:
                    content = f.read()
            else:
                content = "# 贡献者列表\n\n"
            
            # 检查贡献者是否已存在
            contributor_name = contributor_info['name']
            if contributor_name not in content:
                # 添加新贡献者
                contributor_entry = f"\n## {contributor_name}\n\n"
                contributor_entry += f"- **贡献能力数**：1\n"
                contributor_entry += f"- **首次贡献**：{datetime.now().strftime('%Y-%m-%d')}\n"
                contributor_entry += f"- **联系方式**：{contributor_info.get('contact', '-')}\n\n"
                content += contributor_entry
            
            # 写入文件
            with open(self.contributors_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return True
            
        except Exception as e:
            print(f"更新贡献者列表失败: {e}")
            return False
    
    def contribute(self, capability_path: str, name: str, description: str, 
                   category: str, contributor: str, capability_type: str = "skill",
                   version: str = "v1.0.0") -> bool:
        """贡献能力"""
        capability_path = Path(capability_path)
        
        print(f"开始贡献能力: {name}")
        print(f"能力路径: {capability_path}")
        
        # 检查能力完整性
        print("\n检查能力完整性...")
        checks = self.check_capability(capability_path)
        
        if checks["errors"]:
            print("能力检查失败:")
            for error in checks["errors"]:
                print(f"  - {error}")
            print("\n请修复这些问题后重试。")
            return False
        
        print("能力检查通过!")
        
        # 准备能力信息
        capability_info = {
            "name": name,
            "description": description,
            "category": category,
            "contributor": contributor,
            "type": capability_type,
            "version": version,
            "path": str(capability_path),
            "created_date": datetime.now().strftime("%Y-%m-%d")
        }
        
        # 更新注册表
        print("\n更新团队注册表...")
        if not self.update_registry(capability_info):
            print("更新注册表失败!")
            return False
        print("注册表更新成功!")
        
        # 更新贡献者列表
        print("\n更新贡献者列表...")
        contributor_info = {
            "name": contributor,
            "contact": "-"
        }
        if not self.update_contributors(contributor_info):
            print("更新贡献者列表失败!")
            return False
        print("贡献者列表更新成功!")
        
        print(f"\n能力贡献成功! 能力ID: {capability_info['id']}")
        print(f"请查看团队注册表: {self.registry_file}")
        
        return True


def main():
    parser = argparse.ArgumentParser(description="贡献能力到团队共享库")
    parser.add_argument("--capability-path", required=True, help="能力路径")
    parser.add_argument("--name", required=True, help="能力名称")
    parser.add_argument("--description", required=True, help="能力描述")
    parser.add_argument("--category", required=True, help="能力分类")
    parser.add_argument("--contributor", required=True, help="贡献者姓名")
    parser.add_argument("--type", default="skill", choices=["skill", "agent", "local-tool", "mcp"],
                       help="能力类型")
    parser.add_argument("--version", default="v1.0.0", help="能力版本")
    
    args = parser.parse_args()
    
    contributor = CapabilityContributor()
    success = contributor.contribute(
        capability_path=args.capability_path,
        name=args.name,
        description=args.description,
        category=args.category,
        contributor=args.contributor,
        capability_type=args.type,
        version=args.version
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

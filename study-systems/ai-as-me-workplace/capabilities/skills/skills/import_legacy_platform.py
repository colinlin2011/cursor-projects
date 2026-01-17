# -*- coding: utf-8 -*-
"""
导入历史工作平台多维表格数据（使用通用能力）
- 使用token_manager自动获取有效的user_access_token
- 使用bitable_cache_manager读取并缓存多维表格数据
- 支持读取文档内容并缓存
"""

import sys
import os
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

# 修复Windows控制台编码问题
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入通用能力
from token_manager import TokenManager
from bitable_cache_manager import BitableCacheManager, CACHE_DIR
from feishu_doc_collaborator import FeishuDocCollaborator

# 配置信息
APP_ID = "cli_a9c92ca516f99bd9"
APP_SECRET = "zlOKnyZkSuSUSr0WlAl6qbh5Qw4eM6wC"
SPACE_ID = "7353073903872868356"

# 历史工作平台配置
LEGACY_APP_TOKEN = "YWDGbSZZKalcnQskTThcSUSXnub"
LEGACY_TABLE_IDS = [
    "ldxmuDnzIjTSlyRW",  # 第一个表格
    "ldxHfyQ1eqCXMji4",  # 第二个表格
]


def get_user_access_token() -> Optional[str]:
    """获取有效的user_access_token（自动刷新）"""
    token_manager = TokenManager()
    token = token_manager.get_valid_user_access_token()
    if not token:
        print("[!] 无法获取有效token，尝试使用环境变量...")
        token = os.getenv("FEISHU_USER_ACCESS_TOKEN")
    return token


def load_bitable_table(
    manager: BitableCacheManager,
    app_token: str,
    table_id: str,
    output_dir: Path,
    cache_dir: Path
) -> Dict[str, Any]:
    """加载单个数据表并缓存"""
    print(f"  处理数据表: {table_id}")
    
    try:
        # 获取表格结构
        structure = manager.collaborator.get_table_structure(app_token, table_id)
        fields = structure.get('fields', [])
        
        # 获取所有记录
        records = manager.collaborator.get_all_records(app_token, table_id)
        
        print(f"    ✓ 获取到 {len(records)} 条记录，{len(fields)} 个字段")
        
        # 缓存数据
        cache_data = {
            'table_id': table_id,
            'app_token': app_token,
            'cache_time': datetime.now().timestamp(),
            'structure': structure,
            'records': records,
            'record_count': len(records),
            'field_count': len(fields)
        }
        
        cache_file = cache_dir / f"{table_id}.json"
        cache_file.write_text(
            json.dumps(cache_data, indent=2, ensure_ascii=False),
            encoding='utf-8'
        )
        print(f"    ✓ 已缓存到: {cache_file.name}")
        
        # 导出为Markdown
        export_to_markdown(cache_data, output_dir)
        
        return {
            'table_id': table_id,
            'record_count': len(records),
            'field_count': len(fields),
            'cache_file': str(cache_file),
            'success': True
        }
        
    except Exception as e:
        print(f"    ✗ 处理失败: {e}")
        import traceback
        traceback.print_exc()
        return {
            'table_id': table_id,
            'error': str(e),
            'success': False
        }


def export_to_markdown(cache_data: Dict, output_dir: Path):
    """导出数据表为Markdown格式"""
    table_id = cache_data['table_id']
    structure = cache_data['structure']
    records = cache_data['records']
    fields = structure.get('fields', [])
    
    lines = []
    lines.append(f"# 数据表导出")
    lines.append("")
    lines.append(f"**数据表ID**: `{table_id}`")
    lines.append(f"**记录数量**: {len(records)}")
    lines.append(f"**字段数量**: {len(fields)}")
    lines.append(f"**导出时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")
    
    if not records:
        lines.append("数据表为空")
    else:
        # 字段信息
        lines.append("## 字段信息")
        lines.append("")
        for i, field in enumerate(fields, 1):
            field_name = field.get('field_name', '未知')
            field_type = field.get('type', '未知')
            lines.append(f"{i}. **{field_name}** ({field_type})")
        lines.append("")
        
        # 数据记录
        lines.append("## 数据记录")
        lines.append("")
        field_names = [f.get('field_name', '') for f in fields]
        if field_names:
            lines.append("| " + " | ".join(field_names) + " |")
            lines.append("| " + " | ".join(['---'] * len(field_names)) + " |")
            
            # 数据行
            for record in records:
                fields_data = record.get('fields', {})
                row = []
                for field in fields:
                    field_id = field.get('field_id')
                    value = fields_data.get(field_id, '')
                    formatted_value = format_field_value(value, field.get('type', ''))
                    formatted_value = formatted_value.replace('|', '\\|').replace('\n', '<br>')
                    row.append(formatted_value)
                lines.append("| " + " | ".join(row) + " |")
    
    # 保存文件
    output_file = output_dir / f"{table_id}.md"
    output_file.write_text('\n'.join(lines), encoding='utf-8')
    print(f"    ✓ 已导出到: {output_file.name}")


def format_field_value(value: Any, field_type: str) -> str:
    """格式化字段值为字符串"""
    if value is None or value == '':
        return ''
    
    if field_type == '4':  # 单选
        if isinstance(value, list) and len(value) > 0:
            return value[0].get('text', '')
    elif field_type == '5':  # 多选
        if isinstance(value, list):
            return ', '.join([item.get('text', '') for item in value])
    elif field_type == '11':  # 人员
        if isinstance(value, list):
            return ', '.join([item.get('name', '') for item in value])
    
    return str(value)


def load_document_content(
    doc_collaborator: FeishuDocCollaborator,
    node_token: str,
    output_dir: Path,
    cache_dir: Path
) -> Dict[str, Any]:
    """加载文档内容并缓存"""
    print(f"  处理文档: {node_token}")
    
    try:
        # 从飞书读取文档
        cache_file = cache_dir / f"doc_{node_token}.json"
        
        # 检查缓存
        if cache_file.exists():
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            cache_time = cache_data.get('cache_time', 0)
            # 如果缓存未过期（24小时），直接使用
            if datetime.now().timestamp() - cache_time < 86400:
                print(f"    ✓ 使用缓存（缓存时间: {datetime.fromtimestamp(cache_time).strftime('%Y-%m-%d %H:%M:%S')}）")
                content = cache_data.get('content', '')
            else:
                print(f"    ! 缓存已过期，重新加载...")
                content = None
        else:
            content = None
        
        # 如果需要重新加载
        if content is None:
            # 获取document_id
            document_id = doc_collaborator._get_document_id_from_node(node_token)
            if not document_id:
                print(f"    ✗ 无法获取document_id")
                return {'success': False, 'error': '无法获取document_id'}
            
            # 获取文档内容
            blocks = doc_collaborator._get_all_blocks(document_id)
            if not blocks:
                print(f"    ✗ 无法获取文档内容")
                return {'success': False, 'error': '无法获取文档内容'}
            
            # 转换为Markdown
            content = doc_collaborator._blocks_to_markdown(blocks)
            
            # 保存缓存
            cache_data = {
                'node_token': node_token,
                'cache_time': datetime.now().timestamp(),
                'content': content
            }
            cache_file.write_text(
                json.dumps(cache_data, indent=2, ensure_ascii=False),
                encoding='utf-8'
            )
            print(f"    ✓ 已缓存到: {cache_file.name}")
        
        # 导出为Markdown
        output_file = output_dir / f"doc_{node_token}.md"
        output_file.write_text(content, encoding='utf-8')
        print(f"    ✓ 已导出到: {output_file.name}")
        
        return {
            'node_token': node_token,
            'cache_file': str(cache_file),
            'output_file': str(output_file),
            'success': True
        }
        
    except Exception as e:
        print(f"    ✗ 处理失败: {e}")
        import traceback
        traceback.print_exc()
        return {
            'node_token': node_token,
            'error': str(e),
            'success': False
        }


def main():
    """主函数"""
    print("=" * 60)
    print("导入历史工作平台数据（使用通用能力）")
    print("=" * 60)
    print()
    
    # 获取有效的user_access_token（自动刷新）
    print("步骤1：获取有效的user_access_token...")
    user_access_token = get_user_access_token()
    if not user_access_token:
        print("[X] 无法获取user_access_token，请先运行授权脚本")
        print("    运行: python get_user_token_for_bitable.py")
        return
    
    print(f"[OK] 已获取user_access_token: {user_access_token[:20]}...")
    print()
    
    # 创建管理器
    print("步骤2：初始化管理器...")
    manager = BitableCacheManager(
        app_id=APP_ID,
        app_secret=APP_SECRET,
        user_access_token=user_access_token,
        space_id=SPACE_ID
    )
    
    doc_collaborator = FeishuDocCollaborator(
        app_id=APP_ID,
        app_secret=APP_SECRET,
        user_access_token=user_access_token,
        space_id=SPACE_ID
    )
    
    print("[OK] 管理器初始化完成")
    print()
    
    # 创建输出目录
    output_base_dir = Path(__file__).parent.parent.parent.parent / "work" / "legacy-platform"
    output_base_dir.mkdir(parents=True, exist_ok=True)
    
    cache_dir = output_base_dir / "cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    
    tables_dir = output_base_dir / "tables"
    tables_dir.mkdir(parents=True, exist_ok=True)
    
    docs_dir = output_base_dir / "docs"
    docs_dir.mkdir(parents=True, exist_ok=True)
    
    # 获取所有数据表列表
    print("步骤3：获取数据表列表...")
    tables = manager.collaborator.list_tables(LEGACY_APP_TOKEN)
    
    if tables:
        print(f"[OK] 找到 {len(tables)} 个数据表")
        # 更新TABLE_IDS列表
        all_table_ids = [t.get('table_id') for t in tables if t.get('table_id')]
        print(f"  数据表ID列表: {all_table_ids}")
    else:
        print("[!] 无法获取数据表列表，使用指定的table_id")
        all_table_ids = LEGACY_TABLE_IDS
    
    print()
    
    # 处理所有数据表
    print("步骤4：处理数据表...")
    table_results = []
    
    for i, table_id in enumerate(all_table_ids, 1):
        print(f"[{i}/{len(all_table_ids)}]")
        result = load_bitable_table(
            manager,
            LEGACY_APP_TOKEN,
            table_id,
            tables_dir,
            cache_dir
        )
        table_results.append(result)
        print()
    
    # 处理文档（如果有）
    # 注意：这里需要知道文档的node_token，暂时跳过
    
    # 生成总结报告
    print("步骤5：生成总结报告...")
    summary_lines = []
    summary_lines.append("# 历史工作平台数据导入总结")
    summary_lines.append("")
    summary_lines.append(f"**导入时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    summary_lines.append(f"**app_token**: `{LEGACY_APP_TOKEN}`")
    summary_lines.append(f"**数据表总数**: {len(table_results)}")
    summary_lines.append("")
    summary_lines.append("## 数据表导出情况")
    summary_lines.append("")
    summary_lines.append("| 序号 | 数据表ID | 记录数 | 字段数 | 状态 |")
    summary_lines.append("|------|----------|--------|--------|------|")
    
    total_records = 0
    for i, result in enumerate(table_results, 1):
        if result.get('success'):
            total_records += result.get('record_count', 0)
            table_id_short = result['table_id'][:12] + '...' if len(result['table_id']) > 12 else result['table_id']
            summary_lines.append(f"| {i} | `{table_id_short}` | {result.get('record_count', 0)} | {result.get('field_count', 0)} | ✅ 成功 |")
        else:
            summary_lines.append(f"| {i} | `{result.get('table_id', '')[:12]}...` | - | - | ❌ 失败: {result.get('error', '未知错误')} |")
    
    summary_lines.append("")
    summary_lines.append(f"**总记录数**: {total_records}")
    summary_lines.append("")
    summary_lines.append("## 文件位置")
    summary_lines.append("")
    summary_lines.append(f"- **缓存文件**: `{cache_dir}`")
    summary_lines.append(f"- **导出文件**: `{tables_dir}`")
    summary_lines.append("")
    
    # 保存总结报告
    summary_file = output_base_dir / "import-summary.md"
    summary_file.write_text('\n'.join(summary_lines), encoding='utf-8')
    
    print("=" * 60)
    print("导入完成！")
    print(f"总结报告: {summary_file}")
    print(f"缓存文件: {cache_dir}")
    print(f"导出文件: {tables_dir}")
    print(f"总记录数: {total_records}")
    print("=" * 60)


if __name__ == "__main__":
    main()

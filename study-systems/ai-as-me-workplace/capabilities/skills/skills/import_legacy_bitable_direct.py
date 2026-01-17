# -*- coding: utf-8 -*-
"""
直接导入历史工作平台多维表格数据（指定table_id）
支持直接读取指定的数据表，并缓存数据

使用方法：
python import_legacy_bitable_direct.py
"""

import sys
import os
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from feishu_bitable_collaborator import create_bitable_collaborator


# 配置信息
APP_TOKEN = "YWDGbSZZKalcnQskTThcSUSXnub"

# 指定的数据表ID（从URL中提取）
TABLE_IDS = [
    "ldxmuDnzIjTSlyRW",  # 第一个表格
    "ldxHfyQ1eqCXMji4",  # 第二个表格
]


def get_credentials():
    """获取API凭证"""
    app_id = os.getenv('FEISHU_APP_ID')
    app_secret = os.getenv('FEISHU_APP_SECRET')
    user_access_token = os.getenv('FEISHU_USER_ACCESS_TOKEN')
    
    # 如果没有环境变量，尝试从bitable_cache_manager导入
    if not app_id or not app_secret:
        try:
            from bitable_cache_manager import APP_ID, APP_SECRET
            app_id = app_id or APP_ID
            app_secret = app_secret or APP_SECRET
        except ImportError:
            pass
    
    if not user_access_token:
        try:
            from bitable_cache_manager import USER_ACCESS_TOKEN
            user_access_token = USER_ACCESS_TOKEN
        except ImportError:
            pass
    
    # 如果还是没有，使用默认值
    if not app_id:
        app_id = "cli_a9c92ca516f99bd9"
    if not app_secret:
        app_secret = "zlOKnyZkSuSUSr0WlAl6qbh5Qw4eM6wC"
    
    return app_id, app_secret, user_access_token


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
    elif field_type == '5':  # 日期
        if isinstance(value, int):
            return datetime.fromtimestamp(value / 1000).strftime('%Y-%m-%d')
    
    return str(value)


def export_table_data(
    collaborator,
    app_token: str,
    table_id: str,
    table_name: str = None,
    output_dir: Path = None,
    cache_dir: Path = None
) -> Dict[str, Any]:
    """
    导出数据表数据并缓存
    
    Returns:
        包含导出信息的字典
    """
    if table_name is None:
        table_name = f"表-{table_id[:8]}"
    
    print(f"  处理数据表: {table_name} (ID: {table_id})")
    
    # 获取表格结构
    structure = collaborator.get_table_structure(app_token, table_id)
    fields = structure.get('fields', [])
    field_map = {f.get('field_id'): f for f in fields}
    
    # 获取所有记录
    print(f"    正在获取记录...")
    records = collaborator.get_all_records(app_token, table_id)
    print(f"    获取到 {len(records)} 条记录")
    
    # 缓存原始数据（JSON格式）
    if cache_dir:
        cache_dir.mkdir(parents=True, exist_ok=True)
        cache_file = cache_dir / f"{table_id}.json"
        cache_data = {
            'table_id': table_id,
            'table_name': table_name,
            'export_time': datetime.now().isoformat(),
            'structure': structure,
            'records': records
        }
        cache_file.write_text(
            json.dumps(cache_data, indent=2, ensure_ascii=False),
            encoding='utf-8'
        )
        print(f"    已缓存到: {cache_file}")
    
    # 生成Markdown内容
    if output_dir:
        output_dir.mkdir(parents=True, exist_ok=True)
        lines = []
        lines.append(f"# {table_name}")
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
                field_type_name = get_field_type_name(field_type)
                lines.append(f"{i}. **{field_name}** ({field_type_name})")
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
                        field_type = field.get('type', '')
                        formatted_value = format_field_value(value, field_type)
                        # 转义Markdown特殊字符
                        formatted_value = formatted_value.replace('|', '\\|').replace('\n', '<br>')
                        row.append(formatted_value)
                    lines.append("| " + " | ".join(row) + " |")
        
        content = '\n'.join(lines)
        
        # 保存文件
        safe_table_name = "".join(c for c in table_name if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_table_name = safe_table_name.replace(' ', '-')
        output_file = output_dir / f"{safe_table_name}.md"
        output_file.write_text(content, encoding='utf-8')
        print(f"    已导出到: {output_file}")
    
    return {
        'table_id': table_id,
        'table_name': table_name,
        'record_count': len(records),
        'field_count': len(fields),
        'cache_file': str(cache_dir / f"{table_id}.json") if cache_dir else None,
        'output_file': str(output_dir / f"{safe_table_name}.md") if output_dir else None
    }


def get_field_type_name(field_type: str) -> str:
    """获取字段类型名称"""
    field_type_str = str(field_type)
    type_map = {
        '1': '文本',
        '2': '数字',
        '3': '单选',
        '4': '多选',
        '5': '日期',
        '7': '复选框',
        '11': '人员',
        '13': '电话号码',
        '15': '超链接',
        '17': '附件',
        '18': '关联',
        '19': '公式',
        '20': '公式',
        '21': '双向关联',
        '22': '创建人',
        '23': '修改人',
        '1001': '自动编号',
        '1002': '地理位置',
        '1003': '群组',
        '1004': '双向关联',
        '1005': '自动编号'
    }
    return type_map.get(field_type_str, f'未知类型({field_type})')


def main():
    """主函数"""
    print("=" * 60)
    print("直接导入历史工作平台多维表格数据")
    print("=" * 60)
    print()
    
    # 获取凭证
    app_id, app_secret, user_access_token = get_credentials()
    print(f"使用应用ID: {app_id[:10]}...")
    print(f"app_token: {APP_TOKEN}")
    print()
    
    # 创建协作器
    print("正在初始化飞书API连接...")
    collaborator = create_bitable_collaborator(
        app_id=app_id,
        app_secret=app_secret,
        user_access_token=user_access_token
    )
    
    # 获取多维表格信息
    print("正在获取多维表格信息...")
    app_info = collaborator.get_app_info(APP_TOKEN)
    app_name = "Colin个人工作平台"
    
    if app_info:
        if 'code' in app_info and app_info.get('code') == 0:
            app_data = app_info.get('data', {})
            app_name = app_data.get('app', {}).get('name', app_name)
        elif 'app' in app_info:
            app_name = app_info.get('app', {}).get('name', app_name)
    
    print(f"多维表格名称: {app_name}")
    print()
    
    # 创建输出目录
    output_base_dir = Path(__file__).parent.parent.parent.parent / "work" / "legacy-platform"
    output_base_dir.mkdir(parents=True, exist_ok=True)
    
    # 创建缓存目录
    cache_dir = output_base_dir / "cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    
    # 创建数据表导出目录
    tables_dir = output_base_dir / "tables"
    tables_dir.mkdir(parents=True, exist_ok=True)
    
    # 导出每个指定的数据表
    print(f"开始导出 {len(TABLE_IDS)} 个数据表...")
    print()
    
    export_summary = []
    for i, table_id in enumerate(TABLE_IDS, 1):
        print(f"[{i}/{len(TABLE_IDS)}] 处理数据表: {table_id}")
        
        try:
            # 先尝试获取表格名称
            structure = collaborator.get_table_structure(APP_TOKEN, table_id)
            # 从结构信息中可能无法直接获取名称，使用默认名称
            table_name = f"数据表-{i}"
            
            export_info = export_table_data(
                collaborator,
                APP_TOKEN,
                table_id,
                table_name=table_name,
                output_dir=tables_dir,
                cache_dir=cache_dir
            )
            export_summary.append(export_info)
            print(f"  ✓ 成功导出 {export_info['record_count']} 条记录，{export_info['field_count']} 个字段")
        except Exception as e:
            print(f"  ✗ 导出失败: {e}")
            import traceback
            traceback.print_exc()
            export_summary.append({
                'table_id': table_id,
                'table_name': f"数据表-{i}",
                'error': str(e)
            })
        print()
    
    # 尝试获取所有数据表列表（如果权限允许）
    print("尝试获取所有数据表列表...")
    tables = collaborator.list_tables(APP_TOKEN)
    
    if tables:
        print(f"找到 {len(tables)} 个数据表")
        # 导出所有数据表
        for i, table in enumerate(tables, 1):
            table_id = table.get('table_id', '')
            table_name = table.get('name', f'表{i}')
            
            # 检查是否已经处理过
            if table_id in TABLE_IDS:
                print(f"[跳过] {table_name} (已处理)")
                continue
            
            print(f"[{i}/{len(tables)}] 导出数据表: {table_name}")
            try:
                export_info = export_table_data(
                    collaborator,
                    APP_TOKEN,
                    table_id,
                    table_name=table_name,
                    output_dir=tables_dir,
                    cache_dir=cache_dir
                )
                export_summary.append(export_info)
                print(f"  ✓ 成功导出 {export_info['record_count']} 条记录")
            except Exception as e:
                print(f"  ✗ 导出失败: {e}")
                export_summary.append({
                    'table_id': table_id,
                    'table_name': table_name,
                    'error': str(e)
                })
            print()
    else:
        print("无法获取数据表列表（可能权限不足）")
        print("仅导出了指定的数据表")
    
    # 生成总结报告
    print("正在生成总结报告...")
    summary_lines = []
    summary_lines.append("# 历史工作平台数据导入总结")
    summary_lines.append("")
    summary_lines.append(f"**导入时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    summary_lines.append(f"**多维表格名称**: {app_name}")
    summary_lines.append(f"**app_token**: `{APP_TOKEN}`")
    summary_lines.append(f"**数据表总数**: {len(export_summary)}")
    summary_lines.append("")
    summary_lines.append("## 数据表导出情况")
    summary_lines.append("")
    summary_lines.append("| 序号 | 数据表名称 | 数据表ID | 记录数 | 字段数 | 状态 |")
    summary_lines.append("|------|-----------|----------|--------|--------|------|")
    
    total_records = 0
    for i, info in enumerate(export_summary, 1):
        if 'error' in info:
            summary_lines.append(f"| {i} | {info.get('table_name', '未知')} | `{info.get('table_id', '')[:8]}...` | - | - | ❌ 失败: {info['error']} |")
        else:
            total_records += info.get('record_count', 0)
            field_count = info.get('field_count', 0)
            status = "✅ 成功"
            table_id_short = info.get('table_id', '')[:8] + '...' if len(info.get('table_id', '')) > 8 else info.get('table_id', '')
            summary_lines.append(f"| {i} | {info.get('table_name', '未知')} | `{table_id_short}` | {info.get('record_count', 0)} | {field_count} | {status} |")
    
    summary_lines.append("")
    summary_lines.append(f"**总记录数**: {total_records}")
    summary_lines.append("")
    summary_lines.append("## 文件位置")
    summary_lines.append("")
    summary_lines.append(f"- **缓存文件**: `{cache_dir}`")
    summary_lines.append(f"- **导出文件**: `{tables_dir}`")
    summary_lines.append("")
    summary_lines.append("## 缓存文件说明")
    summary_lines.append("")
    summary_lines.append("缓存文件为JSON格式，包含完整的表格结构和记录数据，可用于后续处理。")
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

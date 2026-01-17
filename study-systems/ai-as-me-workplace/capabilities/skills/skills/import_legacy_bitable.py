# -*- coding: utf-8 -*-
"""
导入历史工作平台多维表格数据
从飞书多维表格读取所有数据表和记录，按照工作框架整理

使用方法：
python import_legacy_bitable.py
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


def parse_bitable_url(url: str) -> Optional[str]:
    """
    从多维表格URL中提取app_token
    
    Args:
        url: 多维表格URL，格式如：https://zyt.feishu.cn/base/YWDGbSZZKalcnQskTThcSUSXnub
    
    Returns:
        app_token或None
    """
    # 支持多种URL格式
    if '/base/' in url:
        # 格式：https://zyt.feishu.cn/base/{app_token}
        parts = url.split('/base/')
        if len(parts) > 1:
            app_token = parts[1].split('/')[0].split('?')[0]
            return app_token
    elif '/app/' in url:
        # 格式：https://bitable.feishu.cn/app/{app_token}/table/{table_id}
        parts = url.split('/app/')
        if len(parts) > 1:
            app_token = parts[1].split('/')[0]
            return app_token
    
    return None


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


def export_table_to_markdown(
    collaborator,
    app_token: str,
    table: Dict,
    output_dir: Path
) -> Dict[str, Any]:
    """
    导出数据表为Markdown格式
    
    Returns:
        包含导出信息的字典
    """
    table_id = table.get('table_id', '')
    table_name = table.get('name', '未知表')
    
    print(f"  处理数据表: {table_name} (ID: {table_id})")
    
    # 获取表格结构
    structure = collaborator.get_table_structure(app_token, table_id)
    fields = structure.get('fields', [])
    field_map = {f.get('field_id'): f for f in fields}
    
    # 获取所有记录
    records = collaborator.get_all_records(app_token, table_id)
    
    # 生成Markdown内容
    lines = []
    lines.append(f"# {table_name}")
    lines.append("")
    lines.append(f"**数据表ID**: `{table_id}`")
    lines.append(f"**记录数量**: {len(records)}")
    lines.append(f"**导出时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")
    
    if not records:
        lines.append("数据表为空")
        content = '\n'.join(lines)
        
        # 保存文件
        safe_table_name = "".join(c for c in table_name if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_table_name = safe_table_name.replace(' ', '-')
        output_file = output_dir / f"{safe_table_name}.md"
        output_file.write_text(content, encoding='utf-8')
        
        return {
            'table_name': table_name,
            'table_id': table_id,
            'record_count': 0,
            'output_file': str(output_file)
        }
    
    # 表头
    field_names = [f.get('field_name', '') for f in fields]
    if field_names:
        lines.append("## 数据记录")
        lines.append("")
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
    
    return {
        'table_name': table_name,
        'table_id': table_id,
        'record_count': len(records),
        'field_count': len(fields),
        'output_file': str(output_file)
    }


def main():
    """主函数"""
    # 配置信息
    print("=" * 60)
    print("导入历史工作平台多维表格数据")
    print("=" * 60)
    print()
    
    # 从环境变量或配置文件获取凭证
    app_id = os.getenv('FEISHU_APP_ID')
    app_secret = os.getenv('FEISHU_APP_SECRET')
    
    # 如果没有环境变量，尝试从bitable_cache_manager导入
    if not app_id or not app_secret:
        try:
            from bitable_cache_manager import APP_ID, APP_SECRET
            app_id = app_id or APP_ID
            app_secret = app_secret or APP_SECRET
        except ImportError:
            pass
    
    # 如果还是没有，使用默认值（从其他脚本中看到的）
    if not app_id:
        app_id = "cli_a9c92ca516f99bd9"
    if not app_secret:
        app_secret = "zlOKnyZkSuSUSr0WlAl6qbh5Qw4eM6wC"
    
    print(f"使用应用ID: {app_id[:10]}...")
    
    # 多维表格URL
    bitable_url = "https://zyt.feishu.cn/base/YWDGbSZZKalcnQskTThcSUSXnub"
    print(f"\n多维表格URL: {bitable_url}")
    
    # 解析app_token
    app_token = parse_bitable_url(bitable_url)
    if not app_token:
        print("错误: 无法从URL中提取app_token")
        return
    
    print(f"提取的app_token: {app_token}")
    print()
    
    # 创建协作器
    print("正在初始化飞书API连接...")
    
    # 尝试获取user_access_token
    user_access_token = os.getenv('FEISHU_USER_ACCESS_TOKEN')
    if not user_access_token:
        try:
            from bitable_cache_manager import USER_ACCESS_TOKEN
            user_access_token = USER_ACCESS_TOKEN
        except ImportError:
            pass
    
    # 先尝试使用tenant_access_token（不需要用户授权）
    print("尝试使用tenant_access_token...")
    collaborator = create_bitable_collaborator(
        app_id=app_id,
        app_secret=app_secret
    )
    
    # 获取多维表格信息
    print("正在获取多维表格信息...")
    app_info = collaborator.get_app_info(app_token)
    app_name = "历史工作平台"
    
    if app_info:
        if 'code' in app_info:
            if app_info.get('code') == 0:
                app_data = app_info.get('data', {})
                app_name = app_data.get('app', {}).get('name', '未知')
                print(f"多维表格名称: {app_name}")
            else:
                error_msg = app_info.get('msg', '未知错误')
                print(f"获取表格信息失败: {error_msg}")
                if '99991677' in str(app_info):  # token过期
                    print("提示: token已过期，尝试使用tenant_access_token...")
        elif 'app' in app_info:
            app_name = app_info.get('app', {}).get('name', '未知')
            print(f"多维表格名称: {app_name}")
        else:
            print(f"多维表格名称: {app_name} (默认)")
    else:
        print(f"多维表格名称: {app_name} (默认)")
    
    print()
    
    # 列出所有数据表
    print("正在获取数据表列表...")
    tables = collaborator.list_tables(app_token)
    
    # 调试：查看API返回的原始结果
    if not tables:
        print("调试: 检查API返回结果...")
        from feishu_api_wrapper import FeishuAPI
        api = FeishuAPI("", "", app_id=app_id, app_secret=app_secret)
        raw_result = api.list_bitable_tables(app_token, use_user_token=False)
        print(f"原始返回结果: {json.dumps(raw_result, indent=2, ensure_ascii=False)[:500]}")
    
    # 如果使用tenant_access_token失败，尝试使用user_access_token
    if not tables and user_access_token:
        print("使用tenant_access_token未找到数据表，尝试使用user_access_token...")
        collaborator = create_bitable_collaborator(
            app_id=app_id,
            app_secret=app_secret,
            user_access_token=user_access_token
        )
        tables = collaborator.list_tables(app_token)
    
    if not tables:
        print("未找到数据表")
        print("提示: 可能需要重新获取user_access_token，或者检查应用权限配置")
        print("提示: 请确保应用具有 'bitable:app:readonly' 或 'bitable:app' 权限")
        return
    
    print(f"找到 {len(tables)} 个数据表")
    print()
    
    # 创建输出目录
    output_base_dir = Path(__file__).parent.parent.parent.parent / "work" / "legacy-platform"
    output_base_dir.mkdir(parents=True, exist_ok=True)
    
    # 创建数据表导出目录
    tables_dir = output_base_dir / "tables"
    tables_dir.mkdir(parents=True, exist_ok=True)
    
    # 导出每个数据表
    export_summary = []
    for i, table in enumerate(tables, 1):
        table_name = table.get('name', f'表{i}')
        print(f"[{i}/{len(tables)}] 导出数据表: {table_name}")
        
        try:
            export_info = export_table_to_markdown(
                collaborator,
                app_token,
                table,
                tables_dir
            )
            export_summary.append(export_info)
            print(f"  ✓ 成功导出 {export_info['record_count']} 条记录")
        except Exception as e:
            print(f"  ✗ 导出失败: {e}")
            export_summary.append({
                'table_name': table_name,
                'table_id': table.get('table_id', ''),
                'error': str(e)
            })
        print()
    
    # 生成总结报告
    print("正在生成总结报告...")
    summary_lines = []
    summary_lines.append("# 历史工作平台数据导入总结")
    summary_lines.append("")
    summary_lines.append(f"**导入时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    summary_lines.append(f"**多维表格名称**: {app_name}")
    summary_lines.append(f"**app_token**: `{app_token}`")
    summary_lines.append(f"**数据表总数**: {len(tables)}")
    summary_lines.append("")
    summary_lines.append("## 数据表导出情况")
    summary_lines.append("")
    summary_lines.append("| 序号 | 数据表名称 | 记录数 | 字段数 | 状态 |")
    summary_lines.append("|------|-----------|--------|--------|------|")
    
    total_records = 0
    for i, info in enumerate(export_summary, 1):
        if 'error' in info:
            summary_lines.append(f"| {i} | {info['table_name']} | - | - | ❌ 失败: {info['error']} |")
        else:
            total_records += info.get('record_count', 0)
            field_count = info.get('field_count', 0)
            status = "✅ 成功"
            summary_lines.append(f"| {i} | {info['table_name']} | {info.get('record_count', 0)} | {field_count} | {status} |")
    
    summary_lines.append("")
    summary_lines.append(f"**总记录数**: {total_records}")
    summary_lines.append("")
    summary_lines.append("## 导出文件位置")
    summary_lines.append("")
    summary_lines.append(f"所有数据表导出文件位于: `{tables_dir}`")
    summary_lines.append("")
    
    # 保存总结报告
    summary_file = output_base_dir / "import-summary.md"
    summary_file.write_text('\n'.join(summary_lines), encoding='utf-8')
    
    print("=" * 60)
    print("导入完成！")
    print(f"总结报告: {summary_file}")
    print(f"数据表文件: {tables_dir}")
    print(f"总记录数: {total_records}")
    print("=" * 60)


if __name__ == "__main__":
    main()

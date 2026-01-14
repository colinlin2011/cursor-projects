"""
飞书多维表格今日更新记录总结工具

参考文档：
- ~/.cursor/cursor-projects/tools/feishu interaction/reference/
- api_docs/工作项-16.md：获取工作项操作记录
- api_docs/工作项-1.md：获取工作项列表
- api_docs/视图与度量-2.md：获取视图下工作项列表
- quick_start_example.py：快速开始示例
"""

import requests
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union
from urllib.parse import urlparse, parse_qs
import re

# Reference文档位置（使用动态路径，自动适配C盘或D盘）
REFERENCE_PATH = os.path.join(os.path.expanduser("~"), ".cursor", "cursor-projects", "tools", "feishu interaction", "reference")
API_DOCS_PATH = os.path.join(REFERENCE_PATH, "api_docs")

# API基础URL
# 飞书项目API
PROJECT_BASE_URL = "https://project.feishu.cn"
# 飞书开放平台API
OPEN_BASE_URL = "https://open.feishu.cn"


def get_plugin_token(plugin_id: str, plugin_secret: str) -> Optional[str]:
    """
    获取飞书项目插件令牌
    
    参考文档：api_docs/调用流程-1.md 和 quick_start_example.py
    
    Args:
        plugin_id: 插件ID
        plugin_secret: 插件密钥
    
    Returns:
        str: plugin_token 或 None
    """
    url = f"{PROJECT_BASE_URL}/open_api/authen/plugin_token"
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    data = {
        "plugin_id": plugin_id,
        "plugin_secret": plugin_secret
    }
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        
        if response.status_code == 200:
            result = response.json()
            if result.get('error', {}).get('code', -1) == 0:
                return result.get('data', {}).get('token')
            else:
                print(f"获取plugin_token失败: {result}")
                return None
        else:
            print(f"请求失败，状态码: {response.status_code}, 响应: {response.text}")
            return None
    
    except requests.exceptions.RequestException as e:
        print(f"请求发生错误: {e}")
        return None


def parse_table_identifier(identifier: str) -> Dict[str, str]:
    """
    解析表格标识符（链接或ID）
    
    Args:
        identifier: 表格标识（链接或ID格式）
    
    Returns:
        dict: 包含project_key, view_id等信息
    """
    result = {}
    
    # 如果是链接
    if identifier.startswith("http"):
        parsed = urlparse(identifier)
        path_parts = parsed.path.strip('/').split('/')
        
        # 飞书项目视图链接格式：https://project.feishu.cn/{project_key}/fix_view/{view_id}
        # 或：https://project.feishu.cn/{project_key}/multiProjectView/{view_id}
        if 'fix_view' in path_parts or 'multiProjectView' in path_parts:
            idx = path_parts.index('fix_view') if 'fix_view' in path_parts else path_parts.index('multiProjectView')
            if idx > 0:
                result['project_key'] = path_parts[idx - 1]
                if idx + 1 < len(path_parts):
                    result['view_id'] = path_parts[idx + 1]
        # 飞书项目空间链接格式：https://project.feishu.cn/{project_key}/overview
        elif len(path_parts) >= 1:
            result['project_key'] = path_parts[0]
    
    # 如果是ID格式：project_key:view_id
    elif ':' in identifier:
        parts = identifier.split(':')
        if len(parts) >= 2:
            result['project_key'] = parts[0]
            result['view_id'] = parts[1]
        elif len(parts) == 1:
            result['project_key'] = parts[0]
    
    return result


def get_work_item_operation_records(
    project_key: str,
    work_item_ids: List[int],
    plugin_token: str,
    start_time: int = None,
    end_time: int = None
) -> Optional[Dict]:
    """
    获取工作项操作记录
    
    参考文档：api_docs/工作项-16.md
    
    Args:
        project_key: 空间ID
        work_item_ids: 工作项ID列表
        plugin_token: 插件令牌
        start_time: 开始时间（毫秒级时间戳）
        end_time: 结束时间（毫秒级时间戳）
    
    Returns:
        dict: 操作记录数据
    """
    url = f"{PROJECT_BASE_URL}/open_api/op_record/work_item/list"
    
    headers = {
        'X-PLUGIN-TOKEN': plugin_token,
        'Content-Type': 'application/json'
    }
    
    payload = {
        "project_key": project_key,
        "work_item_ids": work_item_ids
    }
    
    if start_time:
        payload["start"] = start_time
    if end_time:
        payload["end"] = end_time
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        
        if response.status_code == 200:
            result = response.json()
            if result.get('err_code', -1) == 0:
                return result.get('data', {})
            else:
                print(f"获取操作记录失败: {result}")
                return None
        else:
            print(f"请求失败，状态码: {response.status_code}, 响应: {response.text}")
            return None
    
    except requests.exceptions.RequestException as e:
        print(f"请求发生错误: {e}")
        return None


def get_view_work_items(
    project_key: str,
    view_id: str,
    plugin_token: str,
    user_key: str,
    page_size: int = 200
) -> Optional[List[Dict]]:
    """
    获取视图下工作项列表
    
    参考文档：api_docs/视图与度量-2.md
    
    Args:
        project_key: 空间ID
        view_id: 视图ID
        plugin_token: 插件令牌
        user_key: 用户密钥
        page_size: 每页数据条数
    
    Returns:
        list: 工作项列表
    """
    url = f"{PROJECT_BASE_URL}/open_api/{project_key}/fix_view/{view_id}"
    
    headers = {
        'X-PLUGIN-TOKEN': plugin_token,
        'X-USER-KEY': user_key,
        'Content-Type': 'application/json'
    }
    
    params = {
        'page_size': page_size,
        'page_num': 1
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('err_code', -1) == 0:
                data = result.get('data', {})
                return data.get('work_items', [])
            else:
                print(f"获取视图工作项失败: {result}")
                return None
        else:
            print(f"请求失败，状态码: {response.status_code}, 响应: {response.text}")
            return None
    
    except requests.exceptions.RequestException as e:
        print(f"请求发生错误: {e}")
        return None


def get_work_items_by_updated_time(
    project_key: str,
    work_item_type_keys: List[str],
    plugin_token: str,
    user_key: str,
    start_time: int = None,
    end_time: int = None,
    page_size: int = 200
) -> Optional[List[Dict]]:
    """
    按更新时间获取工作项列表
    
    参考文档：api_docs/工作项-1.md
    
    Args:
        project_key: 空间ID
        work_item_type_keys: 工作项类型列表
        plugin_token: 插件令牌
        user_key: 用户密钥
        start_time: 开始时间（毫秒级时间戳）
        end_time: 结束时间（毫秒级时间戳）
        page_size: 每页数据条数
    
    Returns:
        list: 工作项列表
    """
    url = f"{PROJECT_BASE_URL}/open_api/{project_key}/work_item/filter"
    
    headers = {
        'X-PLUGIN-TOKEN': plugin_token,
        'X-USER-KEY': user_key,
        'Content-Type': 'application/json'
    }
    
    payload = {
        "work_item_type_keys": work_item_type_keys,
        "page_size": page_size,
        "page_num": 1
    }
    
    if start_time and end_time:
        payload["updated_at"] = {
            "start": start_time,
            "end": end_time
        }
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        
        if response.status_code == 200:
            result = response.json()
            if result.get('err_code', -1) == 0:
                return result.get('data', [])
            else:
                print(f"获取工作项列表失败: {result}")
                return None
        else:
            print(f"请求失败，状态码: {response.status_code}, 响应: {response.text}")
            return None
    
    except requests.exceptions.RequestException as e:
        print(f"请求发生错误: {e}")
        return None


def format_operation_summary(operation_type: str, record_contents: List[Dict]) -> List[str]:
    """
    格式化操作摘要
    
    Args:
        operation_type: 操作类型
        record_contents: 记录内容
    
    Returns:
        list: 变更摘要列表
    """
    changes = []
    
    for content in record_contents:
        obj = content.get('object', {})
        obj_type = obj.get('object_type', '')
        obj_value = obj.get('object_value', '')
        
        old_values = content.get('old', [])
        new_values = content.get('new', [])
        add_values = content.get('add', [])
        delete_values = content.get('delete', [])
        
        if operation_type == 'modify':
            if old_values and new_values:
                changes.append(f"{obj_value}: {old_values} -> {new_values}")
            elif add_values:
                changes.append(f"{obj_value}: 新增 {add_values}")
            elif delete_values:
                changes.append(f"{obj_value}: 删除 {delete_values}")
        elif operation_type == 'create':
            changes.append(f"新建: {obj_value}")
        elif operation_type == 'delete':
            changes.append(f"删除: {obj_value}")
    
    return changes


def get_bitable_daily_summary(
    table_identifier: str,
    date: str = None,
    plugin_id: str = None,
    plugin_secret: str = None,
    project_key: str = None,
    user_key: str = None,
    work_item_type_keys: List[str] = None,
    app_id: str = None,
    app_secret: str = None
) -> Dict:
    """
    获取飞书多维表格（或飞书项目表格视图）今日更新记录总结
    
    重要：所有API调用参考reference文档
    - 飞书项目API：api_docs/工作项-16.md、工作项-1.md、视图与度量-2.md
    - 飞书开放平台API：api_docs/飞书开放平台-API概述.md、多维表格-获取记录列表.md
    
    Args:
        table_identifier: 表格标识（链接或ID）
        date: 日期（YYYY-MM-DD），默认今天
        # 飞书项目API凭证（用于项目视图）
        plugin_id: 插件ID
        plugin_secret: 插件密钥
        project_key: 空间ID（如果table_identifier是链接，会自动提取）
        user_key: 用户密钥
        work_item_type_keys: 工作项类型列表（可选）
        # 飞书开放平台API凭证（用于多维表格）
        app_id: 应用ID（飞书开放平台）
        app_secret: 应用密钥（飞书开放平台）
    
    Returns:
        dict: 更新记录总结
    """
    # 解析日期
    if date is None:
        target_date = datetime.now().date()
    else:
        target_date = datetime.strptime(date, "%Y-%m-%d").date()
    
    # 计算时间范围（毫秒级时间戳）
    start_time = int(datetime.combine(target_date, datetime.min.time()).timestamp() * 1000)
    end_time = int(datetime.combine(target_date, datetime.max.time()).timestamp() * 1000)
    
    # 解析表格标识
    parsed = parse_table_identifier(table_identifier)
    table_type = parsed.get('type', 'unknown')
    
    # 如果是多维表格
    if table_type == 'bitable':
        app_token = parsed.get('app_token')
        table_id = parsed.get('table_id')
        
        if not app_token or not table_id:
            return {
                "error": "无法识别app_token或table_id，请提供有效的多维表格链接",
                "parsed_info": parsed
            }
        
        if not app_id or not app_secret:
            return {
                "error": "多维表格需要app_id和app_secret（飞书开放平台应用凭证）",
                "suggestion": "请在飞书开放平台创建自建应用，获取app_id和app_secret"
            }
        
        # 获取access_token
        access_token = get_tenant_access_token(app_id, app_secret)
        if not access_token:
            return {
                "error": "获取access_token失败"
            }
        
        # 计算今日时间范围（秒级时间戳）
        today_start = int(datetime.combine(target_date, datetime.min.time()).timestamp())
        today_end = int(datetime.combine(target_date, datetime.max.time()).timestamp())
        
        # 获取所有记录（可能需要分页）
        all_records = []
        page_token = None
        
        while True:
            records_data = get_bitable_records(
                app_token,
                table_id,
                access_token,
                page_size=100,
                page_token=page_token
            )
            
            if not records_data:
                break
            
            records = records_data.get('records', [])
            all_records.extend(records)
            
            if not records_data.get('has_more', False):
                break
            
            page_token = records_data.get('page_token')
        
        # 筛选今日更新的记录
        today_updates = []
        for record in all_records:
            last_modified_time = record.get('last_modified_time', 0)
            if today_start <= last_modified_time <= today_end:
                today_updates.append(record)
        
        # 生成总结
        summary = {
            "total_updates": len(today_updates),
            "new_items": 0,
            "modified_items": len(today_updates),
            "deleted_items": 0
        }
        
        # 分析更新类型
        for record in today_updates:
            created_time = record.get('created_time', 0)
            if today_start <= created_time <= today_end:
                summary["new_items"] += 1
                summary["modified_items"] -= 1
        
        # 生成更新列表
        updates = []
        for record in today_updates:
            last_modified_time = record.get('last_modified_time', 0)
            last_modified_by = record.get('last_modified_by', {})
            fields = record.get('fields', {})
            
            update_time = datetime.fromtimestamp(last_modified_time)
            
            updates.append({
                "time": update_time.strftime("%Y-%m-%d %H:%M:%S"),
                "operator": last_modified_by.get('name', '未知'),
                "operation": "modify" if record.get('created_time', 0) < today_start else "create",
                "record_id": record.get('record_id'),
                "fields": fields
            })
        
        # 生成总结文本
        summary_text = f"{target_date.strftime('%Y-%m-%d')} 更新总结：\n"
        summary_text += f"- 总更新数：{summary['total_updates']}\n"
        summary_text += f"- 新建：{summary['new_items']}\n"
        summary_text += f"- 修改：{summary['modified_items']}\n\n"
        
        if updates:
            summary_text += "详细更新：\n"
            for update in updates[:10]:  # 只显示前10条
                summary_text += f"- [{update['time']}] {update['operation']} - 记录ID: {update['record_id']}\n"
                if update['fields']:
                    # 显示部分字段
                    field_items = list(update['fields'].items())[:3]
                    for field_name, field_value in field_items:
                        summary_text += f"  • {field_name}: {field_value}\n"
        
        return {
            "date": date or target_date.strftime("%Y-%m-%d"),
            "table_name": "多维表格",
            "table_type": "bitable",
            "app_token": app_token,
            "table_id": table_id,
            "summary": summary,
            "updates": updates,
            "summary_text": summary_text
        }
    
    # 如果是Wiki链接
    elif table_type == 'wiki':
        return {
            "error": "Wiki链接需要Wiki API，当前reference文档主要是项目API",
            "wiki_id": parsed.get('wiki_id'),
            "suggestion": "需要飞书开放平台的Wiki API文档来获取Wiki更新记录"
        }
    
    # 如果是飞书项目视图（原有逻辑）
    if not project_key and parsed.get('project_key'):
        project_key = parsed['project_key']
    view_id = parsed.get('view_id')
    
    if not project_key:
        return {
            "error": "无法识别project_key，请提供有效的表格链接或project_key",
            "parsed_info": parsed
        }
    
    if not plugin_id or not plugin_secret:
        return {
            "error": "缺少认证信息：plugin_id和plugin_secret"
        }
    
    if not user_key:
        return {
            "error": "缺少user_key"
        }
    
    # 获取plugin_token
    plugin_token = get_plugin_token(plugin_id, plugin_secret)
    if not plugin_token:
        return {
            "error": "获取plugin_token失败"
        }
    
    # 方案1：如果有view_id，获取视图下的工作项
    if view_id:
        work_items = get_view_work_items(project_key, view_id, plugin_token, user_key)
        if not work_items:
            return {
                "date": date or target_date.strftime("%Y-%m-%d"),
                "table_name": "未知",
                "table_type": "project_view",
                "summary": {
                    "total_updates": 0,
                    "new_items": 0,
                    "modified_items": 0,
                    "deleted_items": 0
                },
                "updates": [],
                "summary_text": f"{target_date.strftime('%Y-%m-%d')} 无更新记录"
            }
        
        work_item_ids = [item.get('work_item_id') for item in work_items if item.get('work_item_id')]
    else:
        # 方案2：如果没有view_id，需要work_item_type_keys来搜索
        if not work_item_type_keys:
            return {
                "error": "缺少work_item_type_keys，无法搜索工作项"
            }
        
        work_items = get_work_items_by_updated_time(
            project_key,
            work_item_type_keys,
            plugin_token,
            user_key,
            start_time,
            end_time
        )
        
        if not work_items:
            return {
                "date": date or target_date.strftime("%Y-%m-%d"),
                "table_name": "未知",
                "table_type": "project",
                "summary": {
                    "total_updates": 0,
                    "new_items": 0,
                    "modified_items": 0,
                    "deleted_items": 0
                },
                "updates": [],
                "summary_text": f"{target_date.strftime('%Y-%m-%d')} 无更新记录"
            }
        
        work_item_ids = [item.get('work_item_id') for item in work_items if item.get('work_item_id')]
    
    # 获取操作记录
    if not work_item_ids:
        return {
            "date": date or target_date.strftime("%Y-%m-%d"),
            "table_name": "未知",
            "table_type": "project_view" if view_id else "project",
            "summary": {
                "total_updates": 0,
                "new_items": 0,
                "modified_items": 0,
                "deleted_items": 0
            },
            "updates": [],
            "summary_text": f"{target_date.strftime('%Y-%m-%d')} 无更新记录"
        }
    
    # 分批获取操作记录（API限制最多50个work_item_ids）
    all_op_records = []
    for i in range(0, len(work_item_ids), 50):
        batch_ids = work_item_ids[i:i+50]
        op_records = get_work_item_operation_records(
            project_key,
            batch_ids,
            plugin_token,
            start_time,
            end_time
        )
        
        if op_records and op_records.get('op_records'):
            all_op_records.extend(op_records['op_records'])
    
    # 处理操作记录
    updates = []
    summary = {
        "total_updates": 0,
        "new_items": 0,
        "modified_items": 0,
        "deleted_items": 0
    }
    
    for record in all_op_records:
        operation_time = record.get('operation_time', 0)
        operation_type = record.get('operation_type', '')
        operator = record.get('operator', '')
        work_item_id = record.get('work_item_id', 0)
        record_contents = record.get('record_contents', [])
        
        # 转换为可读时间
        op_time = datetime.fromtimestamp(operation_time / 1000)
        
        # 格式化变更内容
        changes = format_operation_summary(operation_type, record_contents)
        
        # 查找工作项名称
        work_item_name = "未知"
        for item in work_items:
            if item.get('work_item_id') == work_item_id:
                work_item_name = item.get('name', '未知')
                break
        
        update_info = {
            "time": op_time.strftime("%Y-%m-%d %H:%M:%S"),
            "operator": operator,
            "operation": operation_type,
            "item_id": work_item_id,
            "item_name": work_item_name,
            "changes": changes
        }
        
        updates.append(update_info)
        
        # 统计
        summary["total_updates"] += 1
        if operation_type == "create":
            summary["new_items"] += 1
        elif operation_type == "modify":
            summary["modified_items"] += 1
        elif operation_type == "delete":
            summary["deleted_items"] += 1
    
    # 生成总结文本
    summary_text = f"{target_date.strftime('%Y-%m-%d')} 更新总结：\n"
    summary_text += f"- 总更新数：{summary['total_updates']}\n"
    summary_text += f"- 新建：{summary['new_items']}\n"
    summary_text += f"- 修改：{summary['modified_items']}\n"
    summary_text += f"- 删除：{summary['deleted_items']}\n\n"
    
    if updates:
        summary_text += "详细更新：\n"
        for update in updates[:10]:  # 只显示前10条
            summary_text += f"- [{update['time']}] {update['operation']} - {update['item_name']}\n"
            if update['changes']:
                for change in update['changes'][:3]:  # 每条最多显示3个变更
                    summary_text += f"  • {change}\n"
    
    return {
        "date": date or target_date.strftime("%Y-%m-%d"),
        "table_name": "表格视图" if view_id else "工作项列表",
        "table_type": "project_view" if view_id else "project",
        "summary": summary,
        "updates": updates,
        "summary_text": summary_text
    }


if __name__ == "__main__":
    # 示例1：多维表格
    result = get_bitable_daily_summary(
        table_identifier="https://bitable.feishu.cn/app/xxxxxxxxxx/table/xxxxxxxxxx",
        app_id="your_app_id",
        app_secret="your_app_secret"
    )
    
    # 示例2：项目视图
    # result = get_bitable_daily_summary(
    #     table_identifier="https://project.feishu.cn/your_project_key/fix_view/your_view_id",
    #     plugin_id="your_plugin_id",
    #     plugin_secret="your_plugin_secret",
    #     user_key="your_user_key"
    # )
    
    print(result.get("summary_text", ""))

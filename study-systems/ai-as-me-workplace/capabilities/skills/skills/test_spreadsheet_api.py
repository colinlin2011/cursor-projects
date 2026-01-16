# -*- coding: utf-8 -*-
"""
测试在线表格API
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from feishu_api_wrapper import FeishuAPI
from feishu_spreadsheet_collaborator import create_spreadsheet_collaborator

# 配置信息
APP_ID = "cli_a9c92ca516f99bd9"
APP_SECRET = "zlOKnyZkSuSUSr0WlAl6qbh5Qw4eM6wC"
USER_ACCESS_TOKEN = os.getenv("FEISHU_USER_ACCESS_TOKEN", "u-fjEA3Zj5J4eGr.QY6KVnXg14hgJ04kgVOOwaFMy024ps")
SPACE_ID = "7353073903872868356"
NODE_TOKEN = "TDlnwRfpBikbUIk5guDcRyN5neh"

# 修复Windows控制台编码问题
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

def main():
    # 创建API
    api = FeishuAPI(
        plugin_id="",
        plugin_secret="",
        app_id=APP_ID,
        app_secret=APP_SECRET
    )
    api.set_user_access_token(USER_ACCESS_TOKEN)
    
    # 获取spreadsheet_token
    print("步骤1：获取spreadsheet_token...")
    result = api.get_wiki_node(SPACE_ID, NODE_TOKEN, use_user_token=True)
    
    if result:
        node = result.get('node', result) if 'node' in result else result
        obj_type = node.get('obj_type', '')
        obj_token = node.get('obj_token', '')
        
        print(f"  节点类型: {obj_type}")
        print(f"  对象Token: {obj_token}")
        
        if obj_type in ['sheet', 'spreadsheet']:
            spreadsheet_token = obj_token
            print(f"[OK] spreadsheet_token: {spreadsheet_token}")
        else:
            print(f"[X] 节点类型不是sheet，而是: {obj_type}")
            return
    else:
        print("[X] 无法获取节点信息")
        return
    
    print()
    
    # 创建协作器
    collaborator = create_spreadsheet_collaborator(
        app_id=APP_ID,
        app_secret=APP_SECRET,
        user_access_token=USER_ACCESS_TOKEN
    )
    
    # 获取工作表列表
    print("步骤2：获取工作表列表...")
    sheets = collaborator.get_sheet_list(spreadsheet_token, use_user_token=True)
    
    if sheets:
        print(f"[OK] 找到 {len(sheets)} 个工作表:")
        for sheet in sheets:
            print(f"  - {sheet.get('title', '')} (ID: {sheet.get('sheet_id', '')})")
    else:
        print("[!] 未找到工作表")
        # 尝试直接获取表格信息
        print()
        print("尝试直接获取表格信息...")
        info = collaborator.get_spreadsheet_info(spreadsheet_token, use_user_token=True)
        print(f"返回结果: {info}")
    
    print()
    
    # 如果有工作表，获取第一个工作表的数据
    if sheets and len(sheets) > 0:
        first_sheet = sheets[0]
        sheet_id = first_sheet.get('sheet_id') or first_sheet.get('title', '')
        sheet_title = first_sheet.get('title', '')
        
        print(f"步骤3：获取工作表 '{sheet_title}' 的数据...")
        print(f"  使用sheet_id: {sheet_id}")
        sheet_data = collaborator.get_sheet_data(spreadsheet_token, sheet_id, use_user_token=True)
        
        if sheet_data:
            print(f"[OK] 获取数据成功")
            if 'code' in sheet_data:
                print(f"  Code: {sheet_data.get('code')}")
                print(f"  Msg: {sheet_data.get('msg')}")
            if 'data' in sheet_data:
                values = sheet_data.get('data', {}).get('values', [])
                print(f"  数据行数: {len(values)}")
                if values:
                    print(f"  第一行（表头）: {values[0]}")
                    print(f"  数据示例（前3行）:")
                    for i, row in enumerate(values[:3], 1):
                        print(f"    行{i}: {row}")
        else:
            print("[X] 获取数据失败")

if __name__ == "__main__":
    main()

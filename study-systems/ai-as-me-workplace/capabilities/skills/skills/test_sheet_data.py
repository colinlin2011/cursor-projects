# -*- coding: utf-8 -*-
"""
测试获取工作表数据
"""

import sys
import os
import json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from feishu_api_wrapper import FeishuAPI
from feishu_spreadsheet_collaborator import create_spreadsheet_collaborator

# 配置信息
APP_ID = "cli_a9c92ca516f99bd9"
APP_SECRET = "zlOKnyZkSuSUSr0WlAl6qbh5Qw4eM6wC"
USER_ACCESS_TOKEN = os.getenv("FEISHU_USER_ACCESS_TOKEN", "u-fjEA3Zj5J4eGr.QY6KVnXg14hgJ04kgVOOwaFMy024ps")
SPREADSHEET_TOKEN = "NI2ksibZHhzVoBtg65Fc3Jdznnf"
SHEET_ID = "0EhXbl"  # Revision&Maturity&Ref.

# 修复Windows控制台编码问题
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

def main():
    api = FeishuAPI(
        plugin_id="",
        plugin_secret="",
        app_id=APP_ID,
        app_secret=APP_SECRET
    )
    api.set_user_access_token(USER_ACCESS_TOKEN)
    
    # 直接调用API获取数据
    print("测试获取工作表数据...")
    print(f"Spreadsheet Token: {SPREADSHEET_TOKEN}")
    print(f"Sheet ID: {SHEET_ID}")
    print()
    
    # 方法1: 使用values API
    endpoint1 = f"open-apis/sheets/v2/spreadsheets/{SPREADSHEET_TOKEN}/values/{SHEET_ID}"
    print("方法1: 使用values API（不指定范围）")
    result1 = api._open_platform_request('GET', endpoint1, use_user_token=True)
    print(f"返回结果: {json.dumps(result1, ensure_ascii=False, indent=2) if result1 else 'None'}")
    print()
    
    # 方法2: 指定范围
    endpoint2 = f"open-apis/sheets/v2/spreadsheets/{SPREADSHEET_TOKEN}/values/{SHEET_ID}!A1:Z100"
    print("方法2: 使用values API（指定范围A1:Z100）")
    result2 = api._open_platform_request('GET', endpoint2, use_user_token=True)
    print(f"返回结果: {json.dumps(result2, ensure_ascii=False, indent=2) if result2 else 'None'}")
    print()
    
    # 方法3: 使用协作器
    collaborator = create_spreadsheet_collaborator(
        app_id=APP_ID,
        app_secret=APP_SECRET,
        user_access_token=USER_ACCESS_TOKEN
    )
    print("方法3: 使用协作器")
    result3 = collaborator.get_sheet_data(SPREADSHEET_TOKEN, SHEET_ID, use_user_token=True)
    print(f"返回结果: {json.dumps(result3, ensure_ascii=False, indent=2) if result3 else 'None'}")

if __name__ == "__main__":
    main()

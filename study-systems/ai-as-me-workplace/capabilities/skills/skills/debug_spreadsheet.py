# -*- coding: utf-8 -*-
"""
调试在线表格API返回结构
"""

import sys
import os
import json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from feishu_api_wrapper import FeishuAPI

# 配置信息
APP_ID = "cli_a9c92ca516f99bd9"
APP_SECRET = "zlOKnyZkSuSUSr0WlAl6qbh5Qw4eM6wC"
USER_ACCESS_TOKEN = os.getenv("FEISHU_USER_ACCESS_TOKEN", "u-fjEA3Zj5J4eGr.QY6KVnXg14hgJ04kgVOOwaFMy024ps")
SPREADSHEET_TOKEN = "NI2ksibZHhzVoBtg65Fc3Jdznnf"

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
    
    # 获取metainfo
    print("获取metainfo...")
    endpoint = f"open-apis/sheets/v2/spreadsheets/{SPREADSHEET_TOKEN}/metainfo"
    result = api._open_platform_request('GET', endpoint, use_user_token=True)
    
    print("=" * 80)
    print("Metainfo返回结果:")
    print("=" * 80)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    if result:
        if 'code' in result and result.get('code') == 0:
            data = result.get('data', {})
            sheets = data.get('sheets', [])
            print()
            print("=" * 80)
            print("工作表列表:")
            print("=" * 80)
            for i, sheet in enumerate(sheets, 1):
                print(f"\n工作表 {i}:")
                print(json.dumps(sheet, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()

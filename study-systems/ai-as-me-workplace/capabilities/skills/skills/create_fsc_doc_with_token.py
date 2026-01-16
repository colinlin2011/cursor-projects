# -*- coding: utf-8 -*-
"""
创建舱驾一体域控FSC文档 - 使用user_access_token版本

使用方法：
1. 在脚本中设置 USER_ACCESS_TOKEN 变量
2. 运行脚本：python create_fsc_doc_with_token.py
"""

import sys
import os

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from feishu_api_wrapper import FeishuAPI

# 用户提供的配置信息
APP_ID = "cli_a9c92ca516f99bd9"
APP_SECRET = "zlOKnyZkSuSUSr0WlAl6qbh5Qw4eM6wC"
SPACE_ID = "7353073903872868356"
PARENT_NODE_TOKEN = "V7FXwKKdLiEus3kU9oMcgLwGnpe"
DOC_TITLE = "舱驾一体域控的FSC文档"

# ============================================
# 请在这里设置你的user_access_token
# ============================================
USER_ACCESS_TOKEN = "u-4hjBvG1yl1wpIhqjDPtjcvl4gA75gkOXX20GnRQ00Elr"  # 请在这里填入你获取的user_access_token
# 或者从环境变量读取
if not USER_ACCESS_TOKEN:
    USER_ACCESS_TOKEN = os.getenv("FEISHU_USER_ACCESS_TOKEN", "")

def main():
    print("=" * 60)
    print("创建舱驾一体域控FSC文档")
    print("=" * 60)
    print()
    
    if not USER_ACCESS_TOKEN:
        print("[X] 错误：未设置USER_ACCESS_TOKEN")
        print()
        print("请选择以下方式之一：")
        print("1. 在脚本中设置 USER_ACCESS_TOKEN 变量（第24行）")
        print("2. 设置环境变量：")
        print('   $env:FEISHU_USER_ACCESS_TOKEN="your_token"')
        print()
        return
    
    # 初始化API客户端
    api = FeishuAPI(
        plugin_id="",  # Wiki不需要项目API
        plugin_secret="",
        app_id=APP_ID,
        app_secret=APP_SECRET
    )
    
    # 设置用户身份凭证
    api.set_user_access_token(USER_ACCESS_TOKEN)
    print("使用用户身份凭证创建文档")
    print()
    
    print(f"正在创建文档: {DOC_TITLE}")
    print(f"知识库ID: {SPACE_ID}")
    if PARENT_NODE_TOKEN:
        print(f"父节点token: {PARENT_NODE_TOKEN}")
    else:
        print("父节点token: 未指定（将在知识库根目录创建）")
    print()
    
    # 创建Wiki文档
    # 如果指定了parent_node_token但权限不足，尝试在根目录创建
    doc = None
    if PARENT_NODE_TOKEN:
        print("尝试在指定目录创建文档...")
        doc = api.create_wiki_doc(
            space_id=SPACE_ID,
            parent_node_token=PARENT_NODE_TOKEN,
            title=DOC_TITLE,
            use_user_token=True
        )
        if not doc:
            print("在指定目录创建失败，尝试在知识库根目录创建...")
            doc = api.create_wiki_doc(
                space_id=SPACE_ID,
                parent_node_token=None,
                title=DOC_TITLE,
                use_user_token=True
            )
    else:
        doc = api.create_wiki_doc(
            space_id=SPACE_ID,
            parent_node_token=None,
            title=DOC_TITLE,
            use_user_token=True
        )
    
    if doc:
        # Wiki v2 API返回的节点信息
        node = doc.get('node', {})
        node_token = node.get('node_token') or doc.get('node_token')
        doc_name = node.get('title') or doc.get('title') or DOC_TITLE
        
        print()
        print("=" * 60)
        print("[OK] 文档创建成功！")
        print("=" * 60)
        print()
        print(f"文档名称: {doc_name}")
        print(f"节点token: {node_token}")
        
        # 生成文档链接
        if node_token:
            doc_url = f"https://bytedance.larkoffice.com/wiki/{SPACE_ID}/{node_token}"
            print(f"文档链接: {doc_url}")
        else:
            doc_url = "无法生成链接"
        
        print()
        print("=" * 60)
        print("文档创建完成！")
        print("=" * 60)
        print(f"文档链接: {doc_url}")
        print()
        print("提示：")
        print("1. 文档已创建，可以在飞书中打开查看")
        print("2. 可以在文档中添加FSC相关内容")
        print("3. 建议添加以下章节：")
        print("   - 项目概述")
        print("   - 系统边界")
        print("   - 安全目标")
        print("   - 功能安全概念")
        print("   - 安全机制")
        print("   - 安全需求")
        
        return {
            "success": True,
            "node_token": node_token,
            "doc_name": doc_name,
            "doc_url": doc_url,
            "doc_info": doc
        }
    else:
        print()
        print("=" * 60)
        print("[X] 文档创建失败")
        print("=" * 60)
        print()
        print("常见错误及解决方法：")
        print()
        print("1. 权限错误（错误码99991672或99991679）：")
        print("   错误码99991679表示：用户身份凭证缺少用户授权的权限")
        print("   解决方法：重新获取user_access_token，确保在授权时勾选以下权限：")
        print("   - wiki:wiki")
        print("   - wiki:node:create")
        print()
        print("   重新授权步骤：")
        print("   a) 访问授权URL（确保包含所需权限）：")
        print(f"      https://open.feishu.cn/open-apis/authen/v1/authorize?app_id={APP_ID}&redirect_uri=YOUR_REDIRECT_URI&response_type=code&scope=wiki:wiki wiki:node:create")
        print("   b) 在授权页面，确保勾选了wiki相关权限")
        print("   c) 完成授权后，重新获取user_access_token")
        print()
        print("   或者使用应用权限授权（错误码99991672）：")
        print("   授权链接：")
        print(f"   https://open.feishu.cn/app/{APP_ID}/auth?q=wiki:wiki,wiki:node:create")
        print()
        print("2. 节点权限错误（错误码131006）：")
        print("   即使使用用户身份凭证，也可能需要：")
        print("   - 确保你的用户账号对知识库有编辑权限")
        print("   - 确保你的用户账号对目标目录有编辑权限")
        print("   - 检查user_access_token是否有效（可能已过期）")
        print()
        print("3. 其他排查建议：")
        print("   - 检查app_id和app_secret是否正确")
        print("   - 检查应用是否有云文档和知识库权限")
        print("   - 检查space_id是否正确")
        print("   - 检查parent_node_token是否正确（如果指定了）")
        print("   - 检查user_access_token是否有效")
        
        return {
            "success": False,
            "error": "API调用返回None"
        }

if __name__ == "__main__":
    main()

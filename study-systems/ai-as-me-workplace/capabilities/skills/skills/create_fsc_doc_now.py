# -*- coding: utf-8 -*-
"""
创建舱驾一体域控FSC文档 - 直接执行版本
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
# 用户身份凭证（可选，如果提供则使用用户身份创建文档）
USER_ACCESS_TOKEN = os.getenv("FEISHU_USER_ACCESS_TOKEN", "")

def main():
    print("=" * 60)
    print("创建舱驾一体域控FSC文档")
    print("=" * 60)
    print()
    
    # 初始化API客户端
    api = FeishuAPI(
        plugin_id="",  # Wiki不需要项目API
        plugin_secret="",
        app_id=APP_ID,
        app_secret=APP_SECRET
    )
    
    # 如果提供了用户身份凭证，使用用户身份
    use_user_token = False
    if USER_ACCESS_TOKEN:
        api.set_user_access_token(USER_ACCESS_TOKEN)
        use_user_token = True
        print("使用用户身份凭证创建文档")
    else:
        print("未检测到环境变量 FEISHU_USER_ACCESS_TOKEN")
        print("提示：如果已获取user_access_token，请设置环境变量：")
        print('   $env:FEISHU_USER_ACCESS_TOKEN="your_token"')
        print()
        token_input = input("或者直接输入user_access_token（直接回车跳过）: ").strip()
        if token_input:
            api.set_user_access_token(token_input)
            use_user_token = True
            print("使用用户身份凭证创建文档")
        else:
            print("使用应用身份凭证创建文档（可能需要Wiki成员权限）")
            print("提示：如果遇到权限错误，建议使用用户身份凭证（user_access_token）")
    
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
            use_user_token=use_user_token
        )
        if not doc:
            print("在指定目录创建失败，尝试在知识库根目录创建...")
            doc = api.create_wiki_doc(
                space_id=SPACE_ID,
                parent_node_token=None,
                title=DOC_TITLE,
                use_user_token=use_user_token
            )
    else:
        doc = api.create_wiki_doc(
            space_id=SPACE_ID,
            parent_node_token=None,
            title=DOC_TITLE,
            use_user_token=use_user_token
        )
    
    if doc:
        # Wiki v2 API返回的节点信息
        node = doc.get('node', {})
        node_token = node.get('node_token') or doc.get('node_token')
        doc_name = node.get('title') or doc.get('title') or DOC_TITLE
        
        print("[OK] 文档创建成功！")
        print(f"节点token: {node_token}")
        print(f"文档名称: {doc_name}")
        
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
        print("[X] 文档创建失败")
        print()
        print("常见错误及解决方法：")
        print()
        print("1. 权限错误（错误码99991672）：")
        print("   需要在飞书开放平台应用管理页面授权以下权限：")
        print("   - wiki:wiki")
        print("   - wiki:node:create")
        print("   授权链接：")
        print(f"   https://open.feishu.cn/app/{APP_ID}/auth?q=wiki:wiki,wiki:node:create")
        print()
        print("2. 节点权限错误（错误码131006）：")
        print("   应用对指定的节点没有编辑权限。解决方法：")
        print("   【推荐】使用用户身份凭证（user_access_token）：")
        print("   a) 获取你的user_access_token（参考get_user_token_guide.md）")
        print("   b) 设置环境变量：$env:FEISHU_USER_ACCESS_TOKEN='your_token'")
        print("   c) 重新运行脚本")
        print("   或者：")
        print("   a) 在飞书Wiki中，进入目标目录")
        print("   b) 点击目录右上角的'...'菜单")
        print("   c) 选择'权限设置'或'分享设置'")
        print("   d) 添加应用为'编辑者'或'管理员'（注意：Wiki成员管理只支持真实用户）")
        print("   或者：")
        print("   - 尝试不指定parent_node_token，在知识库根目录创建文档")
        print("   - 检查parent_node_token是否正确")
        print()
        print("3. 其他排查建议：")
        print("   - 检查app_id和app_secret是否正确")
        print("   - 检查应用是否有云文档和知识库权限")
        print("   - 检查space_id是否正确")
        print("   - 检查parent_node_token是否正确（如果指定了）")
        
        return {
            "success": False,
            "error": "API调用返回None"
        }

if __name__ == "__main__":
    main()

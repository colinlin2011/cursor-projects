# -*- coding: utf-8 -*-
"""
创建舱驾一体域控FSC文档脚本

功能：在飞书云文档指定目录创建"舱驾一体域控的FSC文档"

使用方法：
1. 配置认证信息（app_id, app_secret）
2. 配置知识库信息（space_id, parent_node_token）
3. 运行脚本创建文档
"""

import sys
import os
from datetime import datetime

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from feishu_api_wrapper import FeishuAPI


def create_fsc_document(
    app_id: str,
    app_secret: str,
    space_id: str,
    parent_node_token: str = None,
    doc_title: str = "舱驾一体域控的FSC文档"
) -> dict:
    """
    创建FSC文档
    
    Args:
        app_id: 飞书开放平台应用ID
        app_secret: 飞书开放平台应用密钥
        space_id: 知识库ID（Wiki space_id）
        parent_node_token: 父节点token（指定目录，可选）
        doc_title: 文档标题
        
    Returns:
        创建结果字典
    """
    # 初始化API客户端
    api = FeishuAPI(
        plugin_id="",  # Wiki不需要项目API
        plugin_secret="",
        app_id=app_id,
        app_secret=app_secret
    )
    
    print(f"正在创建文档: {doc_title}")
    print(f"知识库ID: {space_id}")
    if parent_node_token:
        print(f"父节点token: {parent_node_token}")
    
    # 创建Wiki文档
    # 注意：根据飞书开放平台API，Wiki文档创建需要使用wiki v2 API
    # 这里先尝试使用drive API创建文档，如果失败则使用wiki API
    
    # 方法1：使用drive API创建文档（如果文档在云盘中）
    if not parent_node_token:
        # 如果没有指定父节点，在根目录创建
        doc = api.create_wiki_doc(
            space_id=space_id,
            title=doc_title
        )
    else:
        # 如果指定了父节点，在指定目录创建
        doc = api.create_wiki_doc(
            space_id=space_id,
            parent_node_token=parent_node_token,
            title=doc_title
        )
    
    if doc:
        file_token = doc.get('token') or doc.get('file_token')
        print(f"✅ 文档创建成功！")
        print(f"文档token: {file_token}")
        print(f"文档名称: {doc.get('name', doc_title)}")
        
        # 生成文档链接（需要根据实际域名调整）
        doc_url = f"https://bytedance.larkoffice.com/docx/{file_token}" if file_token else "无法生成链接"
        print(f"文档链接: {doc_url}")
        
        return {
            "success": True,
            "file_token": file_token,
            "doc_name": doc.get('name', doc_title),
            "doc_url": doc_url,
            "doc_info": doc
        }
    else:
        print("❌ 文档创建失败")
        return {
            "success": False,
            "error": "API调用返回None"
        }


def main():
    """
    主函数
    """
    print("=" * 60)
    print("创建舱驾一体域控FSC文档")
    print("=" * 60)
    print()
    
    # 从环境变量或配置文件读取认证信息
    # 建议使用配置文件或环境变量，不要硬编码
    app_id = os.getenv("FEISHU_APP_ID", "")
    app_secret = os.getenv("FEISHU_APP_SECRET", "")
    space_id = os.getenv("FEISHU_SPACE_ID", "")
    parent_node_token = os.getenv("FEISHU_PARENT_NODE_TOKEN", "")
    
    # 如果环境变量未设置，提示用户输入
    if not app_id:
        app_id = input("请输入飞书开放平台应用ID (app_id): ").strip()
    if not app_secret:
        app_secret = input("请输入飞书开放平台应用密钥 (app_secret): ").strip()
    if not space_id:
        space_id = input("请输入知识库ID (space_id): ").strip()
    
    parent_node_token_input = input("请输入父节点token (parent_node_token，可选，直接回车跳过): ").strip()
    if parent_node_token_input:
        parent_node_token = parent_node_token_input
    
    # 验证必要参数
    if not app_id or not app_secret or not space_id:
        print("❌ 错误：缺少必要参数（app_id, app_secret, space_id）")
        return
    
    # 创建文档
    result = create_fsc_document(
        app_id=app_id,
        app_secret=app_secret,
        space_id=space_id,
        parent_node_token=parent_node_token if parent_node_token else None
    )
    
    if result["success"]:
        print()
        print("=" * 60)
        print("文档创建完成！")
        print("=" * 60)
        print(f"文档链接: {result.get('doc_url', 'N/A')}")
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
    else:
        print()
        print("=" * 60)
        print("文档创建失败")
        print("=" * 60)
        print(f"错误信息: {result.get('error', '未知错误')}")
        print()
        print("排查建议：")
        print("1. 检查app_id和app_secret是否正确")
        print("2. 检查应用是否有云文档权限")
        print("3. 检查space_id是否正确")
        print("4. 检查parent_node_token是否正确（如果指定了）")


if __name__ == "__main__":
    main()

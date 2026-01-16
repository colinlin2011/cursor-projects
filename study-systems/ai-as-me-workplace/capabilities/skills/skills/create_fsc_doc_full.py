# -*- coding: utf-8 -*-
"""
创建舱驾一体域控FSC文档 - 完整版本（包含内容结构）

使用完整的文档协作能力创建FSC文档并添加初始内容结构
"""

import sys
import os
from typing import Optional, Dict

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
USER_ACCESS_TOKEN = "u-4tBMNLQZ15Oqb0cGVm.7W.k1n31w4koprGGymw282HUW"  # 请在这里填入你获取的user_access_token
# 或者从环境变量读取
if not USER_ACCESS_TOKEN:
    USER_ACCESS_TOKEN = os.getenv("FEISHU_USER_ACCESS_TOKEN", "")

# FSC文档章节结构
FSC_SECTIONS = [
    {
        "title": "1. 项目概述",
        "type": 3,  # 标题1
        "content": [
            "本项目旨在开发舱驾一体域控制器，实现座舱与驾驶功能的深度融合。",
            "文档将详细描述系统的功能安全概念（FSC），包括系统边界、安全目标、安全机制和安全需求。"
        ]
    },
    {
        "title": "2. 系统边界",
        "type": 3,  # 标题1
        "content": [
            "系统边界定义了舱驾一体域控制器的功能范围和安全责任边界。",
            "包括：",
            "- 座舱域功能：信息娱乐、人机交互、舒适性控制",
            "- 驾驶域功能：辅助驾驶、自动驾驶、车辆控制",
            "- 域间通信：座舱与驾驶域的数据交互接口",
            "- 外部接口：与车辆其他系统的通信接口"
        ]
    },
    {
        "title": "3. 安全目标",
        "type": 3,  # 标题1
        "content": [
            "基于ISO 26262标准，定义系统的安全目标：",
            "- SG-1: 防止座舱域功能异常影响驾驶域安全",
            "- SG-2: 确保驾驶域关键功能的可用性和可靠性",
            "- SG-3: 防止域间通信的数据错误和延迟",
            "- SG-4: 确保系统在故障情况下的安全状态"
        ]
    },
    {
        "title": "4. 功能安全概念",
        "type": 3,  # 标题1
        "content": [
            "功能安全概念描述了如何通过系统设计实现安全目标：",
            "- 域隔离：座舱域与驾驶域的物理和逻辑隔离",
            "- 安全监控：实时监控系统状态和异常",
            "- 故障处理：定义故障检测、诊断和恢复机制",
            "- 降级策略：在故障情况下的功能降级方案"
        ]
    },
    {
        "title": "5. 安全机制",
        "type": 3,  # 标题1
        "content": [
            "为实现安全目标，系统采用以下安全机制：",
            "- 硬件安全机制：冗余设计、看门狗、电源监控",
            "- 软件安全机制：运行时监控、数据校验、状态机保护",
            "- 通信安全机制：CRC校验、超时检测、序列号检查",
            "- 诊断机制：自检、周期性测试、故障记录"
        ]
    },
    {
        "title": "6. 安全需求",
        "type": 3,  # 标题1
        "content": [
            "基于安全目标和安全概念，导出系统级安全需求：",
            "- SR-1: 系统应实现座舱域与驾驶域的物理隔离",
            "- SR-2: 系统应监控关键功能的执行状态",
            "- SR-3: 系统应在检测到故障时进入安全状态",
            "- SR-4: 系统应记录所有安全相关事件",
            "- SR-5: 系统应支持故障诊断和恢复"
        ]
    }
]

def create_text_block(content: str) -> dict:
    """创建文本块"""
    return {
        "block_type": 2,  # 文本块
        "text": {
            "elements": [
                {
                    "text_run": {
                        "content": content
                    }
                }
            ]
        }
    }

def create_heading_block(title: str, level: int = 3) -> dict:
    """创建标题块
    
    Args:
        title: 标题内容
        level: 标题级别（3=标题1, 4=标题2, 5=标题3）
    """
    # 根据block_type确定对应的字段名
    heading_fields = {
        3: "heading1",
        4: "heading2", 
        5: "heading3",
        6: "heading4",
        7: "heading5",
        8: "heading6",
        9: "heading7",
        10: "heading8",
        11: "heading9"
    }
    
    field_name = heading_fields.get(level, "heading1")
    
    return {
        "block_type": level,
        field_name: {
            "elements": [
                {
                    "text_run": {
                        "content": title
                    }
                }
            ]
        }
    }

def create_bullet_block(content: str) -> dict:
    """创建无序列表块"""
    return {
        "block_type": 12,  # 无序列表
        "bullet": {
            "elements": [
                {
                    "text_run": {
                        "content": content
                    }
                }
            ]
        }
    }

def find_existing_doc(
    api: FeishuAPI,
    space_id: str,
    parent_node_token: Optional[str],
    doc_title: str
) -> Optional[Dict]:
    """
    查找已存在的同名文档
    
    Args:
        api: FeishuAPI实例
        space_id: 知识库ID
        parent_node_token: 父节点token（None表示根节点）
        doc_title: 文档标题
        
    Returns:
        如果找到，返回节点信息（包含node_token和obj_token），否则返回None
    """
    print(f"  检查是否已存在同名文档: {doc_title}")
    
    # 列出父节点下的所有子节点
    result = api.list_wiki_nodes(
        space_id=space_id,
        parent_node_token=parent_node_token,
        page_size=50,
        use_user_token=True
    )
    
    if result:
        # Wiki v2 API的list接口直接返回items，没有code字段
        items = result.get('items', [])
        
        if items:
            # 查找同名文档（按创建时间倒序，优先使用最新的有内容的文档）
            matching_docs = []
            for item in items:
                # 注意：Wiki v2 API返回的节点信息直接在item中，不在node字段
                title = item.get('title', '')
                obj_type = item.get('obj_type', '')
                
                # 检查标题和类型是否匹配
                if title == doc_title and obj_type == 'docx':
                    node_token = item.get('node_token')
                    obj_token = item.get('obj_token')
                    obj_edit_time = item.get('obj_edit_time', '0')  # 编辑时间，用于判断是否有内容
                    
                    matching_docs.append({
                        'node_token': node_token,
                        'obj_token': obj_token,
                        'title': title,
                        'node': item,
                        'edit_time': int(obj_edit_time) if obj_edit_time else 0
                    })
            
            if matching_docs:
                # 按编辑时间倒序排序，优先使用最新的（通常有内容的文档编辑时间更新）
                matching_docs.sort(key=lambda x: x['edit_time'], reverse=True)
                
                # 选择最新的文档
                selected_doc = matching_docs[0]
                print(f"  [OK] 找到 {len(matching_docs)} 个同名文档，使用最新的: {selected_doc['title']}")
                print(f"  节点token: {selected_doc['node_token']}")
                print(f"  文档ID: {selected_doc['obj_token']}")
                
                return selected_doc
        else:
            print(f"  [调试] 未找到子节点")
    # 如果API返回None或没有找到，返回None
    
    print(f"  [OK] 未找到同名文档，将创建新文档")
    return None

def get_document_id_from_wiki_node(api: FeishuAPI, space_id: str, node_token: str) -> str:
    """
    从Wiki节点获取document_id
    
    需要调用Wiki API获取节点的obj_token（即document_id）
    """
    # 获取节点信息
    result = api.get_wiki_node(space_id, node_token, use_user_token=True)
    
    if result:
        if result.get('code') == 0:
            node = result.get('node', {})
            obj_token = node.get('obj_token')
            obj_type = node.get('obj_type')
            
            if obj_type == 'docx' and obj_token:
                return obj_token
            else:
                # 调试信息
                print(f"    [调试] 节点信息: obj_type={obj_type}, obj_token={obj_token}")
        else:
            print(f"    [调试] API返回错误: {result.get('code')}, {result.get('msg')}")
    
    return None

def main():
    sys.stdout.reconfigure(encoding='utf-8')  # 修复编码问题
    
    print("=" * 60)
    print("创建舱驾一体域控FSC文档（完整版本）")
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
        plugin_id="",
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
    print()
    
    # 步骤1：检查是否已存在同名文档
    print("步骤1：检查是否已存在同名文档...")
    existing_doc = None
    if PARENT_NODE_TOKEN:
        existing_doc = find_existing_doc(api, SPACE_ID, PARENT_NODE_TOKEN, DOC_TITLE)
    else:
        existing_doc = find_existing_doc(api, SPACE_ID, None, DOC_TITLE)
    
    if existing_doc:
        # 使用已存在的文档
        node_token = existing_doc['node_token']
        document_id = existing_doc['obj_token']
        doc_name = existing_doc['title']
        
        print()
        print(f"[OK] 使用已存在的文档")
        print(f"节点token: {node_token}")
        print(f"文档ID: {document_id}")
        print()
        
        # 检查文档是否已有内容
        print("步骤1.5：检查文档内容...")
        blocks = api.get_document_blocks(
            document_id=document_id,
            page_size=50,  # 检查更多块，确保能检测到内容
            use_user_token=True
        )
        
        has_content = False
        if blocks:
            if blocks.get('code') == 0:
                items = blocks.get('data', {}).get('items', [])
                # 除了根节点（Page块），如果有其他块，说明文档有内容
                has_content = len(items) > 1  # 根节点算1个
                
                if has_content:
                    print(f"[OK] 文档已有内容（{len(items)-1}个块），将跳过内容添加")
                    print()
                    print("=" * 60)
                    print("[OK] 文档已存在且包含内容")
                    print("=" * 60)
                    print()
                    print(f"文档名称: {doc_name}")
                    print(f"节点token: {node_token}")
                    print(f"文档ID: {document_id}")
                    
                    if node_token:
                        doc_url = f"https://bytedance.larkoffice.com/wiki/{SPACE_ID}/{node_token}"
                        print(f"文档链接: {doc_url}")
                    
                    print()
                    print("提示：")
                    print("1. 文档已存在且包含内容，未创建新文档，也未添加重复内容")
                    print("2. 如需更新内容，可以使用文档协作API")
                    print("3. 如需重新创建，请先删除现有文档")
                    return
                else:
                    print(f"[OK] 文档存在但无内容，将添加内容结构")
                    print()
            else:
                # 如果API返回错误，可能是权限问题，但我们可以根据编辑时间判断
                # 如果文档最近被编辑过（obj_edit_time较新），可能已有内容
                edit_time = existing_doc.get('node', {}).get('obj_edit_time', '0')
                create_time = existing_doc.get('node', {}).get('obj_create_time', '0')
                
                # 如果编辑时间明显晚于创建时间，说明可能有内容
                if edit_time and create_time and int(edit_time) > int(create_time) + 10:  # 至少10秒后编辑
                    print(f"[!] 无法检查文档内容，但文档已被编辑过，可能已有内容")
                    print(f"[!] 为安全起见，将跳过内容添加，避免重复")
                    print()
                    print("=" * 60)
                    print("[OK] 文档已存在（可能包含内容）")
                    print("=" * 60)
                    print()
                    print(f"文档名称: {doc_name}")
                    print(f"节点token: {node_token}")
                    print(f"文档ID: {document_id}")
                    
                    if node_token:
                        doc_url = f"https://bytedance.larkoffice.com/wiki/{SPACE_ID}/{node_token}"
                        print(f"文档链接: {doc_url}")
                    
                    print()
                    print("提示：")
                    print("1. 文档已存在，为避免重复内容，未添加新内容")
                    print("2. 如需更新内容，可以使用文档协作API")
                    print("3. 如需重新创建，请先删除现有文档")
                    return
                else:
                    print(f"[!] 无法检查文档内容: code={blocks.get('code')}, msg={blocks.get('msg')}")
                    print(f"[!] 将尝试添加内容（如果文档已有内容，可能会重复）")
                    print()
        else:
            # blocks为None，可能是API调用失败
            print(f"[!] 无法获取文档内容（API返回None）")
            print(f"[!] 将尝试添加内容（如果文档已有内容，可能会重复）")
            print()
    else:
        # 创建新文档
        print()
        print("步骤1：创建Wiki文档节点...")
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
        
        if not doc:
            print()
            print("=" * 60)
            print("[X] 文档创建失败")
            print("=" * 60)
            print()
            print("请检查：")
            print("1. user_access_token是否有效且包含所需权限")
            print("2. 知识库ID和父节点token是否正确")
            print("3. 用户是否有知识库编辑权限")
            return
        
        # 获取节点信息
        node = doc.get('node', {})
        node_token = node.get('node_token')
        doc_name = node.get('title') or DOC_TITLE
        
        # 尝试从创建结果中直接获取obj_token
        obj_token = node.get('obj_token')
        obj_type = node.get('obj_type')
        
        print(f"[OK] 文档节点创建成功")
        print(f"节点token: {node_token}")
        if obj_token:
            print(f"文档ID（obj_token）: {obj_token}")
        print()
        
        # 获取document_id
        document_id = obj_token if (obj_type == 'docx' and obj_token) else None
    
    # 步骤2：获取document_id（如果还没有）
    if not document_id:
        print("步骤2：获取文档ID（document_id）...")
        import time
        
        print("等待文档完全创建（3秒）...")
        time.sleep(3)  # 等待文档完全创建
        document_id = get_document_id_from_wiki_node(api, SPACE_ID, node_token)
        
        if not document_id:
            print("[!] 第一次尝试获取失败，等待5秒后重试...")
            time.sleep(5)
            document_id = get_document_id_from_wiki_node(api, SPACE_ID, node_token)
        
        if not document_id:
            print("[!] 无法自动获取document_id，需要手动获取")
            print()
            print("解决方法：")
            print("1. 在飞书中打开刚创建的文档")
            print("2. 查看浏览器地址栏，找到document_id")
            print("3. 或者等待几秒后文档完全创建，然后重新运行脚本")
            print()
            print("文档链接：")
            doc_url = f"https://bytedance.larkoffice.com/wiki/{SPACE_ID}/{node_token}"
            print(doc_url)
            print()
            print("文档节点已创建，但内容需要document_id才能添加。")
            print("请获取document_id后，可以手动添加内容或使用update_document_content.py脚本。")
            return
    
    print(f"[OK] 文档ID: {document_id}")
    print()
    
    # 步骤3：添加文档内容
    print("步骤3：添加文档内容结构...")
    import time
    
    for i, section in enumerate(FSC_SECTIONS):
        print(f"  添加章节: {section['title']}")
        
        # 创建标题
        title_block = create_heading_block(section['title'], section['type'])
        
        # 先创建标题块
        result = api.create_block(
            document_id=document_id,
            block_id=document_id,  # 在文档根节点下创建
            children=[title_block],
            document_revision_id=-1,
            use_user_token=True
        )
        
        if not result:
            print(f"    [X] 创建标题块失败")
            time.sleep(1)  # 等待后继续
            continue
        
        print(f"    [OK] 标题块创建成功")
        time.sleep(0.5)  # 避免频率限制
        
        # 创建内容块（逐个创建，避免频率限制）
        for content in section['content']:
            if content.startswith('-'):
                # 列表项
                content_block = create_bullet_block(content[1:].strip())
            else:
                # 普通文本
                content_block = create_text_block(content)
            
            result = api.create_block(
                document_id=document_id,
                block_id=document_id,
                children=[content_block],
                document_revision_id=-1,
                use_user_token=True
            )
            
            if not result:
                print(f"    [X] 创建内容块失败: {content[:30]}...")
            else:
                print(f"    [OK] 内容块创建成功")
            
            time.sleep(0.5)  # 避免频率限制（单篇文档并发编辑上限为每秒3次）
    
    print()
    print("=" * 60)
    print("[OK] 文档创建完成！")
    print("=" * 60)
    print()
    print(f"文档名称: {doc_name}")
    print(f"节点token: {node_token}")
    print(f"文档ID: {document_id}")
    
    # 生成文档链接
    if node_token:
        doc_url = f"https://bytedance.larkoffice.com/wiki/{SPACE_ID}/{node_token}"
        print(f"文档链接: {doc_url}")
    
    print()
    print("文档已包含以下章节：")
    for section in FSC_SECTIONS:
        print(f"  - {section['title']}")
    print()
    print("提示：")
    print("1. 可以在飞书中打开文档查看和编辑")
    print("2. 可以使用文档协作API继续添加或修改内容")
    print("3. 参考 FEISHU-DOC-COLLABORATION-GUIDE.md 了解更多用法")

if __name__ == "__main__":
    main()

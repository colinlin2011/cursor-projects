# -*- coding: utf-8 -*-
"""
飞书API封装工具
支持飞书项目API和飞书开放平台API

重要：所有API调用必须参考reference文档
Reference位置：c:/Users/colin.lin/.cursor/cursor-projects/tools/feishu interaction/reference/
"""

import requests
import json
import time
from typing import Dict, List, Optional, Any
from datetime import datetime


class FeishuAPI:
    """
    飞书API封装类
    支持飞书项目API和飞书开放平台API
    """
    
    def __init__(
        self,
        plugin_id: str,
        plugin_secret: str,
        project_key: Optional[str] = None,
        user_key: Optional[str] = None,
        app_id: Optional[str] = None,
        app_secret: Optional[str] = None,
        base_url: str = "https://project.feishu.cn",
        open_platform_base_url: str = "https://open.feishu.cn",
        timeout: int = 30
    ):
        """
        初始化飞书API客户端
        
        Args:
            plugin_id: 插件ID（飞书项目API）
            plugin_secret: 插件密钥（飞书项目API）
            project_key: 空间ID（飞书项目API，双击空间图标获取）
            user_key: 用户密钥（飞书项目API，双击用户头像获取）
            app_id: 应用ID（飞书开放平台API，用于即时通讯、Wiki、表格等）
            app_secret: 应用密钥（飞书开放平台API）
            base_url: 飞书项目API基础URL
            open_platform_base_url: 飞书开放平台API基础URL
            timeout: 请求超时时间（秒）
        """
        self.plugin_id = plugin_id
        self.plugin_secret = plugin_secret
        self.project_key = project_key
        self.user_key = user_key
        self.app_id = app_id
        self.app_secret = app_secret
        self.base_url = base_url.rstrip('/')
        self.open_platform_base_url = open_platform_base_url.rstrip('/')
        self.timeout = timeout
        
        # Token缓存
        self._plugin_token = None
        self._plugin_token_expires_at = 0
        self._app_access_token = None
        self._app_access_token_expires_at = 0
        self._tenant_access_token = None
        self._tenant_access_token_expires_at = 0
        self._user_access_token = None  # 用户身份凭证（可选）
        self._user_access_token_expires_at = 0
    
    # ==================== 认证相关 ====================
    
    def get_plugin_token(self, force_refresh: bool = False) -> Optional[str]:
        """
        获取飞书项目插件访问凭证
        
        参考文档：api_docs/调用流程-1.md
        
        Args:
            force_refresh: 是否强制刷新token
            
        Returns:
            plugin_token或None
        """
        # 检查缓存
        if not force_refresh and self._plugin_token and time.time() < self._plugin_token_expires_at:
            return self._plugin_token
        
        url = f"{self.base_url}/open_api/authen/plugin_token"
        headers = {'Content-Type': 'application/json'}
        data = {
            "plugin_id": self.plugin_id,
            "plugin_secret": self.plugin_secret
        }
        
        try:
            response = requests.post(url, headers=headers, data=json.dumps(data), timeout=self.timeout)
            if response.status_code == 200:
                result = response.json()
                if result.get('error', {}).get('code', -1) == 0:
                    self._plugin_token = result.get('data', {}).get('token')
                    # 假设token有效期为2小时（实际以API返回为准）
                    self._plugin_token_expires_at = time.time() + 7200
                    return self._plugin_token
                else:
                    print(f"获取plugin_token失败: {result}")
                    return None
            else:
                print(f"请求失败，状态码: {response.status_code}, 响应: {response.text}")
                return None
        except Exception as e:
            print(f"获取plugin_token发生错误: {e}")
            return None
    
    def get_app_access_token(self, force_refresh: bool = False) -> Optional[str]:
        """
        获取飞书开放平台应用访问凭证
        
        Args:
            force_refresh: 是否强制刷新token
            
        Returns:
            app_access_token或None
        """
        if not self.app_id or not self.app_secret:
            print("未配置app_id或app_secret，无法获取app_access_token")
            return None
        
        # 检查缓存
        if not force_refresh and self._app_access_token and time.time() < self._app_access_token_expires_at:
            return self._app_access_token
        
        url = f"{self.open_platform_base_url}/open-apis/auth/v3/app_access_token/internal"
        headers = {'Content-Type': 'application/json'}
        data = {
            "app_id": self.app_id,
            "app_secret": self.app_secret
        }
        
        try:
            response = requests.post(url, headers=headers, data=json.dumps(data), timeout=self.timeout)
            if response.status_code == 200:
                result = response.json()
                if result.get('code', -1) == 0:
                    self._app_access_token = result.get('app_access_token')
                    expire = result.get('expire', 7200)
                    self._app_access_token_expires_at = time.time() + expire
                    return self._app_access_token
                else:
                    print(f"获取app_access_token失败: {result}")
                    return None
            else:
                print(f"请求失败，状态码: {response.status_code}, 响应: {response.text}")
                return None
        except Exception as e:
            print(f"获取app_access_token发生错误: {e}")
            return None
    
    def get_tenant_access_token(self, force_refresh: bool = False) -> Optional[str]:
        """
        获取飞书开放平台租户访问凭证
        
        Args:
            force_refresh: 是否强制刷新token
            
        Returns:
            tenant_access_token或None
        """
        if not self.app_id or not self.app_secret:
            print("未配置app_id或app_secret，无法获取tenant_access_token")
            return None
        
        # 检查缓存
        if not force_refresh and self._tenant_access_token and time.time() < self._tenant_access_token_expires_at:
            return self._tenant_access_token
        
        url = f"{self.open_platform_base_url}/open-apis/auth/v3/tenant_access_token/internal"
        headers = {'Content-Type': 'application/json'}
        data = {
            "app_id": self.app_id,
            "app_secret": self.app_secret
        }
        
        try:
            response = requests.post(url, headers=headers, data=json.dumps(data), timeout=self.timeout)
            if response.status_code == 200:
                result = response.json()
                if result.get('code', -1) == 0:
                    self._tenant_access_token = result.get('tenant_access_token')
                    expire = result.get('expire', 7200)
                    self._tenant_access_token_expires_at = time.time() + expire
                    return self._tenant_access_token
                else:
                    print(f"获取tenant_access_token失败: {result}")
                    return None
            else:
                print(f"请求失败，状态码: {response.status_code}, 响应: {response.text}")
                return None
        except Exception as e:
            print(f"获取tenant_access_token发生错误: {e}")
            return None
    
    # ==================== 飞书项目API ====================
    
    def _project_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None,
        use_user_key: bool = True
    ) -> Optional[Dict]:
        """
        飞书项目API请求封装
        
        Args:
            method: HTTP方法（GET/POST/PUT/DELETE）
            endpoint: API端点（不包含base_url和project_key）
            data: 请求体数据
            params: URL参数
            use_user_key: 是否使用user_key
            
        Returns:
            API响应结果或None
        """
        plugin_token = self.get_plugin_token()
        if not plugin_token:
            print("无法获取plugin_token")
            return None
        
        # 构建URL
        if endpoint.startswith('/'):
            endpoint = endpoint[1:]
        
        if self.project_key and ':project_key' in endpoint:
            url = f"{self.base_url}/open_api/{endpoint.replace(':project_key', self.project_key)}"
        else:
            url = f"{self.base_url}/open_api/{endpoint}"
        
        # 构建Headers
        headers = {
            'Content-Type': 'application/json',
            'X-PLUGIN-TOKEN': plugin_token
        }
        if use_user_key and self.user_key:
            headers['X-USER-KEY'] = self.user_key
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers, params=params, timeout=self.timeout)
            elif method.upper() == 'POST':
                response = requests.post(url, headers=headers, data=json.dumps(data) if data else None, params=params, timeout=self.timeout)
            elif method.upper() == 'PUT':
                response = requests.put(url, headers=headers, data=json.dumps(data) if data else None, params=params, timeout=self.timeout)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, headers=headers, params=params, timeout=self.timeout)
            else:
                print(f"不支持的HTTP方法: {method}")
                return None
            
            if response.status_code == 200:
                result = response.json()
                if result.get('error', {}).get('code', -1) == 0:
                    return result.get('data')
                else:
                    print(f"API调用失败: {result}")
                    return None
            else:
                print(f"请求失败，状态码: {response.status_code}, 响应: {response.text}")
                return None
        except Exception as e:
            print(f"API调用发生错误: {e}")
            return None
    
    # 工作项管理
    def create_work_item(
        self,
        work_item_type_key: str,
        fields: Dict[str, Any],
        project_key: Optional[str] = None
    ) -> Optional[Dict]:
        """
        创建工作项
        
        参考文档：api_docs/工作项-8.md
        
        Args:
            work_item_type_key: 工作项类型key
            fields: 工作项字段
            project_key: 空间ID（可选，默认使用初始化时的project_key）
            
        Returns:
            工作项信息或None
        """
        if project_key:
            self.project_key = project_key
        
        endpoint = f":project_key/work_item/create"
        data = {
            "work_item_type_key": work_item_type_key,
            "fields": fields
        }
        return self._project_request('POST', endpoint, data)
    
    def update_work_item(
        self,
        work_item_type_key: str,
        work_item_id: str,
        update_fields: List[Dict],
        project_key: Optional[str] = None
    ) -> Optional[Dict]:
        """
        更新工作项
        
        参考文档：api_docs/工作项-9.md
        
        Args:
            work_item_type_key: 工作项类型key
            work_item_id: 工作项ID
            update_fields: 更新字段列表
            project_key: 空间ID（可选）
            
        Returns:
            更新结果或None
        """
        if project_key:
            self.project_key = project_key
        
        endpoint = f":project_key/work_item/{work_item_type_key}/{work_item_id}"
        data = {
            "update_fields": update_fields
        }
        return self._project_request('PUT', endpoint, data)
    
    def query_work_item(
        self,
        work_item_type_key: str,
        work_item_id: str,
        project_key: Optional[str] = None
    ) -> Optional[Dict]:
        """
        查询工作项详情
        
        参考文档：api_docs/工作项-6.md
        
        Args:
            work_item_type_key: 工作项类型key
            work_item_id: 工作项ID
            project_key: 空间ID（可选）
            
        Returns:
            工作项详情或None
        """
        if project_key:
            self.project_key = project_key
        
        endpoint = f":project_key/work_item/{work_item_type_key}/query"
        data = {
            "work_item_id": work_item_id
        }
        return self._project_request('POST', endpoint, data)
    
    def search_work_items(
        self,
        work_item_type_key: str,
        filter_conditions: Optional[Dict] = None,
        project_key: Optional[str] = None
    ) -> Optional[Dict]:
        """
        搜索工作项
        
        参考文档：api_docs/工作项-1.md
        
        Args:
            work_item_type_key: 工作项类型key
            filter_conditions: 筛选条件
            project_key: 空间ID（可选）
            
        Returns:
            工作项列表或None
        """
        if project_key:
            self.project_key = project_key
        
        endpoint = f":project_key/work_item/filter"
        data = {
            "work_item_type_key": work_item_type_key
        }
        if filter_conditions:
            data["filter_conditions"] = filter_conditions
        
        return self._project_request('POST', endpoint, data)
    
    def get_work_item_operation_records(
        self,
        work_item_ids: List[str],
        project_key: Optional[str] = None
    ) -> Optional[Dict]:
        """
        获取工作项操作记录
        
        参考文档：api_docs/工作项-16.md
        
        Args:
            work_item_ids: 工作项ID列表
            project_key: 空间ID（可选）
            
        Returns:
            操作记录或None
        """
        if project_key:
            self.project_key = project_key
        
        endpoint = "op_record/work_item/list"
        data = {
            "project_key": project_key or self.project_key,
            "work_item_ids": work_item_ids
        }
        return self._project_request('POST', endpoint, data)
    
    # 流程管理
    def get_workflow(
        self,
        work_item_type_key: str,
        work_item_id: str,
        project_key: Optional[str] = None
    ) -> Optional[Dict]:
        """
        获取工作流详情
        
        参考文档：api_docs/流程与节点-1.md
        
        Args:
            work_item_type_key: 工作项类型key
            work_item_id: 工作项ID
            project_key: 空间ID（可选）
            
        Returns:
            工作流详情或None
        """
        if project_key:
            self.project_key = project_key
        
        endpoint = f":project_key/work_item/{work_item_type_key}/{work_item_id}/workflow/query"
        return self._project_request('POST', endpoint)
    
    def update_node(
        self,
        work_item_type_key: str,
        work_item_id: str,
        node_id: str,
        update_fields: List[Dict],
        project_key: Optional[str] = None
    ) -> Optional[Dict]:
        """
        更新节点/排期
        
        参考文档：api_docs/流程与节点-3.md
        
        Args:
            work_item_type_key: 工作项类型key
            work_item_id: 工作项ID
            node_id: 节点ID
            update_fields: 更新字段列表
            project_key: 空间ID（可选）
            
        Returns:
            更新结果或None
        """
        if project_key:
            self.project_key = project_key
        
        endpoint = f":project_key/workflow/{work_item_type_key}/{work_item_id}/node/{node_id}"
        data = {
            "update_fields": update_fields
        }
        return self._project_request('PUT', endpoint, data)
    
    # 视图管理
    def get_views(
        self,
        project_key: Optional[str] = None
    ) -> Optional[Dict]:
        """
        获取视图列表
        
        参考文档：api_docs/视图与度量-1.md
        
        Args:
            project_key: 空间ID（可选）
            
        Returns:
            视图列表或None
        """
        if project_key:
            self.project_key = project_key
        
        endpoint = f":project_key/view/v1/list"
        return self._project_request('POST', endpoint)
    
    def get_view_items(
        self,
        view_id: str,
        project_key: Optional[str] = None
    ) -> Optional[Dict]:
        """
        获取视图下工作项列表
        
        参考文档：api_docs/视图与度量-2.md
        
        Args:
            view_id: 视图ID
            project_key: 空间ID（可选）
            
        Returns:
            工作项列表或None
        """
        if project_key:
            self.project_key = project_key
        
        endpoint = f":project_key/view/v1/items"
        data = {
            "view_id": view_id
        }
        return self._project_request('POST', endpoint, data)
    
    # ==================== 飞书开放平台API ====================
    
    def _open_platform_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None,
        use_tenant_token: bool = True,
        use_user_token: bool = False
    ) -> Optional[Dict]:
        """
        飞书开放平台API请求封装
        
        Args:
            method: HTTP方法
            endpoint: API端点
            data: 请求体数据
            params: URL参数
            use_tenant_token: 是否使用tenant_access_token（否则使用app_access_token）
            use_user_token: 是否使用user_access_token（用户身份凭证）
            
        Returns:
            API响应结果或None
        """
        if use_user_token and self._user_access_token:
            # 优先使用用户身份凭证
            token = self._user_access_token
        elif use_tenant_token:
            token = self.get_tenant_access_token()
        else:
            token = self.get_app_access_token()
        
        if not token:
            print("无法获取访问凭证")
            return None
        
        # 构建URL
        if endpoint.startswith('/'):
            endpoint = endpoint[1:]
        url = f"{self.open_platform_base_url}/{endpoint}"
        
        # 构建Headers
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}'
        }
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers, params=params, timeout=self.timeout)
            elif method.upper() == 'POST':
                response = requests.post(url, headers=headers, data=json.dumps(data) if data else None, params=params, timeout=self.timeout)
            elif method.upper() == 'PUT':
                response = requests.put(url, headers=headers, data=json.dumps(data) if data else None, params=params, timeout=self.timeout)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, headers=headers, params=params, timeout=self.timeout)
            else:
                print(f"不支持的HTTP方法: {method}")
                return None
            
            if response.status_code == 200:
                result = response.json()
                if result.get('code', -1) == 0:
                    return result.get('data')
                else:
                    print(f"API调用失败: {result}")
                    return None
            else:
                print(f"请求失败，状态码: {response.status_code}, 响应: {response.text}")
                return None
        except Exception as e:
            print(f"API调用发生错误: {e}")
            return None
    
    # 即时通讯
    def send_message(
        self,
        receive_id: str,
        receive_id_type: str,
        msg_type: str,
        content: Dict[str, Any]
    ) -> Optional[Dict]:
        """
        发送消息
        
        参考文档：飞书开放平台 - 发送消息API
        
        Args:
            receive_id: 接收者ID（用户ID或群ID）
            receive_id_type: 接收者类型（open_id/user_id/chat_id）
            msg_type: 消息类型（text/post/image等）
            content: 消息内容
            
        Returns:
            发送结果或None
        """
        endpoint = "open-apis/im/v1/messages"
        data = {
            "receive_id": receive_id,
            "receive_id_type": receive_id_type,
            "msg_type": msg_type,
            "content": json.dumps(content)
        }
        return self._open_platform_request('POST', endpoint, data)
    
    def set_user_access_token(self, user_access_token: str, expires_in: int = 7200):
        """
        设置用户身份凭证（user_access_token）
        
        用于以用户身份调用API，权限由用户的权限决定
        
        Args:
            user_access_token: 用户身份凭证
            expires_in: 有效期（秒），默认7200秒（2小时）
        """
        self._user_access_token = user_access_token
        self._user_access_token_expires_at = time.time() + expires_in
    
    # Wiki云文档
    def create_wiki_doc(
        self,
        space_id: str,
        parent_node_token: Optional[str] = None,
        title: str = "新文档",
        use_user_token: bool = True
    ) -> Optional[Dict]:
        """
        创建Wiki云文档
        
        参考文档：飞书开放平台 - Wiki v2 API
        
        Args:
            space_id: 知识库ID
            parent_node_token: 父节点token（可选）
            title: 文档标题
            use_user_token: 是否使用用户身份凭证（推荐，因为应用无法直接添加到Wiki成员）
            
        Returns:
            文档信息或None
        """
        # 使用Wiki v2 API创建文档节点
        endpoint = f"open-apis/wiki/v2/spaces/{space_id}/nodes"
        data = {
            "obj_type": "docx",  # 文档类型
            "parent_node_token": parent_node_token or "",  # 父节点token，空字符串表示根节点
            "node_type": "origin",  # 节点类型：origin表示原始节点
            "title": title
        }
        return self._open_platform_request('POST', endpoint, data, use_user_token=use_user_token)
    
    def get_wiki_doc(
        self,
        file_token: str
    ) -> Optional[Dict]:
        """
        获取Wiki云文档
        
        Args:
            file_token: 文档token
            
        Returns:
            文档信息或None
        """
        endpoint = f"open-apis/drive/v1/files/{file_token}"
        return self._open_platform_request('GET', endpoint)
    
    def get_wiki_node(
        self,
        space_id: str,
        node_token: str,
        use_user_token: bool = True
    ) -> Optional[Dict]:
        """
        获取Wiki节点信息
        
        参考文档：飞书开放平台 - Wiki v2 API - 获取节点信息
        https://open.feishu.cn/document/ukTMukTMukTM/uUDN04SN0QjL1QDN/wiki-v2/space-node/get
        
        Args:
            space_id: 知识库ID
            node_token: 节点token
            use_user_token: 是否使用用户身份凭证
            
        Returns:
            节点信息或None
        """
        endpoint = f"open-apis/wiki/v2/spaces/{space_id}/nodes/{node_token}"
        return self._open_platform_request('GET', endpoint, use_user_token=use_user_token)
    
    def list_wiki_nodes(
        self,
        space_id: str,
        parent_node_token: Optional[str] = None,
        page_size: int = 50,
        page_token: Optional[str] = None,
        use_user_token: bool = True
    ) -> Optional[Dict]:
        """
        列出Wiki节点（获取子节点列表）
        
        参考文档：飞书开放平台 - Wiki v2 API - 列出节点
        https://open.feishu.cn/document/ukTMukTMukTM/uUDN04SN0QjL1QDN/wiki-v2/space-node/list
        
        Args:
            space_id: 知识库ID
            parent_node_token: 父节点token，为空表示根节点
            page_size: 分页大小
            page_token: 分页token
            use_user_token: 是否使用用户身份凭证
            
        Returns:
            节点列表或None
        """
        endpoint = f"open-apis/wiki/v2/spaces/{space_id}/nodes"
        params = {
            "page_size": page_size
        }
        if parent_node_token:
            params["parent_node_token"] = parent_node_token
        if page_token:
            params["page_token"] = page_token
        
        return self._open_platform_request('GET', endpoint, params=params, use_user_token=use_user_token)
    
    # 文档内容操作（Docx API）
    def get_document_info(
        self,
        document_id: str,
        use_user_token: bool = True
    ) -> Optional[Dict]:
        """
        获取文档基本信息
        
        参考文档：飞书开放平台 - Docx API - 获取文档基本信息
        https://open.feishu.cn/document/ukTMukTMukTM/uUDN04SN0QjL1QDN/document-docx/docx-v1/document/get
        
        Args:
            document_id: 文档ID（document_id）
            use_user_token: 是否使用用户身份凭证
            
        Returns:
            文档信息或None
        """
        endpoint = f"open-apis/docx/v1/documents/{document_id}"
        return self._open_platform_request('GET', endpoint, use_user_token=use_user_token)
    
    def get_document_blocks(
        self,
        document_id: str,
        page_size: int = 500,
        page_token: Optional[str] = None,
        document_revision_id: int = -1,
        use_user_token: bool = True
    ) -> Optional[Dict]:
        """
        获取文档所有块
        
        参考文档：飞书开放平台 - Docx API - 获取文档所有块
        https://open.feishu.cn/document/ukTMukTMukTM/uUDN04SN0QjL1QDN/document-docx/docx-v1/document-block/list
        
        Args:
            document_id: 文档ID
            page_size: 分页大小，最大500
            page_token: 分页token
            document_revision_id: 文档版本ID，-1表示最新版本
            use_user_token: 是否使用用户身份凭证
            
        Returns:
            块列表或None
        """
        endpoint = f"open-apis/docx/v1/documents/{document_id}/blocks"
        params = {
            "page_size": page_size,
            "document_revision_id": document_revision_id
        }
        if page_token:
            params["page_token"] = page_token
        return self._open_platform_request('GET', endpoint, params=params, use_user_token=use_user_token)
    
    def get_block_content(
        self,
        document_id: str,
        block_id: str,
        document_revision_id: int = -1,
        use_user_token: bool = True
    ) -> Optional[Dict]:
        """
        获取块的内容
        
        参考文档：飞书开放平台 - Docx API - 获取块的内容
        https://open.feishu.cn/document/ukTMukTMukTM/uUDN04SN0QjL1QDN/document-docx/docx-v1/document-block/get
        
        Args:
            document_id: 文档ID
            block_id: 块ID
            document_revision_id: 文档版本ID，-1表示最新版本
            use_user_token: 是否使用用户身份凭证
            
        Returns:
            块内容或None
        """
        endpoint = f"open-apis/docx/v1/documents/{document_id}/blocks/{block_id}"
        params = {
            "document_revision_id": document_revision_id
        }
        return self._open_platform_request('GET', endpoint, params=params, use_user_token=use_user_token)
    
    def create_block(
        self,
        document_id: str,
        block_id: str,
        children: List[Dict],
        document_revision_id: int = -1,
        use_user_token: bool = True
    ) -> Optional[Dict]:
        """
        创建块（在指定块的子块列表中创建子块）
        
        参考文档：飞书开放平台 - Docx API - 创建块
        https://open.feishu.cn/document/ukTMukTMukTM/uUDN04SN0QjL1QDN/document-docx/docx-v1/document-block-children/create
        
        Args:
            document_id: 文档ID
            block_id: 父块ID（如果是对文档根节点创建子块，可使用document_id）
            children: 子块列表，每个元素是一个块的定义
            document_revision_id: 文档版本ID，-1表示最新版本
            use_user_token: 是否使用用户身份凭证
            
        Returns:
            创建的块信息或None
        """
        endpoint = f"open-apis/docx/v1/documents/{document_id}/blocks/{block_id}/children"
        params = {
            "document_revision_id": document_revision_id
        }
        data = {
            "children": children
        }
        # 注意：create_block API默认将新块追加到末尾，如果需要指定位置，需要使用index参数
        # 但当前实现是按顺序写入，所以应该能保持顺序
        return self._open_platform_request('POST', endpoint, data, params=params, use_user_token=use_user_token)
    
    def create_descendant(
        self,
        document_id: str,
        block_id: str,
        children_id: List[str],
        descendants: List[Dict],
        index: int = 0,
        document_revision_id: int = -1,
        use_user_token: bool = True
    ) -> Optional[Dict]:
        """
        创建嵌套块（用于创建表格等复杂结构）
        
        参考文档：飞书开放平台 - Docx API - 创建嵌套块
        https://open.feishu.cn/document/ukTMukTMukTM/uUDN04SN0QjL1QDN/document-docx/docx-v1/document-block-descendant/create
        
        Args:
            document_id: 文档ID
            block_id: 父块ID
            children_id: 子块ID列表
            descendants: 嵌套块结构列表
            index: 插入位置
            document_revision_id: 文档版本ID，-1表示最新版本
            use_user_token: 是否使用用户身份凭证
            
        Returns:
            创建的块信息或None
        """
        endpoint = f"open-apis/docx/v1/documents/{document_id}/blocks/{block_id}/descendant"
        params = {
            "document_revision_id": document_revision_id
        }
        data = {
            "index": index,
            "children_id": children_id,
            "descendants": descendants
        }
        return self._open_platform_request('POST', endpoint, data, params=params, use_user_token=use_user_token)
    
    def update_block(
        self,
        document_id: str,
        block_id: str,
        requests: List[Dict],
        document_revision_id: int = -1,
        use_user_token: bool = True
    ) -> Optional[Dict]:
        """
        更新块的内容
        
        参考文档：飞书开放平台 - Docx API - 更新块的内容
        https://open.feishu.cn/document/ukTMukTMukTM/uUDN04SN0QjL1QDN/document-docx/docx-v1/document-block/patch
        
        Args:
            document_id: 文档ID
            block_id: 块ID
            requests: 更新请求列表，每个元素是一个更新操作
            document_revision_id: 文档版本ID，-1表示最新版本
            use_user_token: 是否使用用户身份凭证
            
        Returns:
            更新结果或None
        """
        endpoint = f"open-apis/docx/v1/documents/{document_id}/blocks/{block_id}"
        params = {
            "document_revision_id": document_revision_id
        }
        data = {
            "requests": requests
        }
        return self._open_platform_request('PATCH', endpoint, data, params=params, use_user_token=use_user_token)
    
    def delete_blocks(
        self,
        document_id: str,
        block_id: str,
        start_index: int,
        end_index: int,
        document_revision_id: int = -1,
        use_user_token: bool = True
    ) -> Optional[Dict]:
        """
        删除块（删除指定块的子块）
        
        参考文档：飞书开放平台 - Docx API - 删除块
        https://open.feishu.cn/document/ukTMukTMukTM/uUDN04SN0QjL1QDN/document-docx/docx-v1/document-block-children/batch_delete
        
        Args:
            document_id: 文档ID
            block_id: 父块ID
            start_index: 删除的起始索引（左闭右开）
            end_index: 删除的末尾索引（左闭右开）
            document_revision_id: 文档版本ID，-1表示最新版本
            use_user_token: 是否使用用户身份凭证
            
        Returns:
            删除结果或None
        """
        endpoint = f"open-apis/docx/v1/documents/{document_id}/blocks/{block_id}/children/batch_delete"
        params = {
            "document_revision_id": document_revision_id
        }
        data = {
            "start_index": start_index,
            "end_index": end_index
        }
        return self._open_platform_request('DELETE', endpoint, data, params=params, use_user_token=use_user_token)
    
    # 多维表格
    def create_bitable(
        self,
        name: str,
        folder_token: Optional[str] = None
    ) -> Optional[Dict]:
        """
        创建多维表格
        
        参考文档：飞书开放平台 - 多维表格API
        
        Args:
            name: 表格名称
            folder_token: 文件夹token（可选）
            
        Returns:
            表格信息或None
        """
        endpoint = "open-apis/bitable/v1/apps"
        data = {
            "name": name,
            "folder_token": folder_token or ""
        }
        return self._open_platform_request('POST', endpoint, data)
    
    def get_bitable_records(
        self,
        app_token: str,
        table_id: str,
        page_size: int = 100,
        page_token: Optional[str] = None
    ) -> Optional[Dict]:
        """
        获取多维表格记录
        
        Args:
            app_token: 多维表格app_token
            table_id: 数据表ID
            page_size: 分页大小
            page_token: 分页token
            
        Returns:
            记录列表或None
        """
        endpoint = f"open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records"
        params = {
            "page_size": page_size
        }
        if page_token:
            params["page_token"] = page_token
        return self._open_platform_request('GET', endpoint, params=params)
    
    def create_bitable_record(
        self,
        app_token: str,
        table_id: str,
        fields: Dict[str, Any],
        use_user_token: bool = True
    ) -> Optional[Dict]:
        """
        创建多维表格记录
        
        Args:
            app_token: 多维表格app_token
            table_id: 数据表ID
            fields: 字段数据
            use_user_token: 是否使用用户身份凭证
            
        Returns:
            创建的记录或None
        """
        endpoint = f"open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records"
        data = {
            "fields": fields
        }
        return self._open_platform_request('POST', endpoint, data, use_user_token=use_user_token)
    
    def get_bitable(self, app_token: str, use_user_token: bool = True) -> Optional[Dict]:
        """
        获取多维表格元数据
        
        Args:
            app_token: 多维表格app_token
            use_user_token: 是否使用用户身份凭证
            
        Returns:
            表格元数据或None
        """
        endpoint = f"open-apis/bitable/v1/apps/{app_token}"
        return self._open_platform_request('GET', endpoint, use_user_token=use_user_token)
    
    def list_bitable_tables(
        self,
        app_token: str,
        use_user_token: bool = True
    ) -> Optional[Dict]:
        """
        列出多维表格的所有数据表
        
        Args:
            app_token: 多维表格app_token
            use_user_token: 是否使用用户身份凭证
            
        Returns:
            数据表列表或None
        """
        endpoint = f"open-apis/bitable/v1/apps/{app_token}/tables"
        return self._open_platform_request('GET', endpoint, use_user_token=use_user_token)
    
    def list_bitable_fields(
        self,
        app_token: str,
        table_id: str,
        use_user_token: bool = True
    ) -> Optional[Dict]:
        """
        列出数据表的所有字段
        
        Args:
            app_token: 多维表格app_token
            table_id: 数据表ID
            use_user_token: 是否使用用户身份凭证
            
        Returns:
            字段列表或None
        """
        endpoint = f"open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/fields"
        return self._open_platform_request('GET', endpoint, use_user_token=use_user_token)
    
    def list_bitable_views(
        self,
        app_token: str,
        table_id: str,
        use_user_token: bool = True
    ) -> Optional[Dict]:
        """
        列出数据表的所有视图
        
        Args:
            app_token: 多维表格app_token
            table_id: 数据表ID
            use_user_token: 是否使用用户身份凭证
            
        Returns:
            视图列表或None
        """
        endpoint = f"open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/views"
        return self._open_platform_request('GET', endpoint, use_user_token=use_user_token)
    
    def get_bitable_record(
        self,
        app_token: str,
        table_id: str,
        record_id: str,
        use_user_token: bool = True
    ) -> Optional[Dict]:
        """
        获取单条记录
        
        Args:
            app_token: 多维表格app_token
            table_id: 数据表ID
            record_id: 记录ID
            use_user_token: 是否使用用户身份凭证
            
        Returns:
            记录信息或None
        """
        endpoint = f"open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records/{record_id}"
        return self._open_platform_request('GET', endpoint, use_user_token=use_user_token)
    
    def update_bitable_record(
        self,
        app_token: str,
        table_id: str,
        record_id: str,
        fields: Dict[str, Any],
        use_user_token: bool = True
    ) -> Optional[Dict]:
        """
        更新记录
        
        Args:
            app_token: 多维表格app_token
            table_id: 数据表ID
            record_id: 记录ID
            fields: 字段数据
            use_user_token: 是否使用用户身份凭证
            
        Returns:
            更新后的记录或None
        """
        endpoint = f"open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records/{record_id}"
        data = {
            "fields": fields
        }
        return self._open_platform_request('PUT', endpoint, data, use_user_token=use_user_token)
    
    def delete_bitable_record(
        self,
        app_token: str,
        table_id: str,
        record_id: str,
        use_user_token: bool = True
    ) -> Optional[Dict]:
        """
        删除记录
        
        Args:
            app_token: 多维表格app_token
            table_id: 数据表ID
            record_id: 记录ID
            use_user_token: 是否使用用户身份凭证
            
        Returns:
            删除结果或None
        """
        endpoint = f"open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records/{record_id}"
        return self._open_platform_request('DELETE', endpoint, use_user_token=use_user_token)
    
    def batch_create_bitable_records(
        self,
        app_token: str,
        table_id: str,
        records: List[Dict[str, Any]],
        use_user_token: bool = True
    ) -> Optional[Dict]:
        """
        批量创建记录
        
        Args:
            app_token: 多维表格app_token
            table_id: 数据表ID
            records: 记录列表，每个记录包含fields字段
            use_user_token: 是否使用用户身份凭证
            
        Returns:
            创建的记录列表或None
        """
        endpoint = f"open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records/batch_create"
        data = {
            "records": records
        }
        return self._open_platform_request('POST', endpoint, data, use_user_token=use_user_token)
    
    def batch_update_bitable_records(
        self,
        app_token: str,
        table_id: str,
        records: List[Dict[str, Any]],
        use_user_token: bool = True
    ) -> Optional[Dict]:
        """
        批量更新记录
        
        Args:
            app_token: 多维表格app_token
            table_id: 数据表ID
            records: 记录列表，每个记录包含record_id和fields字段
            use_user_token: 是否使用用户身份凭证
            
        Returns:
            更新后的记录列表或None
        """
        endpoint = f"open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records/batch_update"
        data = {
            "records": records
        }
        return self._open_platform_request('POST', endpoint, data, use_user_token=use_user_token)
    
    def batch_delete_bitable_records(
        self,
        app_token: str,
        table_id: str,
        record_ids: List[str],
        use_user_token: bool = True
    ) -> Optional[Dict]:
        """
        批量删除记录
        
        Args:
            app_token: 多维表格app_token
            table_id: 数据表ID
            record_ids: 记录ID列表
            use_user_token: 是否使用用户身份凭证
            
        Returns:
            删除结果或None
        """
        endpoint = f"open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records/batch_delete"
        data = {
            "records": [{"record_id": rid} for rid in record_ids]
        }
        return self._open_platform_request('POST', endpoint, data, use_user_token=use_user_token)
    
    # 在线表格
    def create_spreadsheet(
        self,
        name: str,
        folder_token: Optional[str] = None
    ) -> Optional[Dict]:
        """
        创建在线表格
        
        参考文档：飞书开放平台 - 电子表格API
        
        Args:
            name: 表格名称
            folder_token: 文件夹token（可选）
            
        Returns:
            表格信息或None
        """
        endpoint = "open-apis/drive/v1/files"
        data = {
            "name": name,
            "type": "sheet",
            "parent_token": folder_token or ""
        }
        return self._open_platform_request('POST', endpoint, data)
    
    def get_spreadsheet(
        self,
        spreadsheet_token: str
    ) -> Optional[Dict]:
        """
        获取在线表格
        
        Args:
            spreadsheet_token: 表格token
            
        Returns:
            表格信息或None
        """
        endpoint = f"open-apis/sheets/v3/spreadsheets/{spreadsheet_token}"
        return self._open_platform_request('GET', endpoint)
    
    def update_spreadsheet_cell(
        self,
        spreadsheet_token: str,
        range: str,
        values: List[List[Any]]
    ) -> Optional[Dict]:
        """
        更新在线表格单元格
        
        Args:
            spreadsheet_token: 表格token
            range: 单元格范围（如"A1:B2"）
            values: 单元格值（二维数组）
            
        Returns:
            更新结果或None
        """
        endpoint = f"open-apis/sheets/v2/spreadsheets/{spreadsheet_token}/values/{range}"
        data = {
            "valueRange": {
                "range": range,
                "values": values
            }
        }
        return self._open_platform_request('PUT', endpoint, data)

"""
飞书API封装工具
支持飞书项目API和飞书开放平台API

重要：所有API调用必须参考reference文档
Reference位置：c:\Users\colin.lin\.cursor\cursor-projects\tools\feishu interaction\reference\
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
        use_tenant_token: bool = True
    ) -> Optional[Dict]:
        """
        飞书开放平台API请求封装
        
        Args:
            method: HTTP方法
            endpoint: API端点
            data: 请求体数据
            params: URL参数
            use_tenant_token: 是否使用tenant_access_token（否则使用app_access_token）
            
        Returns:
            API响应结果或None
        """
        if use_tenant_token:
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
    
    # Wiki云文档
    def create_wiki_doc(
        self,
        space_id: str,
        parent_node_token: Optional[str] = None,
        title: str = "新文档"
    ) -> Optional[Dict]:
        """
        创建Wiki云文档
        
        参考文档：飞书开放平台 - 云文档API
        
        Args:
            space_id: 知识库ID
            parent_node_token: 父节点token（可选）
            title: 文档标题
            
        Returns:
            文档信息或None
        """
        endpoint = "open-apis/drive/v1/files"
        data = {
            "name": title,
            "type": "doc",
            "parent_token": parent_node_token or ""
        }
        return self._open_platform_request('POST', endpoint, data)
    
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
        fields: Dict[str, Any]
    ) -> Optional[Dict]:
        """
        创建多维表格记录
        
        Args:
            app_token: 多维表格app_token
            table_id: 数据表ID
            fields: 字段数据
            
        Returns:
            创建的记录或None
        """
        endpoint = f"open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records"
        data = {
            "fields": fields
        }
        return self._open_platform_request('POST', endpoint, data)
    
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

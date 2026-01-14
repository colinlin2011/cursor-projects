import requests
import json

def get_plugin_token(plugin_id, plugin_secret):
    """
    获取飞书项目插件令牌

    Args:
        plugin_id: 插件ID
        plugin_secret: 插件密钥

    Returns:
        str: plugin_token 或 None
    """
    url = "https://project.feishu.cn/open_api/authen/plugin_token"

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
            if result.get('error',{}).get('code', -1) == 0:  # 假设成功码为0，具体请参考API文档
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

def update_work_item(project_key, work_item_type_key, work_item_id, plugin_token, user_key, update_fields):
    """
    更新飞书项目工作项

    Args:
        project_key: 项目密钥
        work_item_type_key: 工作项类型密钥
        work_item_id: 工作项ID
        plugin_token: 插件令牌
        user_key: 用户密钥
        update_fields: 更新字段列表

    Returns:
        response: HTTP响应对象
    """
    url = f"https://project.feishu.cn/open_api/{project_key}/work_item/{work_item_type_key}/{work_item_id}"

    headers = {
        'X-PLUGIN-TOKEN': plugin_token,
        'X-USER-KEY': user_key,
        'Content-Type': 'application/json'
    }

    payload = {
        "update_fields": update_fields
    }

    try:
        response = requests.put(url, headers=headers, data=json.dumps(payload))
        return response
    except requests.exceptions.RequestException as e:
        print(f"请求发生错误: {e}")
        return None

def main():
    # 插件认证信息
    PLUGIN_ID = "{PLUGIN_ID}"
    PLUGIN_SECRET = "{PLUGIN_SECRET}"

    # 获取plugin_token
    plugin_token = get_plugin_token(PLUGIN_ID, PLUGIN_SECRET)

    if not plugin_token:
        print("获取plugin_token失败，程序退出")
        return

    print(f"获取到plugin_token: {plugin_token[:10]}...")  # 只显示前10位

    # 配置工作项更新参数
    PROJECT_KEY = "{空间 ID}"
    WORK_ITEM_TYPE_KEY = "{工作项类型 ID}"
    WORK_ITEM_ID = "{wi_id}"
    USER_KEY = "{user_key}"  # 你的用户密钥

    # 定义要更新的字段
    update_fields = [
        {
            "field_key": "name",
            "field_value": "New Title from API",
        }
    ]

    # 更新工作项
    response = update_work_item(
        project_key=PROJECT_KEY,
        work_item_type_key=WORK_ITEM_TYPE_KEY,
        work_item_id=WORK_ITEM_ID,
        plugin_token=plugin_token,
        user_key=USER_KEY,
        update_fields=update_fields
    )

    if response:
        print(f"更新工作项状态码: {response.status_code}")
        print(f"更新工作项响应: {response.text}")
    else:
        print(response.text)
        print("更新工作项失败")

if __name__ == "__main__":
    main()

 
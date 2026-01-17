# 更新飞书API Token说明

## 当前问题

导入脚本运行时出现以下错误：
- `Authentication token expired. Please request a new one.` (错误码: 99991677)
- `WrongTableId` (错误码: 1254004)

这说明：
1. **user_access_token已过期**，需要重新获取
2. 可能table_id不正确，需要先获取所有tables列表

## 解决方案

### 步骤1：获取新的user_access_token

运行以下脚本获取新的token：

```powershell
cd "P:\Cursor Project\study-systems\ai-as-me-workplace\capabilities\skills\skills"
python get_user_token_for_bitable.py
```

按照提示：
1. 在浏览器中完成授权
2. 从回调URL中获取`code`参数
3. 将code输入到脚本中
4. 获取新的`user_access_token`

### 步骤2：设置环境变量

在PowerShell中设置环境变量：

```powershell
$env:FEISHU_USER_ACCESS_TOKEN = "新的user_access_token"
```

或者永久设置（当前会话）：

```powershell
[System.Environment]::SetEnvironmentVariable('FEISHU_USER_ACCESS_TOKEN', '新的user_access_token', 'User')
```

### 步骤3：重新运行导入脚本

```powershell
python import_legacy_bitable_direct.py
```

## 如果仍然失败

如果仍然出现`WrongTableId`错误，可能需要：

1. **先获取所有tables列表**，确认正确的table_id
2. **检查URL中的table参数**是否是view_id而不是table_id

可以运行以下脚本获取所有tables：

```python
from feishu_bitable_collaborator import create_bitable_collaborator
from bitable_cache_manager import APP_ID, APP_SECRET, USER_ACCESS_TOKEN

collaborator = create_bitable_collaborator(
    app_id=APP_ID,
    app_secret=APP_SECRET,
    user_access_token=USER_ACCESS_TOKEN
)

app_token = "YWDGbSZZKalcnQskTThcSUSXnub"
tables = collaborator.list_tables(app_token)

for table in tables:
    print(f"名称: {table.get('name')}, ID: {table.get('table_id')}")
```

## 参考文档

- 获取token脚本：`capabilities/skills/skills/get_user_token_for_bitable.py`
- 导入脚本：`capabilities/skills/skills/import_legacy_bitable_direct.py`

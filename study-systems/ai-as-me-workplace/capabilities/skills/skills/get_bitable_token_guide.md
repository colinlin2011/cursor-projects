# 获取多维表格访问权限指南

## 问题说明

当前获取的 `user_access_token` 只包含了 wiki 相关权限，缺少多维表格（bitable）访问权限。

## 解决方案

### 方法1：使用授权URL重新获取token（推荐）

1. **打开授权URL**（包含所有必要权限）：
   ```
   https://open.feishu.cn/open-apis/authen/v1/index?app_id=cli_a9c92ca516f99bd9&redirect_uri=https://open.feishu.cn/app/cli_a9c92ca516f99bd9/auth&scope=wiki:wiki wiki:node:create wiki:node:read wiki:node:update docx:document bitable:app bitable:app:readonly base:app:read base:field:read base:view:read
   ```

2. **完成授权**后，从浏览器URL中获取 `code` 参数

3. **使用code获取token**：
   ```bash
   python get_token_from_code.py YOUR_CODE
   ```

### 方法2：检查多维表格URL格式

请提供完整的多维表格URL，格式应该是：
```
https://bitable.feishu.cn/app/{app_token}/table/{table_id}
```

或者提供：
- 完整的多维表格链接
- 确认 `app_token` 和 `table_id` 是否正确

### 方法3：检查多维表格权限

确保：
1. 应用已添加为多维表格的协作者
2. 应用有查看/编辑该多维表格的权限
3. `user_access_token` 包含以下权限：
   - `bitable:app`
   - `bitable:app:readonly`
   - `base:app:read`
   - `base:field:read`
   - `base:view:read`

## 当前状态

- ✅ 已获取新的 `user_access_token`
- ❌ Token缺少 bitable 相关权限
- ❌ 无法访问多维表格（返回 NOTEXIST 错误）

## 下一步

请选择以下方式之一：
1. 重新授权获取包含 bitable 权限的 token
2. 提供完整的多维表格URL以确认参数
3. 检查多维表格的访问权限设置

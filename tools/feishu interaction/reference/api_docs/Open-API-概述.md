Open API 概述

开发一个插件包含以下创建插件、添加构成、开发调试客户端、开发服务端、测试插件、发布插件等步骤，详情参见​开发并发布第一个插件。针对开发服务端场景，飞书项目开放平台提供 Open API 能力，可实现数据的获取与操作（与飞书项目页面的大部分操作等效）。借助这一能力，开发者能够依据自身使用场景，丰富和优化业务流程，增强自身业务与现有工具之间的协同效应。 ​

API 结构介绍​

URL 结构​

飞书项目开放平台提供的 Open API 遵循 RESTful 风格，URL 格式一般如下：​

​

Plain Text

复制

https://{Base URL}/open_api/:project_key/business/all ​

|--域名--| |---路径参数---||---查询参数---|​

​

​

参数​| 说明​  
---|---  
{Base URL}​| 开发者需要根据实际访问域名来调用 API，例如若当前使用的飞书项目域名为：[project.feishu.cn](http://project.feishu.cn/)，则将 {Base URL} 替换为 [project.feishu.cn](http://project.feishu.cn/)。​  
:project_key​| 在飞书项目空间双击空间图标获取 project_key。​​​​​​  
  
​

完整 URL 示例​

​

Plain Text

复制

https://project.feishu.cn/open_api/projectkeyisme/work_item/create​

|------域名-------| |---路径参数---||----查询参数-----|​

​

Header​

​

字段​| 值​| 备注​  
---|---|---  
Content-Type ​| application/json ​| 必须 ​  
X-PLUGIN-TOKEN ​ ​​| 用户在开放平台中获取的 Token，可选以下两种凭证： ​

1.插件身份凭证（plugin_token，等同于 plugin_access_token），需要配合 X-USER-KEY 使用。插件身份凭证获取参见​获取插件访问凭证 plugin_access_token。​


2.用户身份凭证（user_plugin_token，等同于 user_access_token），获取方法参见​获取用户访问凭证 user_access_token。​
| 必须 ​  
X-USER-KEY ​ ​| 当选择使用插件身份凭证时，需要选择指定接口调用的用户 user_key，user_key 可双击用户头像获取。​| 可选 ​ ​  
X-IDEM-UUID ​| 写类型接口的幂等串，可以不设置，设置后会进行同一个 X-PLUGIN-TOKEN 下同一接口的幂等判断。 ​| 可选 ​  
  
​

服务端 API 调用限制​

服务端 API 对每个 Token 调用单个接口均限制了 15 QPS 的访问限制，请合理设计服务端 API 调用逻辑。部分非 15QPS 限制的接口明细如下： ​

​

接口 ​| 限流阈值 ​  
---|---  
[POST]/open_api/view/v1/update_condition_view ​| 同时限制 15 QPS 和 450 QPM ​  
[POST]/open_api/work_items/filter_across_project ​| 同时限制 15 QPS 和 450 QPM ​  
[POST]/open_api/work_item/subtask/search ​| 同时限制 15 QPS 和 450 QPM ​  
[POST]/open_api/:project_key/work_item/:work_item_type_key/search/params ​| 同时限制 15 QPS 和 450 QPM ​  
[POST]/open_api/:project_key/work_item/filter ​| 同时限制 15 QPS 和 450 QPM ​  
[POST]/open_api/:project_key/work_item/:work_item_type_key/:work_item_id/search_by_relation ​| 10 QPS ​  
[POST]/open_api/work_item/actual_time/update ​| 10 QPS ​  
  
​

API 调用流程​

API 调用流程如下：​

​

​​​

​

1.

获取访问凭证：调用飞书项目开放平台 OpenAPI 前，插件需要获取对应的访问凭证。访问凭证代表插件从平台/用户手中获取的授权，包含插件信息和调用者的身份信息。参见文档​获取访问凭证。​




2.

授权接口：在飞书项目开放平台插件详情页授权需要调用的 Open API 接口。参见文档​权限管理。​




3.

调用 API：在 Postman 中快速体验如何调用 API。参见文档​使用 postman 调用 API 接口。​




格式说明​

​

说明​| 简介​  
---|---  
​通用说明​| 包含 Open API 的名词介绍、频控以及错误码说明。​  
​数据结构汇总​| 列出了飞书项目开发方平台所有 Open API 的数据结构。​  
​字段与属性解析格式​| Open API 统一了用户创建和查询的字段格式，以属性和字段的方式进行描述。​  
​Open API 错误码​| 列出了服务端调用常见错误码及原因分析。​  
  
​

开发示例​

  * 调用接口创建工作项：实现插件通过调用 API 创建 story 工作项，并通过 postman 演示。参见文档​使用 postman 调用 API 接口。​



  * 搜索参数格式及常用示例：列出了搜索参数格式及常用示例，参见​搜索参数格式及常用示例​



  * 全量搜索参数格式及常用示例：列出了全量搜索参数格式及常用示例，参见​全量搜索参数格式及常用示例。​



​

上一篇

开发实践 X 字段类型组件

下一篇

获取访问凭证

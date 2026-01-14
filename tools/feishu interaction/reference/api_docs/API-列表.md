API 列表

用户&用户组​

​

API名称​| 解释​  
---|---  
POST - /open_api/user/query​​获取用户详情​| 获取指定用户的详细信息​  
POST - /open_api/user/search​​搜索租户内的用户列表​| 模糊搜索租户内的用户并返回其详细信息​  
POST - /open_api/:project_key/user_group​​创建自定义用户组​| 创建自定义用户组​  
PATCH - /open_api/:project_key/user_group/members​​更新用户组成员​| 更新用户组成员​  
POST - /open_api/:project_key/user_groups/members/page​​查询用户组成员​| 查询用户组成员​  
  
​

空间​

​

API名称​| 解释​  
---|---  
POST - /open_api/projects​ ​获取空间列表​| 获取指定用户有权限访问空间和插件安装的空间的交集​  
POST - /open_api/projects/detail​​获取空间详情​| 获取查询空间和插件安装空间交集的空间详情信息，包括管理员信息​  
  
​

工作项​

工作项实例搜索​

​

API名称​| 解释​  
---|---  
POST - /open_api/:project_key/work_item/filter​ ​获取指定的工作项列表（单空间）​| 在指定一个空间，搜索符合请求参数中传入条件的工作项实例列表​  
POST - /open_api/work_items/filter_across_project​​获取指定的工作项列表（跨空间）​| 跨多个空间，搜索符合请求参数中传入条件的工作项实例列表​  
POST - /open_api/:project_key/work_item/:work_item_type_key/search/params​​获取指定的工作项列表（单空间-复杂传参）​| 在指定一个空间，搜索符合“复杂筛选条件”的工作项实例列表​  
POST - /open_api/compositive_search​​获取指定的工作项列表（全局搜索）​| 获取跨空间和工作项类型搜索符合条件的工作项实例列表​  
POST - /open_api/:project_key/work_item/:work_item_type_key/:work_item_id/search_by_relation​​获取指定的关联工作项列表（单空间）​| 获取与指定工作项实例存在工作项关联的工作项实例列表​  
  
​

​

工作项实例读写​

​

API名称​| 解释​  
---|---  
POST - /open_api/:project_key/work_item/:work_item_type_key/query​ ​获取工作项详情​| 获取指定空间和工作项类型下的一个工作项实例的详细信息​  
GET - /open_api/:project_key/work_item/:work_item_type_key/meta​​获取创建工作项元数据​| 获取指定工作项类型的“元数据”，它是创建一个工作项实例的最小数据单元​  
POST - /open_api/:project_key/work_item/create​​创建工作项​| 在指定空间和工作项类型下新增一个“工作项实例”，实例可以是一个需求或者缺陷等。​可初始化赋值的字段，可以从​获取创建工作项元数据 接口中获取​  
PUT - /open_api/:project_key/work_item/:work_item_type_key/:work_item_id​​更新工作项​| 修改指定空间和工作项类型下的一个“工作项实例”，可修改字段可以从​获取创建工作项元数据 接口中获取​  
DELETE - /open_api/:project_key/work_item/:work_item_type_key/:work_item_id​​删除工作项​| 删除指定空间和工作项类型下的一个“工作项实例”​  
PUT - /open_api/:project_key/work_item/:work_item_type_key/:work_item_id/abort​​终止/恢复工作项​| 用于终止或者恢复指定空间和工作项类型下的一个“工作项实例”​  
POST - /open_api/op_record/work_item/list​​获取工作项操作记录​| 用于获取指定空间下的多个工作项实例的操作记录，包括一个工作项实例（如一个需求）的操作记录​  
POST - /open_api/work_item/finished/batch_query​​批量查询评审意见、评审结论​| 用于批量查询节点的评审意见和结论​  
POST - /open_api/work_item/finished/update​​修改评审结论和评审意见​| 用于更新节点评审意见和结论，或执行置空操作​  
POST - /open_api/work_item/finished/query_conclusion_option​​评审结论标签值查询​| 用于查询节点下配置的评审结论标签​  
POST - /open_api/work_item/man_hour/records​​获取工作项的工时登记记录列表​| 仅在安装使用官方插件-[工时登记](https://bytedance.larkoffice.com/docx/TecJdQQl1osoPWxDjSwchV7knWf)时有效，用于获取指定空间和工作项类型下的指定工作项实例的工时记录详细信息​  
POST - /open_api/:project_key/work_item/:work_item_type_key/:work_item_id/work_hour_record​​新增工时登记记录​| 仅在安装使用官方插件-[工时登记](https://bytedance.larkoffice.com/docx/TecJdQQl1osoPWxDjSwchV7knWf)时有效，用于指定空间和工作项类型下的指定工作项实例下添加工时记录信息​  
PUT - /open_api/:project_key/work_item/:work_item_type_key/:work_item_id/work_hour_record​​更新工时登记记录​| 仅在安装使用官方插件-[工时登记](https://bytedance.larkoffice.com/docx/TecJdQQl1osoPWxDjSwchV7knWf)时有效，用于更新指定空间和工作项类型下的指定工作项实例的某个操作者的多个工时记录​  
DELETE - /open_api/:project_key/work_item/:work_item_type_key/:work_item_id/work_hour_record​​删除工时登记记录​| 仅在安装并使用官方插件-[工时登记](https://bytedance.larkoffice.com/docx/TecJdQQl1osoPWxDjSwchV7knWf)时有效，用于删除指定空间和工作项类型下的指定工作项实例的某个操作者的多个工时记录​  
PUT - /open_api/work_item/freeze​​冻结/解冻工作项​| 接口用于冻结/解冻工作项实例​  
POST - /open_api/work_item/deliverable/batch_query​​交付物信息批量查询（WBS）​| 用于查询交付物详情信息，目前支持查询工作项交付物（节点交付物待建设）​  
  
​

流程与节点​

​

API名称​| 解释​  
---|---  
POST - /open_api/:project_key/work_item/:work_item_type_key/:work_item_id/workflow/query​ ​获取工作流详情​| 用于获取指定空间和工作项类型下的一个工作项实例的工作流信息，包括节点的状态、负责人、估分以及表单、子任务等。对应的平台功能介绍，如节点流类型以需求实例举例，可参考​流程图，如状态流类型以缺陷举例，可参考​新建缺陷​  
GET - /open_api/:project_key/work_item/:work_item_type_key/:work_item_id/wbs_view​​获取工作流详情（WBS）​| 用于获取行业专版中一个节点流工作项实例的WBS工作流信息​  
PUT - /open_api/:project_key/workflow/:work_item_type_key/:work_item_id/node/:node_id​​更新节点/排期​| 用于更新一个工作项实例的指定节点信息（节点流），包括节点负责人、排期和表单信息等​  
POST - /open_api/:project_key/workflow/:work_item_type_key/:work_item_id/node/:node_id/operate​​节点完成/回滚​| 用于完成或者回滚一个工作项实例的指定节点（节点流），同时更新节点信息，包括节点负责人、排期和表单信息等​  
POST - /open_api/:project_key/workflow/:work_item_type_key/:work_item_id/node/state_change​​状态流转​| 用于流转一个工作项实例到指定状态（状态流），同时更新节点信息，包括人员角色和表单信息等​  
POST - /open_api/work_item/transition_required_info/get​​获取指定节点/状态流转所需必填信息​| 用于获取一个工作项实例指定节点流转所需的必填信息，返回包括必填表单项、必填节点字段、必填子任务、必填交付物在内的必填信息​  
  
​

子任务​

​

API名称​| 解释​  
---|---  
POST - /open_api/work_item/subtask/search​ ​获取指定的子任务列表（跨空间）​| 用于跨空间搜索符合传入条件的子任务，对应平台的功能，如实例侧操作可参考​任务管理，如流程节点上默认的子任务配置可参考​完成任务​  
GET - /open_api/:project_key/work_item/:work_item_type_key/:work_item_id/workflow/task?node_id=:node_id​​获取子任务详情​| 获取指定工作项实例上的子任务详细信息​  
POST - /open_api/:project_key/work_item/:work_item_type_key/:work_item_id/workflow/task​​创建子任务​| 在一个工作项实例的指定节点上创建一个子任务​  
POST - /open_api/:project_key/work_item/:work_item_type_key/:work_item_id/workflow/:node_id/task/:task_id​​更新子任务​| 更新工作项实例指定节点上的一个子任务详细信息​  
POST - /open_api/:project_key/work_item/:work_item_type_key/:work_item_id/subtask/modify​​子任务完成/回滚​| 用于完成或者回滚工作项实例指定节点上的一个子任务​  
DELETE - /open_api/:project_key/work_item/:work_item_type_key/:work_item_id/task/:task_id​​删除子任务​| 用于删除指定工作项实例中的一个子任务​  
  
​

附件​

​

API名称​| 解释​  
---|---  
POST - /open_api/:project_key/work_item/:work_item_type_key/:work_item_id/file/upload​​添加附件​| 用于在指定工作项的一个“附件类型”字段中添加附件​  
POST - /open_api/:project_key/file/upload​​上传文件或富文本图片​| 通用的文件上传接口，会返回上传后的资源路径，主要用于富文本中上传图片​  
POST - /open_api/:project_key/work_item/:work_item_type_key/:work_item_id/file/download​​下载附件​| 用于下载一个工作项下的指定附件​  
POST - /open_api/file/delete​​删除附件​| 用于在指定工作项的一个“附件类型”字段中删除附件​  
  
​

空间关联​

​

API名称​| 解释​  
---|---  
POST - /open_api/:project_key/relation/rules​ ​获取空间关联规则列表​| 获取指定空间下配置的空间关联规则列表​  
POST - /open_api/:project_key/relation/:work_item_type_key/:work_item_id/work_item_list​​获取空间关联下的关联工作项实例列表​| 获取与指定工作项实例有空间关联的工作项实例列表​  
POST - /open_api/:project_key/relation/:work_item_type_key/:work_item_id/batch_bind​​绑定空间关联的关联工作项实例​| 将指定工作项实例和传入的工作项实例列表建立空间关联绑定关系​  
DELETE - /open_api/:project_key/relation/:work_item_type_key/:work_item_id​​解绑空间关联的关联工作项实例​| 将指定工作项实例和传入的工作项实例解除空间关联绑定关系​  
  
​

群组​

​

API名称​| 解释​  
---|---  
POST - /open_api/:project_key/work_item/:work_item_id/bot_join_chat​​拉机器人入群​| 用于将指定的飞书机器人拉入工作项关联群​  
  
​

配置​

空间配置​

​

API名称​| 解释​  
---|---  
GET - /open_api/:project_key/business/all​​获取空间下业务线详情​| 获取查询空间的业务线信息​  
GET - /open_api/:project_key/work_item/all-types​​获取空间下工作项类型​| 获取空间下所有的工作项类型​  
GET - /open_api/:project_key/teams/all​​获取空间下团队人员​| 获取团队详情信息，包括团队人员列表、管理员列表等​  
  
​

工作项配置​

​

API名称​| 解释​  
---|---  
GET - /open_api/:project_key/work_item/type/:work_item_type_key​ ​获取工作项基础信息配置​| 获取指定工作项类型的基础信息配置​  
PUT - /open_api/:project_key/work_item/type/:work_item_type_key​​更新工作项基础信息配置​| 更新指定工作项类型的基础信息配置​  
POST - /open_api/:project_key/field/all​​获取字段信息​| 获取指定空间或一个工作项类型下所有字段的基础信息，对应的平台功能介绍详见​字段配置​  
POST - /open_api/:project_key/field/:work_item_type_key/create​​创建自定义字段​| 在指定工作项类型下创建一个新的自定义字段​  
PUT - /open_api/:project_key/field/:work_item_type_key​​更新自定义字段​| 更新指定自定义字段的配置信息​  
GET - /open_api/:project_key/work_item/relation​​获取工作项关系列表​| 获取指定空间下的工作项关联关系列表，对应的平台功能介绍详见​关系管理​  
POST - /open_api/work_item/relation/create​​新增工作项关系​| 在指定空间下新增一个工作项关联关系​  
POST - /open_api/work_item/relation/update​​更新工作项关系​| 更新指定工作项关联关系的配置信息​  
DELETE - /open_api/work_item/relation/delete​​删除工作项关系​| 删除指定空间下的工作项关联关系​  
  
​

流程模板配置​

​

API名称​| 解释​  
---|---  
GET - /open_api/:project_key/template_list/:work_item_type_key​ ​获取工作项下的流程模板列表​| 用于获取指定工作项类型下所有“流程模板”列表，对应的平台功能介绍详见​节点流程规则配置或​状态流程配置​  
GET - /open_api/:project_key/template_detail/:template_id​​获取流程模板配置详情​| 用于获取指定流程模板的配置信息详情，包括节点信息配置和节点流转配置，节点事件配置暂不支持​  
POST - /open_api/template/v2/create_template​​新增流程模板​| 该接口用于在指定工作项类型下创建一个新的“流程模板”​  
PUT - /open_api/template/v2/update_template​​更新流程模板​| 用于更新指定流程模板的配置信息​  
DELETE - /open_api/template/v2/delete_template/:project_key/:template_id​​删除流程模板​| 用于删除指定的流程模板​  
  
​

流程角色配置​

​

API名称​| 解释​  
---|---  
GET - /open_api/:project_key/flow_roles/:work_item_type_key​ ​获取流程角色配置详情​| 用于获取指定工作项类型下所有“角色与人员”的相关配置信息​  
  
​

​

视图​

​

API名称​| 解释​  
---|---  
POST - /open_api/:project_key/view_conf/list​ ​获取视图列表及配置信息​| 用于在指定空间，搜索符合请求参数中传入条件的视图列表及相关配置信息​对应的平台功能介绍详见​视图介绍​  
GET - /open_api/:project_key/fix_view/:view_id?page_size=:page_size&page_num=:page_num​​获取视图下工作项列表（非全景视图）​| 用于获取指定视图中的所有工作项实例列表​  
POST - /open_api/:project_key/view/:view_id​​获取视图下工作项列表（全景视图）​| 该接口用于获取指定全景视图中的所有工作项实例列表和详情信息​  
POST - /open_api/:project_key/:work_item_type_key/fix_view​​创建固定视图​| 该接口用于在指定空间和工作项类型下新增一个固定视图​  
POST - /open_api/:project_key/:work_item_type_key/fix_view/:view_id​​更新固定视图​| 该接口用于对一个指定固定视图增/删其中的工作项实例​  
POST - /open_api/view/v1/create_condition_view​​创建条件视图​| 用于在指定空间和工作项类型下新增一个条件视图​  
POST - /open_api/view/v1/update_condition_view​​更新条件视图​| 用于对一个指定条件视图更新其筛选条件和协作者信息​  
DELETE - /open_api/:project_key/fix_view/:view_id​​删除视图​| 用于删除指定空间的一个视图，支持条件、固定以及全景视图​  
  
​

评论​

​

API名称​| 解释​  
---|---  
POST - /open_api/:project_key/work_item/:work_item_type_key/:work_item_id/comment/create​​添加评论​| 用于在指定工作项下添加一条评论，添加的评论内容会出现在工作项详情页——评论/备注tab页中，并会显示该评论由插件添加​  
GET - /open_api/:project_key/work_item/:work_item_type_key/:work_item_id/comments​​查询评论​| 用于获取指定工作项下的所有评论信息​  
PUT - /open_api/:project_key/work_item/:work_item_type_key/:work_item_id/comment/:comment_id​​更新评论​| 用于对指定评论更新其内容，被更新的评论会显示该评论由插件添加​  
DELETE - /open_api/:project_key/work_item/:work_item_type_key/:work_item_id/comment/:comment_id​​删除评论​| 用于删除工作项下一条指定的评论信息​  
  
​

度量​

​

API名称​| 解释​  
---|---  
GET - /open_api/:project_key/measure/:chart_id​​获取度量图表明细数据​| 用于获取一个指定度量图表的明细数据​  
  
​

​

上一篇

全量搜索参数格式及常用示例

下一篇

获取用户详情

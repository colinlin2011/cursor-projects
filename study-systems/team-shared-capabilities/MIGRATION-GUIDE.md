# 能力迁移指南

## 迁移说明

本指南说明如何将现有共享能力迁移到团队共享能力库。

---

## 迁移流程

### 步骤1：准备能力文件

确保能力文件满足以下要求：
- 能力功能完整可用
- 有基本文档说明
- 有使用示例（可选但推荐）

### 步骤2：创建能力目录

在团队共享库中创建能力目录：
```bash
mkdir -p capabilities/skills/[能力名称]
```

### 步骤3：复制能力文件

将能力文件复制到团队共享库：
```bash
cp [源路径]/[能力文件].py capabilities/skills/[能力名称]/
cp [源路径]/README.md capabilities/skills/[能力名称]/  # 如果有
```

### 步骤4：使用贡献脚本

使用贡献脚本注册能力：
```bash
python scripts/contribute_capability.py \
    --capability-path capabilities/skills/[能力名称] \
    --name "[能力名称]" \
    --description "[能力描述]" \
    --category "[分类]" \
    --contributor "[贡献者姓名]" \
    --type skill
```

### 步骤5：验证迁移

验证能力已成功迁移：
1. 检查能力注册表：`capabilities/registry.md`
2. 检查贡献者列表：`contributors/contributors.md`
3. 测试能力是否可用

---

## 首批迁移能力建议

### 推荐迁移的能力

1. **飞书API封装工具** (SKILL-001)
   - 路径：`../ai-as-me-workplace/capabilities/skills/skills/feishu_api_wrapper.py`
   - 描述：飞书API的Python封装工具
   - 分类：飞书集成

2. **飞书文档协作器** (SKILL-005)
   - 路径：`../ai-as-me-workplace/capabilities/skills/skills/feishu_doc_collaborator.py`
   - 描述：通用的飞书文档协作能力包
   - 分类：飞书集成

3. **Markdown转Word文档转换器** (SKILL-010)
   - 路径：`../ai-as-me-workplace/capabilities/skills/document-converter/`
   - 描述：将Markdown格式文档转换为Word格式
   - 分类：文档处理

---

## 迁移示例

### 示例：迁移飞书API封装工具

```bash
# 1. 创建能力目录
mkdir -p capabilities/skills/feishu-api-wrapper

# 2. 复制能力文件
cp ../ai-as-me-workplace/capabilities/skills/skills/feishu_api_wrapper.py \
   capabilities/skills/feishu-api-wrapper/

# 3. 创建README（如果没有）
# 参考 CONTRIBUTION-TEMPLATE.md 创建README.md

# 4. 使用贡献脚本
python scripts/contribute_capability.py \
    --capability-path capabilities/skills/feishu-api-wrapper \
    --name "飞书API封装工具" \
    --description "飞书API的Python封装工具，支持消息、Wiki、表格、多维表格、项目等操作" \
    --category "飞书集成" \
    --contributor "Colin" \
    --type skill \
    --version v1.0.0

# 5. 验证迁移
# 检查 capabilities/registry.md 中是否已添加
# 检查 contributors/contributors.md 中是否已记录
```

---

## 迁移注意事项

### 1. 文件路径调整

迁移后，能力文件路径会改变，需要：
- 更新相对路径引用
- 更新导入语句
- 更新配置文件路径

### 2. 依赖管理

确保：
- 依赖项在 `requirements.txt` 中列出
- 依赖版本明确指定
- 依赖兼容性说明清楚

### 3. 配置管理

- 敏感配置（Token、Secret）不应包含在能力文件中
- 使用环境变量或配置文件管理敏感信息
- 提供配置模板

### 4. 文档完整性

确保：
- README.md 完整清晰
- 使用示例可用
- API文档完整

---

## 迁移后维护

### 更新能力

能力更新后，需要：
1. 更新能力文件
2. 更新版本号
3. 更新注册表中的版本信息
4. 更新变更日志

### 废弃能力

能力废弃后，需要：
1. 更新注册表中的状态为"已废弃"
2. 说明废弃原因
3. 提供替代方案（如有）

---

## 相关文档

- [能力贡献模板](CONTRIBUTION-TEMPLATE.md)
- [团队能力注册表](capabilities/registry.md)
- [贡献者列表](contributors/contributors.md)

---

**提示**：迁移能力时，确保能力质量，提供完整文档，方便团队成员使用。

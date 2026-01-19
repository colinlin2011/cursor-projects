# 团队共享能力库

## 概述

团队共享能力库是功能安全部门（33人）共同使用的Cursor作业能力库，旨在实现：

1. **个人能力共享给团队**：个人开发的能力可以被团队复用
2. **团队能力被个人使用**：团队沉淀的能力可以被个人使用
3. **形成复利效应**：每次使用都积累价值，重复利用产生复利
4. **降低使用门槛**：团队成员可以轻松发现和使用共享能力

## 核心理念

**Cursor应用是提效，是作业方式的变革**。通过共享和复用，让每个团队成员都能：
- 快速上手，无需重复造轮子
- 贡献能力，形成团队复利
- 持续优化，不断提升效率

## 目录结构

```
team-shared-capabilities/
├── README.md                 # 本文件
├── capabilities/             # 共享的AI能力
│   ├── skills/               # 共享的Skill能力
│   ├── agents/               # 共享的Agent能力
│   ├── local-tools/          # 共享的本地工具
│   └── registry.md           # 团队能力注册表
├── configs/                  # 共享的配置文件
│   ├── feishu_resources/     # 飞书资源配置（团队共享）
│   └── team_configs.json     # 团队统一配置
├── knowledge/                # 团队知识库
│   ├── standards/            # 团队标准知识
│   ├── patterns/             # 团队工作模式
│   ├── lessons-learned/      # 团队经验教训
│   └── templates/            # 知识贡献模板
├── templates/                # 团队模板库
│   ├── documents/             # 文档模板
│   ├── workflows/            # 工作流模板
│   └── prompts/              # Prompt模板
├── contributors/             # 贡献者记录
│   ├── contributors.md       # 能力贡献者列表
│   └── contributor-stats.md  # 贡献者统计
├── scripts/                  # 工具脚本
│   ├── contribute_capability.py    # 能力贡献脚本
│   ├── discover_capabilities.py   # 能力发现工具
│   └── sync_config.py             # 配置同步脚本
└── usage/                    # 使用追踪
    ├── usage-history.md      # 使用记录
    └── compound-effect.md    # 复利反馈
```

## 快速开始

### 1. 使用团队能力

#### 方法1：查看能力注册表
```bash
# 打开团队能力注册表
code ../team-shared-capabilities/capabilities/registry.md
```

#### 方法2：使用能力发现工具
```bash
# 搜索能力
python ../team-shared-capabilities/scripts/discover_capabilities.py --search "飞书"

# 按场景推荐
python ../team-shared-capabilities/scripts/discover_capabilities.py --scenario "文档协作"

# 查看使用统计
python ../team-shared-capabilities/scripts/discover_capabilities.py --stats
```

#### 方法3：在个人CURSOR.md中引用
在你的个人 `ai-as-me-workplace/CURSOR.md` 中，已经集成了团队能力引用，可以直接使用。

### 2. 贡献新能力

#### 步骤1：开发能力
在你的个人 `ai-as-me-workplace` 中开发能力，确保：
- 功能完整可用
- 代码清晰规范
- 有基本文档

#### 步骤2：使用贡献脚本
```bash
# 使用贡献脚本提交能力
python ../team-shared-capabilities/scripts/contribute_capability.py \
    --capability-path capabilities/skills/skills/my_skill.py \
    --name "我的能力" \
    --description "能力描述" \
    --category "工具类"
```

#### 步骤3：填写贡献信息
脚本会引导你填写：
- 能力ID和名称
- 功能描述和使用场景
- 依赖和配置要求
- 使用示例

#### 步骤4：自动注册
脚本会自动：
- 检查能力完整性
- 生成贡献文档
- 更新团队注册表
- 记录贡献者信息

### 3. 同步团队配置

```bash
# 同步团队配置到个人配置
python ../team-shared-capabilities/scripts/sync_config.py \
    --source team_configs.json \
    --target ../ai-as-me-workplace/work/feishu_resources_config.json \
    --merge
```

## 能力分类

### 按功能分类
- **飞书集成**：飞书API封装、文档协作、表格操作等
- **文档处理**：Markdown转换、文档生成、模板处理等
- **数据分析**：数据提取、统计分析、报告生成等
- **工作流**：自动化流程、任务管理、进度跟踪等

### 按类型分类
- **Skill能力**：单一功能的AI能力
- **Agent能力**：具有自主决策能力的AI代理
- **本地工具**：封装为Skill的本地工具
- **MCP能力**：通过MCP协议集成的外部服务

## 使用原则

### 1. 优先使用团队能力
- 在使用能力前，先查看团队能力注册表
- 优先使用团队共享能力，避免重复开发
- 如果团队能力不满足需求，考虑扩展而非新建

### 2. 及时贡献能力
- 开发了通用能力后，及时贡献到团队
- 贡献前确保能力可用、文档完整
- 遵循贡献模板和流程

### 3. 持续优化
- 使用后提供反馈，帮助改进能力
- 发现bug或改进点，及时提出
- 根据使用情况优化能力

## 贡献者

感谢所有为团队共享能力库做出贡献的成员！

查看贡献者列表：[contributors/contributors.md](contributors/contributors.md)

查看贡献统计：[contributors/contributor-stats.md](contributors/contributor-stats.md)

## 使用统计

查看能力使用情况：[usage/usage-history.md](usage/usage-history.md)

查看复利效应分析：[usage/compound-effect.md](usage/compound-effect.md)

## 相关文档

- [能力贡献模板](CONTRIBUTION-TEMPLATE.md)
- [团队能力注册表](capabilities/registry.md)
- [配置同步指南](scripts/sync_config.py)
- [知识贡献模板](knowledge/templates/)

## 更新日志

### v1.0.0 (2026-01-20)
- 初始版本发布
- 建立基础目录结构
- 实现能力贡献和发现机制
- 实现配置共享机制

## 联系方式

如有问题或建议，请联系：
- 团队管理员：[待填写]
- 技术支持：[待填写]

---

**记住**：共享和复用是提效的关键。每次贡献和使用都在积累团队复利！

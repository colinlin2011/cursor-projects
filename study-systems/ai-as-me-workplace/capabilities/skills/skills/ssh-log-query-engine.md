# SSH日志泛化查询能力

**Tool ID**：SKILL-008  
**Tool名称**：SSH日志泛化查询引擎  
**创建日期**：2026-01-16  
**最后更新**：2026-01-16  
**版本**：v1.0  
**状态**：可用  
**维护人**：系统

---

## 工具描述

### 功能概述

SSH日志泛化查询引擎是一个通用的远程日志查询和提取能力，支持：

- SSH访问远程日志数据
- 自定义关键字查询（支持模糊匹配、多关键字AND/OR组合）
- 自定义信息提取（正则表达式、上下文提取）
- 灵活的查询方式（远程grep、本地搜索，自动选择）
- 多种输出格式（JSON、文本）

### 适用场景

- 故障定位：查询日志中的故障相关信息
- 数据分析：从日志中提取特定数据
- 问题排查：通过关键字快速定位问题
- 日志审计：搜索和提取审计相关信息

---

## 核心功能

### 1. SSH连接管理

- 自动连接管理：自动建立和维护SSH连接
- 连接池：复用连接，避免频繁连接
- 自动重连：连接断开时自动重连
- 配置复用：复用现有的SSH配置（`fault_diagnosis_config.py`）

### 2. 灵活的查询方式

- **自动选择**：根据文件大小自动选择查询方式
  - 小文件（<10MB）：下载到本地后搜索
  - 大文件（≥10MB）：使用远程grep命令
- **手动指定**：支持手动指定查询方式（remote/local）

### 3. 关键字匹配

- **单关键字查询**：支持单个关键字查询
- **多关键字查询**：支持多个关键字组合查询
- **逻辑运算符**：支持AND/OR逻辑
  - AND：所有关键字都必须匹配
  - OR：任意关键字匹配即可
- **模糊匹配**：支持忽略大小写的模糊匹配

### 4. 信息提取

- **正则表达式提取**：使用正则表达式从匹配行中提取指定信息
- **上下文提取**：提取匹配行的前后N行上下文
- **多捕获组**：支持正则表达式的多个捕获组

### 5. 输出格式

- **JSON格式**：结构化的JSON数据，便于程序处理
- **文本格式**：人类可读的文本报告
- **混合格式**：同时返回JSON和文本格式

---

## 工具接口

### 接口定义

```python
from ssh_log_query_engine import SSHLogQueryEngine, create_query_engine

# 创建查询引擎
engine = create_query_engine()  # 使用默认配置
# 或
engine = SSHLogQueryEngine(ssh_config=custom_config)

# 执行查询
result = engine.query(
    remote_path: str,                    # 远程文件或目录路径
    keywords: Union[str, List[str]],     # 关键字（单个字符串或列表）
    extract_pattern: Optional[str] = None,  # 正则表达式提取模式（可选）
    context_lines: int = 0,              # 上下文行数（默认0）
    logic: str = "OR",                   # 逻辑运算符（AND/OR，默认OR）
    output_format: str = "both",         # 输出格式（json/text/both，默认both）
    fuzzy_match: bool = True,            # 是否模糊匹配（默认True）
    max_results: int = 100,              # 最大结果数（默认100）
    query_method: Optional[str] = None    # 查询方式（remote/local/None，None表示自动选择）
) -> Dict[str, Any]
```

### 参数说明

#### remote_path (必需)

远程文件或目录路径。

- 支持单个文件：`/rawdata/roadtestv3/.../log.gz`
- 支持目录：`/rawdata/roadtestv3/.../log/`（会搜索目录下的所有日志文件）

#### keywords (必需)

查询关键字。

- **单个关键字**：字符串，如 `"Fault ID"`
- **多个关键字**：列表，如 `["SetFunc", "fu_st:0x3"]`

#### extract_pattern (可选)

正则表达式提取模式。

- 用于从匹配行中提取指定信息
- 支持捕获组，如 `r"fa_id[:\s]+(0x[0-9A-Fa-f]+)"`
- 如果提供，会在结果中包含 `extracted_info` 字段

#### context_lines (可选，默认0)

上下文行数。

- 提取匹配行的前后N行上下文
- 0表示不提取上下文
- 最大限制：50行

#### logic (可选，默认"OR")

逻辑运算符。

- `"OR"`：任意关键字匹配即可
- `"AND"`：所有关键字都必须匹配

#### output_format (可选，默认"both")

输出格式。

- `"json"`：仅返回JSON格式
- `"text"`：仅返回文本格式
- `"both"`：同时返回JSON和文本格式

#### fuzzy_match (可选，默认True)

是否启用模糊匹配。

- `True`：忽略大小写匹配
- `False`：精确匹配

#### max_results (可选，默认100)

最大结果数。

- 限制返回的匹配结果数量
- 最大限制：10000

#### query_method (可选，默认None)

查询方式。

- `None`：自动选择（根据文件大小）
- `"remote"`：强制使用远程grep
- `"local"`：强制下载到本地后搜索

### 返回值

根据 `output_format` 参数返回不同格式的结果：

**output_format="json"**:
```python
{
    "query_params": {...},
    "matches": [
        {
            "line_number": 123,
            "line_content": "...",
            "file_path": "...",
            "extracted_info": [...],  # 如果提供了extract_pattern
            "context": {...}  # 如果context_lines > 0
        }
    ],
    "statistics": {
        "total_matches": 10,
        "query_time": "2026-01-16T22:30:00"
    }
}
```

**output_format="text"**:
```python
{
    "text": "人类可读的文本报告..."
}
```

**output_format="both"**:
```python
{
    "json": {...},
    "text": "..."
}
```

---

## 使用示例

### 示例1：单关键字查询

```python
from ssh_log_query_engine import create_query_engine

engine = create_query_engine()

result = engine.query(
    remote_path="/rawdata/roadtestv3/.../log.gz",
    keywords="Fault ID",
    context_lines=3,
    output_format="json"
)

print(result['statistics']['total_matches'])  # 匹配数量
for match in result['matches']:
    print(f"行 {match['line_number']}: {match['line_content']}")
```

### 示例2：多关键字AND查询

```python
result = engine.query(
    remote_path="/rawdata/roadtestv3/.../log",
    keywords=["SetFunc", "fu_st:0x3"],
    logic="AND",
    fuzzy_match=True,
    output_format="text"
)

print(result['text'])
```

### 示例3：正则表达式提取

```python
result = engine.query(
    remote_path="/rawdata/roadtestv3/.../log.gz",
    keywords="fa_id",
    extract_pattern=r"fa_id[:\s]+(0x[0-9A-Fa-f]+)",
    output_format="json"
)

for match in result['matches']:
    if 'extracted_info' in match:
        for info in match['extracted_info']:
            print(f"提取的Fault ID: {info['groups'][0]}")
```

### 示例4：上下文提取

```python
result = engine.query(
    remote_path="/rawdata/roadtestv3/.../log",
    keywords="error",
    context_lines=5,  # 提取前后5行
    output_format="both"
)

# 查看JSON格式的上下文
for match in result['json']['matches']:
    if 'context' in match:
        ctx = match['context']
        print(f"匹配行: {ctx['line']}")
        print(f"前文: {ctx['before']}")
        print(f"后文: {ctx['after']}")
```

### 示例5：强制使用远程grep

```python
result = engine.query(
    remote_path="/rawdata/roadtestv3/.../large_log.gz",
    keywords="Fault ID",
    query_method="remote",  # 强制使用远程grep
    max_results=50
)
```

### 示例6：关闭连接

```python
engine = create_query_engine()
try:
    result = engine.query(...)
finally:
    engine.close()  # 关闭SSH连接
```

---

## 实现细节

### 查询方式选择

系统会根据文件大小自动选择查询方式：

- **文件大小 < 10MB**：下载到本地后搜索
  - 优点：可以多次查询，支持复杂提取
  - 缺点：需要下载文件，占用本地存储
  
- **文件大小 ≥ 10MB**：使用远程grep
  - 优点：不需要下载文件，速度快
  - 缺点：每次查询都需要执行远程命令

### 关键字匹配实现

**单关键字**:
- 模糊匹配：使用 `grep -i`（忽略大小写）
- 精确匹配：使用 `grep`（区分大小写）

**多关键字OR逻辑**:
- 使用 `grep -E` 和正则表达式：`grep -iE "keyword1|keyword2"`

**多关键字AND逻辑**:
- 使用grep管道：`grep keyword1 | grep keyword2`

### 信息提取实现

**正则表达式提取**:
- 使用Python的 `re` 模块
- 支持多个捕获组
- 返回所有匹配结果

**上下文提取**:
- 需要读取完整文件内容
- 提取匹配行的前后N行
- 支持去重和合并

---

## 配置说明

### SSH配置

SSH配置复用 `fault_diagnosis_config.py` 中的配置：

```python
SSH_CONFIG = {
    "host": os.getenv("LOG_SERVER_HOST", "10.241.120.100"),
    "port": int(os.getenv("LOG_SERVER_PORT", "22")),
    "username": os.getenv("LOG_SERVER_USER", "dji"),
    "password": os.getenv("LOG_SERVER_PASSWORD", "AutoXPC.246!"),
    "timeout": int(os.getenv("SSH_TIMEOUT", "30"))
}
```

可以通过环境变量覆盖默认配置。

### 默认查询参数

在 `ssh_log_query_config.py` 中配置：

- `FILE_SIZE_THRESHOLD`: 文件大小阈值（默认10MB）
- `MAX_RESULTS_LIMIT`: 最大结果数限制（默认10000）
- `MAX_CONTEXT_LINES`: 最大上下文行数（默认50）

---

## 注意事项

1. **SSH连接**：
   - 确保SSH服务器可访问
   - 确保用户名和密码正确
   - 确保有权限访问目标文件

2. **文件路径**：
   - 路径必须是绝对路径
   - 支持文件和目录路径
   - 目录路径会搜索所有支持的日志文件（.log, .txt, .gz等）

3. **性能考虑**：
   - 大文件建议使用远程grep
   - 小文件可以下载到本地多次查询
   - 限制最大结果数避免返回过多数据

4. **编码问题**：
   - 自动处理UTF-8编码
   - 遇到编码错误会忽略并继续处理

5. **依赖要求**：
   - 需要安装 `paramiko` 库：`pip install paramiko`

---

## 故障排查

### 问题1：SSH连接失败

**症状**：提示"SSH连接失败"

**解决方案**：
1. 检查SSH服务器地址和端口
2. 检查用户名和密码
3. 检查网络连接
4. 检查防火墙设置

### 问题2：文件不存在

**症状**：提示"无法确定路径类型"

**解决方案**：
1. 检查远程路径是否正确
2. 确保路径是绝对路径
3. 检查文件权限

### 问题3：查询结果为空

**症状**：返回0个匹配结果

**可能原因**：
1. 关键字不匹配
2. 逻辑运算符使用错误（AND/OR）
3. 文件内容确实不包含关键字

**解决方案**：
1. 检查关键字是否正确
2. 尝试使用模糊匹配
3. 检查逻辑运算符（AND/OR）

### 问题4：正则表达式提取失败

**症状**：提示"正则表达式提取失败"

**解决方案**：
1. 检查正则表达式语法
2. 使用在线工具测试正则表达式
3. 确保转义特殊字符

---

## 关联记录

### 相关能力

- **SKILL-001~007**：飞书相关能力
- 故障定位系统：可以作为故障定位系统的底层查询能力

### 相关文件

- `ssh_log_query_engine.py` - 核心实现
- `ssh_log_query_config.py` - 配置文件
- `ssh_log_query_example.py` - 使用示例
- `fault_diagnosis_config.py` - SSH配置（复用）

### 相关使用记录

- [使用记录链接](../../usage/usage-history.md)

---

## 工具版本历史

| 版本 | 日期 | 更新内容 | 更新人 |
|------|------|---------|--------|
| v1.0 | 2026-01-16 | 初始创建 | 系统 |

# SSH日志查询引擎 - 快速开始指南

## 第一步：安装依赖

确保已安装 `paramiko` 库：

```bash
pip install paramiko
```

## 第二步：检查SSH配置

SSH配置已集成在系统中，默认使用 `fault_diagnosis_config.py` 中的配置。如果需要自定义，可以通过环境变量设置：

```bash
# Windows PowerShell
$env:LOG_SERVER_HOST="10.241.120.100"
$env:LOG_SERVER_PORT="22"
$env:LOG_SERVER_USER="dji"
$env:LOG_SERVER_PASSWORD="your_password"

# Linux/Mac
export LOG_SERVER_HOST="10.241.120.100"
export LOG_SERVER_PORT="22"
export LOG_SERVER_USER="dji"
export LOG_SERVER_PASSWORD="your_password"
```

## 第三步：最简单的使用示例

创建一个测试脚本 `test_ssh_query.py`：

```python
# -*- coding: utf-8 -*-
import sys
import os

# 添加路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ssh_log_query_engine import create_query_engine

# 创建查询引擎
engine = create_query_engine()

try:
    # 执行查询
    result = engine.query(
        remote_path="/rawdata/roadtestv3/.../log",  # 替换为实际的日志路径
        keywords="Fault ID",  # 要查询的关键字
        output_format="json",
        max_results=10
    )
    
    # 查看结果
    print(f"找到 {result['statistics']['total_matches']} 条匹配")
    print()
    
    for match in result['matches']:
        print(f"行 {match['line_number']}: {match['line_content']}")
        
finally:
    # 关闭连接
    engine.close()
```

运行：

```bash
cd capabilities/skills/skills
python test_ssh_query.py
```

## 常用场景示例

### 场景1：查找包含特定关键字的日志行

```python
from ssh_log_query_engine import create_query_engine

engine = create_query_engine()
result = engine.query(
    remote_path="/rawdata/roadtestv3/.../log.gz",
    keywords="error",
    output_format="json"
)

for match in result['matches']:
    print(f"行 {match['line_number']}: {match['line_content']}")
engine.close()
```

### 场景2：查找同时包含多个关键字的日志（AND逻辑）

```python
engine = create_query_engine()
result = engine.query(
    remote_path="/rawdata/roadtestv3/.../log",
    keywords=["SetFunc", "fu_st:0x3"],  # 两个关键字都必须出现
    logic="AND",
    output_format="text"
)
print(result['text'])
engine.close()
```

### 场景3：提取Fault ID（使用正则表达式）

```python
engine = create_query_engine()
result = engine.query(
    remote_path="/rawdata/roadtestv3/.../log.gz",
    keywords="fa_id",
    extract_pattern=r"fa_id[:\s]+(0x[0-9A-Fa-f]+)",  # 提取Fault ID
    output_format="json"
)

for match in result['matches']:
    if 'extracted_info' in match:
        for info in match['extracted_info']:
            fault_id = info['groups'][0]  # 第一个捕获组
            print(f"找到Fault ID: {fault_id}")
engine.close()
```

### 场景4：查看匹配行的上下文（前后N行）

```python
engine = create_query_engine()
result = engine.query(
    remote_path="/rawdata/roadtestv3/.../log",
    keywords="error",
    context_lines=5,  # 提取前后5行上下文
    output_format="json"
)

for match in result['matches']:
    if 'context' in match:
        ctx = match['context']
        print(f"匹配行 ({ctx['line_number']}): {ctx['line']}")
        print("前文:")
        for line in ctx['before']:
            print(f"  {line}")
        print("后文:")
        for line in ctx['after']:
            print(f"  {line}")
engine.close()
```

### 场景5：获取文本格式的报告

```python
engine = create_query_engine()
result = engine.query(
    remote_path="/rawdata/roadtestv3/.../log",
    keywords="Fault ID",
    context_lines=3,
    output_format="text"  # 返回人类可读的文本报告
)
print(result['text'])
engine.close()
```

## 参数说明

### 必需参数

- **remote_path**: 远程日志文件或目录路径（绝对路径）
- **keywords**: 查询关键字
  - 单个关键字：`"Fault ID"`
  - 多个关键字：`["keyword1", "keyword2"]`

### 可选参数

- **extract_pattern**: 正则表达式提取模式（如：`r"fa_id[:\s]+(0x[0-9A-Fa-f]+)"`）
- **context_lines**: 上下文行数（默认0，不提取上下文）
- **logic**: 逻辑运算符（`"OR"` 或 `"AND"`，默认`"OR"`）
- **output_format**: 输出格式（`"json"`、`"text"` 或 `"both"`，默认`"both"`）
- **fuzzy_match**: 是否模糊匹配（默认`True`，忽略大小写）
- **max_results**: 最大结果数（默认100）
- **query_method**: 查询方式（`"remote"`、`"local"` 或 `None`，`None`表示自动选择）

## 运行完整示例

系统已提供完整的示例文件，可以直接运行：

```bash
cd capabilities/skills/skills
python ssh_log_query_example.py
```

然后选择要运行的示例（1-7）。

## 常见问题

### Q1: 连接失败怎么办？

**A**: 检查以下几点：
1. SSH服务器地址和端口是否正确
2. 用户名和密码是否正确
3. 网络连接是否正常
4. 防火墙是否允许SSH连接

### Q2: 查询结果为空？

**A**: 可能原因：
1. 关键字不匹配（尝试使用模糊匹配）
2. 文件路径不正确
3. 文件确实不包含该关键字

### Q3: 如何查询大文件？

**A**: 系统会自动选择查询方式：
- 小文件（<10MB）：下载到本地后搜索
- 大文件（≥10MB）：使用远程grep

也可以手动指定：
```python
result = engine.query(
    remote_path="/path/to/large_file.log",
    keywords="keyword",
    query_method="remote"  # 强制使用远程grep
)
```

### Q4: 如何提取多个信息？

**A**: 使用正则表达式的多个捕获组：
```python
result = engine.query(
    remote_path="/path/to/log",
    keywords="pattern",
    extract_pattern=r"key1:(\w+).*key2:(\w+)",  # 两个捕获组
    output_format="json"
)

for match in result['matches']:
    if 'extracted_info' in match:
        for info in match['extracted_info']:
            value1 = info['groups'][0]  # 第一个捕获组
            value2 = info['groups'][1]  # 第二个捕获组
```

## 下一步

- 查看完整文档：[ssh-log-query-engine.md](ssh-log-query-engine.md)
- 查看更多示例：[ssh_log_query_example.py](ssh_log_query_example.py)
- 了解配置选项：[ssh_log_query_config.py](ssh_log_query_config.py)

## 快速测试

最简单的测试命令：

```python
from ssh_log_query_engine import create_query_engine

engine = create_query_engine()
result = engine.query(
    remote_path="/rawdata/roadtestv3/.../log",  # 替换为实际路径
    keywords="test",
    max_results=5
)
print(f"找到 {result['statistics']['total_matches']} 条匹配")
engine.close()
```

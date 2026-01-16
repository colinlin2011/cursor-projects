# 故障定位系统改进说明

## 改进时间
2025年1月

## 改进内容

### 1. 支持第5个故障定位指引文档 ✅

**改进说明**：
- 系统已自动支持从配置文件 `work/fault_diagnosis_guides_config.json` 加载所有指引文档
- 第5个文档（node_token: `R3NowdLHoiVOtMks6lzcW7sYnCf`）已存在于配置文件中，系统会自动加载

**配置文件位置**：
- `work/fault_diagnosis_guides_config.json`

**相关代码**：
- `fault_diagnosis_config.py` - `get_guide_docs()` 函数自动从配置文件读取
- `fault_guide_reader.py` - `load_all_guides()` 方法会加载所有配置的指引文档

---

### 2. 理解grep命令语义并智能提取Fault ID ✅

**改进说明**：
系统现在能够理解指引文档中的grep命令语义，例如：

```
zcat log.gz |grep SetFunc |grep -E "fu_st:0x3|fu_st:0x4"
```

**语义理解**：
1. 先过滤包含 `SetFunc` 的行
2. 再过滤包含 `fu_st:0x3` 或 `fu_st:0x4` 的行
3. 从过滤后的行中提取 `fa_id`（如 `0x165`）

**实现方式**：
- `fault_guide_reader.py` - 新增 `_parse_grep_command()` 方法，解析grep命令
- `log_fault_id_extractor.py` - 改进 `extract_fault_ids()` 方法，支持基于过滤条件提取Fault ID

**关键改进点**：
1. **命令解析**：解析管道命令，提取过滤条件和提取模式
2. **多级过滤**：支持多个grep过滤条件（如 `SetFunc` 和 `fu_st:0x3|fu_st:0x4`）
3. **智能提取**：从过滤后的日志行中提取 `fa_id` 字段

**示例**：
```python
# 指引文档中的命令
"zcat log.gz |grep SetFunc |grep -E \"fu_st:0x3|fu_st:0x4\""

# 系统解析后的结构
{
    'filters': ['SetFunc', 'fu_st:0x3|fu_st:0x4'],
    'extract_pattern': r'fa_id[:\s]+(0x[0-9A-Fa-f]+)',
    'original_command': 'zcat log.gz |grep SetFunc |grep -E "fu_st:0x3|fu_st:0x4"'
}
```

---

### 3. 生成飞书文档报告并回填链接 ✅

**改进说明**：
系统现在会生成结构化的飞书文档报告，并将文档链接回填到"工具回传"字段，而不是直接回填零散的文本信息。

**实现方式**：
- `fault_report_generator.py` - 新增报告生成器模块
- `fault_result_writer.py` - 改进结果回填逻辑

**报告结构**：
1. **问题单信息**
   - 工作项ID
   - 记录ID
   - 分析时间
   - Fault ID
   - 日志路径

2. **提取到的Fault ID**
   - 列出所有提取到的Fault ID

3. **详细分析结果**
   - 每个Fault ID的分析结果
   - 故障定位指引
   - AI分析结果

4. **总结**
   - 分析统计信息

**回填内容**：
```
分析时间: 2025-01-XX XX:XX:XX

故障分析报告已生成，请查看：
https://zyt.feishu.cn/wiki/...

报告标题: 故障分析报告-6683487902-20250112-143022
```

**优势**：
1. **结构化展示**：报告以清晰的章节结构展示
2. **易于阅读**：使用飞书文档的富文本格式
3. **便于分享**：文档链接可以方便地分享给团队成员
4. **信息完整**：包含所有故障相关信息，不遗漏

---

## 技术实现细节

### grep命令解析算法

```python
def _parse_grep_command(self, command: str) -> Optional[Dict[str, Any]]:
    """
    解析grep命令语义
    
    支持的命令格式：
    - zcat log.gz |grep SetFunc |grep -E "fu_st:0x3|fu_st:0x4"
    - grep pattern
    - grep -E "pattern1|pattern2"
    """
    # 1. 分割管道命令
    parts = [p.strip() for p in command.split('|')]
    
    # 2. 提取过滤条件
    filters = []
    for part in parts:
        if part.startswith('grep'):
            # 提取grep模式
            grep_match = re.match(r'grep(?:\s+-[Ee])?\s+(.+)', part)
            if grep_match:
                pattern = grep_match.group(1).strip().strip('"\'')
                filters.append(pattern)
    
    # 3. 提取fa_id提取模式
    extract_pattern = r'fa_id[:\s]+(0x[0-9A-Fa-f]+)'
    
    return {
        'filters': filters,
        'extract_pattern': extract_pattern,
        'original_command': command
    }
```

### Fault ID提取流程

```python
def extract_fault_ids(self, log_content: str, guide_info: Optional[Dict] = None):
    # 1. 检查是否有grep命令
    if guide_info and guide_info.get('grep_command'):
        grep_cmd = guide_info['grep_command']
        
        # 2. 应用过滤条件
        filtered_content = log_content
        for filter_pattern in grep_cmd['filters']:
            lines = filtered_content.split('\n')
            filtered_lines = [
                line for line in lines 
                if re.search(filter_pattern, line, re.IGNORECASE)
            ]
            filtered_content = '\n'.join(filtered_lines)
        
        # 3. 从过滤后的内容提取fa_id
        extract_pattern = grep_cmd['extract_pattern']
        matches = re.finditer(extract_pattern, filtered_content, re.IGNORECASE)
        # ... 提取并规范化Fault ID
```

### 报告生成流程

```python
def create_report_document(self, ticket_id, ticket_info, analysis_results):
    # 1. 创建飞书文档
    doc_info = self.doc_collaborator._create_doc(...)
    
    # 2. 生成报告内容结构
    blocks = self._generate_report_content(...)
    
    # 3. 写入文档内容
    self._write_document_content(doc_info['document_id'], blocks)
    
    # 4. 返回文档信息（包含链接）
    return doc_info
```

---

## 使用说明

### 1. 添加新的指引文档

在 `work/fault_diagnosis_guides_config.json` 中添加新文档：

```json
{
  "guide_docs": [
    {
      "name": "故障定位指引文档5",
      "node_token": "R3NowdLHoiVOtMks6lzcW7sYnCf",
      "url": "https://zyt.feishu.cn/wiki/R3NowdLHoiVOtMks6lzcW7sYnCf"
    }
  ]
}
```

系统会自动加载新文档。

### 2. 在指引文档中编写grep命令

在指引文档的表格中，可以在"grep模式"或"命令"列中写入grep命令：

```
| Fault ID | grep模式 | 故障描述 |
|----------|----------|----------|
| 0x0165   | zcat log.gz \|grep SetFunc \|grep -E "fu_st:0x3\|fu_st:0x4" | 轨迹丢失 |
```

系统会自动解析命令语义并应用。

### 3. 查看生成的报告

运行故障定位系统后，系统会：
1. 生成飞书文档报告
2. 将文档链接回填到"工具回传"字段
3. 点击链接即可查看完整的结构化报告

---

## 测试建议

1. **测试grep命令解析**：
   - 使用包含复杂grep命令的指引文档
   - 验证系统能正确解析并应用过滤条件

2. **测试报告生成**：
   - 运行完整的故障定位流程
   - 验证报告文档创建成功
   - 验证文档链接正确回填

3. **测试第5个文档加载**：
   - 验证系统能加载所有5个指引文档
   - 验证新文档中的Fault ID能被正确识别

---

## 注意事项

1. **grep命令格式**：
   - 支持标准的grep命令格式
   - 支持管道命令（`|`）
   - 支持扩展正则表达式（`-E`）

2. **报告文档位置**：
   - 报告文档创建在Wiki知识库的根目录
   - 可以通过配置 `parent_node_token` 指定父目录

3. **文档权限**：
   - 确保 `user_access_token` 有创建Wiki文档的权限
   - 需要 `wiki:node:create` 和 `docx:document` 权限

---

## 总结

本次改进实现了三个核心功能：
1. ✅ 支持第5个指引文档（自动加载）
2. ✅ 理解grep命令语义并智能提取Fault ID
3. ✅ 生成结构化飞书文档报告并回填链接

系统现在能够更智能地处理故障定位指引，生成更易读的分析报告，提升用户体验。

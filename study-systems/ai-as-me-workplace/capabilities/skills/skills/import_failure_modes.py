# -*- coding: utf-8 -*-
"""
失效模式导入器

从FMEA数据中提取失效模式并导入到"失效模式影响分析表_SW"
注意：Function Description是合并单元格，一个功能对应多个Guide Word
"""

import sys
import os
import time
from typing import Dict, List, Any, Optional

# 修复Windows控制台编码问题
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fmea_data_reader import FMEADataReader
from fmea_import_utils import FMEAImportUtils
from feishu_bitable_collaborator import create_bitable_collaborator
from feishu_api_wrapper import FeishuAPI
from bitable_cache_manager import APP_ID, APP_SECRET

# 配置
BATCH_SIZE = 500  # 每批最多500条记录
MAX_RETRIES = 3
RETRY_DELAY = 2


class FailureModeImporter:
    """失效模式导入器"""
    
    def __init__(
        self,
        app_token: str,
        table_id: str,
        function_table_id: str,
        user_access_token: str = None
    ):
        """
        初始化导入器
        
        Args:
            app_token: 多维表格app_token
            table_id: 失效模式影响分析表_SW的table_id
            function_table_id: 子功能清单表的table_id（用于查找功能记录）
            user_access_token: 用户访问令牌
        """
        self.app_token = app_token
        self.table_id = table_id
        self.function_table_id = function_table_id
        self.user_access_token = user_access_token or os.getenv("FEISHU_USER_ACCESS_TOKEN")
        
        self.utils = FMEAImportUtils(app_token, user_access_token)
        
        # 获取表格结构信息
        self.structure_info = self.utils.get_table_structure_info(table_id)
        self.field_name_to_id = self.structure_info['field_name_to_id']
        
        # 获取子功能清单表的结构
        self.function_structure_info = self.utils.get_table_structure_info(function_table_id)
        
        # 统计信息
        self.stats = {
            'total': 0,
            'created': 0,
            'existing': 0,
            'failed': 0,
            'skipped': 0,  # 跳过的（找不到对应的功能）
            'errors': []
        }
        
        # Function Description到record_id的映射（从子功能清单表加载）
        self.function_to_record_id = {}
    
    def load_function_mappings(self):
        """从子功能清单表加载Function Description到record_id的映射"""
        print("加载子功能清单表的映射关系...")
        
        records = self.utils.collaborator.get_all_records(
            self.app_token,
            self.function_table_id
        )
        
        for record in records:
            record_fields = record.get('fields', {})
            function_description = record_fields.get('功能描述', '')
            
            # 处理富文本格式，提取纯文本
            func_text = self._extract_text_from_richtext(function_description)
            
            if func_text and func_text.strip():
                # 使用纯文本作为key
                self.function_to_record_id[func_text.strip()] = record.get('record_id')
        
        print(f"[OK] 加载了 {len(self.function_to_record_id)} 个功能的映射")
    
    def prepare_failure_mode_rows(
        self,
        fmea_rows: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        准备失效模式行数据（处理合并单元格）
        
        Args:
            fmea_rows: FMEA行数据列表
            
        Returns:
            处理后的行数据列表，每行包含完整的字段信息
        """
        prepared_rows = []
        last_function = None
        last_element = None
        
        for row in fmea_rows:
            # 处理Element Name（合并单元格）
            elem = row.get('Element Name')
            if elem and str(elem).strip():
                last_element = str(elem).strip()
            
            # 处理Function Description（合并单元格，可能是富文本格式）
            func = row.get('Function Description', '')
            func_str = self._extract_text_from_richtext(func)
            # 如果Function Description为空或带删除线，跳过这一行
            if func_str and func_str.strip():
                last_function = func_str.strip()
            else:
                # Function Description为空或带删除线，跳过这一行
                continue
            
            # 获取其他字段
            guide_word = row.get('Guide Word', '')
            failure_mode = row.get('Potential Failure Mode', '')
            failure_effect = row.get('Potential Failure Effect', '')
            safety_related = row.get('Safety Related？', '')
            
            # 只处理有失效模式数据的行（至少要有Guide Word或Potential Failure Mode）
            # 并且Function Description必须有效（不为空且不带删除线）
            if (guide_word and str(guide_word).strip()) or (failure_mode and str(failure_mode).strip()):
                # 使用填充后的Function Description
                func_str = last_function if last_function else None
                
                # 如果Function Description为空或带删除线，跳过这一行
                if func_str and func_str.strip():
                    # 提取其他字段的文本（可能也是富文本）
                    guide_word_str = self._extract_text_from_richtext(guide_word)
                    failure_mode_str = self._extract_text_from_richtext(failure_mode)
                    failure_effect_str = self._extract_text_from_richtext(failure_effect)
                    safety_related_str = self._extract_text_from_richtext(safety_related)
                    
                    # 如果Element Name为空，尝试从function_to_record_id中查找对应的功能
                    # 然后通过功能找到对应的架构元素
                    elem_str = last_element if last_element else str(elem or '').strip()
                    
                    # 如果Element Name仍然为空，尝试从已加载的功能映射中推断
                    if not elem_str:
                        # 通过Function Description查找对应的功能记录，然后查找架构元素
                        # 这需要额外的查询，暂时跳过
                        pass
                    
                    prepared_rows.append({
                        'Function Description': func_str,
                        'Element Name': elem_str,
                        'Guide Word': guide_word_str.strip() if guide_word_str else '',
                        'Potential Failure Mode': failure_mode_str.strip() if failure_mode_str else '',
                        'Potential Failure Effect': failure_effect_str.strip() if failure_effect_str else '',
                        'Safety Related？': safety_related_str.strip() if safety_related_str else ''
                    })
        
        return prepared_rows
    
    def prepare_failure_mode_record(
        self,
        row_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        准备失效模式记录数据
        
        Args:
            row_data: 处理后的行数据
            
        Returns:
            字段数据字典，如果找不到对应的功能则返回None
        """
        function_description = row_data.get('Function Description', '').strip()
        
        # 查找对应的功能record_id（使用纯文本匹配）
        function_record_id = self.function_to_record_id.get(function_description)
        
        # 如果精确匹配失败，尝试模糊匹配（去除换行符、空格等）
        if not function_record_id:
            func_normalized = function_description.replace('\n', ' ').replace('\r', ' ').strip()
            for key, record_id in self.function_to_record_id.items():
                key_normalized = key.replace('\n', ' ').replace('\r', ' ').strip()
                if func_normalized == key_normalized:
                    function_record_id = record_id
                    break
        
        if not function_record_id:
            # 找不到对应的功能，跳过
            return None
        
        fields = {}
        
        # 关联功能（双向关联字段，需要传入记录ID数组）
        function_field_name = '关联功能'
        if function_field_name in self.field_name_to_id:
            fields[function_field_name] = [function_record_id]
        
        # 引导词（需要匹配选项值）
        guide_word = row_data.get('Guide Word', '').strip()
        if guide_word:
            guide_word_field_name = '引导词'
            if guide_word_field_name in self.field_name_to_id:
                # 获取字段信息以匹配选项值
                field_id = self.field_name_to_id[guide_word_field_name]
                field_info = None
                for field in self.structure_info['fields']:
                    if field.get('field_id') == field_id:
                        field_info = field
                        break
                
                # 尝试匹配选项值
                matched_guide_word = self._match_guide_word_option(guide_word, field_info)
                if matched_guide_word:
                    fields[guide_word_field_name] = matched_guide_word
                else:
                    # 如果找不到匹配，使用原始值（让API决定）
                    # 注意：如果API不接受，可能需要手动添加选项值
                    fields[guide_word_field_name] = guide_word
        
        # 实际识别的失效模式
        failure_mode = row_data.get('Potential Failure Mode', '').strip()
        if failure_mode:
            failure_mode_field_name = '实际识别的失效模式'
            if failure_mode_field_name in self.field_name_to_id:
                fields[failure_mode_field_name] = failure_mode
        
        # 潜在失效影响
        failure_effect = row_data.get('Potential Failure Effect', '').strip()
        if failure_effect:
            failure_effect_field_name = '潜在失效影响'
            if failure_effect_field_name in self.field_name_to_id:
                fields[failure_effect_field_name] = failure_effect
        
        # SW_Safety Related
        safety_related = row_data.get('Safety Related？', '').strip()
        if safety_related:
            safety_related_field_name = 'SW_Safety Related'
            if safety_related_field_name in self.field_name_to_id:
                # 处理选项值映射
                safety_related_lower = safety_related.lower()
                if 'yes' in safety_related_lower or '是' in safety_related_lower or safety_related == 'Y':
                    fields[safety_related_field_name] = '是'
                elif 'no' in safety_related_lower or '否' in safety_related_lower or safety_related == 'N':
                    fields[safety_related_field_name] = '否'
                else:
                    fields[safety_related_field_name] = safety_related
        
        return fields if fields else None
    
    def _match_guide_word_option(
        self,
        guide_word: str,
        field_info: Optional[Dict[str, Any]]
    ) -> Optional[str]:
        """
        匹配引导词选项值
        
        Args:
            guide_word: FMEA表格中的引导词值
            field_info: 字段信息（包含选项列表）
            
        Returns:
            匹配的选项值，如果找不到则返回None
        """
        if not field_info:
            return None
        
        # 引导词映射（FMEA表格值 -> 多维表格值）
        guide_word_mapping = {
            "no/loss": "缺失",
            "no": "缺失",
            "loss": "缺失",
            "missing": "缺失",
            "stuck": "错误",
            "wrong": "错误",
            "earlier": "过早",
            "early": "过早",
            "later": "过晚",
            "late": "过晚",
            "corrupted": "错误",
            "corrupt": "错误",
            "incomplete": "不完整",
            "inaccurate": "不准确",
            "untimely": "不及时",
            "无": "无",
            "缺失": "缺失",
            "错误": "错误",
            "过早": "过早",
            "过晚": "过晚",
            "不准确": "不准确",
            "不完整": "不完整",
            "不及时": "不及时",
            "其他": "其他"
        }
        
        guide_word_lower = guide_word.lower()
        
        # 1. 优先使用映射表
        if guide_word_lower in guide_word_mapping:
            mapped_value = guide_word_mapping[guide_word_lower]
            # 检查映射后的值是否在多维表格的选项中
            if field_info:
                property_info = field_info.get('property')
                if property_info and isinstance(property_info, dict):
                    options = property_info.get('options', [])
                    for option in options:
                        if option.get('name') == mapped_value:
                            return mapped_value
            # 如果字段信息不可用，直接返回映射值
            return mapped_value
        
        # 2. 直接检查多维表格的选项（精确匹配）
        if field_info:
            property_info = field_info.get('property')
            if property_info and isinstance(property_info, dict):
                options = property_info.get('options', [])
                for option in options:
                    option_name = option.get('name', '')
                    if guide_word == option_name or guide_word_lower == option_name.lower():
                        return option_name
        
        # 3. 模糊匹配多维表格的选项
        if field_info:
            property_info = field_info.get('property')
            if property_info and isinstance(property_info, dict):
                options = property_info.get('options', [])
                for option in options:
                    option_name = option.get('name', '')
                    option_lower = option_name.lower()
                    if guide_word_lower in option_lower or option_lower in guide_word_lower:
                        return option_name
        
        return None
    
    def _extract_text_from_richtext(self, value: Any) -> Optional[str]:
        """
        从富文本格式中提取纯文本
        
        Args:
            value: 可能是字符串、列表（富文本）或其他格式
            
        Returns:
            提取的纯文本字符串，如果有删除线或没有内容则返回None（表示应跳过）
        """
        if not value:
            return None  # 没有内容，返回None表示跳过
        
        if isinstance(value, list):
            # 富文本格式：列表，每个元素是包含'text'字段的字典
            text_parts = []
            has_strikethrough = False
            
            for item in value:
                if isinstance(item, dict) and 'text' in item:
                    # 检查是否有删除线
                    segment_style = item.get('segmentStyle', {})
                    if segment_style.get('strikeThrough', False):
                        has_strikethrough = True
                    text_parts.append(str(item['text']))
            
            # 如果有删除线，返回None表示跳过
            if has_strikethrough:
                return None
            
            # 如果没有文本内容，返回None
            if not text_parts:
                return None
            
            return ''.join(text_parts)
        else:
            text = str(value).strip()
            return text if text else None
    
    def import_failure_modes(
        self,
        fmea_rows: List[Dict[str, Any]],
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        导入失效模式
        
        Args:
            fmea_rows: FMEA行数据列表
            dry_run: 是否为试运行
            
        Returns:
            导入结果字典
        """
        self.stats = {
            'total': 0,
            'created': 0,
            'existing': 0,
            'failed': 0,
            'skipped': 0,
            'errors': []
        }
        
        print("\n开始导入失效模式...")
        print("=" * 80)
        
        # 1. 加载功能映射
        self.load_function_mappings()
        print()
        
        # 2. 准备失效模式行数据（处理合并单元格）
        print("处理合并单元格，准备失效模式数据...")
        prepared_rows = self.prepare_failure_mode_rows(fmea_rows)
        self.stats['total'] = len(prepared_rows)
        
        print(f"[OK] 找到 {len(prepared_rows)} 行失效模式数据")
        if len(prepared_rows) <= 10:
            for i, row in enumerate(prepared_rows[:10], 1):
                print(f"  {i}. {row.get('Function Description', '')[:50]} | {row.get('Guide Word', '')[:20]} | {row.get('Potential Failure Mode', '')[:30]}")
        else:
            print("  前5行:")
            for i, row in enumerate(prepared_rows[:5], 1):
                print(f"    {i}. {row.get('Function Description', '')[:50]} | {row.get('Guide Word', '')[:20]}")
        print()
        
        if dry_run:
            print("[试运行] 准备导入的失效模式:")
            for i, row in enumerate(prepared_rows[:10], 1):
                fields = self.prepare_failure_mode_record(row)
                if fields:
                    print(f"  {i}. {fields}")
                else:
                    print(f"  {i}. [跳过，找不到对应的功能]")
            return {
                'success': True,
                'dry_run': True,
                'stats': self.stats
            }
        
        # 3. 批量导入失效模式
        print(f"批量导入失效模式（每批最多 {BATCH_SIZE} 条）...")
        print()
        
        records_to_create = []
        skipped_items = []  # 记录跳过的条目详情
        
        for row_data in prepared_rows:
            fields = self.prepare_failure_mode_record(row_data)
            
            if fields:
                records_to_create.append({"fields": fields})
            else:
                self.stats['skipped'] += 1
                # 记录跳过的条目详情
                skipped_items.append({
                    'reason': '找不到对应的功能',
                    'data': {
                        'Function Description': row_data.get('Function Description', ''),
                        'Element Name': row_data.get('Element Name', ''),
                        'Guide Word': row_data.get('Guide Word', ''),
                        'Potential Failure Mode': row_data.get('Potential Failure Mode', '')[:100] if row_data.get('Potential Failure Mode') else ''
                    }
                })
        
        print(f"准备就绪的记录数: {len(records_to_create)}")
        print(f"跳过的记录数: {self.stats['skipped']}")
        
        # 打印跳过的条目详情
        if skipped_items:
            print("\n跳过的条目详情:")
            for i, item in enumerate(skipped_items[:10], 1):  # 只显示前10个
                print(f"  {i}. {item['reason']}")
                data = item.get('data', {})
                func_desc = data.get('Function Description', '')
                if func_desc:
                    print(f"     功能描述: {func_desc[:60]}...")
                guide_word = data.get('Guide Word', '')
                if guide_word:
                    print(f"     引导词: {guide_word}")
            if len(skipped_items) > 10:
                print(f"     ... 还有 {len(skipped_items) - 10} 条跳过的记录")
        print()
        
        if not records_to_create:
            print("[!] 没有可导入的记录")
            return {
                'success': False,
                'stats': self.stats
            }
        
        # 分批导入
        total_batches = (len(records_to_create) + BATCH_SIZE - 1) // BATCH_SIZE
        
        for batch_idx in range(total_batches):
            start_idx = batch_idx * BATCH_SIZE
            end_idx = min(start_idx + BATCH_SIZE, len(records_to_create))
            batch_records = records_to_create[start_idx:end_idx]
            
            print(f"[{batch_idx + 1}/{total_batches}] 导入第 {start_idx + 1}-{end_idx} 条记录...", end=' ')
            
            try:
                result = self.utils.api.batch_create_bitable_records(
                    self.app_token,
                    self.table_id,
                    batch_records,
                    use_user_token=True
                )
                
                if not result:
                    raise Exception("API返回为空")
                
                # 检查返回结果
                if 'code' in result:
                    if result.get('code') == 0:
                        data = result.get('data', {})
                        items = data.get('items', [])
                        created_count = len(items)
                        self.stats['created'] += created_count
                        print(f"[OK] 成功: {created_count}")
                    else:
                        error_msg = result.get('msg', '未知错误')
                        error_detail = result.get('error', {})
                        if isinstance(error_detail, dict):
                            error_detail_msg = error_detail.get('message', '')
                            if error_detail_msg:
                                error_msg = f"{error_msg} - {error_detail_msg}"
                        raise Exception(f"API错误: {error_msg}")
                elif 'records' in result:
                    # 直接返回records格式（成功）
                    records = result.get('records', [])
                    created_count = len(records)
                    self.stats['created'] += created_count
                    print(f"[OK] 成功: {created_count}")
                elif 'data' in result:
                    # 直接返回data格式
                    data = result.get('data', {})
                    items = data.get('items', [])
                    created_count = len(items)
                    self.stats['created'] += created_count
                    print(f"[OK] 成功: {created_count}")
                elif 'items' in result:
                    # 直接包含items
                    created_count = len(result['items'])
                    self.stats['created'] += created_count
                    print(f"[OK] 成功: {created_count}")
                else:
                    # 打印详细错误信息用于调试
                    import json
                    error_detail = json.dumps(result, ensure_ascii=False, indent=2)[:500]
                    raise Exception(f"返回格式异常: {error_detail}")
            
            except Exception as e:
                self.stats['failed'] += len(batch_records)
                self.stats['errors'].append({
                    'batch': batch_idx + 1,
                    'error': str(e)
                })
                print(f"[X] 失败: {str(e)}")
            
            # 避免请求过快
            if batch_idx < total_batches - 1:
                time.sleep(0.5)
        
        print()
        print("=" * 80)
        print("失效模式导入完成")
        print("=" * 80)
        print(f"总计: {self.stats['total']}")
        print(f"成功: {self.stats['created']}")
        print(f"失败: {self.stats['failed']}")
        print(f"跳过: {self.stats['skipped']} (找不到对应的功能)")
        
        if self.stats['errors']:
            print(f"\n错误详情（前5个）:")
            for error in self.stats['errors'][:5]:
                print(f"  批次 {error['batch']}: {error['error']}")
        
        return {
            'success': self.stats['failed'] == 0,
            'stats': {
                **self.stats,
                'skipped_items': skipped_items  # 包含跳过的条目详情
            }
        }


def main():
    """测试函数"""
    # 这里需要实际的app_token和table_id
    app_token = "test_app_token"
    table_id = "test_table_id"
    function_table_id = "test_function_table_id"
    
    importer = FailureModeImporter(app_token, table_id, function_table_id)
    
    # 测试数据
    test_rows = [
        {
            'Element Name': 'CtrlReciver',
            'Function Description': 'Receive the PoseData from Egomotion',
            'Guide Word': 'Missing',
            'Potential Failure Mode': 'No data received',
            'Potential Failure Effect': 'System cannot function',
            'Safety Related？': 'Yes'
        },
        {
            'Element Name': '',
            'Function Description': '',  # 合并单元格
            'Guide Word': 'Wrong',
            'Potential Failure Mode': 'Incorrect data',
            'Potential Failure Effect': 'System error',
            'Safety Related？': 'No'
        }
    ]
    
    result = importer.import_failure_modes(test_rows, dry_run=True)
    print(result)


if __name__ == "__main__":
    main()

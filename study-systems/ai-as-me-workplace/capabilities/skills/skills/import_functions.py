# -*- coding: utf-8 -*-
"""
子功能导入器

从FMEA数据中提取功能（Function Description）并导入到"子功能清单表"，关联到架构元素
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

# 配置
BATCH_SIZE = 100  # 每批最多100条记录
MAX_RETRIES = 3
RETRY_DELAY = 2


class FunctionImporter:
    """子功能导入器"""
    
    def __init__(
        self,
        app_token: str,
        table_id: str,
        element_name_to_record_id: Dict[str, str],
        user_access_token: str = None
    ):
        """
        初始化导入器
        
        Args:
            app_token: 多维表格app_token
            table_id: 子功能清单表的table_id
            element_name_to_record_id: Element Name到record_id的映射（从架构元素导入器获取）
            user_access_token: 用户访问令牌
        """
        self.app_token = app_token
        self.table_id = table_id
        self.element_name_to_record_id = element_name_to_record_id
        self.utils = FMEAImportUtils(app_token, user_access_token)
        
        # 获取表格结构信息
        self.structure_info = self.utils.get_table_structure_info(table_id)
        self.field_name_to_id = self.structure_info['field_name_to_id']
        
        # 统计信息
        self.stats = {
            'total': 0,
            'created': 0,
            'existing': 0,
            'failed': 0,
            'skipped': 0,  # 跳过的（找不到对应的架构元素）
            'errors': []
        }
        
        # Function Description到record_id的映射（用于后续关联）
        self.function_to_record_id = {}
    
    def extract_function_element_pairs(
        self,
        fmea_rows: List[Dict[str, Any]]
    ) -> List[Dict[str, str]]:
        """
        从FMEA数据中提取Function Description和Element Name的对应关系
        注意：Element Name可能是合并单元格，需要填充空值
        
        Args:
            fmea_rows: FMEA行数据列表
            
        Returns:
            对应关系列表，每个元素是 {'Function Description': value1, 'Element Name': value2}
        """
        # 先处理合并单元格：填充空的Element Name
        filled_rows = []
        last_elem = None
        
        for row in fmea_rows:
            elem = row.get('Element Name')
            func = row.get('Function Description', '')
            
            # 处理Element Name（合并单元格）
            if elem and str(elem).strip():
                last_elem = str(elem).strip()
            
            # 处理Function Description（可能是富文本格式）
            func_str = self._extract_text_from_richtext(func)
            
            # 只处理有Function Description的行，且没有删除线
            if func_str and func_str.strip():
                # 如果Element Name为空，使用上一个非空值
                elem_str = last_elem if last_elem else str(elem or '').strip()
                
                # 如果Element Name仍然为空，尝试从element_name_to_record_id中推断
                # （这通常意味着需要从FMEA名称推断，已在架构元素导入时处理）
                if not elem_str and self.element_name_to_record_id:
                    # 如果只有一个架构元素，使用它
                    if len(self.element_name_to_record_id) == 1:
                        elem_str = list(self.element_name_to_record_id.keys())[0]
                
                # 如果Element Name仍然为空，但Function Description有效，仍然添加
                # （后续可以通过其他方式关联架构元素）
                if func_str:
                    filled_rows.append({
                        'Function Description': func_str.strip(),
                        'Element Name': elem_str if elem_str else None
                    })
        
        return filled_rows
    
    def _extract_text_from_richtext(self, value: Any) -> Optional[str]:
        """
        从富文本格式中提取纯文本
        
        Args:
            value: 可能是字符串、列表（富文本）或其他格式
            
        Returns:
            提取的纯文本字符串，如果有删除线则返回None（表示应跳过）
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
    
    def prepare_function_record(
        self,
        function_description: str,
        element_name: str
    ) -> Optional[Dict[str, Any]]:
        """
        准备子功能记录数据
        
        Args:
            function_description: 功能描述（已提取纯文本）
            element_name: 对应的Element Name
            
        Returns:
            字段数据字典，如果找不到对应的架构元素则返回None
        """
        # 如果Element Name为空，尝试从唯一的架构元素推断
        if not element_name and len(self.element_name_to_record_id) == 1:
            element_name = list(self.element_name_to_record_id.keys())[0]
        
        # 查找对应的架构元素record_id
        element_record_id = self.element_name_to_record_id.get(element_name) if element_name else None
        
        if not element_record_id:
            # 找不到对应的架构元素，跳过
            return None
        
        # 确保功能描述是纯文本（去除多余的换行符和空格）
        func_text = function_description.replace('\n', ' ').replace('\r', ' ').strip()
        
        fields = {
            '功能描述': func_text
        }
        
        # 处理"架构元素"字段（双向关联）
        # 双向关联字段需要传入记录ID数组
        architecture_field_name = '架构元素'
        if architecture_field_name in self.field_name_to_id:
            fields[architecture_field_name] = [element_record_id]
        
        return fields
    
    def import_functions(
        self,
        fmea_rows: List[Dict[str, Any]],
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        导入子功能
        
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
        
        print("\n开始导入子功能...")
        print("=" * 80)
        
        # 1. 提取Function Description和Element Name的对应关系
        print("提取Function Description和Element Name的对应关系...")
        function_element_pairs = self.extract_function_element_pairs(fmea_rows)
        self.stats['total'] = len(function_element_pairs)
        
        # 先推断空的Element Name（在打印之前）
        inferred_count = 0
        if self.element_name_to_record_id:
            # 找出非Control的架构元素（通常Control是父元素）
            non_control_elements = [name for name in self.element_name_to_record_id.keys() if name != 'Control']
            
            # 如果只有一个非Control元素，使用它来推断
            if len(non_control_elements) == 1:
                inferred_name = non_control_elements[0]
                for pair in function_element_pairs:
                    element_name = pair.get('Element Name')
                    if not element_name or element_name is None:
                        # 更新pair的Element Name
                        pair['Element Name'] = inferred_name
                        inferred_count += 1
                
                if inferred_count > 0:
                    print(f"[!] 推断Element Name: {inferred_name} (从唯一非Control架构元素，共{inferred_count}个功能)")
            elif len(self.element_name_to_record_id) == 1:
                # 如果只有一个架构元素（可能是Control），也使用它
                inferred_name = list(self.element_name_to_record_id.keys())[0]
                for pair in function_element_pairs:
                    element_name = pair.get('Element Name')
                    if not element_name or element_name is None:
                        pair['Element Name'] = inferred_name
                        inferred_count += 1
                
                if inferred_count > 0:
                    print(f"[!] 推断Element Name: {inferred_name} (从唯一架构元素，共{inferred_count}个功能)")
        
        print(f"[OK] 找到 {len(function_element_pairs)} 个唯一的Function-Element对应关系")
        if len(function_element_pairs) <= 20:
            for pair in function_element_pairs:
                print(f"  - {pair['Function Description']} -> {pair['Element Name']}")
        else:
            print(f"  前10个:")
            for pair in function_element_pairs[:10]:
                print(f"    - {pair['Function Description']} -> {pair['Element Name']}")
        print()
        
        # 检查有多少能找到对应的架构元素
        found_elements = 0
        missing_elements = set()
        for pair in function_element_pairs:
            element_name = pair.get('Element Name')
            if element_name and element_name in self.element_name_to_record_id:
                found_elements += 1
            elif element_name:
                missing_elements.add(element_name)
            else:
                missing_elements.add('(空)')
        
        if missing_elements:
            print(f"[!] 警告: {len(missing_elements)} 个Element Name找不到对应的架构元素:")
            for name in list(missing_elements)[:10]:
                print(f"    - {name}")
            print()
        
        if dry_run:
            print("[试运行] 准备导入的子功能:")
            for pair in function_element_pairs[:10]:
                fields = self.prepare_function_record(
                    pair['Function Description'],
                    pair['Element Name']
                )
                if fields:
                    print(f"  - {pair['Function Description']}: {fields}")
                else:
                    print(f"  - {pair['Function Description']}: [跳过，找不到架构元素]")
            return {
                'success': True,
                'dry_run': True,
                'stats': self.stats,
                'function_to_record_id': {}
            }
        
        # 2. 批量导入子功能
        print(f"批量导入子功能（每批最多 {BATCH_SIZE} 条）...")
        print()
        
        total_batches = (len(function_element_pairs) + BATCH_SIZE - 1) // BATCH_SIZE
        all_skipped_items = []  # 记录所有跳过的条目详情
        
        for batch_idx in range(total_batches):
            start_idx = batch_idx * BATCH_SIZE
            end_idx = min(start_idx + BATCH_SIZE, len(function_element_pairs))
            batch_pairs = function_element_pairs[start_idx:end_idx]
            
            print(f"[{batch_idx + 1}/{total_batches}] 导入第 {start_idx + 1}-{end_idx} 个功能...", end=' ')
            
            batch_created = 0
            batch_existing = 0
            batch_failed = 0
            batch_skipped = 0
            skipped_items = []  # 记录跳过的条目详情
            
            for pair in batch_pairs:
                function_description = pair['Function Description']
                element_name = pair['Element Name']
                
                try:
                    # 准备记录数据
                    fields = self.prepare_function_record(function_description, element_name)
                    
                    if not fields:
                        # 找不到对应的架构元素，跳过
                        batch_skipped += 1
                        self.stats['skipped'] += 1
                        skipped_items.append({
                            'reason': f'找不到对应的架构元素: {element_name}',
                            'data': {
                                'Function Description': function_description,
                                'Element Name': element_name
                            }
                        })
                        continue
                    
                    # 查找或创建记录
                    # 注意：同一个Function Description可能对应多个Element Name
                    # 这里使用Function Description + Element Name的组合来查找
                    # 但由于"架构元素"是关联字段，我们需要先检查是否已存在相同的Function Description和架构元素组合
                    result = self.utils.find_or_create_record(
                        self.table_id,
                        fields,
                        search_field='功能描述',
                        search_value=function_description
                    )
                    
                    if result['created']:
                        batch_created += 1
                        self.stats['created'] += 1
                    else:
                        # 检查已存在的记录是否关联到相同的架构元素
                        existing_record = result['record']
                        existing_fields = existing_record.get('fields', {})
                        
                        # 获取架构元素字段的ID
                        architecture_field_id = self.field_name_to_id.get('架构元素')
                        if architecture_field_id:
                            existing_element_ids = existing_fields.get(architecture_field_id, [])
                            if isinstance(existing_element_ids, list):
                                element_record_id = self.element_name_to_record_id.get(element_name)
                                if element_record_id not in existing_element_ids:
                                    # 需要更新记录，添加新的架构元素关联
                                    # 这里暂时跳过，因为更新关联比较复杂
                                    batch_existing += 1
                                    self.stats['existing'] += 1
                                else:
                                    batch_existing += 1
                                    self.stats['existing'] += 1
                            else:
                                batch_existing += 1
                                self.stats['existing'] += 1
                        else:
                            batch_existing += 1
                            self.stats['existing'] += 1
                    
                    # 保存映射（使用Function Description作为key）
                    # 注意：如果有多个Element Name对应同一个Function Description，
                    # 这里只保存最后一个，后续可能需要优化
                    self.function_to_record_id[function_description] = result['record_id']
                    
                except Exception as e:
                    batch_failed += 1
                    self.stats['failed'] += 1
                    self.stats['errors'].append({
                        'function_description': function_description,
                        'element_name': element_name,
                        'error': str(e)
                    })
            
            print(f"[OK] 新建: {batch_created}, 已存在: {batch_existing}, 跳过: {batch_skipped}, 失败: {batch_failed}")
            
            # 收集跳过的条目
            all_skipped_items.extend(skipped_items)
            
            # 避免请求过快
            if batch_idx < total_batches - 1:
                time.sleep(0.5)
        
        print()
        print("=" * 80)
        print("子功能导入完成")
        print("=" * 80)
        print(f"总计: {self.stats['total']}")
        print(f"新建: {self.stats['created']}")
        print(f"已存在: {self.stats['existing']}")
        print(f"跳过: {self.stats['skipped']} (找不到对应的架构元素)")
        print(f"失败: {self.stats['failed']}")
        
        if self.stats['errors']:
            print(f"\n错误详情（前5个）:")
            for error in self.stats['errors'][:5]:
                print(f"  {error['function_description']} ({error['element_name']}): {error['error']}")
        
        return {
            'success': self.stats['failed'] == 0,
            'stats': {
                **self.stats,
                'skipped_items': all_skipped_items  # 包含跳过的条目详情
            },
            'function_to_record_id': self.function_to_record_id
        }


def main():
    """测试函数"""
    # 这里需要实际的app_token和table_id
    app_token = "test_app_token"
    table_id = "test_table_id"
    element_name_to_record_id = {'Element1': 'rec1', 'Element2': 'rec2'}
    
    importer = FunctionImporter(app_token, table_id, element_name_to_record_id)
    
    # 测试数据
    test_rows = [
        {'Element Name': 'Element1', 'Function Description': 'Func1'},
        {'Element Name': 'Element2', 'Function Description': 'Func2'},
        {'Element Name': 'Element1', 'Function Description': 'Func3'},
    ]
    
    result = importer.import_functions(test_rows, dry_run=True)
    print(result)


if __name__ == "__main__":
    main()

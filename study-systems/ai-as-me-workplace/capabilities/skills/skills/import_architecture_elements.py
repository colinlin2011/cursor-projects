# -*- coding: utf-8 -*-
"""
架构元素导入器

从FMEA数据中提取架构元素（Element Name）并导入到"架构元素表"
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
BATCH_SIZE = 100  # 每批最多100条记录（架构元素通常不会太多）
MAX_RETRIES = 3
RETRY_DELAY = 2


class ArchitectureElementImporter:
    """架构元素导入器"""
    
    def __init__(
        self,
        app_token: str,
        table_id: str,
        user_access_token: str = None
    ):
        """
        初始化导入器
        
        Args:
            app_token: 多维表格app_token
            table_id: 架构元素表的table_id
            user_access_token: 用户访问令牌
        """
        self.app_token = app_token
        self.table_id = table_id
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
            'errors': []
        }
        
        # Element Name到record_id的映射（用于后续关联）
        self.element_name_to_record_id = {}
    
    def find_or_create_control_parent(self, dry_run: bool = False) -> Optional[str]:
        """
        查找或创建"Control"父元素
        
        Args:
            dry_run: 是否为试运行模式
            
        Returns:
            Control记录的record_id，如果失败则返回None
        """
        print("查找或创建Control父元素...")
        
        # 查找是否已存在
        existing = self.utils.find_record_by_field_value(
            self.table_id,
            '元素名称',
            'Control',
            exact_match=True
        )
        
        if existing:
            record_id = existing.get('record_id')
            print(f"[OK] Control父元素已存在: {record_id}")
            self.element_name_to_record_id['Control'] = record_id
            return record_id
        
        # 如果不存在，创建Control父元素
        if dry_run:
            print("[试运行] Control父元素不存在，将在实际导入时创建")
            # 返回一个模拟的record_id用于试运行
            mock_record_id = "rec_control_mock"
            self.element_name_to_record_id['Control'] = mock_record_id
            return mock_record_id
        
        print("[!] Control父元素不存在，正在创建...")
        
        # 准备字段数据
        fields = {
            '元素名称': 'Control',
            '架构层级': '软件层',
            '元素类型': '应用算法'
        }
        
        result = self.utils.find_or_create_record(
            self.table_id,
            fields,
            search_field='元素名称',
            search_value='Control'
        )
        
        if result['created']:
            print(f"[OK] Control父元素创建成功: {result['record_id']}")
        else:
            print(f"[OK] Control父元素已存在: {result['record_id']}")
        
        self.element_name_to_record_id['Control'] = result['record_id']
        return result['record_id']
    
    def extract_element_names(
        self, 
        fmea_rows: List[Dict[str, Any]], 
        fmea_name: Optional[str] = None
    ) -> List[str]:
        """
        从FMEA数据中提取唯一的Element Name
        
        Args:
            fmea_rows: FMEA行数据列表
            fmea_name: FMEA表格名称（用于推断Element Name，如果数据中为空）
            
        Returns:
            唯一的Element Name列表
        """
        element_names = self.utils.extract_unique_values(fmea_rows, 'Element Name')
        
        # 如果Element Name为空，尝试从FMEA名称推断
        if not element_names and fmea_name:
            # 从FMEA名称中提取Element Name
            # 例如：08_SceneNet_System_SW_FMEA -> SceneNet
            # 或者：Control_System_SW_FMEA -> Control
            parts = fmea_name.split('_')
            for part in parts:
                # 跳过数字和常见后缀
                if part and not part.isdigit() and part not in ['System', 'SW', 'FMEA', 'HW']:
                    element_names = [part]
                    print(f"[!] Element Name为空，从FMEA名称推断: {part}")
                    break
        
        return element_names
    
    def prepare_element_record(
        self,
        element_name: str,
        control_record_id: str
    ) -> Dict[str, Any]:
        """
        准备架构元素记录数据
        
        Args:
            element_name: 元素名称
            control_record_id: Control父元素的record_id
            
        Returns:
            字段数据字典
        """
        fields = {
            '元素名称': element_name,
            '架构层级': '软件层',
            '元素类型': '应用算法'
        }
        
        # 处理"所属父元素"字段（双向关联）
        # 双向关联字段需要传入记录ID数组
        parent_field_name = '所属父元素'
        if parent_field_name in self.field_name_to_id:
            fields[parent_field_name] = [control_record_id]
        
        return fields
    
    def import_elements(
        self,
        fmea_rows: List[Dict[str, Any]],
        fmea_name: Optional[str] = None,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        导入架构元素
        
        Args:
            fmea_rows: FMEA行数据列表
            fmea_name: FMEA表格名称（用于推断Element Name，如果数据中为空）
            dry_run: 是否为试运行
            
        Returns:
            导入结果字典
        """
        self.stats = {
            'total': 0,
            'created': 0,
            'existing': 0,
            'failed': 0,
            'errors': []
        }
        
        print("\n开始导入架构元素...")
        print("=" * 80)
        
        # 1. 查找或创建Control父元素
        control_record_id = self.find_or_create_control_parent(dry_run=dry_run)
        if not control_record_id:
            return {
                'success': False,
                'error': '无法创建Control父元素',
                'stats': self.stats
            }
        
        print()
        
        # 2. 提取唯一的Element Name
        print("提取Element Name...")
        element_names = self.extract_element_names(fmea_rows, fmea_name)
        self.stats['total'] = len(element_names)
        
        print(f"[OK] 找到 {len(element_names)} 个唯一的Element Name")
        if len(element_names) <= 20:
            for name in element_names:
                print(f"  - {name}")
        else:
            print(f"  前10个: {', '.join(element_names[:10])}...")
        print()
        
        if dry_run:
            print("[试运行] 准备导入的架构元素:")
            for name in element_names:
                fields = self.prepare_element_record(name, control_record_id)
                print(f"  - {name}: {fields}")
            return {
                'success': True,
                'dry_run': True,
                'stats': self.stats,
                'element_name_to_record_id': {}
            }
        
        # 3. 批量导入架构元素
        print(f"批量导入架构元素（每批最多 {BATCH_SIZE} 条）...")
        print()
        
        total_batches = (len(element_names) + BATCH_SIZE - 1) // BATCH_SIZE
        
        for batch_idx in range(total_batches):
            start_idx = batch_idx * BATCH_SIZE
            end_idx = min(start_idx + BATCH_SIZE, len(element_names))
            batch_elements = element_names[start_idx:end_idx]
            
            print(f"[{batch_idx + 1}/{total_batches}] 导入第 {start_idx + 1}-{end_idx} 个元素...", end=' ')
            
            batch_created = 0
            batch_existing = 0
            batch_failed = 0
            
            for element_name in batch_elements:
                try:
                    # 准备记录数据
                    fields = self.prepare_element_record(element_name, control_record_id)
                    
                    # 查找或创建记录
                    result = self.utils.find_or_create_record(
                        self.table_id,
                        fields,
                        search_field='元素名称',
                        search_value=element_name
                    )
                    
                    if result['created']:
                        batch_created += 1
                        self.stats['created'] += 1
                    else:
                        batch_existing += 1
                        self.stats['existing'] += 1
                    
                    # 保存映射
                    self.element_name_to_record_id[element_name] = result['record_id']
                    
                except Exception as e:
                    batch_failed += 1
                    self.stats['failed'] += 1
                    self.stats['errors'].append({
                        'element_name': element_name,
                        'error': str(e)
                    })
            
            print(f"[OK] 新建: {batch_created}, 已存在: {batch_existing}, 失败: {batch_failed}")
            
            # 避免请求过快
            if batch_idx < total_batches - 1:
                time.sleep(0.5)
        
        print()
        print("=" * 80)
        print("架构元素导入完成")
        print("=" * 80)
        print(f"总计: {self.stats['total']}")
        print(f"新建: {self.stats['created']}")
        print(f"已存在: {self.stats['existing']}")
        print(f"失败: {self.stats['failed']}")
        
        if self.stats['errors']:
            print(f"\n错误详情（前5个）:")
            for error in self.stats['errors'][:5]:
                print(f"  {error['element_name']}: {error['error']}")
        
        result = {
            'success': self.stats['failed'] == 0,
            'stats': self.stats,
            'element_name_to_record_id': self.element_name_to_record_id
        }
        
        # 确保返回element_name_to_record_id
        if not result.get('element_name_to_record_id'):
            result['element_name_to_record_id'] = self.element_name_to_record_id
        
        return result


def main():
    """测试函数"""
    # 这里需要实际的app_token和table_id
    app_token = "test_app_token"
    table_id = "test_table_id"
    
    importer = ArchitectureElementImporter(app_token, table_id)
    
    # 测试数据
    test_rows = [
        {'Element Name': 'Element1', 'Function Description': 'Func1'},
        {'Element Name': 'Element2', 'Function Description': 'Func2'},
        {'Element Name': 'Element1', 'Function Description': 'Func3'},
    ]
    
    result = importer.import_elements(test_rows, dry_run=True)
    print(result)


if __name__ == "__main__":
    main()

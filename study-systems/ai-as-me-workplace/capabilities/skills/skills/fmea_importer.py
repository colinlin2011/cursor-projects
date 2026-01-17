# -*- coding: utf-8 -*-
"""
FMEA数据导入器

实现批量创建记录、分批处理、错误处理和进度显示
"""

import sys
import os
import time
from typing import Dict, List, Any, Optional
from datetime import datetime

# 修复Windows控制台编码问题
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from feishu_bitable_collaborator import create_bitable_collaborator
from feishu_api_wrapper import FeishuAPI
from fmea_field_mapper import FMEAFieldMapper
from bitable_cache_manager import APP_ID, APP_SECRET, SPACE_ID
from bitable_query_interface import get_query_interface

# 配置
BATCH_SIZE = 500  # 每批最多500条记录
MAX_RETRIES = 3  # 最大重试次数
RETRY_DELAY = 2  # 重试延迟（秒）


class FMEAImporter:
    """FMEA数据导入器"""
    
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
            table_id: 目标表ID
            user_access_token: 用户访问令牌
        """
        self.app_token = app_token
        self.table_id = table_id
        self.user_access_token = user_access_token or os.getenv("FEISHU_USER_ACCESS_TOKEN")
        
        # 创建协作器
        self.collaborator = create_bitable_collaborator(
            app_id=APP_ID,
            app_secret=APP_SECRET,
            user_access_token=self.user_access_token
        )
        
        # 获取表格结构（实时从API获取，确保字段ID是最新的）
        print(f"[!] 正在获取表格结构...")
        self.table_structure = self.collaborator.get_table_structure(app_token, table_id)
        self.bitable_fields = self.table_structure.get('fields', [])
        
        if not self.bitable_fields:
            print(f"[X] 无法获取表格字段结构")
        else:
            print(f"[OK] 获取到 {len(self.bitable_fields)} 个字段")
        
        # 创建字段映射器
        self.field_mapper = FMEAFieldMapper(self.bitable_fields)
        
        # 统计信息
        self.stats = {
            'total': 0,
            'success': 0,
            'failed': 0,
            'skipped': 0,
            'errors': []
        }
    
    def prepare_records(
        self,
        fmea_rows: List[Dict[str, Any]],
        skip_relations: bool = True
    ) -> List[Dict[str, Any]]:
        """
        准备记录数据（映射字段）
        
        Args:
            fmea_rows: FMEA行数据列表
            skip_relations: 是否跳过关联字段（关联字段需要单独处理）
            
        Returns:
            准备好的记录列表，每个记录包含fields字段
        """
        records = []
        
        for i, fmea_row in enumerate(fmea_rows):
            try:
                # 映射字段
                mapped = self.field_mapper.map_row(fmea_row, skip_relations=skip_relations)
                
                # 检查是否有有效字段
                if not mapped['fields']:
                    self.stats['skipped'] += 1
                    self.stats['errors'].append({
                        'row': i + 1,
                        'error': '没有可映射的字段',
                        'data': fmea_row
                    })
                    continue
                
                # 构建记录
                record = {
                    'fields': mapped['fields']
                }
                
                records.append(record)
                
            except Exception as e:
                self.stats['failed'] += 1
                self.stats['errors'].append({
                    'row': i + 1,
                    'error': str(e),
                    'data': fmea_row
                })
                continue
        
        return records
    
    def batch_create_records(
        self,
        records: List[Dict[str, Any]],
        retry_count: int = 0
    ) -> Dict[str, Any]:
        """
        批量创建记录
        
        Args:
            records: 记录列表
            retry_count: 当前重试次数
            
        Returns:
            创建结果字典
        """
        if not records:
            return {'success': True, 'created': 0, 'errors': []}
        
        try:
            # 调用批量创建API
            result = self.collaborator.api.batch_create_bitable_records(
                self.app_token,
                self.table_id,
                records,
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
                    self.stats['success'] += created_count
                    return {
                        'success': True,
                        'created': created_count,
                        'errors': []
                    }
                else:
                    error_msg = result.get('msg', '未知错误')
                    error_detail = result.get('error', {})
                    raise Exception(f"API错误: {error_msg} - {error_detail}")
            else:
                # 直接返回data格式（批量创建API可能直接返回records）
                if 'records' in result:
                    created_count = len(result['records'])
                    self.stats['success'] += created_count
                    return {
                        'success': True,
                        'created': created_count,
                        'errors': []
                    }
                elif 'items' in result:
                    created_count = len(result['items'])
                    self.stats['success'] += created_count
                    return {
                        'success': True,
                        'created': created_count,
                        'errors': []
                    }
                else:
                    # 打印调试信息
                    print(f"  [调试] API返回: {result}")
                    raise Exception(f"返回格式异常: {result}")
        
        except Exception as e:
            # 重试逻辑
            if retry_count < MAX_RETRIES:
                print(f"  [!] 创建失败，{RETRY_DELAY}秒后重试 ({retry_count + 1}/{MAX_RETRIES})...")
                time.sleep(RETRY_DELAY)
                return self.batch_create_records(records, retry_count + 1)
            else:
                error_msg = str(e)
                self.stats['failed'] += len(records)
                self.stats['errors'].append({
                    'batch': True,
                    'error': error_msg,
                    'record_count': len(records)
                })
                return {
                    'success': False,
                    'created': 0,
                    'errors': [error_msg]
                }
    
    def import_data(
        self,
        fmea_rows: List[Dict[str, Any]],
        skip_relations: bool = True,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        导入数据（主方法）
        
        Args:
            fmea_rows: FMEA行数据列表
            skip_relations: 是否跳过关联字段
            dry_run: 是否为试运行（不实际创建记录）
            
        Returns:
            导入结果字典
        """
        self.stats = {
            'total': len(fmea_rows),
            'success': 0,
            'failed': 0,
            'skipped': 0,
            'errors': []
        }
        
        print(f"\n开始导入数据...")
        print(f"  总行数: {self.stats['total']}")
        print(f"  试运行: {dry_run}")
        print(f"  跳过关联字段: {skip_relations}")
        print()
        
        if dry_run:
            # 试运行：只准备数据，不实际创建
            records = self.prepare_records(fmea_rows, skip_relations)
            print(f"[试运行] 准备就绪的记录数: {len(records)}")
            print(f"[试运行] 跳过的记录数: {self.stats['skipped']}")
            return {
                'success': True,
                'dry_run': True,
                'prepared': len(records),
                'stats': self.stats
            }
        
        # 准备记录
        records = self.prepare_records(fmea_rows, skip_relations)
        
        if not records:
            print("[X] 没有可导入的记录")
            return {
                'success': False,
                'stats': self.stats
            }
        
        print(f"准备就绪的记录数: {len(records)}")
        print(f"跳过的记录数: {self.stats['skipped']}")
        print()
        
        # 分批导入
        total_batches = (len(records) + BATCH_SIZE - 1) // BATCH_SIZE
        print(f"分批导入: {total_batches} 批（每批最多 {BATCH_SIZE} 条）")
        print()
        
        for batch_idx in range(total_batches):
            start_idx = batch_idx * BATCH_SIZE
            end_idx = min(start_idx + BATCH_SIZE, len(records))
            batch_records = records[start_idx:end_idx]
            
            print(f"[{batch_idx + 1}/{total_batches}] 导入第 {start_idx + 1}-{end_idx} 条记录...", end=' ')
            
            result = self.batch_create_records(batch_records)
            
            if result['success']:
                print(f"[OK] 成功创建 {result['created']} 条记录")
            else:
                print(f"[X] 失败: {result['errors']}")
            
            # 避免请求过快
            if batch_idx < total_batches - 1:
                time.sleep(0.5)
        
        print()
        print("=" * 80)
        print("导入完成")
        print("=" * 80)
        print(f"总计: {self.stats['total']}")
        print(f"成功: {self.stats['success']}")
        print(f"失败: {self.stats['failed']}")
        print(f"跳过: {self.stats['skipped']}")
        
        if self.stats['errors']:
            print(f"\n错误详情（前10个）:")
            for error in self.stats['errors'][:10]:
                if 'row' in error:
                    print(f"  第{error['row']}行: {error['error']}")
                elif 'batch' in error:
                    print(f"  批次: {error['error']}")
        
        return {
            'success': self.stats['failed'] == 0,
            'stats': self.stats
        }


def main():
    """测试函数"""
    # 这里需要实际的app_token和table_id
    app_token = "your_app_token"
    table_id = "your_table_id"
    
    importer = FMEAImporter(app_token, table_id)
    
    # 测试数据
    test_rows = [
        {
            '失效模式': '功能输出错误',
            '失效影响': '系统无法正常工作',
            '引导词': '错误',
            '分析日期': '2024-01-15'
        }
    ]
    
    result = importer.import_data(test_rows, dry_run=True)
    print(result)


if __name__ == "__main__":
    main()

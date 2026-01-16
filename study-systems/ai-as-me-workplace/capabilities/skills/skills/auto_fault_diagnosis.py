# -*- coding: utf-8 -*-
"""
自动故障定位与闭环系统 - 主流程控制器

整合所有模块，实现完整的故障定位和闭环流程
"""

import sys
import os
from typing import Dict, Any, Optional, List
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fault_ticket_monitor import get_ticket_monitor
from log_path_extractor import LogPathExtractor
from log_fault_id_extractor import LogFaultIdExtractor
from fault_guide_reader import get_guide_reader
from log_analyzer import LogAnalyzer
from fault_result_writer import FaultResultWriter
from fault_diagnosis_config import get_monitor_config

# 修复Windows控制台编码问题
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass


class AutoFaultDiagnosis:
    """自动故障定位系统"""
    
    def __init__(self):
        """初始化系统"""
        self.ticket_monitor = get_ticket_monitor()
        self.log_path_extractor = LogPathExtractor()
        self.fault_id_extractor = LogFaultIdExtractor()
        self.guide_reader = get_guide_reader()
        self.log_analyzer = LogAnalyzer()
        self.result_writer = FaultResultWriter()
    
    def process_ticket(self, ticket_id: str) -> Dict[str, Any]:
        """
        处理单个问题单
        
        Args:
            ticket_id: 问题单记录ID或工作项ID
            
        Returns:
            处理结果字典
        """
        print("=" * 80)
        print("处理问题单")
        print("=" * 80)
        print()
        print(f"问题单ID: {ticket_id}")
        print()
        
        # 刷新指引文档缓存（如果需要）
        try:
            self.guide_reader.refresh_all_guides_if_needed(max_cache_age_hours=24)
        except Exception as e:
            print(f"[!] 刷新指引文档缓存失败: {e}")
        
        result = {
            'success': False,
            'ticket_id': ticket_id,
            'steps': []
        }
        
        try:
            # 步骤1: 获取问题单信息
            print("步骤1: 获取问题单信息...")
            ticket_info = self.ticket_monitor.get_ticket_info(ticket_id)
            if not ticket_info:
                print("[X] 无法获取问题单信息")
                result['error'] = "无法获取问题单信息"
                return result
            
            record_id = ticket_info.get('record_id')
            work_item_id = ticket_info.get('work_item_id', '')
            print(f"[OK] 问题单信息获取成功")
            print(f"  记录ID: {record_id}")
            print(f"  工作项ID: {work_item_id}")
            print()
            result['steps'].append({'step': 'get_ticket_info', 'success': True})
            
            # 步骤2: 提取日志路径
            print("步骤2: 提取日志路径...")
            log_paths = self.log_path_extractor.extract_from_ticket(ticket_info)
            if not log_paths:
                print("[X] 未找到日志路径")
                result['error'] = "未找到日志路径"
                return result
            
            print(f"[OK] 找到 {len(log_paths)} 个日志路径:")
            for path in log_paths:
                print(f"  - {path}")
            print()
            result['steps'].append({'step': 'extract_log_path', 'success': True, 'log_paths': log_paths})
            
            # 步骤3: 从日志中提取Fault ID
            print("步骤3: 从日志中提取Fault ID...")
            all_fault_ids = []
            log_cache_paths = []
            
            for log_path in log_paths:
                fault_ids, cache_path = self.fault_id_extractor.process_log_path(log_path)
                all_fault_ids.extend(fault_ids)
                if cache_path:
                    log_cache_paths.append(cache_path)
            
            if not all_fault_ids:
                print("[X] 未从日志中提取到Fault ID")
                result['error'] = "未从日志中提取到Fault ID"
                return result
            
            # 去重
            unique_fault_ids = list(set(all_fault_ids))
            print(f"[OK] 提取到 {len(unique_fault_ids)} 个Fault ID: {unique_fault_ids}")
            print()
            result['steps'].append({'step': 'extract_fault_id', 'success': True, 'fault_ids': unique_fault_ids})
            
            # 步骤4: 对每个Fault ID进行分析
            print("步骤4: 分析Fault ID...")
            all_analysis_results = []
            
            for fault_id in unique_fault_ids:
                print(f"  分析 Fault ID: {fault_id}")
                
                # 获取故障定位指引
                guide_info = self.guide_reader.get_guide_by_fault_id(fault_id)
                if guide_info:
                    print(f"    [OK] 找到故障定位指引")
                else:
                    print(f"    [!] 未找到故障定位指引，使用通用分析")
                
                # 读取日志内容
                log_content = ""
                for cache_path in log_cache_paths:
                    if cache_path and cache_path.exists():
                        if cache_path.is_file():
                            try:
                                # 尝试读取文件（可能是文本或二进制）
                                with open(cache_path, 'r', encoding='utf-8', errors='ignore') as f:
                                    log_content += f.read()
                            except UnicodeDecodeError:
                                # 如果是二进制文件，尝试以二进制模式读取
                                try:
                                    with open(cache_path, 'rb') as f:
                                        content = f.read()
                                        # 尝试解码
                                        log_content += content.decode('utf-8', errors='ignore')
                                except Exception as e:
                                    print(f"    [!] 读取日志文件失败: {e}")
                            except Exception as e:
                                print(f"    [!] 读取日志文件失败: {e}")
                        elif cache_path.is_dir():
                            # 读取所有可能的日志文件
                            for pattern in ["*.log", "*.txt", "*.dat", "trace*", "*log*"]:
                                for log_file in cache_path.glob(pattern):
                                    try:
                                        # 跳过.gz文件（应该已经解压）
                                        if log_file.name.endswith('.gz'):
                                            continue
                                        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                                            log_content += f.read()
                                    except UnicodeDecodeError:
                                        # 尝试二进制模式
                                        try:
                                            with open(log_file, 'rb') as f:
                                                content = f.read()
                                                log_content += content.decode('utf-8', errors='ignore')
                                        except:
                                            pass
                                    except Exception as e:
                                        print(f"    [!] 读取日志文件失败 {log_file.name}: {e}")
                
                # 如果没有日志内容，仍然进行分析（使用问题单信息和指引）
                if not log_content:
                    print(f"    [!] 警告: 无法读取日志内容，将基于问题单信息和故障定位指引进行分析")
                    # 创建一个空的日志内容，让分析器基于指引进行分析
                    log_content = ""
                
                # 分析日志（即使没有日志内容，也可以基于指引进行分析）
                try:
                    analysis_result = self.log_analyzer.analyze_log_by_guide(
                        log_content,
                        fault_id,
                        guide_info
                    )
                    all_analysis_results.append(analysis_result)
                    print(f"    [OK] 分析完成")
                except Exception as e:
                    print(f"    [!] 分析过程出错: {e}")
                    # 即使分析出错，也创建一个基本的结果
                    analysis_result = {
                        'fault_id': fault_id,
                        'analysis_time': datetime.now().isoformat(),
                        'key_errors': [],
                        'error_count': 0,
                        'log_size': 0,
                        'guide_info': guide_info,
                        'analysis_points': [],
                        'timeline': [],
                        'modules_affected': []
                    }
                    all_analysis_results.append(analysis_result)
            
            if not all_analysis_results:
                print("[X] 无法完成分析")
                result['error'] = "无法完成分析"
                return result
            
            print()
            result['steps'].append({'step': 'analyze_log', 'success': True, 'analysis_count': len(all_analysis_results)})
            
            # 步骤5: 生成综合报告
            print("步骤5: 生成分析报告...")
            combined_report = self._combine_analysis_results(all_analysis_results)
            
            # 将执行步骤添加到combined_report中，供报告生成使用
            combined_report['steps'] = result.get('steps', [])
            
            # 保存日志内容到result中，供报告生成使用
            # 优化：限制日志文件大小，避免内存溢出
            MAX_LOG_SIZE = 500 * 1024 * 1024  # 500MB限制
            MAX_LINES_PER_FILE = 10_000_000  # 每个文件最多1000万行
            
            combined_log_content = ""
            total_size = 0
            print(f"[INFO] 开始读取日志文件，最多处理 {MAX_LOG_SIZE / 1024 / 1024:.0f}MB...")
            print(f"[INFO] log_cache_paths数量: {len(log_cache_paths)}")
            
            for idx, cache_path in enumerate(log_cache_paths, 1):
                if total_size >= MAX_LOG_SIZE:
                    print(f"[!] 警告: 日志总大小已达到限制 ({MAX_LOG_SIZE / 1024 / 1024:.0f}MB)，停止读取")
                    break
                    
                if cache_path and cache_path.exists():
                    print(f"[INFO] [{idx}/{len(log_cache_paths)}] 处理: {cache_path.name if cache_path.is_file() else cache_path.name}...")
                    
                    if cache_path.is_file():
                        try:
                            file_size = cache_path.stat().st_size
                            if file_size > MAX_LOG_SIZE:
                                print(f"    [!] 文件过大 ({file_size / 1024 / 1024:.1f}MB)，跳过")
                                continue
                            
                            if total_size + file_size > MAX_LOG_SIZE:
                                # 只读取部分内容
                                remaining = MAX_LOG_SIZE - total_size
                                print(f"    [!] 文件较大，只读取前 {remaining / 1024 / 1024:.1f}MB")
                                with open(cache_path, 'r', encoding='utf-8', errors='ignore') as f:
                                    # 限制行数
                                    lines_read = 0
                                    for line in f:
                                        if lines_read >= MAX_LINES_PER_FILE:
                                            break
                                        combined_log_content += line
                                        lines_read += 1
                                        total_size += len(line.encode('utf-8'))
                                        if total_size >= MAX_LOG_SIZE:
                                            break
                            else:
                                with open(cache_path, 'r', encoding='utf-8', errors='ignore') as f:
                                    content = f.read()
                                    combined_log_content += content
                                    total_size += len(content.encode('utf-8'))
                            
                            print(f"    [OK] 读取了 {len(combined_log_content) / 1024 / 1024:.1f}MB (累计: {total_size / 1024 / 1024:.1f}MB)")
                        except Exception as e:
                            print(f"    [!] 读取文件失败: {e}")
                    elif cache_path.is_dir():
                        file_count = 0
                        # 优先查找 log/snapshot-txtlog-192.168.1.101/log.gz 解压后的文件（用户指定的标准路径）
                        # 1. 优先查找解压后的 log 文件（从 log/snapshot-txtlog-192.168.1.101/log.gz 解压而来）
                        log_files_priority = []
                        
                        # 只查找 log/snapshot-txtlog-192.168.1.101/log 文件（固定IP地址）
                        target_log_file = cache_path / "log" / "snapshot-txtlog-192.168.1.101" / "log"
                        if target_log_file.exists() and target_log_file.is_file():
                            log_files_priority.append(target_log_file)
                            print(f"    [INFO] 找到标准日志文件: {target_log_file}")
                        
                        # 如果还是没找到，跳过其他文件（避免处理大文件）
                        if not log_files_priority:
                            print(f"    [!] 未找到标准日志文件 (log/snapshot-txtlog-192.168.1.101/log)，跳过该目录")
                            continue
                        
                        # 读取优先级文件
                        for log_file in log_files_priority:
                            if total_size >= MAX_LOG_SIZE:
                                break
                            
                            try:
                                file_size = log_file.stat().st_size
                                # 对于标准的 log 文件（从 log/snapshot-txtlog-*/log.gz 解压而来），即使大于100MB也要读取
                                # 但限制读取大小，避免内存溢出
                                if file_size > 100 * 1024 * 1024 and log_file.name != "log":
                                    print(f"    [!] 跳过大文件: {log_file.name} ({file_size / 1024 / 1024:.1f}MB)")
                                    continue
                                
                                # 如果是标准的 log 文件，即使很大也要读取（但限制大小）
                                # 对于 log 文件，我们需要读取整个文件，因为 SetFunc 可能在文件的任何位置
                                if log_file.name == "log":
                                    if file_size > MAX_LOG_SIZE:
                                        print(f"    [!] log文件较大 ({file_size / 1024 / 1024:.1f}MB)，只读取前 {MAX_LOG_SIZE / 1024 / 1024:.0f}MB")
                                    else:
                                        print(f"    [INFO] 读取标准log文件: {log_file.name} ({file_size / 1024 / 1024:.1f}MB)")
                                
                                # 读取文件并过滤二进制行
                                # 对于大文件，使用逐行读取避免内存溢出
                                read_limit = MAX_LOG_SIZE - total_size
                                if read_limit <= 0:
                                    print(f"    [!] 已达到日志大小限制，跳过剩余文件")
                                    break
                                
                                with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                                    lines_read = 0
                                    bytes_read = 0
                                    for line in f:
                                        if lines_read >= MAX_LINES_PER_FILE:
                                            break
                                        if bytes_read >= read_limit:
                                            break
                                        
                                        # 过滤：只保留包含可打印字符的行（至少50%是可打印字符）
                                        printable_chars = sum(1 for c in line if 32 <= ord(c) < 127 or c in '\n\r\t')
                                        if len(line) > 0 and printable_chars / len(line) >= 0.5:
                                            line_bytes = len(line.encode('utf-8'))
                                            if bytes_read + line_bytes > read_limit:
                                                break
                                            combined_log_content += line
                                            lines_read += 1
                                            bytes_read += line_bytes
                                            total_size += line_bytes
                                    
                                    print(f"    [INFO] 从 {log_file.name} 读取了 {lines_read} 行 ({bytes_read / 1024 / 1024:.1f}MB)")
                                    
                                    # 调试：检查是否包含 SetFunc
                                    if log_file.name == "log":
                                        setfunc_count = combined_log_content.count('SetFunc')
                                        setfunc_fu_st_count = len([l for l in combined_log_content.split('\n') if 'SetFunc' in l and ('fu_st:0x3' in l or 'fu_st:0x4' in l)])
                                        print(f"    [DEBUG] log文件内容中SetFunc行数: {setfunc_count}, 包含fu_st:0x3/0x4的行数: {setfunc_fu_st_count}")
                                
                                file_count += 1
                                print(f"    [OK] 读取文件: {log_file.name} (累计: {len(combined_log_content) / 1024 / 1024:.1f}MB)")
                            except Exception as e:
                                print(f"    [!] 读取文件 {log_file.name} 失败: {e}")
                        
                        print(f"    [OK] 从目录读取了 {file_count} 个日志文件")
            
            print(f"[OK] 日志读取完成，总大小: {len(combined_log_content) / 1024 / 1024:.1f}MB ({len(combined_log_content)} 字符)")
            combined_report['log_content'] = combined_log_content
            
            print("[OK] 报告生成完成")
            print()
            result['steps'].append({'step': 'generate_report', 'success': True})
            
            # 步骤6: 回填结果
            print("步骤6: 回填分析结果...")
            # 构建ticket_info
            ticket_info = {
                '工作项ID': work_item_id,
                '记录ID': record_id
            }
            # 从ticket_monitor获取问题单数据（如果可用）
            try:
                ticket_data = self.ticket_monitor.get_ticket_info(work_item_id or record_id)
                if ticket_data:
                    # 提取字段信息
                    fields = ticket_data.get('fields', {})
                    ticket_info.update(fields)
                    # 确保工作项ID正确
                    if '工作项ID' not in ticket_info:
                        ticket_info['工作项ID'] = ticket_data.get('work_item_id', work_item_id)
            except:
                pass
            if unique_fault_ids:
                ticket_info['Fault ID'] = ', '.join(unique_fault_ids)
            if log_paths:
                ticket_info['日志路径'] = ', '.join(log_paths)
            
            write_success = self.result_writer.write_analysis_result(
                record_id,
                combined_report,
                ticket_info=ticket_info
            )
            if write_success:
                print("[OK] 结果回填成功")
                result['success'] = True
            else:
                print("[X] 结果回填失败")
                result['error'] = "结果回填失败"
            
            result['steps'].append({'step': 'write_result', 'success': write_success})
            
            # 标记为已处理
            if write_success:
                if work_item_id:
                    self.ticket_monitor.mark_as_processed(work_item_id)
                if record_id:
                    self.ticket_monitor.mark_as_processed(record_id)
            
            print()
            print("=" * 80)
            if result['success']:
                print("处理完成")
            else:
                print("处理失败")
            print("=" * 80)
            
        except Exception as e:
            print(f"[X] 处理过程中发生错误: {e}")
            import traceback
            traceback.print_exc()
            result['error'] = str(e)
        
        finally:
            # 断开SSH连接
            self.fault_id_extractor.disconnect()
            
            # 注册日志文件用于自动清理（如果分析成功）
            if result.get('success') and log_cache_paths:
                try:
                    from log_cleanup_manager import register_log_for_cleanup
                    analysis_time = datetime.now()
                    for cache_path in log_cache_paths:
                        if cache_path and cache_path.exists():
                            register_log_for_cleanup(cache_path, analysis_time)
                    print(f"[OK] 已注册 {len(log_cache_paths)} 个日志路径用于自动清理")
                except Exception as e:
                    print(f"[!] 注册日志清理失败: {e}")
        
        return result
    
    def process_fault_id(self, fault_id: str, log_path: str) -> Dict[str, Any]:
        """
        直接处理Fault ID诊断（不通过问题单）
        
        Args:
            fault_id: Fault ID
            log_path: 日志路径
            
        Returns:
            处理结果字典
        """
        print("=" * 80)
        print("直接诊断Fault ID")
        print("=" * 80)
        print()
        print(f"Fault ID: {fault_id}")
        print(f"日志路径: {log_path}")
        print()
        
        result = {
            'success': False,
            'fault_id': fault_id,
            'log_path': log_path
        }
        
        try:
            # 提取Fault ID（从日志中）
            fault_ids, cache_path = self.fault_id_extractor.process_log_path(log_path)
            
            # 获取故障定位指引
            guide_info = self.guide_reader.get_guide_by_fault_id(fault_id)
            
            # 读取日志内容
            log_content = ""
            if cache_path and cache_path.exists():
                if cache_path.is_file():
                    with open(cache_path, 'r', encoding='utf-8', errors='ignore') as f:
                        log_content = f.read()
                elif cache_path.is_dir():
                    for log_file in cache_path.glob("*.log"):
                        try:
                            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                                log_content += f.read()
                        except:
                            pass
            
            if not log_content:
                result['error'] = "无法读取日志内容"
                return result
            
            # 分析日志
            analysis_result = self.log_analyzer.analyze_log_by_guide(
                log_content,
                fault_id,
                guide_info
            )
            
            # 生成报告
            report_text = self.log_analyzer.generate_analysis_report(analysis_result)
            
            result['success'] = True
            result['analysis_result'] = analysis_result
            result['report'] = report_text
            
            print()
            print("=" * 80)
            print("诊断完成")
            print("=" * 80)
            print()
            print(report_text)
            
        except Exception as e:
            print(f"[X] 诊断过程中发生错误: {e}")
            import traceback
            traceback.print_exc()
            result['error'] = str(e)
        
        finally:
            self.fault_id_extractor.disconnect()
        
        return result
    
    def _combine_analysis_results(self, analysis_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """合并多个分析结果"""
        if len(analysis_results) == 1:
            # 单个结果也要确保包含analysis_results字段
            result = analysis_results[0].copy()
            result['analysis_results'] = analysis_results
            return result
        
        # 合并多个Fault ID的分析结果
        combined = {
            'fault_ids': [r.get('fault_id') for r in analysis_results],
            'analysis_time': datetime.now().isoformat(),
            'key_errors': [],
            'error_count': 0,
            'analysis_points': [],
            'timeline': [],
            'modules_affected': [],
            'analysis_results': analysis_results  # 保留所有分析结果，供报告生成使用
        }
        
        for result in analysis_results:
            combined['key_errors'].extend(result.get('key_errors', []))
            combined['error_count'] += result.get('error_count', 0)
            combined['analysis_points'].extend(result.get('analysis_points', []))
            combined['timeline'].extend(result.get('timeline', []))
            combined['modules_affected'].extend(result.get('modules_affected', []))
        
        # 去重
        combined['analysis_points'] = list(set(combined['analysis_points']))
        combined['modules_affected'] = list(set(combined['modules_affected']))
        
        return combined
    
    def run_auto_monitor(self, interval: Optional[int] = None):
        """
        运行自动监控
        
        Args:
            interval: 监控间隔（秒），如果为None则使用配置中的值
        """
        def process_callback(ticket: Dict[str, Any]):
            """处理新问题单的回调函数"""
            record_id = ticket.get('record_id')
            work_item_id = ticket.get('work_item_id', '')
            
            print(f"\n处理新问题单: {work_item_id}")
            result = self.process_ticket(record_id or work_item_id)
            
            if result.get('success'):
                print(f"[OK] 问题单处理成功: {work_item_id}")
            else:
                print(f"[X] 问题单处理失败: {work_item_id}")
                print(f"错误: {result.get('error', 'Unknown error')}")
        
        self.ticket_monitor.run_auto_monitor(interval, process_callback)


def process_ticket(ticket_id: str) -> Dict[str, Any]:
    """
    处理问题单（便捷函数）
    
    Args:
        ticket_id: 问题单记录ID或工作项ID
        
    Returns:
        处理结果字典
    """
    system = AutoFaultDiagnosis()
    return system.process_ticket(ticket_id)


def process_fault_id(fault_id: str, log_path: str) -> Dict[str, Any]:
    """
    直接诊断Fault ID（便捷函数）
    
    Args:
        fault_id: Fault ID
        log_path: 日志路径
        
    Returns:
        处理结果字典
    """
    system = AutoFaultDiagnosis()
    return system.process_fault_id(fault_id, log_path)


def run_auto_monitor(interval: Optional[int] = None):
    """
    运行自动监控（便捷函数）
    
    Args:
        interval: 监控间隔（秒）
    """
    system = AutoFaultDiagnosis()
    system.run_auto_monitor(interval)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='自动故障定位系统')
    parser.add_argument('--ticket', type=str, help='处理指定问题单ID')
    parser.add_argument('--fault-id', type=str, help='诊断指定Fault ID')
    parser.add_argument('--log-path', type=str, help='日志路径（与--fault-id一起使用）')
    parser.add_argument('--monitor', action='store_true', help='启动自动监控')
    parser.add_argument('--interval', type=int, help='监控间隔（秒）')
    
    args = parser.parse_args()
    
    if args.ticket:
        result = process_ticket(args.ticket)
        sys.exit(0 if result.get('success') else 1)
    elif args.fault_id and args.log_path:
        result = process_fault_id(args.fault_id, args.log_path)
        sys.exit(0 if result.get('success') else 1)
    elif args.monitor:
        run_auto_monitor(args.interval)
    else:
        parser.print_help()

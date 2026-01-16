# -*- coding: utf-8 -*-
"""
Fault ID统计信息提取器

从日志中提取Fault ID的统计信息：首次/最后出现时间、出现次数、fu_st等
"""

import re
from typing import Dict, Optional, List
from datetime import datetime


class FaultStatisticsExtractor:
    """Fault ID统计信息提取器"""
    
    def extract_statistics(
        self,
        log_content: str,
        fault_id: str
    ) -> Dict[str, any]:
        """
        提取Fault ID的统计信息
        
        Args:
            log_content: 日志内容
            fault_id: Fault ID（如0x0165）
            
        Returns:
            统计信息字典，包含：
            - first_occurrence: 首次出现时间
            - last_occurrence: 最后出现时间
            - occurrence_count: 出现次数
            - fu_st: fu_st值（如果存在）
        """
        # #region agent log
        import json
        try:
            # 检查日志内容格式
            has_setfunc = 'SetFunc' in log_content if log_content else False
            has_text_chars = False
            printable_ratio = 0.0
            if log_content:
                # 检查前1000个字符中是否有可打印的ASCII字符
                preview = log_content[:1000]
                printable_count = sum(1 for c in preview[:100] if 32 <= ord(c) < 127)
                has_text_chars = printable_count > 0
                printable_ratio = printable_count / 100.0 if len(preview) > 0 else 0.0
                
                # 检查是否包含0x165
                has_fault_165 = '0x165' in log_content or '0x0165' in log_content
            
            with open(r'd:\Users\colin.lin\.cursor\.cursor\debug.log', 'a', encoding='utf-8') as f:
                f.write(json.dumps({
                    'sessionId': 'debug-session',
                    'runId': 'run1',
                    'hypothesisId': 'E',
                    'location': 'fault_statistics_extractor.py:extract_statistics:entry',
                    'message': 'extract_statistics called',
                    'data': {
                        'fault_id': fault_id,
                        'log_content_length': len(log_content) if log_content else 0,
                        'has_setfunc': has_setfunc,
                        'has_text_chars': has_text_chars,
                        'printable_ratio': printable_ratio,
                        'has_fault_165': has_fault_165 if log_content else False,
                        'log_content_preview': repr(log_content[:200]) if log_content else None,
                        'first_100_chars_hex': log_content[:100].encode('utf-8', errors='ignore').hex() if log_content else None
                    },
                    'timestamp': int(__import__('time').time() * 1000)
                }, ensure_ascii=False) + '\n')
        except Exception as e:
            try:
                with open(r'd:\Users\colin.lin\.cursor\.cursor\debug.log', 'a', encoding='utf-8') as f:
                    f.write(json.dumps({
                        'sessionId': 'debug-session',
                        'runId': 'run1',
                        'hypothesisId': 'E',
                        'location': 'fault_statistics_extractor.py:extract_statistics:entry:error',
                        'message': 'Error in debug log',
                        'data': {'error': str(e)},
                        'timestamp': int(__import__('time').time() * 1000)
                    }, ensure_ascii=False) + '\n')
            except:
                pass
        # #endregion
        
        if not log_content or not fault_id:
            return {
                'first_occurrence': None,
                'last_occurrence': None,
                'occurrence_count': 0,
                'fu_st': None
            }
        
        # 规范化Fault ID格式（支持多种格式）
        fault_id_normalized = self._normalize_fault_id(fault_id)
        # 同时尝试无前导0的格式（日志中可能是0x165而不是0x0165）
        fault_id_no_zero = fault_id_normalized
        if fault_id_normalized.startswith('0X'):
            num_part = fault_id_normalized[2:]
            if num_part.startswith('0') and len(num_part) > 1:
                fault_id_no_zero = '0x' + num_part.lstrip('0') or '0'
        
        # 提取所有包含该Fault ID的行，并提取故障状态
        # 优化策略：
        # 方式1（优先）：类似 v log.gz |grep SetFunc |grep -E "fu_st:0x3|fu_st:0x4"
        #   1. 先过滤包含 SetFunc 的行（这些行包含故障设置信息）
        #   2. 只关注 fu_st:0x3(OutOfService) 和 fu_st:0x4(Damaged) 等级的故障
        #   3. 可以提取故障出现次数
        # 方式2（备用）：类似 v log.gz |grep DegTbl |grep Drv
        #   1. 当方式1找不到有效信息时（可能因为日志丢失），使用此方式
        #   2. 只提取Fault ID信息，不提取出现次数
        
        # 规则：
        # 1. fa_st:0x1表示fault_id上报，fa_st:0x0表示清除
        # 2. fu_st:0x3/0x4表示kOutOfService/kDamage等级上报，fu_st_n:0x3/0x4表示清除
        # 3. 只关注kOutOfService(0x3)和kDamage(0x4)等级的故障
        
        lines_with_fault = []
        use_deg_tbl_mode = False  # 标记是否使用DegTbl方式
        
        # 方式1：优先使用 SetFunc 方式
        if len(log_content) > 100 * 1024 * 1024:  # 大于100MB时使用迭代器
            # 使用迭代器逐行处理，避免内存溢出
            from io import StringIO
            log_stream = StringIO(log_content)
            line_num = 0
            processed_count = 0
            filtered_count = 0
            
            for line in log_stream:
                line_num += 1
                
                # 第一步过滤：只处理包含 SetFunc 的行
                if 'SetFunc' not in line:
                    continue
                filtered_count += 1
                
                # #region agent log
                if filtered_count <= 3:  # 只记录前3个SetFunc行
                    try:
                        with open(r'd:\Users\colin.lin\.cursor\.cursor\debug.log', 'a', encoding='utf-8') as f:
                            f.write(json.dumps({
                                'sessionId': 'debug-session',
                                'runId': 'run1',
                                'hypothesisId': 'A',
                                'location': 'fault_statistics_extractor.py:extract_statistics:SetFunc_found',
                                'message': 'Found SetFunc line',
                                'data': {
                                    'fault_id': fault_id,
                                    'line_num': line_num,
                                    'line_preview': line[:300]
                                },
                                'timestamp': int(__import__('time').time() * 1000)
                            }, ensure_ascii=False) + '\n')
                    except:
                        pass
                # #endregion
                
                # 第二步过滤：只处理包含 fu_st:0x3 或 fu_st:0x4 的行
                # 必须同时包含 SetFunc 和 fu_st:0x3/0x4，然后检查是否包含目标Fault ID
                has_target_fu_st = bool(re.search(r'fu_st[:\s=]+0x[34]', line, re.IGNORECASE))
                
                if not has_target_fu_st:
                    continue
                
                # 第三步：检查是否包含目标Fault ID
                has_fault_id = (self._line_contains_fault_id(line, fault_id_normalized) or 
                               self._line_contains_fault_id(line, fault_id_no_zero))
                
                # #region agent log
                if filtered_count <= 3:
                    try:
                        with open(r'd:\Users\colin.lin\.cursor\.cursor\debug.log', 'a', encoding='utf-8') as f:
                            f.write(json.dumps({
                                'sessionId': 'debug-session',
                                'runId': 'run1',
                                'hypothesisId': 'B',
                                'location': 'fault_statistics_extractor.py:extract_statistics:fault_id_check',
                                'message': 'Checking fault ID match',
                                'data': {
                                    'fault_id': fault_id,
                                    'fault_id_normalized': fault_id_normalized,
                                    'fault_id_no_zero': fault_id_no_zero,
                                    'has_target_fu_st': has_target_fu_st,
                                    'has_fault_id': has_fault_id,
                                    'line_preview': line[:300]
                                },
                                'timestamp': int(__import__('time').time() * 1000)
                            }, ensure_ascii=False) + '\n')
                    except:
                        pass
                # #endregion
                
                if not has_fault_id:
                    continue
                
                processed_count += 1
                
                # 提取故障状态
                timestamp = self._extract_timestamp(line)
                fa_st = self._extract_fa_st(line)
                fu_st = self._extract_fu_st_from_line(line)
                fu_st_n = self._extract_fu_st_n_from_line(line)
                
                # #region agent log
                if processed_count <= 3:
                    try:
                        with open(r'd:\Users\colin.lin\.cursor\.cursor\debug.log', 'a', encoding='utf-8') as f:
                            f.write(json.dumps({
                                'sessionId': 'debug-session',
                                'runId': 'run1',
                                'hypothesisId': 'C',
                                'location': 'fault_statistics_extractor.py:extract_statistics:timestamp_extracted',
                                'message': 'Extracted timestamp and state',
                                'data': {
                                    'fault_id': fault_id,
                                    'timestamp': timestamp,
                                    'fa_st': fa_st,
                                    'fu_st': fu_st,
                                    'fu_st_n': fu_st_n,
                                    'line_preview': line[:300]
                                },
                                'timestamp': int(__import__('time').time() * 1000)
                            }, ensure_ascii=False) + '\n')
                    except:
                        pass
                # #endregion
                
                lines_with_fault.append({
                    'line_num': line_num,
                    'line': line,
                    'timestamp': timestamp,
                    'fa_st': fa_st,
                    'fu_st': fu_st,
                    'fu_st_n': fu_st_n
                })
            
            if filtered_count > 0:
                print(f"[DEBUG] SetFunc方式: 总行数={line_num}, SetFunc行数={filtered_count}, 匹配行数={processed_count}, 提取行数={len(lines_with_fault)}")
            else:
                # #region agent log
                try:
                    with open(r'd:\Users\colin.lin\.cursor\.cursor\debug.log', 'a', encoding='utf-8') as f:
                        f.write(json.dumps({
                            'sessionId': 'debug-session',
                            'runId': 'run1',
                            'hypothesisId': 'D',
                            'location': 'fault_statistics_extractor.py:extract_statistics:no_setfunc_lines',
                            'message': 'No SetFunc lines found in log content',
                            'data': {
                                'fault_id': fault_id,
                                'log_content_length': len(log_content),
                                'total_lines_processed': line_num,
                                'first_1000_chars': repr(log_content[:1000]) if log_content else None
                            },
                            'timestamp': int(__import__('time').time() * 1000)
                        }, ensure_ascii=False) + '\n')
                except:
                    pass
                # #endregion
        else:
            # 小文件直接split
            lines = log_content.split('\n')
            processed_count = 0
            filtered_count = 0
            
            for line_num, line in enumerate(lines):
                # 第一步过滤：只处理包含 SetFunc 的行
                if 'SetFunc' not in line:
                    continue
                filtered_count += 1
                
                # 第二步过滤：只处理包含 fu_st:0x3 或 fu_st:0x4 的行
                # 必须同时包含 SetFunc 和 fu_st:0x3/0x4，然后检查是否包含目标Fault ID
                has_target_fu_st = bool(re.search(r'fu_st[:\s=]+0x[34]', line, re.IGNORECASE))
                
                if not has_target_fu_st:
                    continue
                
                # 第三步：检查是否包含目标Fault ID
                has_fault_id = (self._line_contains_fault_id(line, fault_id_normalized) or 
                               self._line_contains_fault_id(line, fault_id_no_zero))
                
                if not has_fault_id:
                    continue
                
                processed_count += 1
                
                # 提取故障状态
                timestamp = self._extract_timestamp(line)
                fa_st = self._extract_fa_st(line)
                fu_st = self._extract_fu_st_from_line(line)
                fu_st_n = self._extract_fu_st_n_from_line(line)
                
                lines_with_fault.append({
                    'line_num': line_num,
                    'line': line,
                    'timestamp': timestamp,
                    'fa_st': fa_st,  # 0x1=上报, 0x0=清除
                    'fu_st': fu_st,  # 0x3或0x4表示kOutOfService/kDamage上报
                    'fu_st_n': fu_st_n  # 0x3或0x4表示kOutOfService/kDamage清除
                })
            
            if filtered_count > 0:
                print(f"[DEBUG] SetFunc方式: 总行数={len(lines)}, SetFunc行数={filtered_count}, 匹配行数={processed_count}, 提取行数={len(lines_with_fault)}")
        
        # 方式2：如果方式1没找到有效信息，使用 DegTbl + Drv 方式
        if len(lines_with_fault) == 0:
            print(f"[INFO] SetFunc方式未找到信息，尝试使用DegTbl+Drv方式...")
            use_deg_tbl_mode = True
            
            if len(log_content) > 100 * 1024 * 1024:
                from io import StringIO
                log_stream = StringIO(log_content)
                line_num = 0
                processed_count = 0
                filtered_count = 0
                
                for line in log_stream:
                    line_num += 1
                    
                    # 过滤：只处理包含 DegTbl 和 Drv 的行
                    if 'DegTbl' not in line or 'Drv' not in line:
                        continue
                    filtered_count += 1
                    
                    # 检查是否包含该Fault ID
                    if not (self._line_contains_fault_id(line, fault_id_normalized) or 
                           self._line_contains_fault_id(line, fault_id_no_zero)):
                        continue
                    
                    processed_count += 1
                    
                    # 只提取时间戳和Fault ID，不提取状态信息（因为这种方式无法准确提取）
                    timestamp = self._extract_timestamp(line)
                    
                    lines_with_fault.append({
                        'line_num': line_num,
                        'line': line,
                        'timestamp': timestamp,
                        'fa_st': None,  # DegTbl方式不提取状态
                        'fu_st': None,
                        'fu_st_n': None
                    })
                
                if filtered_count > 0:
                    print(f"[DEBUG] DegTbl方式: 总行数={line_num}, DegTbl+Drv行数={filtered_count}, 匹配行数={processed_count}, 提取行数={len(lines_with_fault)}")
            else:
                lines = log_content.split('\n')
                processed_count = 0
                filtered_count = 0
                
                for line_num, line in enumerate(lines):
                    # 过滤：只处理包含 DegTbl 和 Drv 的行
                    if 'DegTbl' not in line or 'Drv' not in line:
                        continue
                    filtered_count += 1
                    
                    # 检查是否包含该Fault ID
                    if not (self._line_contains_fault_id(line, fault_id_normalized) or 
                           self._line_contains_fault_id(line, fault_id_no_zero)):
                        continue
                    
                    processed_count += 1
                    
                    # 只提取时间戳和Fault ID，不提取状态信息
                    timestamp = self._extract_timestamp(line)
                    
                    lines_with_fault.append({
                        'line_num': line_num,
                        'line': line,
                        'timestamp': timestamp,
                        'fa_st': None,  # DegTbl方式不提取状态
                        'fu_st': None,
                        'fu_st_n': None
                    })
                
                if filtered_count > 0:
                    print(f"[DEBUG] DegTbl方式: 总行数={len(lines)}, DegTbl+Drv行数={filtered_count}, 匹配行数={processed_count}, 提取行数={len(lines_with_fault)}")
        
        # 计算出现次数
        # 注意：如果使用DegTbl方式，不计算出现次数（因为无法准确提取状态信息）
        occurrence_count = 0
        
        if not use_deg_tbl_mode:
            # 只有使用SetFunc方式时才计算出现次数
            # 规则：从上报到清除算一次出现
            # 可以使用fa_st（fa_st:0x1 -> fa_st:0x0）或fu_st/fu_st_n（fu_st:0x3/0x4 -> fu_st_n:0x3/0x4）
            last_fa_st = None  # 用于跟踪fa_st状态变化
            last_fu_st_state = None  # 用于跟踪fu_st/fu_st_n状态（'report'或'clear'）
            
            for line_info in lines_with_fault:
                # 方法1：使用fa_st判断
                current_fa_st = line_info.get('fa_st')
                if current_fa_st is not None:
                    # 从上报(0x1)到清除(0x0)算一次出现
                    if last_fa_st == 0x1 and current_fa_st == 0x0:
                        occurrence_count += 1
                    last_fa_st = current_fa_st
                
                # 方法2：使用fu_st/fu_st_n判断（只关注0x3和0x4）
                current_fu_st = line_info.get('fu_st')
                current_fu_st_n = line_info.get('fu_st_n')
                
                # 判断当前状态
                current_state = None
                if current_fu_st in [0x3, 0x4]:  # fu_st:0x3或0x4表示上报
                    current_state = 'report'
                elif current_fu_st_n in [0x3, 0x4]:  # fu_st_n:0x3或0x4表示清除
                    current_state = 'clear'
                
                # 从上报到清除算一次出现
                if last_fu_st_state == 'report' and current_state == 'clear':
                    occurrence_count += 1
                
                if current_state:
                    last_fu_st_state = current_state
            
            # 如果使用fa_st或fu_st/fu_st_n都没有计算出出现次数，但有上报记录，至少算1次
            if occurrence_count == 0 and lines_with_fault:
                has_report = any(
                    line_info.get('fa_st') == 0x1 or 
                    line_info.get('fu_st') in [0x3, 0x4] 
                    for line_info in lines_with_fault
                )
                if has_report:
                    occurrence_count = 1
        else:
            # DegTbl方式：不计算出现次数
            print(f"[INFO] DegTbl方式：不计算出现次数")
            occurrence_count = 0
        
        # 提取首次和最后出现时间
        first_occurrence = None
        last_occurrence = None
        
        if lines_with_fault:
            # 首次出现：找到第一个上报的记录
            for line_info in lines_with_fault:
                if (line_info.get('fa_st') == 0x1 or 
                    line_info.get('fu_st') in [0x3, 0x4]):
                    first_occurrence = line_info.get('timestamp')
                    break
            
            # 如果没找到上报记录，使用第一条记录
            if not first_occurrence:
                first_occurrence = lines_with_fault[0].get('timestamp')
            
            # 最后出现：最后一条记录的时间
            last_occurrence = lines_with_fault[-1].get('timestamp')
            
            # #region agent log - 记录提取到的时间戳作为证据
            try:
                with open(r'd:\Users\colin.lin\.cursor\.cursor\debug.log', 'a', encoding='utf-8') as f:
                    f.write(json.dumps({
                        'sessionId': 'debug-session',
                        'runId': 'run1',
                        'hypothesisId': 'C',
                        'location': 'fault_statistics_extractor.py:extract_statistics:timestamps_extracted',
                        'message': 'Timestamps extracted as evidence',
                        'data': {
                            'fault_id': fault_id,
                            'first_occurrence': first_occurrence,
                            'last_occurrence': last_occurrence,
                            'lines_with_fault_count': len(lines_with_fault),
                            'all_timestamps': [line_info.get('timestamp') for line_info in lines_with_fault[:5]]  # 前5个时间戳
                        },
                        'timestamp': int(__import__('time').time() * 1000)
                    }, ensure_ascii=False) + '\n')
            except:
                pass
            # #endregion
        
        # 提取fu_st值（从所有匹配行中提取，优先0x3和0x4）
        fu_st = None
        for line_info in lines_with_fault:
            current_fu_st = line_info.get('fu_st')
            if current_fu_st in [3, 4]:  # 优先kOutOfService和kDamage
                fu_st = f"0x{current_fu_st:X}"
                break
        
        # 如果没找到0x3或0x4，尝试从原始日志中提取（兼容旧逻辑）
        if not fu_st:
            fu_st = self._extract_fu_st(log_content, fault_id_normalized)
            if not fu_st:
                fu_st = self._extract_fu_st(log_content, fault_id_no_zero)
        
        return {
            'first_occurrence': first_occurrence,
            'last_occurrence': last_occurrence,
            'occurrence_count': occurrence_count,
            'fu_st': fu_st
        }
    
    def _normalize_fault_id(self, fault_id: str) -> str:
        """规范化Fault ID格式"""
        if not fault_id:
            return ""
        
        fault_id = fault_id.strip().upper()
        
        # 转换为标准格式
        if fault_id.startswith('0X'):
            # 确保格式为0xXXXX
            num_part = fault_id[2:]
            try:
                num = int(num_part, 16)
                return f"0x{num:04X}"
            except:
                return fault_id
        elif fault_id.isdigit():
            try:
                num = int(fault_id)
                return f"0x{num:04X}"
            except:
                return fault_id
        
        return fault_id
    
    def _line_contains_fault_id(self, line: str, fault_id: str) -> bool:
        """检查行是否包含Fault ID"""
        if not line or not fault_id:
            return False
        
        # 规范化fault_id用于匹配（去掉0x前缀，支持多种格式）
        fault_id_upper = fault_id.upper()
        fault_id_clean = fault_id_upper.replace('0X', '').replace('0x', '')
        # 去掉前导0
        fault_id_clean_no_zero = fault_id_clean.lstrip('0') or '0'
        
        # 支持多种格式（匹配0x0165和0x165）
        patterns = [
            # 完整匹配（带0x前缀）
            rf'\b{re.escape(fault_id_upper)}\b',  # 完整匹配 0x0165
            rf'\b0x{re.escape(fault_id_clean)}\b',  # 0x0165 (带前导0)
            rf'\b0x{re.escape(fault_id_clean_no_zero)}\b',  # 0x165 (无前导0)
            
            # fa_id格式
            rf'fa_id[:\s=]+{re.escape(fault_id_upper)}',  # fa_id: 0x0165 或 fa_id=0x0165
            rf'fa_id[:\s=]+0x{re.escape(fault_id_clean)}',  # fa_id: 0x0165 (带前导0)
            rf'fa_id[:\s=]+0x{re.escape(fault_id_clean_no_zero)}',  # fa_id: 0x165 (无前导0)
            
            # 括号格式 (e_id, fa_id, fa_st)=( 3,     0x165, 1)
            rf'\([^)]*fa_id[^)]*\)[^=]*=\s*\([^)]*0x{re.escape(fault_id_clean_no_zero)}',  # (e_id, fa_id, fa_st)=( 3, 0x165, 1)
            rf'\([^)]*fa_id[^)]*\)[^=]*=\s*\([^)]*0x{re.escape(fault_id_clean)}',  # (e_id, fa_id, fa_st)=( 3, 0x0165, 1)
            
            # Fault ID格式
            rf'Fault\s*ID[:\s]+{re.escape(fault_id_upper)}',  # Fault ID: 0x0165
            rf'fault_id[:\s=]+{re.escape(fault_id_upper)}',  # fault_id: 0x0165
            
            # 其他格式
            rf'faults?[:\s]*\(0x{re.escape(fault_id_clean)}',  # faults:(0x165 )
            rf'faults?[:\s]*\(0x{re.escape(fault_id_clean_no_zero)}',  # faults:(0x165 )
        ]
        
        for pattern in patterns:
            if re.search(pattern, line, re.IGNORECASE):
                return True
        
        return False
    
    def _extract_timestamp(self, line: str) -> Optional[str]:
        """从日志行中提取时间戳（日志最前面的[20260116_103432]格式）"""
        if not line:
            return None
        
        # 优先匹配日志最前面的[20260116_103432]格式
        # 示例：[20260116_103432][1630.929][W][61][MOD:dji_bf_app]...
        timestamp_pattern = r'^\[(\d{8}_\d{6})\]'
        match = re.search(timestamp_pattern, line)
        if match:
            timestamp = match.group(1)
            # #region agent log - 记录提取到的原始时间戳格式作为证据
            try:
                with open(r'd:\Users\colin.lin\.cursor\.cursor\debug.log', 'a', encoding='utf-8') as f:
                    f.write(json.dumps({
                        'sessionId': 'debug-session',
                        'runId': 'run1',
                        'hypothesisId': 'C',
                        'location': 'fault_statistics_extractor.py:_extract_timestamp:matched',
                        'message': 'Timestamp pattern matched - EVIDENCE',
                        'data': {
                            'raw_timestamp_format': f'[{timestamp}]',  # 原始格式，如[20260116_103432]
                            'raw_timestamp': timestamp,  # 去掉括号的格式，如20260116_103432
                            'line_preview': line[:300]
                        },
                        'timestamp': int(__import__('time').time() * 1000)
                    }, ensure_ascii=False) + '\n')
            except:
                pass
            # #endregion
            # 根据用户要求，直接返回原始格式 [20260116_103432]，而不是转换为可读格式
            # 这样可以作为成功提取时刻的证据
            return f"[{timestamp}]"
        
        # 兼容其他格式
        fallback_patterns = [
            r'\[(\d{8}_\d{6})\]',  # [20251219_182854]
            r'(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}(?:\.\d+)?)',  # 2026-01-12 14:17:09.123
            r'(\d{4}/\d{2}/\d{2}\s+\d{2}:\d{2}:\d{2}(?:\.\d+)?)',  # 2026/01/12 14:17:09.123
        ]
        
        for pattern in fallback_patterns:
            match = re.search(pattern, line)
            if match:
                timestamp = match.group(1)
                if re.match(r'\d{8}_\d{6}', timestamp):
                    date_part = timestamp[:8]
                    time_part = timestamp[9:]
                    formatted = f"{date_part[:4]}-{date_part[4:6]}-{date_part[6:8]} {time_part[:2]}:{time_part[2:4]}:{time_part[4:6]}"
                    return formatted
                return timestamp
        
        # #region agent log
        try:
            with open(r'd:\Users\colin.lin\.cursor\.cursor\debug.log', 'a', encoding='utf-8') as f:
                f.write(json.dumps({
                    'sessionId': 'debug-session',
                    'runId': 'run1',
                    'hypothesisId': 'C',
                    'location': 'fault_statistics_extractor.py:_extract_timestamp:no_match',
                    'message': 'No timestamp pattern matched',
                    'data': {
                        'line_preview': line[:200]
                    },
                    'timestamp': int(__import__('time').time() * 1000)
                }, ensure_ascii=False) + '\n')
        except:
            pass
        # #endregion
        
        return None
    
    def _extract_fu_st(self, log_content: str, fault_id: str) -> Optional[str]:
        """提取fu_st值"""
        if not log_content or not fault_id:
            return None
        
        # 规范化fault_id用于匹配
        fault_id_normalized = self._normalize_fault_id(fault_id)
        fault_id_no_zero = fault_id_normalized
        if fault_id_normalized.startswith('0X'):
            num_part = fault_id_normalized[2:]
            if num_part.startswith('0') and len(num_part) > 1:
                fault_id_no_zero = '0x' + num_part.lstrip('0') or '0'
        
        # 查找包含该Fault ID的行，并提取fu_st
        lines = log_content.split('\n')
        
        for line in lines:
            if self._line_contains_fault_id(line, fault_id_normalized) or self._line_contains_fault_id(line, fault_id_no_zero):
                # 尝试提取fu_st值
                # 格式：fu_st:0x3, fu_st:0x4, fu_st=0x3等
                fu_st_patterns = [
                    r'fu_st[:\s=]+(0x[0-9A-Fa-f]+)',
                    r'fu_st[:\s=]+([0-9]+)',
                ]
                
                for pattern in fu_st_patterns:
                    match = re.search(pattern, line, re.IGNORECASE)
                    if match:
                        fu_st_value = match.group(1)
                        # 规范化格式
                        if not fu_st_value.startswith('0x'):
                            try:
                                num = int(fu_st_value)
                                return f"0x{num:X}"
                            except:
                                pass
                        return fu_st_value.upper()
        
        return None
    
    def _extract_fa_st(self, line: str) -> Optional[int]:
        """提取fa_st值（fa_st:0x1表示上报，fa_st:0x0表示清除）"""
        if not line:
            return None
        
        # 匹配 fa_st:0x1 或 fa_st:0x0
        patterns = [
            r'fa_st[:\s=]+0x([0-9A-Fa-f]+)',
            r'fa_st[:\s=]+([01])',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                value_str = match.group(1)
                try:
                    # 转换为整数
                    if len(value_str) > 1 or value_str in ['0', '1']:
                        value = int(value_str, 16) if len(value_str) > 1 else int(value_str)
                        return value
                except:
                    pass
        
        return None
    
    def _extract_fu_st_from_line(self, line: str) -> Optional[int]:
        """提取fu_st值（fu_st:0x3/0x4表示kOutOfService/kDamage等级上报）"""
        if not line:
            return None
        
        # 匹配 fu_st:0x3 或 fu_st:0x4（只关注kOutOfService和kDamage）
        # 注意：日志中可能有fu_st::0x1（两个冒号）的情况
        patterns = [
            r'fu_st[:]+0x([0-9A-Fa-f]+)',  # 匹配fu_st:0x或fu_st::0x
            r'fu_st[:\s=]+0x([0-9A-Fa-f]+)',  # 兼容其他格式
            r'fu_st[:\s=]+([0-9]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                value_str = match.group(1)
                try:
                    # 转换为整数
                    if len(value_str) > 1 or value_str.isdigit():
                        value = int(value_str, 16) if len(value_str) > 1 else int(value_str)
                        # 只返回0x3(kOutOfService)或0x4(kDamage)
                        if value in [3, 4]:
                            return value
                except:
                    pass
        
        return None
    
    def _extract_fu_st_n_from_line(self, line: str) -> Optional[int]:
        """提取fu_st_n值（fu_st_n:0x3/0x4表示kOutOfService/kDamage等级清除）"""
        if not line:
            return None
        
        # 匹配 fu_st_n:0x3 或 fu_st_n:0x4（只关注kOutOfService和kDamage）
        # 注意：日志中可能有fu_st_n::0x1（两个冒号）的情况
        patterns = [
            r'fu_st_n[:]+0x([0-9A-Fa-f]+)',  # 匹配fu_st_n:0x或fu_st_n::0x
            r'fu_st_n[:\s=]+0x([0-9A-Fa-f]+)',  # 兼容其他格式
            r'fu_st_n[:\s=]+([0-9]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                value_str = match.group(1)
                try:
                    # 转换为整数
                    if len(value_str) > 1 or value_str.isdigit():
                        value = int(value_str, 16) if len(value_str) > 1 else int(value_str)
                        # 只返回0x3(kOutOfService)或0x4(kDamage)
                        if value in [3, 4]:
                            return value
                except:
                    pass
        
        return None
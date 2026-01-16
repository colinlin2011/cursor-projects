# -*- coding: utf-8 -*-
"""
日志数据获取与Fault ID提取模块

通过SSH连接服务器获取日志文件，根据故障定位指引中的固定grep方式提取Fault ID
"""

import sys
import os
import re
import subprocess
from typing import List, Optional, Dict, Any, Tuple
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import paramiko
    HAS_PARAMIKO = True
except ImportError:
    HAS_PARAMIKO = False
    print("[!] 警告: paramiko未安装，SSH功能将不可用")

from fault_diagnosis_config import (
    SSH_CONFIG, LOG_CACHE_DIR, get_ssh_config
)
from fault_guide_reader import get_guide_reader

# 修复Windows控制台编码问题
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass


class LogFaultIdExtractor:
    """日志Fault ID提取器"""
    
    def __init__(self):
        """初始化提取器"""
        self.ssh_config = get_ssh_config()
        self.ssh_client = None
        self.sftp_client = None
        self.guide_reader = get_guide_reader()
    
    def connect_to_server(self) -> bool:
        """
        连接到SSH服务器
        
        Returns:
            是否连接成功
        """
        if not HAS_PARAMIKO:
            print("[X] paramiko未安装，无法连接SSH服务器")
            return False
        
        try:
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # 尝试连接
            self.ssh_client.connect(
                hostname=self.ssh_config['host'],
                port=self.ssh_config['port'],
                username=self.ssh_config['username'],
                password=self.ssh_config['password'],
                timeout=self.ssh_config['timeout'],
                allow_agent=False,
                look_for_keys=False
            )
            
            print(f"[OK] SSH连接成功: {self.ssh_config['host']}")
            return True
            
        except paramiko.AuthenticationException as e:
            print(f"[X] SSH认证失败: {e}")
            print(f"    请检查用户名和密码是否正确")
            print(f"    用户名: {self.ssh_config['username']}")
            print(f"    主机: {self.ssh_config['host']}")
            return False
        except paramiko.SSHException as e:
            print(f"[X] SSH连接异常: {e}")
            return False
        except Exception as e:
            print(f"[X] SSH连接失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def disconnect(self):
        """断开SSH连接"""
        if self.sftp_client:
            self.sftp_client.close()
            self.sftp_client = None
        if self.ssh_client:
            self.ssh_client.close()
            self.ssh_client = None
    
    def download_log_files(self, remote_path: str, local_cache_dir: Optional[Path] = None) -> Optional[Path]:
        """
        下载日志文件到本地缓存
        
        Args:
            remote_path: 远程日志路径
            local_cache_dir: 本地缓存目录
            
        Returns:
            本地文件路径
        """
        # 规范化路径：如果路径不是以 / 开头，且包含 roadtest，则添加 /rawdata/ 前缀
        if remote_path and not remote_path.startswith('/'):
            if 'roadtest' in remote_path.lower():
                remote_path = '/rawdata/' + remote_path.lstrip('/')
                print(f"[INFO] 自动添加路径前缀: {remote_path}")
        
        # 确保SSH连接存在且有效
        if not self.ssh_client:
            if not self.connect_to_server():
                return None
        else:
            # 检查连接是否仍然有效
            try:
                self.ssh_client.exec_command('echo test', timeout=5)
            except:
                # 连接已断开，重新连接
                self.disconnect()
                if not self.connect_to_server():
                    return None
        
        if local_cache_dir is None:
            local_cache_dir = LOG_CACHE_DIR
        
        local_cache_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # 检查远程路径是文件还是目录
            stdin, stdout, stderr = self.ssh_client.exec_command(f'test -f "{remote_path}" && echo "file" || echo "dir"')
            path_type = stdout.read().decode().strip()
            
            if path_type == "file":
                # 下载单个文件
                local_file = local_cache_dir / Path(remote_path).name
                if not local_file.exists():
                    if not self.sftp_client:
                        self.sftp_client = self.ssh_client.open_sftp()
                    self.sftp_client.get(remote_path, str(local_file))
                    print(f"[OK] 下载文件: {remote_path} -> {local_file}")
                else:
                    print(f"[OK] 使用缓存文件: {local_file}")
                return local_file
            else:
                # 下载目录中的所有日志文件（递归查找）
                # 优先查找 log/snapshot-txtlog-*/log.gz 文件（用户指定的标准路径）
                files = []
                
                # 1. 优先查找 log/snapshot-txtlog-192.168.1.101/log.gz 文件（用户指定的标准路径）
                # 只查找 snapshot-txtlog-192.168.1.101 目录（固定IP地址）
                # 确保路径格式正确（移除末尾的斜杠，避免双斜杠）
                remote_path_clean = remote_path.rstrip('/')
                target_snapshot_dir = f"{remote_path_clean}/log/snapshot-txtlog-192.168.1.101"
                stdin, stdout, stderr = self.ssh_client.exec_command(f'test -d "{target_snapshot_dir}" && echo "exists" || echo "not_exists"')
                dir_exists = stdout.read().decode().strip()
                
                # #region agent log
                import json
                try:
                    with open(r'd:\Users\colin.lin\.cursor\.cursor\debug.log', 'a', encoding='utf-8') as f:
                        f.write(json.dumps({
                            'sessionId': 'debug-session',
                            'runId': 'run1',
                            'hypothesisId': 'F',
                            'location': 'log_fault_id_extractor.py:download_log_files:check_target_dir',
                            'message': 'Check if snapshot-txtlog-192.168.1.101 directory exists',
                            'data': {
                                'remote_path': remote_path,
                                'target_snapshot_dir': target_snapshot_dir,
                                'dir_exists': dir_exists
                            },
                            'timestamp': int(__import__('time').time() * 1000)
                        }, ensure_ascii=False) + '\n')
                except:
                    pass
                # #endregion
                
                if dir_exists == "exists":
                    # 查找该目录下的 log.gz 文件
                    stdin, stdout, stderr = self.ssh_client.exec_command(f'find "{target_snapshot_dir}" -type f -name "log.gz" 2>/dev/null')
                    log_gz_files = stdout.read().decode().strip().split('\n')
                    log_gz_files = [f for f in log_gz_files if f]
                    if log_gz_files:
                        files.extend(log_gz_files)
                        print(f"[INFO] 找到标准日志文件: {log_gz_files[0]}")
                        # #region agent log
                        try:
                            with open(r'd:\Users\colin.lin\.cursor\.cursor\debug.log', 'a', encoding='utf-8') as f:
                                f.write(json.dumps({
                                    'sessionId': 'debug-session',
                                    'runId': 'run1',
                                    'hypothesisId': 'F',
                                    'location': 'log_fault_id_extractor.py:download_log_files:found_log_gz',
                                    'message': 'Found log.gz file in snapshot-txtlog-192.168.1.101 directory',
                                    'data': {
                                        'snapshot_dir': target_snapshot_dir,
                                        'log_gz_file': log_gz_files[0]
                                    },
                                    'timestamp': int(__import__('time').time() * 1000)
                                }, ensure_ascii=False) + '\n')
                        except:
                            pass
                        # #endregion
                else:
                    print(f"[!] 未找到目标目录: {target_snapshot_dir}")
                
                # 如果没找到 snapshot-txtlog-* 目录，尝试直接查找 log 目录下的 log.gz
                if not files:
                    stdin, stdout, stderr = self.ssh_client.exec_command(f'find "{remote_path}/log" -type f -name "log.gz" 2>/dev/null | head -5')
                    log_gz_files = stdout.read().decode().strip().split('\n')
                    log_gz_files = [f for f in log_gz_files if f]
                    if log_gz_files:
                        files.extend(log_gz_files)
                        print(f"[INFO] 找到日志文件: {log_gz_files[0]}")
                
                # 2. 如果没找到，查找 log 目录下的所有文件
                if not files:
                    stdin, stdout, stderr = self.ssh_client.exec_command(f'find "{remote_path}/log" -type f 2>/dev/null | head -30')
                    log_files = stdout.read().decode().strip().split('\n')
                    files = [f for f in log_files if f]
                
                # 3. 如果log目录没找到，在整个目录中查找
                if not files:
                    stdin, stdout, stderr = self.ssh_client.exec_command(f'find "{remote_path}" -type f \\( -name "*.log" -o -name "*.txt" -o -name "*.gz" -o -name "*log*" \\) 2>/dev/null | head -30')
                    files = stdout.read().decode().strip().split('\n')
                    files = [f for f in files if f]
                
                # 4. 如果还是没找到，直接查找log子目录下的.gz文件
                if not files:
                    stdin, stdout, stderr = self.ssh_client.exec_command(f'find "{remote_path}/log" -type f -name "*.gz" 2>/dev/null | head -20')
                    gz_files = stdout.read().decode().strip().split('\n')
                    files = [f for f in gz_files if f]
                
                if files:
                    # 创建子目录
                    dir_name = Path(remote_path).name
                    local_dir = local_cache_dir / dir_name
                    local_dir.mkdir(parents=True, exist_ok=True)
                    
                    downloaded_files = []
                    if not self.sftp_client:
                        self.sftp_client = self.ssh_client.open_sftp()
                    
                    # 优先处理 log/snapshot-txtlog-192.168.1.101/log.gz 文件（用户指定的标准路径）
                    # 只下载这一个文件，避免处理其他大文件
                    standard_log_gz = None
                    for remote_file in files:
                        # 检查是否是标准的 log/snapshot-txtlog-192.168.1.101/log.gz 文件（固定IP地址）
                        if '/snapshot-txtlog-192.168.1.101/' in remote_file and remote_file.endswith('/log.gz'):
                            standard_log_gz = remote_file
                            print(f"[INFO] 找到标准日志文件: {standard_log_gz}")
                            break
                    
                    # 如果找到标准日志文件，只下载这一个
                    if standard_log_gz:
                        # 保持目录结构：log/snapshot-txtlog-192.168.1.101/log.gz
                        # 计算相对于 remote_path 的相对路径（确保路径格式正确）
                        remote_path_clean = remote_path.rstrip('/')
                        rel_path = Path(standard_log_gz).relative_to(Path(remote_path_clean))
                        local_file = local_dir / rel_path
                        
                        # 检查并创建父目录，如果存在同名文件，先删除
                        parent_dir = local_file.parent
                        
                        # 递归检查并创建目录路径，如果路径中的任何部分是文件，先删除
                        current_path = local_dir
                        for part in rel_path.parts[:-1]:  # 除了最后一个文件名，其他都是目录
                            current_path = current_path / part
                            if current_path.exists():
                                if current_path.is_file():
                                    print(f"[!] 发现同名文件，删除: {current_path}")
                                    current_path.unlink()
                                    current_path.mkdir(parents=True, exist_ok=True)
                                elif current_path.is_dir():
                                    # 已经是目录，继续
                                    pass
                            else:
                                # 不存在，创建目录
                                current_path.mkdir(parents=True, exist_ok=True)
                        
                        # 最后确保父目录存在
                        if not parent_dir.exists():
                            parent_dir.mkdir(parents=True, exist_ok=True)
                        
                        # #region agent log
                        import json
                        try:
                            with open(r'd:\Users\colin.lin\.cursor\.cursor\debug.log', 'a', encoding='utf-8') as f:
                                f.write(json.dumps({
                                    'sessionId': 'debug-session',
                                    'runId': 'run1',
                                    'hypothesisId': 'F',
                                    'location': 'log_fault_id_extractor.py:download_log_files:found_standard_log',
                                    'message': 'Found standard log.gz file',
                                    'data': {
                                        'remote_file': standard_log_gz,
                                        'local_file': str(local_file),
                                        'rel_path': str(rel_path)
                                    },
                                    'timestamp': int(__import__('time').time() * 1000)
                                }, ensure_ascii=False) + '\n')
                        except:
                            pass
                        # #endregion
                        
                        file_downloaded = False
                        if not local_file.exists():
                            try:
                                self.sftp_client.get(standard_log_gz, str(local_file))
                                downloaded_files.append(local_file)
                                file_downloaded = True
                                print(f"[OK] 下载标准日志文件: {standard_log_gz} -> {local_file}")
                            except Exception as e:
                                print(f"[!] 下载文件失败 {standard_log_gz}: {e}")
                        else:
                            downloaded_files.append(local_file)
                            print(f"[OK] 使用缓存文件: {local_file}")
                        
                        # 解压 log.gz 文件
                        if local_file.exists() and local_file.suffix == '.gz':
                            try:
                                import gzip
                                decompressed_file = local_file.with_suffix('')  # log.gz -> log
                                if not decompressed_file.exists() or file_downloaded:
                                    with gzip.open(local_file, 'rb') as f_in:
                                        with open(decompressed_file, 'wb') as f_out:
                                            f_out.write(f_in.read())
                                    if file_downloaded:
                                        print(f"[OK] 解压文件: {local_file.name} -> {decompressed_file.name}")
                                    downloaded_files.append(decompressed_file)
                                    file_size_mb = decompressed_file.stat().st_size / 1024 / 1024
                                    print(f"[OK] 解压后的日志文件: {decompressed_file} ({file_size_mb:.1f}MB)")
                                    
                                    # #region agent log
                                    try:
                                        with open(r'd:\Users\colin.lin\.cursor\.cursor\debug.log', 'a', encoding='utf-8') as f:
                                            f.write(json.dumps({
                                                'sessionId': 'debug-session',
                                                'runId': 'run1',
                                                'hypothesisId': 'F',
                                                'location': 'log_fault_id_extractor.py:download_log_files:decompressed',
                                                'message': 'Decompressed log.gz file',
                                                'data': {
                                                    'decompressed_file': str(decompressed_file),
                                                    'file_size_mb': file_size_mb
                                                },
                                                'timestamp': int(__import__('time').time() * 1000)
                                            }, ensure_ascii=False) + '\n')
                                    except:
                                        pass
                                    # #endregion
                            except Exception as e:
                                print(f"[!] 解压文件失败 {local_file.name}: {e}")
                                import traceback
                                traceback.print_exc()
                        
                        print(f"[OK] 下载了 {len(downloaded_files)} 个文件到 {local_dir}")
                        return local_dir
                    else:
                        # 如果没找到标准日志文件，返回None，避免下载其他大文件
                        print(f"[!] 未找到标准日志文件 (log/snapshot-txtlog-192.168.1.101/log.gz)，跳过下载其他文件")
                        return None
                else:
                    print(f"[!] 目录中未找到日志文件: {remote_path}")
                    return None
                    
        except Exception as e:
            print(f"[X] 下载日志文件失败: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def read_log_content(self, log_path: Path) -> str:
        """
        读取日志文件内容
        
        优先读取 log/snapshot-txtlog-*/log.gz 解压后的 log 文件
        
        Args:
            log_path: 日志文件路径（本地或远程）
            
        Returns:
            日志内容
        """
        if isinstance(log_path, str):
            log_path = Path(log_path)
        
        # 如果是本地文件
        if log_path.exists() and log_path.is_file():
            try:
                with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                    return f.read()
            except Exception as e:
                print(f"[!] 读取本地文件失败: {e}")
                return ""
        
        # 如果是目录，读取所有文件
        if log_path.is_dir():
            content = ""
            # 优先读取解压后的 log 文件（从 log/snapshot-txtlog-192.168.1.101/log.gz 解压而来）
            # 只查找 log/snapshot-txtlog-192.168.1.101/log 文件（固定IP地址）
            target_log_file = log_path / "log" / "snapshot-txtlog-192.168.1.101" / "log"
            if target_log_file.exists() and target_log_file.is_file():
                try:
                    with open(target_log_file, 'r', encoding='utf-8', errors='ignore') as f:
                        file_content = f.read()
                        if file_content:
                            content += file_content
                            print(f"[INFO] 读取标准日志文件: {target_log_file} ({len(file_content) / 1024 / 1024:.1f}MB)")
                            # 找到标准日志文件后，直接返回，不再读取其他文件
                            return content
                except Exception as e:
                    print(f"[!] 读取日志文件失败 {target_log_file}: {e}")
            
            # 如果没找到标准日志文件，尝试查找根目录下的 log 文件（向后兼容）
            log_file = log_path / "log"
            if log_file.exists() and log_file.is_file():
                try:
                    with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                        file_content = f.read()
                        if file_content:
                            content += file_content
                            print(f"[INFO] 读取日志文件: {log_file.name} ({len(file_content) / 1024 / 1024:.1f}MB)")
                            return content
                except Exception as e:
                    print(f"[!] 读取日志文件失败 {log_file.name}: {e}")
            
            # 如果没找到 log 文件，读取其他文本格式的文件
            if not content:
                for pattern in ["*.log", "*.txt", "trace*"]:
                    for file in log_path.glob(pattern):
                        # 跳过.gz文件（应该已经解压）
                        if file.name.endswith('.gz'):
                            continue
                        # 跳过已读取的 log 文件
                        if file.name == "log":
                            continue
                        try:
                            # 尝试文本模式读取
                            with open(file, 'r', encoding='utf-8', errors='ignore') as f:
                                file_content = f.read()
                                if file_content:  # 只添加非空内容
                                    content += f"\n=== {file.name} ===\n"
                                    content += file_content
                        except UnicodeDecodeError:
                            # 如果是二进制文件，尝试以二进制模式读取并解码
                            try:
                                with open(file, 'rb') as f:
                                    file_content = f.read()
                                    # 尝试解码
                                    decoded = file_content.decode('utf-8', errors='ignore')
                                    if decoded:
                                        content += f"\n=== {file.name} ===\n"
                                        content += decoded
                            except:
                                pass
                        except Exception as e:
                            print(f"[!] 读取文件失败 {file.name}: {e}")
            return content
        
        # 如果是远程路径，尝试通过SSH读取
        if not self.ssh_client:
            if not self.connect_to_server():
                return ""
        
        try:
            stdin, stdout, stderr = self.ssh_client.exec_command(f'cat "{log_path}"')
            content = stdout.read().decode('utf-8', errors='ignore')
            return content
        except Exception as e:
            print(f"[!] 读取远程文件失败: {e}")
            return ""
    
    def grep_fault_ids(self, log_file: Path, grep_patterns: List[str]) -> List[str]:
        """
        使用grep模式提取Fault ID
        
        Args:
            log_file: 日志文件路径
            grep_patterns: grep模式列表
            
        Returns:
            提取到的Fault ID列表
        """
        fault_ids = []
        
        # 读取日志内容
        log_content = self.read_log_content(log_file)
        if not log_content:
            return fault_ids
        
        # 对每个grep模式执行搜索
        for pattern in grep_patterns:
            # 执行grep（使用Python正则表达式）
            try:
                matches = re.finditer(pattern, log_content, re.IGNORECASE | re.MULTILINE)
                for match in matches:
                    # 尝试从匹配结果中提取Fault ID
                    matched_text = match.group(0)
                    # 查找Fault ID模式
                    fault_id_matches = re.findall(r'0x[0-9A-Fa-f]+|[0-9]+', matched_text)
                    fault_ids.extend(fault_id_matches)
            except Exception as e:
                print(f"[!] grep模式执行失败 {pattern}: {e}")
        
        # 去重并规范化
        unique_ids = []
        seen = set()
        for fault_id in fault_ids:
            normalized = self._normalize_fault_id(fault_id)
            if normalized and normalized not in seen:
                unique_ids.append(normalized)
                seen.add(normalized)
        
        return unique_ids
    
    def extract_fault_ids(self, log_content: str, guide_info: Optional[Dict] = None) -> List[str]:
        """
        根据指引提取Fault ID
        
        默认使用标准方式：v log.gz |grep SetFunc |grep -E "fu_st:0x3|fu_st:0x4"
        即先过滤包含SetFunc且fu_st为0x3或0x4的行，然后从这些行中提取fa_id
        
        Args:
            log_content: 日志内容
            guide_info: 指引信息（可选）
            
        Returns:
            提取到的Fault ID列表
        """
        fault_ids = []
        
        # 默认使用标准方式：先过滤SetFunc和fu_st:0x3|fu_st:0x4，再提取fa_id
        # 这是用户的标准工作流程
        lines = log_content.split('\n')
        
        # 第一步：过滤包含SetFunc的行
        setfunc_lines = [line for line in lines if 'SetFunc' in line]
        
        # 第二步：过滤包含fu_st:0x3或fu_st:0x4的行
        filtered_lines = []
        for line in setfunc_lines:
            if re.search(r'fu_st:0x[34]', line, re.IGNORECASE):
                filtered_lines.append(line)
        
        # 第三步：从过滤后的行中提取fa_id
        if filtered_lines:
            # 提取fa_id模式：fa_id:0x165 或 fa_id=0x165 或 fa_id 0x165
            fa_id_pattern = r'fa_id[:\s=]+(0x[0-9A-Fa-f]+)'
            for line in filtered_lines:
                matches = re.finditer(fa_id_pattern, line, re.IGNORECASE)
                for match in matches:
                    fault_id = match.group(1)
                    normalized = self._normalize_fault_id(fault_id)
                    if normalized:
                        fault_ids.append(normalized)
            
            # 如果标准方式找到了结果，直接返回，不再使用备用方式
            if fault_ids:
                # 去重并返回
                unique_ids = []
                seen = set()
                for fault_id in fault_ids:
                    if fault_id not in seen:
                        unique_ids.append(fault_id)
                        seen.add(fault_id)
                print(f"[INFO] 使用标准方式（SetFunc + fu_st:0x3/0x4）提取到 {len(unique_ids)} 个Fault ID")
                return unique_ids
        
        # 如果标准方式没找到，尝试备用方式：DegTbl + Drv
        if not fault_ids:
            print("[INFO] 标准方式（SetFunc + fu_st:0x3/0x4）未找到结果，尝试备用方式（DegTbl + Drv）...")
            degtbl_lines = [line for line in lines if 'DegTbl' in line and 'Drv' in line]
            if degtbl_lines:
                fa_id_pattern = r'fa_id[:\s=]+(0x[0-9A-Fa-f]+)'
                for line in degtbl_lines:
                    matches = re.finditer(fa_id_pattern, line, re.IGNORECASE)
                    for match in matches:
                        fault_id = match.group(1)
                        normalized = self._normalize_fault_id(fault_id)
                        if normalized:
                            fault_ids.append(normalized)
                if fault_ids:
                    # 去重并返回
                    unique_ids = []
                    seen = set()
                    for fault_id in fault_ids:
                        if fault_id not in seen:
                            unique_ids.append(fault_id)
                            seen.add(fault_id)
                    print(f"[INFO] 使用备用方式（DegTbl + Drv）提取到 {len(unique_ids)} 个Fault ID")
                    return unique_ids
        
        # 注意：不再使用指引信息或其他方式提取Fault ID
        # 只使用标准方式（SetFunc + fu_st:0x3/0x4）或备用方式（DegTbl + Drv）
        # 如果提供了指引信息，不再使用（已移除）
        if False and guide_info:
            grep_command = guide_info.get('grep_command')
            if grep_command and isinstance(grep_command, dict):
                # 使用解析后的grep命令
                filters = grep_command.get('filters', [])
                extract_pattern = grep_command.get('extract_pattern', r'fa_id[:\s]+(0x[0-9A-Fa-f]+)')
                
                # 先应用过滤条件
                filtered_content = log_content
                for filter_pattern in filters:
                    # 将grep模式转换为正则表达式
                    # 例如: "fu_st:0x3|fu_st:0x4" -> r"fu_st:0x3|fu_st:0x4"
                    if '|' in filter_pattern:
                        # 扩展正则表达式模式
                        regex_pattern = filter_pattern
                    else:
                        regex_pattern = re.escape(filter_pattern)
                    
                    # 过滤行
                    lines = filtered_content.split('\n')
                    filtered_lines = [line for line in lines if re.search(regex_pattern, line, re.IGNORECASE)]
                    filtered_content = '\n'.join(filtered_lines)
                
                # 从过滤后的内容中提取fa_id
                if isinstance(extract_pattern, str):
                    matches = re.finditer(extract_pattern, filtered_content, re.IGNORECASE)
                    for match in matches:
                        fault_id = match.group(1) if match.groups() else match.group(0)
                        normalized = self._normalize_fault_id(fault_id)
                        if normalized:
                            fault_ids.append(normalized)
                
                if fault_ids:
                    # 去重并返回
                    unique_ids = []
                    seen = set()
                    for fault_id in fault_ids:
                        if fault_id not in seen:
                            unique_ids.append(fault_id)
                            seen.add(fault_id)
                    return unique_ids
        
        # 注意：不再使用通用模式从整个日志中提取所有Fault ID
        # 只使用标准方式（SetFunc + fu_st:0x3/0x4）或备用方式（DegTbl + Drv）
        # 如果以上两种方式都没找到，返回空列表
        
        # 去重并返回（即使为空列表）
        unique_ids = []
        seen = set()
        for fault_id in fault_ids:
            if fault_id not in seen:
                unique_ids.append(fault_id)
                seen.add(fault_id)
        
        if not unique_ids:
            print("[INFO] 未找到符合要求的Fault ID（需要同时包含SetFunc和fu_st:0x3/0x4，或DegTbl+Drv）")
        
        return unique_ids
    
    def _normalize_fault_id(self, fault_id: str) -> Optional[str]:
        """规范化Fault ID格式"""
        if not fault_id:
            return None
        
        fault_id = fault_id.strip()
        
        # 转换为标准格式
        if fault_id.startswith('0x'):
            fault_id = '0x' + fault_id[2:].upper()
        elif fault_id.isdigit():
            # 如果是纯数字，转换为0x格式
            num = int(fault_id)
            fault_id = f"0x{num:04X}"
        else:
            return None
        
        return fault_id
    
    def process_log_path(self, log_path: str) -> Tuple[List[str], Optional[Path]]:
        """
        处理日志路径，下载日志并提取Fault ID
        
        Args:
            log_path: 日志路径（远程或本地）
            
        Returns:
            (Fault ID列表, 本地缓存路径)
        """
        print(f"处理日志路径: {log_path}")
        
        # 下载日志文件
        local_path = self.download_log_files(log_path)
        if not local_path:
            print("[X] 无法下载日志文件")
            return [], None
        
        # 读取日志内容
        log_content = self.read_log_content(local_path)
        if not log_content:
            print("[X] 无法读取日志内容")
            return [], local_path
        
        # 提取Fault ID（先尝试通用提取）
        fault_ids = self.extract_fault_ids(log_content)
        
        print(f"[OK] 提取到 {len(fault_ids)} 个Fault ID: {fault_ids}")
        return fault_ids, local_path


def extract_fault_ids_from_log(log_path: str) -> Tuple[List[str], Optional[Path]]:
    """
    从日志路径提取Fault ID（便捷函数）
    
    Args:
        log_path: 日志路径
        
    Returns:
        (Fault ID列表, 本地缓存路径)
    """
    extractor = LogFaultIdExtractor()
    try:
        return extractor.process_log_path(log_path)
    finally:
        extractor.disconnect()

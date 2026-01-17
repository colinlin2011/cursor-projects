# -*- coding: utf-8 -*-
"""
SSH日志泛化查询引擎

支持自定义关键字查询（模糊匹配、多关键字AND/OR组合）和自定义信息提取（正则表达式、上下文提取）
"""

import sys
import os
import re
import json
import gzip
from typing import Dict, List, Optional, Union, Any, Tuple
from pathlib import Path
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import paramiko
    HAS_PARAMIKO = True
except ImportError:
    HAS_PARAMIKO = False
    paramiko = None  # 避免类型检查错误
    print("[!] 警告: paramiko未安装，SSH功能将不可用")

from fault_diagnosis_config import SSH_CONFIG, LOG_CACHE_DIR, get_ssh_config

# 修复Windows控制台编码问题
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass


class SSHConnectionManager:
    """SSH连接管理器"""
    
    def __init__(self, ssh_config: Optional[Dict] = None):
        """
        初始化SSH连接管理器
        
        Args:
            ssh_config: SSH配置字典，如果为None则使用默认配置
        """
        self.ssh_config = ssh_config or get_ssh_config()
        self.ssh_client = None
        self.sftp_client = None
        self._connected = False
    
    def connect(self) -> bool:
        """
        连接到SSH服务器
        
        Returns:
            连接是否成功
        """
        if not HAS_PARAMIKO:
            print("[X] paramiko未安装，无法建立SSH连接")
            return False
        
        if self._connected and self.ssh_client:
            # 检查连接是否仍然有效
            try:
                self.ssh_client.exec_command('echo test', timeout=5)
                return True
            except:
                # 连接已断开，需要重新连接
                self.disconnect()
        
        try:
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            self.ssh_client.connect(
                hostname=self.ssh_config['host'],
                port=self.ssh_config['port'],
                username=self.ssh_config['username'],
                password=self.ssh_config['password'],
                timeout=self.ssh_config['timeout'],
                allow_agent=False,
                look_for_keys=False
            )
            
            self._connected = True
            return True
        except Exception as e:
            print(f"[X] SSH连接失败: {e}")
            self._connected = False
            return False
    
    def disconnect(self):
        """断开SSH连接"""
        if self.sftp_client:
            try:
                self.sftp_client.close()
            except:
                pass
            self.sftp_client = None
        
        if self.ssh_client:
            try:
                self.ssh_client.close()
            except:
                pass
            self.ssh_client = None
        
        self._connected = False
    
    def is_connected(self) -> bool:
        """检查是否已连接"""
        return self._connected and self.ssh_client is not None
    
    def execute_command(self, command: str, timeout: int = 30) -> Tuple[str, str, int]:
        """
        执行SSH命令
        
        Args:
            command: 要执行的命令
            timeout: 超时时间（秒）
            
        Returns:
            (stdout, stderr, exit_code)
        """
        if not self.is_connected():
            if not self.connect():
                return "", "SSH连接失败", -1
        
        try:
            stdin, stdout, stderr = self.ssh_client.exec_command(command, timeout=timeout)
            exit_code = stdout.channel.recv_exit_status()
            stdout_text = stdout.read().decode('utf-8', errors='ignore')
            stderr_text = stderr.read().decode('utf-8', errors='ignore')
            return stdout_text, stderr_text, exit_code
        except Exception as e:
            return "", f"命令执行失败: {e}", -1
    
    def get_file_size(self, remote_path: str) -> Optional[int]:
        """
        获取远程文件大小
        
        Args:
            remote_path: 远程文件路径
            
        Returns:
            文件大小（字节），如果失败返回None
        """
        stdout, stderr, exit_code = self.execute_command(f'stat -c%s "{remote_path}" 2>/dev/null || stat -f%z "{remote_path}" 2>/dev/null || echo ""')
        if exit_code == 0 and stdout.strip():
            try:
                return int(stdout.strip())
            except:
                pass
        return None
    
    def download_file(self, remote_path: str, local_path: Path) -> bool:
        """
        下载远程文件到本地
        
        Args:
            remote_path: 远程文件路径
            local_path: 本地保存路径
            
        Returns:
            下载是否成功
        """
        if not self.is_connected():
            if not self.connect():
                return False
        
        try:
            if not self.sftp_client:
                self.sftp_client = self.ssh_client.open_sftp()
            
            local_path.parent.mkdir(parents=True, exist_ok=True)
            self.sftp_client.get(remote_path, str(local_path))
            return True
        except Exception as e:
            print(f"[X] 下载文件失败: {e}")
            return False


class KeywordMatcher:
    """关键字匹配器"""
    
    def __init__(self, fuzzy_match: bool = True):
        """
        初始化关键字匹配器
        
        Args:
            fuzzy_match: 是否启用模糊匹配（忽略大小写）
        """
        self.fuzzy_match = fuzzy_match
    
    def build_grep_pattern(self, keywords: Union[str, List[str]], logic: str = "OR") -> str:
        """
        构建grep命令模式
        
        Args:
            keywords: 关键字（单个字符串或列表）
            logic: 逻辑运算符（AND/OR）
            
        Returns:
            grep命令模式字符串
        """
        if isinstance(keywords, str):
            keywords = [keywords]
        
        if not keywords:
            return ""
        
        # 转义特殊字符
        escaped_keywords = [re.escape(kw) for kw in keywords]
        
        if logic.upper() == "AND":
            # AND逻辑：使用多个grep管道
            pattern = " | ".join([f'grep -i "{kw}"' if self.fuzzy_match else f'grep "{kw}"' for kw in escaped_keywords])
            return pattern
        else:
            # OR逻辑：使用grep -E
            pattern = "|".join(escaped_keywords)
            flags = "-iE" if self.fuzzy_match else "-E"
            return f'grep {flags} "{pattern}"'
    
    def match_line(self, line: str, keywords: Union[str, List[str]], logic: str = "OR") -> bool:
        """
        检查行是否匹配关键字
        
        Args:
            line: 要检查的行
            keywords: 关键字（单个字符串或列表）
            logic: 逻辑运算符（AND/OR）
            
        Returns:
            是否匹配
        """
        if isinstance(keywords, str):
            keywords = [keywords]
        
        if not keywords:
            return False
        
        line_lower = line.lower() if self.fuzzy_match else line
        
        if logic.upper() == "AND":
            # AND逻辑：所有关键字都必须匹配
            return all(kw.lower() in line_lower if self.fuzzy_match else kw in line for kw in keywords)
        else:
            # OR逻辑：任意关键字匹配即可
            return any(kw.lower() in line_lower if self.fuzzy_match else kw in line for kw in keywords)


class LogFileFinder:
    """日志文件查找器"""
    
    def __init__(self, connection_manager: SSHConnectionManager):
        """
        初始化日志文件查找器
        
        Args:
            connection_manager: SSH连接管理器
        """
        self.conn_mgr = connection_manager
    
    def find_target_log_file(self, base_path: str) -> Optional[Dict[str, str]]:
        """
        查找目标日志文件
        
        从给定路径开始，递归查找"snapshot-txtlog-192.168.1.101"目录，
        然后在该目录下查找"log"或"log.gz"文件
        
        Args:
            base_path: 基础路径
            
        Returns:
            {
                'file_path': '/path/to/log.gz',
                'file_type': 'gz' or 'log',
                'snapshot_dir': '/path/to/snapshot-txtlog-192.168.1.101'
            } 或 None
        """
        # 规范化路径
        base_path = base_path.rstrip('/')
        
        print(f"[INFO] 开始查找目标日志文件，基础路径: {base_path}")
        
        # 1. 查找snapshot-txtlog-192.168.1.101目录
        find_command = f'find "{base_path}" -type d -name "snapshot-txtlog-192.168.1.101" 2>/dev/null | head -1'
        stdout, stderr, exit_code = self.conn_mgr.execute_command(find_command)
        
        if exit_code != 0:
            print(f"[!] 查找snapshot目录失败: {stderr}")
            return None
        
        snapshot_dirs = [d.strip() for d in stdout.strip().split('\n') if d.strip()]
        
        if not snapshot_dirs:
            print(f"[!] 未找到snapshot-txtlog-192.168.1.101目录")
            return None
        
        snapshot_dir = snapshot_dirs[0]
        print(f"[INFO] 找到snapshot目录: {snapshot_dir}")
        
        # 2. 在该目录下查找log.gz文件（优先）
        log_gz_path = f"{snapshot_dir}/log.gz"
        stdout, stderr, exit_code = self.conn_mgr.execute_command(f'test -f "{log_gz_path}" && echo "exists" || echo "not_exists"')
        
        if stdout.strip() == "exists":
            print(f"[OK] 找到log.gz文件: {log_gz_path}")
            return {
                'file_path': log_gz_path,
                'file_type': 'gz',
                'snapshot_dir': snapshot_dir
            }
        
        # 3. 如果没找到log.gz，查找log文件
        log_path = f"{snapshot_dir}/log"
        stdout, stderr, exit_code = self.conn_mgr.execute_command(f'test -f "{log_path}" && echo "exists" || echo "not_exists"')
        
        if stdout.strip() == "exists":
            print(f"[OK] 找到log文件: {log_path}")
            return {
                'file_path': log_path,
                'file_type': 'log',
                'snapshot_dir': snapshot_dir
            }
        
        print(f"[!] 在snapshot目录中未找到log或log.gz文件")
        return None


class InfoExtractor:
    """信息提取器"""
    
    def __init__(self):
        """初始化信息提取器"""
        pass
    
    def extract_with_regex(self, text: str, pattern: str) -> List[Dict[str, Any]]:
        """
        使用正则表达式提取信息
        
        Args:
            text: 要提取的文本
            pattern: 正则表达式模式
            
        Returns:
            提取结果列表，每个结果包含匹配信息和捕获组
        """
        results = []
        try:
            regex = re.compile(pattern, re.IGNORECASE | re.MULTILINE)
            for match in regex.finditer(text):
                groups = match.groups()
                result = {
                    'full_match': match.group(0),
                    'groups': list(groups) if groups else [],
                    'start': match.start(),
                    'end': match.end()
                }
                results.append(result)
        except Exception as e:
            print(f"[!] 正则表达式提取失败: {e}")
        
        return results
    
    def extract_context(self, lines: List[str], match_indices: List[int], context_lines: int) -> Dict[int, Dict[str, Any]]:
        """
        提取匹配行的上下文
        
        Args:
            lines: 所有行的列表
            match_indices: 匹配行的索引列表
            context_lines: 上下文行数
            
        Returns:
            上下文字典，key为行号，value为上下文信息
        """
        context_dict = {}
        
        for idx in match_indices:
            start_idx = max(0, idx - context_lines)
            end_idx = min(len(lines), idx + context_lines + 1)
            
            context_dict[idx] = {
                'before': lines[start_idx:idx] if start_idx < idx else [],
                'line': lines[idx] if idx < len(lines) else "",
                'after': lines[idx + 1:end_idx] if idx + 1 < len(lines) else [],
                'line_number': idx + 1  # 1-based line number
            }
        
        return context_dict
    
    def extract_fa_id(self, line: str) -> Optional[Dict[str, Any]]:
        """
        从行中提取fa_id值
        
        Args:
            line: 要提取的行
            
        Returns:
            {
                'fa_id': '0x165',
                'full_line': '...',
                'match_position': (start, end)
            } 或 None
        """
        # fa_id提取模式（支持多种格式）
        fa_id_patterns = [
            r'fa_id[:\s=]+(0x[0-9A-Fa-f]+)',  # fa_id: 0x165, fa_id=0x165
            r'fa_id[:\s=]+([0-9]+)',  # fa_id: 165
            r'fa_id[:\s=]+(0x[0-9]+)',  # fa_id: 0x165 (十进制格式)
        ]
        
        for pattern in fa_id_patterns:
            try:
                regex = re.compile(pattern, re.IGNORECASE)
                match = regex.search(line)
                if match:
                    fa_id = match.group(1)
                    # 规范化fa_id格式（统一为0x格式）
                    if not fa_id.startswith('0x'):
                        try:
                            # 如果是纯数字，转换为十六进制
                            num = int(fa_id)
                            fa_id = f"0x{num:04X}"
                        except:
                            fa_id = f"0x{fa_id}"
                    else:
                        # 确保格式正确（0x0165）
                        try:
                            num = int(fa_id, 16)
                            fa_id = f"0x{num:04X}"
                        except:
                            pass
                    
                    return {
                        'fa_id': fa_id,
                        'full_line': line,
                        'match_position': (match.start(), match.end()),
                        'raw_value': match.group(1)
                    }
            except Exception as e:
                continue
        
        return None


class RemoteGrepExecutor:
    """远程grep执行器"""
    
    def __init__(self, connection_manager: SSHConnectionManager):
        """
        初始化远程grep执行器
        
        Args:
            connection_manager: SSH连接管理器
        """
        self.conn_mgr = connection_manager
        self.keyword_matcher = KeywordMatcher()
    
    def _get_file_content_command(self, file_path: str, file_type: str) -> str:
        """
        获取读取文件内容的命令
        
        Args:
            file_path: 文件路径
            file_type: 'gz' 或 'log'
            
        Returns:
            读取文件内容的命令字符串
        """
        if file_type == 'gz':
            # 优先使用zcat
            return f'zcat "{file_path}"'
        else:
            return f'cat "{file_path}"'
    
    def _try_alternative_command(self, file_path: str, file_type: str, original_command: str) -> Optional[str]:
        """
        尝试备用命令（当zcat失败时）
        
        Args:
            file_path: 文件路径
            file_type: 'gz' 或 'log'
            original_command: 原始命令
            
        Returns:
            备用命令字符串或None
        """
        if file_type == 'gz':
            # 尝试使用v命令（用户提到的备用方法）
            return f'v "{file_path}"'
        return None
    
    def execute(self, remote_path: str, keywords: Union[str, List[str]], 
                logic: str = "OR", fuzzy_match: bool = True, 
                max_results: int = 100, file_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        在远程服务器上执行grep查询
        
        Args:
            remote_path: 远程文件或目录路径
            keywords: 关键字（单个字符串或列表）
            logic: 逻辑运算符（AND/OR）
            fuzzy_match: 是否模糊匹配
            max_results: 最大结果数
            file_type: 文件类型（'gz'或'log'），如果为None则自动检测
            
        Returns:
            匹配结果列表
        """
        self.keyword_matcher.fuzzy_match = fuzzy_match
        
        # 检查路径是文件还是目录
        stdout, stderr, exit_code = self.conn_mgr.execute_command(f'test -f "{remote_path}" && echo "file" || echo "dir"')
        path_type = stdout.strip()
        
        if path_type != "file" and path_type != "dir":
            print(f"[!] 无法确定路径类型: {remote_path}")
            return []
        
        # 自动检测文件类型
        if file_type is None and path_type == "file":
            if remote_path.endswith('.gz'):
                file_type = 'gz'
            else:
                file_type = 'log'
        
        # 构建grep命令
        if path_type == "file":
            # 单个文件
            # 获取读取文件内容的命令
            read_cmd = self._get_file_content_command(remote_path, file_type or 'log')
            
            grep_pattern = self.keyword_matcher.build_grep_pattern(keywords, logic)
            if logic.upper() == "AND":
                # AND逻辑需要管道
                command = f'{read_cmd} | {grep_pattern} | head -{max_results}'
            else:
                # OR逻辑直接grep
                command = f'{read_cmd} | {grep_pattern} | head -{max_results}'
        else:
            # 目录：查找所有日志文件
            grep_pattern = self.keyword_matcher.build_grep_pattern(keywords, logic)
            if logic.upper() == "AND":
                command = f'find "{remote_path}" -type f \\( -name "*.log" -o -name "*.txt" -o -name "*.gz" \\) -exec sh -c \'cat "$1" | {grep_pattern}\' _ {{}} \\; | head -{max_results}'
            else:
                command = f'find "{remote_path}" -type f \\( -name "*.log" -o -name "*.txt" -o -name "*.gz" \\) -exec {grep_pattern} {{}} \\; | head -{max_results}'
        
        # 执行命令
        stdout, stderr, exit_code = self.conn_mgr.execute_command(command)
        
        # 如果zcat失败，尝试备用命令
        if exit_code != 0 and exit_code != 1 and file_type == 'gz' and 'zcat' in command:
            print(f"[!] zcat命令失败，尝试备用方法...")
            alt_cmd = self._try_alternative_command(remote_path, file_type, command)
            if alt_cmd:
                grep_pattern = self.keyword_matcher.build_grep_pattern(keywords, logic)
                if logic.upper() == "AND":
                    command = f'{alt_cmd} | {grep_pattern} | head -{max_results}'
                else:
                    command = f'{alt_cmd} | {grep_pattern} | head -{max_results}'
                
                stdout, stderr, exit_code = self.conn_mgr.execute_command(command)
        
        if exit_code != 0 and exit_code != 1:  # grep返回1表示未找到匹配
            print(f"[!] grep命令执行失败: {stderr}")
            return []
        
        # 解析结果
        results = []
        lines = stdout.strip().split('\n')
        
        for i, line in enumerate(lines):
            if line.strip():
                results.append({
                    'line_number': i + 1,
                    'line_content': line,
                    'file_path': remote_path
                })
        
        return results[:max_results]


class LocalFileSearcher:
    """本地文件搜索器"""
    
    def __init__(self, connection_manager: SSHConnectionManager):
        """
        初始化本地文件搜索器
        
        Args:
            connection_manager: SSH连接管理器（用于下载文件）
        """
        self.conn_mgr = connection_manager
        self.keyword_matcher = KeywordMatcher()
        self.cache_dir = LOG_CACHE_DIR
    
    def search(self, remote_path: str, keywords: Union[str, List[str]], 
               logic: str = "OR", fuzzy_match: bool = True,
               max_results: int = 100) -> List[Dict[str, Any]]:
        """
        下载文件到本地后搜索
        
        Args:
            remote_path: 远程文件路径
            keywords: 关键字（单个字符串或列表）
            logic: 逻辑运算符（AND/OR）
            fuzzy_match: 是否模糊匹配
            max_results: 最大结果数
            
        Returns:
            匹配结果列表
        """
        self.keyword_matcher.fuzzy_match = fuzzy_match
        
        # 下载文件到本地缓存
        cache_file = self._download_to_cache(remote_path)
        if not cache_file:
            return []
        
        # 读取文件内容
        content = self._read_file(cache_file)
        if not content:
            return []
        
        # 搜索匹配行
        lines = content.split('\n')
        matches = []
        
        for i, line in enumerate(lines):
            if self.keyword_matcher.match_line(line, keywords, logic):
                matches.append({
                    'line_number': i + 1,
                    'line_content': line,
                    'file_path': remote_path,
                    'local_file': str(cache_file)
                })
                if len(matches) >= max_results:
                    break
        
        return matches
    
    def _download_to_cache(self, remote_path: str) -> Optional[Path]:
        """
        下载文件到本地缓存
        
        Args:
            remote_path: 远程文件路径
            
        Returns:
            本地缓存文件路径，如果失败返回None
        """
        # 生成缓存文件名
        cache_filename = Path(remote_path).name
        cache_file = self.cache_dir / cache_filename
        
        # 如果文件已存在且较新，直接使用
        if cache_file.exists():
            # 可以添加时间戳检查，这里简化处理
            return cache_file
        
        # 下载文件
        if self.conn_mgr.download_file(remote_path, cache_file):
            return cache_file
        else:
            return None
    
    def _read_file(self, file_path: Path) -> Optional[str]:
        """
        读取文件内容（支持gzip压缩文件）
        
        Args:
            file_path: 文件路径
            
        Returns:
            文件内容，如果失败返回None
        """
        try:
            if file_path.suffix == '.gz':
                with gzip.open(file_path, 'rt', encoding='utf-8', errors='ignore') as f:
                    return f.read()
            else:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    return f.read()
        except Exception as e:
            print(f"[!] 读取文件失败: {e}")
            return None


class ResultFormatter:
    """结果格式化器"""
    
    def __init__(self):
        """初始化结果格式化器"""
        pass
    
    def format_json(self, query_params: Dict, matches: List[Dict], 
                   extracted_info: Optional[Dict] = None) -> Dict[str, Any]:
        """
        格式化为JSON格式
        
        Args:
            query_params: 查询参数
            matches: 匹配结果列表
            extracted_info: 提取的信息（可选）
            
        Returns:
            JSON格式的结果字典
        """
        result = {
            'query_params': query_params,
            'matches': matches,
            'statistics': {
                'total_matches': len(matches),
                'query_time': datetime.now().isoformat()
            }
        }
        
        if extracted_info:
            result['extracted_info'] = extracted_info
        
        return result
    
    def format_text(self, query_params: Dict, matches: List[Dict],
                   extracted_info: Optional[Dict] = None) -> str:
        """
        格式化为文本格式
        
        Args:
            query_params: 查询参数
            matches: 匹配结果列表
            extracted_info: 提取的信息（可选）
            
        Returns:
            文本格式的结果
        """
        lines = []
        lines.append("=" * 80)
        lines.append("SSH日志查询结果")
        lines.append("=" * 80)
        lines.append("")
        
        # 查询参数
        lines.append("查询参数:")
        lines.append(f"  远程路径: {query_params.get('remote_path', 'N/A')}")
        lines.append(f"  关键字: {query_params.get('keywords', 'N/A')}")
        lines.append(f"  逻辑: {query_params.get('logic', 'OR')}")
        lines.append(f"  模糊匹配: {query_params.get('fuzzy_match', True)}")
        lines.append("")
        
        # 匹配结果
        lines.append(f"匹配结果 ({len(matches)} 条):")
        lines.append("-" * 80)
        
        for i, match in enumerate(matches, 1):
            lines.append(f"\n[{i}] 行号: {match.get('line_number', 'N/A')}")
            lines.append(f"内容: {match.get('line_content', '')}")
            if 'context' in match:
                ctx = match['context']
                if ctx.get('before'):
                    lines.append(f"上下文（前{len(ctx['before'])}行）:")
                    for line in ctx['before']:
                        lines.append(f"  {line}")
                if ctx.get('after'):
                    lines.append(f"上下文（后{len(ctx['after'])}行）:")
                    for line in ctx['after']:
                        lines.append(f"  {line}")
            if 'extracted_info' in match:
                lines.append(f"提取信息: {match['extracted_info']}")
        
        lines.append("")
        lines.append("=" * 80)
        
        return "\n".join(lines)


class SSHLogQueryEngine:
    """SSH日志查询引擎"""
    
    def __init__(self, ssh_config: Optional[Dict] = None, 
                 file_size_threshold: int = 10 * 1024 * 1024):  # 默认10MB
        """
        初始化SSH日志查询引擎
        
        Args:
            ssh_config: SSH配置字典，如果为None则使用默认配置
            file_size_threshold: 文件大小阈值（字节），超过此值使用远程grep
        """
        self.conn_mgr = SSHConnectionManager(ssh_config)
        self.remote_grep = RemoteGrepExecutor(self.conn_mgr)
        self.local_searcher = LocalFileSearcher(self.conn_mgr)
        self.info_extractor = InfoExtractor()
        self.formatter = ResultFormatter()
        self.file_finder = LogFileFinder(self.conn_mgr)
        self.file_size_threshold = file_size_threshold
    
    def query(
        self,
        remote_path: str,
        keywords: Union[str, List[str]],
        extract_pattern: Optional[str] = None,
        context_lines: int = 0,
        logic: str = "OR",
        output_format: str = "both",
        fuzzy_match: bool = True,
        max_results: int = 100,
        query_method: Optional[str] = None  # "remote" or "local" or None (auto)
    ) -> Dict[str, Any]:
        """
        执行日志查询
        
        Args:
            remote_path: 远程文件或目录路径
            keywords: 关键字（单个字符串或列表）
            extract_pattern: 正则表达式提取模式（可选）
            context_lines: 上下文行数（默认0，不提取上下文）
            logic: 逻辑运算符（AND/OR，默认OR）
            output_format: 输出格式（json/text/both，默认both）
            fuzzy_match: 是否模糊匹配（默认True）
            max_results: 最大结果数（默认100）
            query_method: 查询方式（remote/local/None，None表示自动选择）
            
        Returns:
            查询结果字典
        """
        query_params = {
            'remote_path': remote_path,
            'keywords': keywords if isinstance(keywords, list) else [keywords],
            'extract_pattern': extract_pattern,
            'context_lines': context_lines,
            'logic': logic,
            'fuzzy_match': fuzzy_match,
            'max_results': max_results,
            'query_method': query_method or 'auto'
        }
        
        # 确定查询方式
        if query_method is None:
            # 自动选择：检查文件大小
            file_size = self.conn_mgr.get_file_size(remote_path)
            if file_size and file_size > self.file_size_threshold:
                query_method = "remote"
            else:
                query_method = "local"
        
        # 执行查询
        if query_method == "remote":
            matches = self.remote_grep.execute(
                remote_path, keywords, logic, fuzzy_match, max_results
            )
        else:
            matches = self.local_searcher.search(
                remote_path, keywords, logic, fuzzy_match, max_results
            )
        
        # 信息提取
        extracted_info = None
        if extract_pattern:
            extracted_info = {}
            for match in matches:
                line = match.get('line_content', '')
                extracted = self.info_extractor.extract_with_regex(line, extract_pattern)
                if extracted:
                    match['extracted_info'] = extracted
                    extracted_info[match.get('line_number', 0)] = extracted
        
        # 上下文提取
        if context_lines > 0:
            # 需要读取完整文件内容来提取上下文
            if query_method == "local":
                # 本地文件可以直接读取
                cache_file = self.local_searcher._download_to_cache(remote_path)
                if cache_file:
                    content = self.local_searcher._read_file(cache_file)
                    if content:
                        lines = content.split('\n')
                        match_indices = [m.get('line_number', 1) - 1 for m in matches]
                        context_dict = self.info_extractor.extract_context(lines, match_indices, context_lines)
                        for match in matches:
                            line_num = match.get('line_number', 1)
                            if line_num - 1 in context_dict:
                                match['context'] = context_dict[line_num - 1]
            else:
                # 远程查询需要重新获取上下文
                # 简化处理：只返回匹配行，不提取上下文
                pass
        
        # 格式化输出
        result = {}
        
        if output_format in ["json", "both"]:
            result['json'] = self.formatter.format_json(query_params, matches, extracted_info)
        
        if output_format in ["text", "both"]:
            result['text'] = self.formatter.format_text(query_params, matches, extracted_info)
        
        # 如果只选择一种格式，直接返回该格式的结果
        if output_format == "json":
            return result.get('json', {})
        elif output_format == "text":
            return {'text': result.get('text', '')}
        else:
            return result
    
    def query_setfunc_fault(
        self,
        base_path: str,
        output_format: str = "json"
    ) -> Dict[str, Any]:
        """
        查询SetFunc相关的故障信息
        
        实现特定查询逻辑：grep SetFunc | grep -E "fu_st:0x3|fu_st:0x4"
        即：包含"SetFunc"且包含("fu_st:0x3"或"fu_st:0x4")的行
        
        Args:
            base_path: 基础路径（会自动查找目标文件）
            output_format: 输出格式（json/text/both，默认json）
            
        Returns:
            查询结果，包含fa_id和整行信息
        """
        print("=" * 80)
        print("查询SetFunc相关故障信息")
        print("=" * 80)
        print()
        
        # 1. 查找目标日志文件
        file_info = self.file_finder.find_target_log_file(base_path)
        if not file_info:
            error_result = {
                'error': '未找到目标日志文件',
                'base_path': base_path
            }
            if output_format in ["text", "both"]:
                error_result['text'] = f"错误: 未找到目标日志文件\n基础路径: {base_path}"
            return error_result
        
        file_path = file_info['file_path']
        file_type = file_info['file_type']
        snapshot_dir = file_info['snapshot_dir']
        
        print(f"[INFO] 目标文件: {file_path}")
        print(f"[INFO] 文件类型: {file_type}")
        print()
        
        # 2. 构建查询命令
        # 查询逻辑：grep SetFunc | grep -E "fu_st:0x3|fu_st:0x4"
        # 即：包含SetFunc且包含(fu_st:0x3或fu_st:0x4)的行
        
        # 获取读取文件内容的命令
        read_cmd = self.remote_grep._get_file_content_command(file_path, file_type)
        
        # 构建grep命令
        query_command = f'{read_cmd} | grep SetFunc | grep -E "fu_st:0x3|fu_st:0x4"'
        
        print(f"[INFO] 执行查询命令: {query_command}")
        print()
        
        # 3. 执行查询
        stdout, stderr, exit_code = self.conn_mgr.execute_command(query_command)
        
        # 如果zcat失败，尝试备用方法
        if exit_code != 0 and exit_code != 1 and file_type == 'gz':
            print(f"[!] zcat命令失败，尝试备用方法...")
            alt_cmd = self.remote_grep._try_alternative_command(file_path, file_type, query_command)
            if alt_cmd:
                query_command = f'{alt_cmd} | grep SetFunc | grep -E "fu_st:0x3|fu_st:0x4"'
                print(f"[INFO] 使用备用命令: {query_command}")
                stdout, stderr, exit_code = self.conn_mgr.execute_command(query_command)
        
        if exit_code != 0 and exit_code != 1:
            error_result = {
                'error': f'查询命令执行失败: {stderr}',
                'file_path': file_path,
                'command': query_command
            }
            if output_format in ["text", "both"]:
                error_result['text'] = f"错误: 查询命令执行失败\n命令: {query_command}\n错误: {stderr}"
            return error_result
        
        # 4. 解析结果并提取fa_id
        all_matches = []
        lines = stdout.strip().split('\n')
        
        for i, line in enumerate(lines):
            if line.strip():
                # 提取fa_id
                fa_id_info = self.info_extractor.extract_fa_id(line)
                
                match_data = {
                    'line_number': i + 1,
                    'line_content': line,
                    'file_path': file_path,
                    'full_line': line  # 整行信息
                }
                
                if fa_id_info:
                    match_data['fa_id'] = fa_id_info['fa_id']
                    match_data['fa_id_raw'] = fa_id_info.get('raw_value', '')
                    match_data['fa_id_position'] = fa_id_info.get('match_position', (0, 0))
                
                all_matches.append(match_data)
        
        print(f"[OK] 找到 {len(all_matches)} 条匹配记录")
        
        # 5. 按fa_id分组，对于相同fa_id出现很多行的情况，只保留前2行和后2行
        matches = self._filter_matches_by_fa_id(all_matches)
        
        if len(matches) < len(all_matches):
            print(f"[INFO] 过滤后保留 {len(matches)} 条记录（相同fa_id只保留前2行和后2行）")
        print()
        
        # 6. 提取故障概况（对每个唯一的fa_id）
        print("=" * 80)
        print("提取故障概况")
        print("=" * 80)
        print()
        
        unique_fa_ids = list(set([m.get('fa_id') for m in matches if m.get('fa_id')]))
        fault_summaries = {}
        
        if unique_fa_ids:
            try:
                from fault_summary_extractor import FaultSummaryExtractor
                summary_extractor = FaultSummaryExtractor()
                
                for fa_id in unique_fa_ids:
                    print(f"提取fa_id {fa_id}的故障概况...")
                    summary = summary_extractor.extract_fault_summary(fa_id, use_grep=True)
                    fault_summaries[fa_id] = summary
                    print()
            except Exception as e:
                print(f"[!] 提取故障概况失败: {e}")
                import traceback
                traceback.print_exc()
                print()
        
        # 7. 格式化输出
        query_params = {
            'base_path': base_path,
            'file_path': file_path,
            'file_type': file_type,
            'snapshot_dir': snapshot_dir,
            'query_pattern': 'SetFunc AND (fu_st:0x3 OR fu_st:0x4)',
            'command': query_command,
            'total_matches_before_filter': len(all_matches),
            'total_matches_after_filter': len(matches)
        }
        
        result = {}
        
        if output_format in ["json", "both"]:
            result['json'] = self.formatter.format_json(query_params, matches)
            # 添加fa_id汇总
            fa_ids = [m.get('fa_id') for m in matches if m.get('fa_id')]
            if fa_ids:
                result['json']['fa_id_summary'] = {
                    'unique_fa_ids': list(set(fa_ids)),
                    'total_fa_ids': len(fa_ids)
                }
            # 添加过滤统计
            if len(all_matches) > len(matches):
                result['json']['filter_statistics'] = {
                    'original_count': len(all_matches),
                    'filtered_count': len(matches),
                    'filtered_ratio': f"{len(matches)}/{len(all_matches)}"
                }
            # 添加故障概况
            if fault_summaries:
                result['json']['fault_summaries'] = {}
                for fa_id, summary in fault_summaries.items():
                    result['json']['fault_summaries'][fa_id] = {
                        'fault_id': summary.get('fault_id'),
                        'summary_text': summary.get('summary_text', ''),
                        'has_guide_info': summary.get('guide_info') is not None,
                        'has_safety_requirement_info': summary.get('safety_requirement_info') is not None,
                        'has_bitable_summary': summary.get('bitable_summary') is not None
                    }
        
        if output_format in ["text", "both"]:
            text_lines = []
            text_lines.append("=" * 80)
            text_lines.append("SetFunc故障查询结果")
            text_lines.append("=" * 80)
            text_lines.append("")
            text_lines.append(f"基础路径: {base_path}")
            text_lines.append(f"目标文件: {file_path}")
            text_lines.append(f"文件类型: {file_type}")
            text_lines.append(f"查询模式: SetFunc AND (fu_st:0x3 OR fu_st:0x4)")
            text_lines.append("")
            if len(all_matches) > len(matches):
                text_lines.append(f"匹配结果: {len(all_matches)} 条（过滤后保留 {len(matches)} 条）")
                text_lines.append(f"过滤规则: 相同fa_id出现超过4行时，只保留前2行和后2行")
            else:
                text_lines.append(f"匹配结果 ({len(matches)} 条):")
            text_lines.append("-" * 80)
            
            for i, match in enumerate(matches, 1):
                text_lines.append(f"\n[{i}] 行号: {match.get('line_number', 'N/A')}")
                if match.get('fa_id'):
                    text_lines.append(f"FA_ID: {match['fa_id']}")
                text_lines.append(f"完整行: {match.get('full_line', match.get('line_content', ''))}")
            
            # fa_id汇总
            fa_ids = [m.get('fa_id') for m in matches if m.get('fa_id')]
            if fa_ids:
                text_lines.append("")
                text_lines.append("-" * 80)
                text_lines.append(f"FA_ID汇总:")
                text_lines.append(f"  唯一FA_ID: {', '.join(set(fa_ids))}")
                text_lines.append(f"  总数: {len(fa_ids)}")
            
            # 故障概况
            if fault_summaries:
                text_lines.append("")
                text_lines.append("=" * 80)
                text_lines.append("故障概况")
                text_lines.append("=" * 80)
                text_lines.append("")
                
                for fa_id, summary in fault_summaries.items():
                    summary_text = summary.get('summary_text', '')
                    if summary_text:
                        text_lines.append(summary_text)
                        text_lines.append("")
            
            text_lines.append("=" * 80)
            result['text'] = "\n".join(text_lines)
        
        if output_format == "json":
            return result.get('json', {})
        elif output_format == "text":
            return {'text': result.get('text', '')}
        else:
            return result
    
    def _filter_matches_by_fa_id(self, matches: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        过滤匹配结果：对于相同fa_id出现很多行的情况，只保留前2行和后2行
        
        Args:
            matches: 所有匹配结果列表
            
        Returns:
            过滤后的匹配结果列表
        """
        # 按fa_id分组
        fa_id_groups = {}
        no_fa_id_matches = []
        
        for match in matches:
            fa_id = match.get('fa_id')
            if fa_id:
                if fa_id not in fa_id_groups:
                    fa_id_groups[fa_id] = []
                fa_id_groups[fa_id].append(match)
            else:
                # 没有fa_id的匹配，直接保留
                no_fa_id_matches.append(match)
        
        # 处理每个fa_id组
        filtered_matches = []
        
        for fa_id, group_matches in fa_id_groups.items():
            if len(group_matches) <= 4:
                # 如果行数少于等于4行，保留所有行
                filtered_matches.extend(group_matches)
            else:
                # 如果行数超过4行，只保留前2行和后2行
                first_two = group_matches[:2]
                last_two = group_matches[-2:]
                
                # 检查是否有重复（前2行和后2行可能重叠）
                if len(group_matches) == 5:
                    # 5行的情况：前2行 + 最后1行（避免重复）
                    filtered_matches.extend(first_two)
                    if group_matches[-1] not in first_two:
                        filtered_matches.append(group_matches[-1])
                else:
                    # 6行及以上：前2行 + 后2行
                    filtered_matches.extend(first_two)
                    # 确保后2行不与前2行重复
                    for match in last_two:
                        if match not in first_two:
                            filtered_matches.append(match)
        
        # 添加没有fa_id的匹配
        filtered_matches.extend(no_fa_id_matches)
        
        # 按原始行号排序
        filtered_matches.sort(key=lambda x: x.get('line_number', 0))
        
        return filtered_matches
    
    def close(self):
        """关闭SSH连接"""
        self.conn_mgr.disconnect()


def create_query_engine(ssh_config: Optional[Dict] = None) -> SSHLogQueryEngine:
    """
    创建SSH日志查询引擎实例（便捷函数）
    
    Args:
        ssh_config: SSH配置字典，如果为None则使用默认配置
        
    Returns:
        SSHLogQueryEngine实例
    """
    return SSHLogQueryEngine(ssh_config)

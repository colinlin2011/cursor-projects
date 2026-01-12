"""
文档转换工具 - 启动脚本
用于启动Streamlit应用
"""

import subprocess
import sys
import os
import webbrowser
import time
from pathlib import Path

def main():
    """主函数"""
    base_path = Path(__file__).parent
    main_file = base_path / 'main.py'
    
    print("=" * 50)
    print("文档转换工具")
    print("=" * 50)
    print("正在启动应用...")
    print("浏览器将自动打开，如果没有自动打开，请访问: http://localhost:8502")
    print("=" * 50)
    print()
    
    # 启动Streamlit（使用8502端口，避免与excel-processor冲突）
    cmd = [
        sys.executable, '-m', 'streamlit', 'run', str(main_file),
        '--server.port', '8502',
        '--browser.gatherUsageStats', 'false'
    ]
    
    try:
        process = subprocess.Popen(cmd, cwd=str(base_path))
        
        # 等待服务器启动
        time.sleep(3)
        
        # 打开浏览器
        try:
            webbrowser.open('http://localhost:8502')
        except:
            pass
        
        # 等待进程结束
        process.wait()
        
    except KeyboardInterrupt:
        print("\n正在关闭应用...")
        if process.poll() is None:
            process.terminate()
            process.wait()
    except Exception as e:
        print(f"启动时出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

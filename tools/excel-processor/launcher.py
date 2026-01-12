"""
启动脚本 - 用于打包成 exe 文件
这个脚本会在后台启动 Streamlit 服务器并自动打开浏览器
"""

import subprocess
import sys
import os
import webbrowser
import time
import threading
from pathlib import Path

def resource_path(relative_path):
    """获取资源文件的绝对路径（兼容打包和开发环境）"""
    try:
        # PyInstaller 创建的临时文件夹路径
        base_path = sys._MEIPASS
    except Exception:
        # 开发环境
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

_browser_opened = False  # 全局标志，确保只打开一次
_app_running = False  # 应用运行标志

def wait_for_server(max_wait=30):
    """等待服务器启动"""
    import socket
    for _ in range(max_wait):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('localhost', 8501))
            sock.close()
            if result == 0:
                return True
        except:
            pass
        time.sleep(1)
    return False

def open_browser():
    """延迟打开浏览器，等待服务器启动"""
    global _browser_opened
    
    if _browser_opened:
        return
    
    # 等待服务器启动
    if wait_for_server():
        try:
            webbrowser.open('http://localhost:8501')
            _browser_opened = True
        except Exception:
            pass

def main():
    """主函数"""
    global _app_running
    
    # 防止重复启动
    if _app_running:
        return
    
    _app_running = True
    
    # 获取资源文件路径
    if getattr(sys, 'frozen', False):
        # 打包后的环境：使用临时解压目录
        try:
            base_path = Path(sys._MEIPASS)
        except:
            base_path = Path(sys.executable).parent
    else:
        # 开发环境
        base_path = Path(__file__).parent
    
    # 设置工作目录为 exe 所在目录（用于保存文件）
    if getattr(sys, 'frozen', False):
        exe_dir = Path(sys.executable).parent
        os.chdir(exe_dir)
    else:
        exe_dir = base_path
        os.chdir(base_path)
    
    # 主程序文件路径（在打包环境中，文件在临时目录）
    # 优先使用 resource_path 获取路径
    if getattr(sys, 'frozen', False):
        main_file = Path(resource_path('main.py'))
    else:
        main_file = base_path / 'main.py'
    
    # 转换为绝对路径
    main_file = main_file.resolve()
    
    if not main_file.exists():
        print(f"错误：找不到主程序文件 main.py")
        print(f"\n尝试的路径: {main_file}")
        print(f"当前工作目录: {os.getcwd()}")
        print(f"sys.executable: {sys.executable}")
        if getattr(sys, 'frozen', False):
            try:
                print(f"sys._MEIPASS (临时目录): {sys._MEIPASS}")
                # 列出临时目录中的文件
                temp_dir = Path(sys._MEIPASS)
                print(f"\n临时目录中的文件:")
                for item in temp_dir.iterdir():
                    print(f"  - {item.name}")
            except Exception as e:
                print(f"无法访问临时目录: {e}")
        input("\n按 Enter 键退出...")
        return
    
    print("=" * 50)
    print("Excel 处理工具")
    print("=" * 50)
    print("正在启动应用...")
    print("浏览器将自动打开，如果没有自动打开，请访问: http://localhost:8501")
    print("=" * 50)
    print("提示：关闭此窗口将关闭应用程序")
    print("=" * 50)
    print()
    
    # 注意：浏览器打开逻辑已移到 Streamlit 启动后
    # 这里不再提前打开浏览器，等待服务器启动后再打开
    
    try:
        # 打印调试信息
        print(f"主程序文件路径: {main_file}")
        print(f"文件是否存在: {main_file.exists()}")
        print()
        
        # 启动 Streamlit
        # 在打包环境中，直接调用 Streamlit 模块，而不是通过 subprocess
        if getattr(sys, 'frozen', False):
            # 打包环境：直接调用 Streamlit
            print("\n正在启动 Streamlit 服务器...")
            print("=" * 50)
            
            # 设置环境变量
            os.environ['STREAMLIT_SERVER_HEADLESS'] = 'true'
            os.environ['STREAMLIT_BROWSER_GATHER_USAGE_STATS'] = 'false'
            os.environ['STREAMLIT_BROWSER_SERVER_ADDRESS'] = 'localhost'
            os.environ['STREAMLIT_GLOBAL_DEVELOPMENT_MODE'] = 'false'  # 禁用开发模式
            
            # 确保 Streamlit 能找到资源文件
            if getattr(sys, 'frozen', False):
                try:
                    import streamlit
                    # 设置 Streamlit 的资源路径
                    streamlit_path = Path(streamlit.__file__).parent
                    if hasattr(sys, '_MEIPASS'):
                        # 在打包环境中，确保资源路径正确
                        os.environ['STREAMLIT_STATIC_PATH'] = str(Path(sys._MEIPASS) / 'streamlit' / 'static')
                except:
                    pass
            
            # 直接调用 Streamlit
            # 在导入前修补 importlib.metadata 以避免元数据错误
            try:
                import importlib.metadata
                # 保存原始函数
                _original_version = getattr(importlib.metadata, 'version', None)
                _original_distribution = getattr(importlib.metadata, 'distribution', None)
                
                # 创建修补函数
                def _patched_version(name):
                    try:
                        if _original_version:
                            return _original_version(name)
                    except:
                        pass
                    # 如果找不到，返回默认版本
                    if name == 'streamlit':
                        return '1.28.0'
                    raise importlib.metadata.PackageNotFoundError(name)
                
                def _patched_distribution(name):
                    try:
                        if _original_distribution:
                            return _original_distribution(name)
                    except:
                        pass
                    raise importlib.metadata.PackageNotFoundError(name)
                
                # 应用修补
                importlib.metadata.version = _patched_version
                importlib.metadata.distribution = _patched_distribution
            except:
                pass  # 如果修补失败，继续尝试导入
            
            # 导入 Streamlit
            import streamlit.web.cli as stcli
            
            import sys as sys_module
            
            # 设置 sys.argv 为 Streamlit 命令
            original_argv = sys_module.argv[:]
            sys_module.argv = [
                'streamlit', 'run', str(main_file),
                '--server.headless', 'true',
                '--server.port', '8501',
                '--browser.gatherUsageStats', 'false',
                '--server.enableCORS', 'false',
                '--server.enableXsrfProtection', 'false',
                '--server.runOnSave', 'false',
                '--browser.serverAddress', 'localhost',
                '--global.developmentMode', 'false'  # 禁用开发模式以避免端口冲突
            ]
            
            try:
                # Streamlit 必须在主线程中运行（信号处理器要求）
                # 在后台线程中等待服务器启动并打开浏览器
                def wait_and_open_browser():
                    global _browser_opened  # 必须在函数开头声明
                    if wait_for_server(max_wait=30):
                        print("\nStreamlit 服务器已启动！")
                        print("=" * 50)
                        # 打开浏览器
                        if not _browser_opened:
                            try:
                                webbrowser.open('http://localhost:8501')
                                _browser_opened = True
                            except:
                                pass
                    else:
                        print("\n警告：等待服务器启动超时，但可能仍在启动中...")
                
                browser_thread = threading.Thread(target=wait_and_open_browser, daemon=True)
                browser_thread.start()
                
                # 在主线程中直接调用 Streamlit（阻塞调用）
                print("\n正在启动 Streamlit 服务器...")
                print("=" * 50)
                stcli.main()  # 这会阻塞直到 Streamlit 退出
            except Exception as e:
                print(f"\n启动 Streamlit 时出错: {e}")
                import traceback
                print("=" * 50)
                print("详细错误信息：")
                traceback.print_exc()
                print("=" * 50)
                input("按 Enter 键退出...")
            finally:
                sys_module.argv = original_argv
            
            return
        else:
            # 开发环境：使用 subprocess
            cmd = [
                sys.executable, '-m', 'streamlit', 'run', str(main_file),
                '--server.headless', 'true',
                '--server.port', '8501',
                '--browser.gatherUsageStats', 'false',
                '--server.enableCORS', 'false',
                '--server.enableXsrfProtection', 'false',
                '--server.runOnSave', 'false',
                '--browser.serverAddress', 'localhost'
            ]
        
        # 在打包环境中，可能需要设置环境变量
        env = os.environ.copy()
        env['STREAMLIT_SERVER_HEADLESS'] = 'true'
        env['STREAMLIT_BROWSER_GATHER_USAGE_STATS'] = 'false'
        # 禁用 Streamlit 自动打开浏览器
        env['STREAMLIT_BROWSER_SERVER_ADDRESS'] = 'localhost'
        
        # 检查端口是否被占用
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        port_in_use = sock.connect_ex(('localhost', 8501)) == 0
        sock.close()
        
        # Streamlit 是长期运行的进程
        # 不使用 PIPE，让输出直接显示在控制台，这样用户可以看到错误信息
        print("\n正在启动 Streamlit 服务器...")
        print("=" * 50)
        
        if getattr(sys, 'frozen', False):
            process = subprocess.Popen(cmd, env=env, cwd=str(exe_dir))
        else:
            process = subprocess.Popen(cmd, env=env)
        
        # 等待进程结束，同时检查是否有错误
        try:
            # 先等待一小段时间，检查是否立即失败
            time.sleep(5)  # 增加等待时间，让 Streamlit 有时间启动
            if process.poll() is not None:
                # 进程已退出，说明启动失败
                print(f"\n错误：Streamlit 启动失败（进程已退出，返回码: {process.returncode}）")
                print("请检查上面的错误信息")
                input("按 Enter 键退出...")
                return
            else:
                # 进程仍在运行，说明启动成功
                print("Streamlit 服务器已启动！")
                print("=" * 50)
                # 正常等待进程结束
                process.wait()
        except KeyboardInterrupt:
            print("\n正在关闭应用...")
            process.terminate()
            process.wait()
        except Exception as e:
            print(f"启动时出错: {e}")
            import traceback
            traceback.print_exc()
            if process.poll() is None:
                process.terminate()
            input("按 Enter 键退出...")
        finally:
            _app_running = False
    except Exception as e:
        # 外层异常处理
        print(f"\n发生错误: {e}")
        import traceback
        print("=" * 50)
        print("详细错误信息：")
        traceback.print_exc()
        print("=" * 50)
        _app_running = False
        input("\n按 Enter 键退出...")
    finally:
        _app_running = False

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n程序被用户中断")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n未捕获的异常: {e}")
        import traceback
        traceback.print_exc()
        input("\n按 Enter 键退出...")
        sys.exit(1)

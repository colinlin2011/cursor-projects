# -*- mode: python ; coding: utf-8 -*-
# PyInstaller 配置文件

import os
from pathlib import Path

block_cipher = None

# 获取当前目录
current_dir = Path.cwd()

# 数据文件列表（需要包含的所有文件）
datas = [
    ('main.py', '.'),
    ('config.py', '.'),
    ('utils', 'utils'),
]

# 收集 streamlit 的元数据文件和静态资源（如果存在）
try:
    import streamlit
    streamlit_path = Path(streamlit.__file__).parent
    
    # 查找 streamlit 的 dist-info 目录
    streamlit_dist_info = list(streamlit_path.parent.glob('streamlit*.dist-info'))
    if not streamlit_dist_info:
        # 尝试在 site-packages 中查找
        import site
        for site_pkg in site.getsitepackages():
            dist_info = Path(site_pkg).glob('streamlit*.dist-info')
            streamlit_dist_info.extend(dist_info)
    
    if streamlit_dist_info:
        for dist_info in streamlit_dist_info:
            datas.append((str(dist_info), str(dist_info.name)))
    
    # 收集 streamlit 的静态资源文件
    streamlit_static = streamlit_path / 'static'
    if streamlit_static.exists():
        datas.append((str(streamlit_static), 'streamlit/static'))
    
    # 收集 streamlit 的 web 资源
    streamlit_web = streamlit_path / 'web'
    if streamlit_web.exists():
        # 只包含必要的 web 资源
        for item in streamlit_web.iterdir():
            if item.is_dir() and item.name in ['static', 'static', 'components']:
                datas.append((str(item), f'streamlit/web/{item.name}'))
            elif item.suffix in ['.html', '.js', '.css']:
                datas.append((str(item), f'streamlit/web'))
except Exception as e:
    # 如果无法找到资源，继续（代码中会处理）
    print(f"警告：无法收集 Streamlit 资源: {e}")
    pass

# 隐藏导入（PyInstaller 可能无法自动检测的模块）
hiddenimports = [
    'streamlit',
    'pandas',
    'openpyxl',
    'xlrd',
    'streamlit.web.cli',
    'streamlit.runtime',
    'streamlit.runtime.scriptrunner',
    'streamlit.runtime.scriptrunner.magic_funcs',
    'streamlit.runtime.scriptrunner.script_runner',
    'streamlit.runtime.scriptrunner.script_run_context',
    'streamlit.runtime.scriptrunner.script_requests',
    'streamlit.runtime.state',
    'streamlit.runtime.state.session_state',
    'streamlit.runtime.caching',
    'streamlit.runtime.caching.cache_utils',
    'streamlit.runtime.caching.cache_errors',
    'streamlit.runtime.caching.cache_data_api',
    'streamlit.runtime.legacy_caching',
    'streamlit.runtime.legacy_caching.caching',
    'streamlit.runtime.metrics_util',
    'streamlit.runtime.uploaded_file_manager',
    'streamlit.runtime.uploaded_file_manager.uploaded_file_manager',
    'streamlit.runtime.secrets',
    'streamlit.runtime.cached_func',
    'streamlit.version',
    'streamlit.web.server',
    'streamlit.web.bootstrap',
    'streamlit.config',
    'streamlit.logger',
    'streamlit.file_util',
    'streamlit.source_util',
    'streamlit.watcher',
    'streamlit.watcher.path_watcher',
    'streamlit.watcher.polling_path_watcher',
    'altair',
    'plotly',
    'PIL',
    'pkg_resources.py2_warn',
    'importlib.metadata',
    'importlib_metadata',
    'watchdog',
    'watchdog.observers',
    'watchdog.events',
    'tornado',
    'tornado.web',
    'tornado.ioloop',
    'tornado.httpserver',
    'blinker',
]

a = Analysis(
    ['launcher.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'scipy',
        'numpy.distutils',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Excel处理工具',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # 显示控制台窗口（可以看到日志）
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # 可以在这里指定图标文件路径，例如: icon='icon.ico'
)

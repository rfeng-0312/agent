#!/usr/bin/env python3
"""
启动脚本 - 从项目根目录运行
"""

import subprocess
import sys
import os

# 切换到src目录
src_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src')
os.chdir(src_dir)

# 运行Flask应用
subprocess.run([sys.executable, 'app.py'])
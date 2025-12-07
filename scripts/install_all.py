#!/usr/bin/env python3
"""
简化的安装脚本
"""

import subprocess
import sys

def install_package(package):
    """安装单个包"""
    print(f"Installing {package}...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"OK: {package}")
        return True
    except:
        print(f"FAIL: {package}")
        return False

# 需要安装的包列表
packages = [
    "Flask==2.3.3",
    "Flask-CORS==4.0.0",
    "Werkzeug==2.3.7",
    "openai==1.14.3",
    "python-dotenv==1.0.0",
    "requests==2.32.5"
]

print("="*60)
print("Installing packages for 名侦探作业帮")
print("="*60)

# 升级pip
print("\n1. Upgrading pip...")
subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])

# 安装所有包
print("\n2. Installing packages...")
success_count = 0
for pkg in packages:
    if install_package(pkg):
        success_count += 1

print("\n" + "="*60)
print(f"Installation complete: {success_count}/{len(packages)} packages installed")
print("="*60)

# 创建必要的目录
import os
dirs_to_create = ['uploads', 'sessions']
for d in dirs_to_create:
    if not os.path.exists(d):
        os.makedirs(d)
        print(f"Created directory: {d}")

print("\nReady to run!")
print("Start with: python app.py")
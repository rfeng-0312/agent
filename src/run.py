#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
启动脚本 - 言简意赅
"""

import subprocess
import sys
import os

def main():
    print("="*60)
    print("言简意赅 - AI智能解题助手")
    print("="*60)
    print("\n正在启动服务器...")

    # 检查.env文件
    if not os.path.exists('.env'):
        print("\n警告: 未找到.env文件!")
        print("请按照以下步骤配置:")
        print("1. 复制 .env.example 为 .env")
        print("2. 在 .env 文件中填入你的 DeepSeek API Key")
        print("\n继续使用默认配置启动...")

    # 启动Flask应用
    try:
        print("\n服务器启动中...")
        print("访问地址: http://localhost:5000")
        print("按 Ctrl+C 停止服务器")
        print("-"*60)

        # 启动app.py
        os.execv(sys.executable, ['python', 'app.py'])

    except KeyboardInterrupt:
        print("\n\n服务器已停止")
    except Exception as e:
        print(f"\n启动失败: {str(e)}")
        input("\n按任意键退出...")

if __name__ == "__main__":
    main()

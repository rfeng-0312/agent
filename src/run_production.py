#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生产环境启动脚本
使用Waitress WSGI服务器运行Flask应用
"""

import os
import sys
from waitress import serve
from dotenv import load_dotenv

# 加载环境变量
load_dotenv('.env.production')

# 导入Flask应用
from app import app

if __name__ == '__main__':
    # 从环境变量获取配置
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))

    print(f"""
    ========================================
    言简意赅 - 生产环境启动
    ========================================
    服务器地址: http://{host}:{port}
    环境模式: {os.getenv('FLASK_ENV', 'production')}
    ========================================
    """)

    # 使用Waitress WSGI服务器运行
    serve(
        app,
        host=host,
        port=port,
        threads=os.getenv('THREADS', 8),
        connection_limit=os.getenv('CONNECTION_LIMIT', 1000),
        cleanup_interval=os.getenv('CLEANUP_INTERVAL', 10),
        channel_timeout=os.getenv('CHANNEL_TIMEOUT', 120),
        send_bytes=int(os.getenv('SEND_BYTES', 1024)),
        max_request_body_size=int(os.getenv('MAX_REQUEST_BODY_SIZE', 16777216)),  # 16MB
        expose_tracebacks=False,
        url_scheme='https' if os.getenv('HTTPS', 'false').lower() == 'true' else 'http'
    )

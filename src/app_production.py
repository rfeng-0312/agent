#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生产环境Flask应用配置
修改app.py以适应生产环境需求
"""

import os
import logging
import importlib
from logging.handlers import RotatingFileHandler
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

# 加载生产环境变量
load_dotenv('.env.production')

def create_app():
    """应用工厂函数"""
    app = Flask(__name__)

    # 生产环境配置
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))  # 16MB
    app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', 'uploads')

    # CORS配置 - 仅允许特定域名
    cors_origins = os.getenv('CORS_ORIGINS', 'http://localhost:3000,http://localhost:5000').split(',')
    CORS(app, origins=cors_origins, supports_credentials=True)

    # 配置日志
    setup_logging(app)

    # 注册蓝图和路由
    register_blueprints(app)

    return app

def setup_logging(app):
    """配置日志系统"""
    log_level = os.getenv('LOG_LEVEL', 'INFO')
    log_file = os.getenv('LOG_FILE', 'logs/app.log')

    # 确保日志目录存在
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # 配置文件日志处理器
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=10
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(getattr(logging, log_level))

    # 添加到应用日志器
    app.logger.addHandler(file_handler)
    app.logger.setLevel(getattr(logging, log_level))
    app.logger.info('言简意赅启动')

def register_blueprints(app):
    """注册蓝图和路由"""
    # 导入路由
    importlib.import_module("app")

    # 健康检查端点
    @app.route('/health')
    def health_check():
        return {'status': 'healthy', 'message': 'Flask backend is running'}

    # 错误处理
    @app.errorhandler(404)
    def not_found_error(error):
        return {'error': 'Resource not found'}, 404

    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f'Server Error: {error}')
        return {'error': 'Internal server error'}, 500

    @app.errorhandler(413)
    def too_large(error):
        return {'error': 'File too large'}, 413

# 创建应用实例
app = create_app()

if __name__ == '__main__':
    # 开发模式（直接运行此文件时）
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('PORT', 5000)),
        debug=os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    )

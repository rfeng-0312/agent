# -*- coding: utf-8 -*-
"""
数据库模块 - MySQL 连接和用户管理
"""

import os
import mysql.connector
from mysql.connector import Error
import hashlib
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_db_connection():
    """获取数据库连接"""
    try:
        connection = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST', 'sjc1.clusters.zeabur.com'),
            port=int(os.getenv('MYSQL_PORT', 29007)),
            user=os.getenv('MYSQL_USER', 'root'),
            password=os.getenv('MYSQL_PASSWORD'),
            database=os.getenv('MYSQL_DATABASE', 'zeabur'),
            charset='utf8mb4'
        )
        return connection
    except Error as e:
        logger.error(f"Database connection error: {e}")
        return None


def init_database():
    """初始化数据库表"""
    connection = get_db_connection()
    if not connection:
        logger.error("Cannot initialize database - no connection")
        return False

    try:
        cursor = connection.cursor()

        # 创建用户表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(255) DEFAULT NULL,
                phone VARCHAR(20) DEFAULT NULL,
                password_hash VARCHAR(255) NOT NULL,
                physics_score INT DEFAULT NULL,
                chemistry_score INT DEFAULT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                UNIQUE KEY unique_email (email),
                UNIQUE KEY unique_phone (phone)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        ''')

        connection.commit()
        logger.info("Database initialized successfully")
        return True
    except Error as e:
        logger.error(f"Database initialization error: {e}")
        return False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


def hash_password(password):
    """密码哈希"""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


def register_user(name, password, email=None, phone=None, physics_score=None, chemistry_score=None):
    """
    注册新用户

    Returns:
        dict: {'success': bool, 'message': str, 'user_id': int or None}
    """
    if not email and not phone:
        return {'success': False, 'message': '请提供邮箱或手机号'}

    connection = get_db_connection()
    if not connection:
        return {'success': False, 'message': '数据库连接失败'}

    try:
        cursor = connection.cursor()

        # 检查邮箱或手机号是否已存在
        if email:
            cursor.execute('SELECT id FROM users WHERE email = %s', (email,))
            if cursor.fetchone():
                return {'success': False, 'message': '该邮箱已被注册'}

        if phone:
            cursor.execute('SELECT id FROM users WHERE phone = %s', (phone,))
            if cursor.fetchone():
                return {'success': False, 'message': '该手机号已被注册'}

        # 插入新用户
        password_hash = hash_password(password)
        cursor.execute('''
            INSERT INTO users (name, email, phone, password_hash, physics_score, chemistry_score)
            VALUES (%s, %s, %s, %s, %s, %s)
        ''', (name, email, phone, password_hash, physics_score, chemistry_score))

        connection.commit()
        user_id = cursor.lastrowid

        return {'success': True, 'message': '注册成功', 'user_id': user_id}
    except Error as e:
        logger.error(f"Registration error: {e}")
        return {'success': False, 'message': f'注册失败: {str(e)}'}
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


def login_user(account, password):
    """
    用户登录

    Args:
        account: 用户名、邮箱或手机号
        password: 密码

    Returns:
        dict: {'success': bool, 'message': str, 'user': dict or None}
    """
    connection = get_db_connection()
    if not connection:
        return {'success': False, 'message': '数据库连接失败'}

    try:
        cursor = connection.cursor(dictionary=True)

        # 查找用户（通过用户名、邮箱或手机号）
        cursor.execute('''
            SELECT id, name, email, phone, password_hash, physics_score, chemistry_score
            FROM users
            WHERE name = %s OR email = %s OR phone = %s
        ''', (account, account, account))

        user = cursor.fetchone()

        if not user:
            return {'success': False, 'message': '账号不存在'}

        # 验证密码
        if user['password_hash'] != hash_password(password):
            return {'success': False, 'message': '密码错误'}

        # 移除密码哈希后返回用户信息
        del user['password_hash']
        return {'success': True, 'message': '登录成功', 'user': user}
    except Error as e:
        logger.error(f"Login error: {e}")
        return {'success': False, 'message': f'登录失败: {str(e)}'}
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


def check_account_exists(account):
    """
    检查账号（邮箱或手机号）是否存在

    Returns:
        dict: {'exists': bool, 'user_id': int or None, 'name': str or None}
    """
    connection = get_db_connection()
    if not connection:
        return {'exists': False, 'user_id': None, 'name': None}

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute('''
            SELECT id, name FROM users
            WHERE email = %s OR phone = %s
        ''', (account, account))

        user = cursor.fetchone()

        if user:
            return {'exists': True, 'user_id': user['id'], 'name': user['name']}
        return {'exists': False, 'user_id': None, 'name': None}
    except Error as e:
        logger.error(f"Check account error: {e}")
        return {'exists': False, 'user_id': None, 'name': None}
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


def reset_password(account, new_password):
    """
    重置密码

    Args:
        account: 邮箱或手机号
        new_password: 新密码

    Returns:
        dict: {'success': bool, 'message': str}
    """
    connection = get_db_connection()
    if not connection:
        return {'success': False, 'message': '数据库连接失败'}

    try:
        cursor = connection.cursor()

        password_hash = hash_password(new_password)
        cursor.execute('''
            UPDATE users SET password_hash = %s
            WHERE email = %s OR phone = %s
        ''', (password_hash, account, account))

        if cursor.rowcount == 0:
            return {'success': False, 'message': '账号不存在'}

        connection.commit()
        return {'success': True, 'message': '密码重置成功'}
    except Error as e:
        logger.error(f"Reset password error: {e}")
        return {'success': False, 'message': f'重置失败: {str(e)}'}
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


def get_user_by_id(user_id):
    """根据ID获取用户信息"""
    connection = get_db_connection()
    if not connection:
        return None

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute('''
            SELECT id, name, email, phone, physics_score, chemistry_score
            FROM users WHERE id = %s
        ''', (user_id,))
        return cursor.fetchone()
    except Error as e:
        logger.error(f"Get user error: {e}")
        return None
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

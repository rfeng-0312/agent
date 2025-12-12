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

        # 创建日记表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS diaries (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                content TEXT NOT NULL,
                ai_response TEXT DEFAULT NULL,
                mood_score INT DEFAULT NULL COMMENT '心情评分 1-5',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                INDEX idx_user_id (user_id),
                INDEX idx_created_at (created_at)
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


# ==================== 日记相关函数 ====================

def create_diary(user_id, content, mood_score=None):
    """创建新日记"""
    connection = get_db_connection()
    if not connection:
        return {'success': False, 'message': '数据库连接失败', 'diary_id': None}

    try:
        cursor = connection.cursor()
        cursor.execute('''
            INSERT INTO diaries (user_id, content, mood_score)
            VALUES (%s, %s, %s)
        ''', (user_id, content, mood_score))

        connection.commit()
        diary_id = cursor.lastrowid

        return {'success': True, 'message': '日记保存成功', 'diary_id': diary_id}
    except Error as e:
        logger.error(f"Create diary error: {e}")
        return {'success': False, 'message': f'保存失败: {str(e)}', 'diary_id': None}
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


def update_diary_ai_response(diary_id, ai_response):
    """更新日记的AI回复"""
    connection = get_db_connection()
    if not connection:
        return {'success': False, 'message': '数据库连接失败'}

    try:
        cursor = connection.cursor()
        cursor.execute('''
            UPDATE diaries SET ai_response = %s WHERE id = %s
        ''', (ai_response, diary_id))

        connection.commit()
        return {'success': True, 'message': 'AI回复已更新'}
    except Error as e:
        logger.error(f"Update diary AI response error: {e}")
        return {'success': False, 'message': f'更新失败: {str(e)}'}
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


def get_diary_by_id(diary_id, user_id):
    """根据ID获取日记详情"""
    connection = get_db_connection()
    if not connection:
        return None

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute('''
            SELECT id, content, ai_response, mood_score, created_at, updated_at
            FROM diaries WHERE id = %s AND user_id = %s
        ''', (diary_id, user_id))

        result = cursor.fetchone()
        if result:
            result['created_at'] = result['created_at'].isoformat() if result['created_at'] else None
            result['updated_at'] = result['updated_at'].isoformat() if result['updated_at'] else None
        return result
    except Error as e:
        logger.error(f"Get diary error: {e}")
        return None
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


def get_user_diaries(user_id, limit=20, offset=0):
    """获取用户的日记列表"""
    connection = get_db_connection()
    if not connection:
        return []

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute('''
            SELECT id,
                   LEFT(content, 100) as content,
                   LEFT(ai_response, 50) as ai_response,
                   mood_score,
                   created_at
            FROM diaries
            WHERE user_id = %s
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
        ''', (user_id, limit, offset))

        results = cursor.fetchall()
        for r in results:
            r['created_at'] = r['created_at'].isoformat() if r['created_at'] else None
        return results
    except Error as e:
        logger.error(f"Get user diaries error: {e}")
        return []
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


def get_diary_count(user_id):
    """获取用户日记总数"""
    connection = get_db_connection()
    if not connection:
        return 0

    try:
        cursor = connection.cursor()
        cursor.execute('SELECT COUNT(*) FROM diaries WHERE user_id = %s', (user_id,))
        result = cursor.fetchone()
        return result[0] if result else 0
    except Error as e:
        logger.error(f"Get diary count error: {e}")
        return 0
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


def check_diary_today(user_id):
    """检查用户今天是否已写日记"""
    connection = get_db_connection()
    if not connection:
        return {'has_diary': False, 'diary_id': None}

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute('''
            SELECT id FROM diaries
            WHERE user_id = %s AND DATE(created_at) = CURDATE()
            ORDER BY created_at DESC LIMIT 1
        ''', (user_id,))

        result = cursor.fetchone()
        if result:
            return {'has_diary': True, 'diary_id': result['id']}
        return {'has_diary': False, 'diary_id': None}
    except Error as e:
        logger.error(f"Check diary today error: {e}")
        return {'has_diary': False, 'diary_id': None}
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


def get_diary_streak(user_id):
    """获取用户连续写日记天数"""
    connection = get_db_connection()
    if not connection:
        return 0

    try:
        cursor = connection.cursor()
        cursor.execute('''
            SELECT DISTINCT DATE(created_at) as diary_date
            FROM diaries
            WHERE user_id = %s
            ORDER BY diary_date DESC
        ''', (user_id,))

        dates = [row[0] for row in cursor.fetchall()]
        if not dates:
            return 0

        from datetime import date, timedelta
        today = date.today()
        streak = 0

        # 检查今天或昨天是否有日记
        if dates[0] != today and dates[0] != today - timedelta(days=1):
            return 0

        # 计算连续天数
        expected_date = dates[0]
        for diary_date in dates:
            if diary_date == expected_date:
                streak += 1
                expected_date = diary_date - timedelta(days=1)
            else:
                break

        return streak
    except Error as e:
        logger.error(f"Get diary streak error: {e}")
        return 0
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


def delete_diary(diary_id, user_id):
    """删除日记"""
    connection = get_db_connection()
    if not connection:
        return {'success': False, 'message': '数据库连接失败'}

    try:
        cursor = connection.cursor()
        cursor.execute('''
            DELETE FROM diaries WHERE id = %s AND user_id = %s
        ''', (diary_id, user_id))

        if cursor.rowcount == 0:
            return {'success': False, 'message': '日记不存在或无权删除'}

        connection.commit()
        return {'success': True, 'message': '日记已删除'}
    except Error as e:
        logger.error(f"Delete diary error: {e}")
        return {'success': False, 'message': f'删除失败: {str(e)}'}
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

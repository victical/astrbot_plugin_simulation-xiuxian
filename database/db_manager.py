# astrbot_xiuxian_plugin/database/db_manager.py

import sqlite3
from ..config import settings
from . import schemas

def create_connection():
    """创建并返回一个到 SQLite 数据库的连接"""
    conn = None
    try:
        conn = sqlite3.connect(settings.DATABASE_FILE)
        return conn
    except sqlite3.Error as e:
        print(f"数据库连接错误: {e}")
    return conn

def execute_query(sql, params=()):
    """
    执行一个SQL语句 (INSERT, UPDATE, DELETE)
    :param sql: SQL 语句
    :param params: SQL 语句的参数
    """
    try:
        with create_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            conn.commit()
    except sqlite3.Error as e:
        print(f"数据库查询执行错误: {e}")

def fetch_query(sql, params=(), one=False):
    """
    执行一个 SELECT 查询并返回结果
    :param sql: SQL 语句
    :param params: SQL 语句的参数
    :param one: 如果为 True, 返回单条记录，否则返回所有记录
    :return: 查询结果
    """
    try:
        with create_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            if one:
                return cursor.fetchone()
            return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"数据库查询获取错误: {e}")
        return None

def initialize_database():
    """初始化数据库，创建所有必要的表"""
    print("正在初始化数据库...")
    execute_query(schemas.CREATE_PLAYERS_TABLE_SQL)
    print("数据库表 'players' 已成功创建或已存在。")
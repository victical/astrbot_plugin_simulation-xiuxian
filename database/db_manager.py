# astrbot_xiuxian_plugin/database/db_manager.py
from astrbot.core import logger
import sqlite3
from ..config import settings
from . import schemas

def create_connection():
    """创建并返回一个到 SQLite 数据库的连接"""
    conn = None
    try:
        logger.info(f"正在连接数据库: {settings.DATABASE_FILE}")
        conn = sqlite3.connect(settings.DATABASE_FILE)
        logger.info("数据库连接成功。")
        return conn
    except sqlite3.Error as e:
        logger.error(f"数据库连接错误: {e}", exc_info=True)
    return conn

def execute_query(sql, params=()):
    """
    执行一个SQL语句 (INSERT, UPDATE, DELETE)
    :param sql: SQL 语句
    :param params: SQL 语句的参数
    """
    try:
        with create_connection() as conn:
            if conn is None:
                logger.error("无法执行查询，因为数据库连接失败。")
                return
            cursor = conn.cursor()
            logger.debug(f"执行 SQL: {sql} with params: {params}")
            cursor.execute(sql, params)
            conn.commit()
    except sqlite3.Error as e:
        logger.error(f"数据库查询执行错误: {e}", exc_info=True)

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
            if conn is None:
                logger.error("无法执行查询，因为数据库连接失败。")
                return None
            cursor = conn.cursor()
            logger.debug(f"执行 SQL: {sql} with params: {params}")
            cursor.execute(sql, params)
            if one:
                return cursor.fetchone()
            return cursor.fetchall()
    except sqlite3.Error as e:
        logger.error(f"数据库查询获取错误: {e}", exc_info=True)
        return None

def initialize_database():
    """初始化数据库，创建所有必要的表"""
    logger.info("正在初始化数据库...")
    execute_query(schemas.CREATE_PLAYERS_TABLE_SQL)
    logger.info("数据库表 'players' 已成功创建或已存在。")

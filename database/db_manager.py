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

def _update_database_schema():
    """检查并更新数据库表结构，用于平滑升级"""
    logger.info("正在检查数据库表结构更新...")
    try:
        with create_connection() as conn:
            if conn is None:
                return
            cursor = conn.cursor()
            
            # 检查 players 表的列信息
            cursor.execute("PRAGMA table_info(players)")
            columns = [row[1] for row in cursor.fetchall()]
            
            # 迁移：mp -> spirit_power
            if 'mp' in columns and 'spirit_power' not in columns:
                logger.info("检测到旧版 'mp' 字段，正在迁移到 'spirit_power'...")
                cursor.execute("ALTER TABLE players RENAME COLUMN mp TO spirit_power")
                logger.info("字段 'mp' 已成功重命名为 'spirit_power'。")

            # 新增：max_spirit_power
            if 'max_spirit_power' not in columns:
                logger.info("正在添加 'max_spirit_power' 字段...")
                # 注意：为现有用户设置一个合理的默认值，例如 100
                cursor.execute("ALTER TABLE players ADD COLUMN max_spirit_power INTEGER NOT NULL DEFAULT 100")
                logger.info("字段 'max_spirit_power' 已成功添加。")

            # 新增：meditation_start_time
            if 'meditation_start_time' not in columns:
                logger.info("正在添加 'meditation_start_time' 字段...")
                cursor.execute("ALTER TABLE players ADD COLUMN meditation_start_time TIMESTAMP")
                logger.info("字段 'meditation_start_time' 已成功添加。")
            
            conn.commit()
            logger.info("数据库表结构检查更新完成。")
    except sqlite3.Error as e:
        logger.error(f"更新数据库表结构时出错: {e}", exc_info=True)

def initialize_database():
    """初始化数据库，创建所有必要的表，并执行数据迁移"""
    logger.info("正在初始化数据库...")
    execute_query(schemas.CREATE_PLAYERS_TABLE_SQL)
    logger.info("数据库表 'players' 已成功创建或已存在。")
    _update_database_schema()  # 执行表结构更新检查

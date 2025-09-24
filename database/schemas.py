# astrbot_xiuxian_plugin/database/schemas.py

# 定义创建玩家表的 SQL 语句
# 使用 TEXT 作为 user_id 的类型以兼容不同平台的ID格式
# 使用 TEXT 类型存储 JSON 格式的背包和技能数据
CREATE_PLAYERS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS players (
    user_id TEXT PRIMARY KEY,
    user_name TEXT NOT NULL,
    level TEXT NOT NULL,
    experience INTEGER NOT NULL,
    spirit_stones INTEGER NOT NULL,
    hp INTEGER NOT NULL,
    mp INTEGER NOT NULL,
    attack INTEGER NOT NULL,
    defense INTEGER NOT NULL,
    sect TEXT,
    sect_rank TEXT,
    contribution INTEGER DEFAULT 0,
    inventory TEXT,
    learned_skills TEXT,
    current_mission TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

# 未来可以添加其他表的创建语句
# CREATE_SECTS_TABLE_SQL = "..."
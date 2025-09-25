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
    spirit_power INTEGER NOT NULL,
    max_spirit_power INTEGER NOT NULL,
    attack INTEGER NOT NULL,
    defense INTEGER NOT NULL,
    meditation_start_time TIMESTAMP,
    sect TEXT,
    sect_rank TEXT,
    contribution INTEGER DEFAULT 0,
    inventory TEXT,
    skills TEXT,
    equipment TEXT,
    current_mission TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

# 定义创建物品表的 SQL 语句
CREATE_ITEMS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    type TEXT NOT NULL,  -- weapon, artifact, elixir, material, skill
    level_requirement TEXT,  -- 使用该物品所需的最低修仙等级
    description TEXT,
    attributes TEXT,  -- JSON 格式的属性数据
    crafting_materials TEXT,  -- JSON 格式的合成材料需求
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

# 定义创建玩家物品表的 SQL 语句
CREATE_PLAYER_ITEMS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS player_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_id TEXT NOT NULL,
    item_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 1,
    enhancement_level INTEGER DEFAULT 0,  -- 强化等级
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (player_id) REFERENCES players (user_id) ON DELETE CASCADE,
    FOREIGN KEY (item_id) REFERENCES items (id) ON DELETE CASCADE
);
"""

# 定义创建合成配方表的 SQL 语句
CREATE_RECIPES_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS recipes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    result_item_id INTEGER NOT NULL,
    required_materials TEXT NOT NULL,  -- JSON 格式: {"material_name": quantity, ...}
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (result_item_id) REFERENCES items (id) ON DELETE CASCADE
);
"""
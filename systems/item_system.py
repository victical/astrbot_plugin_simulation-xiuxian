# astrbot_xiuxian_plugin/systems/item_system.py
import random
import json
from ..database.repositories import player_repository
from ..database.db_manager import execute_query, fetch_query
from ..config.cultivation_levels import LEVEL_ORDER, CULTIVATION_LEVELS

class ItemType:
    WEAPON = "weapon"
    ARTIFACT = "artifact" 
    ELIXIR = "elixir"
    SKILL = "skill"
    MATERIAL = "material"

# 物品属性配置
ITEM_ATTRIBUTES_CONFIG = {
    ItemType.WEAPON: {
        "炼气": {"attack": (5, 15), "crit_rate": (0, 5), "crit_damage": (10, 30)},
        "筑基": {"attack": (20, 50), "crit_rate": (2, 10), "crit_damage": (20, 50)},
        "金丹": {"attack": (60, 150), "crit_rate": (5, 15), "crit_damage": (30, 80)},
        "元婴": {"attack": (200, 500), "crit_rate": (10, 25), "crit_damage": (50, 150)},
        "化神": {"attack": (600, 1500), "crit_rate": (15, 35), "crit_damage": (100, 300)},
        "炼虚": {"attack": (2000, 5000), "crit_rate": (20, 50), "crit_damage": (200, 500)},
        "合体": {"attack": (6000, 15000), "crit_rate": (25, 60), "crit_damage": (300, 800)},
        "大乘": {"attack": (20000, 50000), "crit_rate": (30, 75), "crit_damage": (500, 1500)},
    },
    ItemType.ARTIFACT: {
        "炼气": {"defense": (3, 10), "hp": (20, 50), "spirit_power": (10, 30)},
        "筑基": {"defense": (15, 40), "hp": (100, 300), "spirit_power": (50, 150)},
        "金丹": {"defense": (50, 150), "hp": (500, 1500), "spirit_power": (200, 600)},
        "元婴": {"defense": (200, 600), "hp": (2000, 6000), "spirit_power": (1000, 3000)},
        "化神": {"defense": (800, 2400), "hp": (8000, 24000), "spirit_power": (4000, 12000)},
        "炼虚": {"defense": (3000, 9000), "hp": (30000, 90000), "spirit_power": (15000, 45000)},
        "合体": {"defense": (10000, 30000), "hp": (100000, 300000), "spirit_power": (50000, 150000)},
        "大乘": {"defense": (30000, 100000), "hp": (300000, 1000000), "spirit_power": (150000, 500000)},
    },
    ItemType.ELIXIR: {
        "炼气": {"exp_bonus": (50, 200), "spirit_power_restore": (20, 100)},
        "筑基": {"exp_bonus": (300, 1000), "spirit_power_restore": (100, 500)},
        "金丹": {"exp_bonus": (1500, 5000), "spirit_power_restore": (500, 2000)},
        "元婴": {"exp_bonus": (8000, 30000), "spirit_power_restore": (2000, 10000)},
        "化神": {"exp_bonus": (40000, 150000), "spirit_power_restore": (10000, 50000)},
        "炼虚": {"exp_bonus": (200000, 800000), "spirit_power_restore": (50000, 200000)},
        "合体": {"exp_bonus": (1000000, 4000000), "spirit_power_restore": (200000, 1000000)},
        "大乘": {"exp_bonus": (5000000, 20000000), "spirit_power_restore": (1000000, 5000000)},
    }
}

# 物品名称前缀和后缀，用于生成霸气名称
WEAPON_NAME_PREFIXES = [
    "斩龙", "破天", "诛仙", "屠魔", "裂空", "焚天", "冰封", "雷鸣", "噬魂", "碎星",
    "绝世", "无双", "霸天", "惊鸿", "龙吟", "凤鸣", "虎啸", "龙威", "神罚", "天谴"
]

WEAPON_NAME_SUFFIXES = [
    "剑", "刀", "枪", "戟", "斧", "锤", "弓", "弩", "鞭", "爪",
    "扇", "伞", "镜", "铃", "琴", "箫", "笛", "钟", "鼓", "印"
]

ARTIFACT_NAME_PREFIXES = [
    "九天", "玄天", "太虚", "混元", "太极", "无极", "乾坤", "阴阳", "五行", "八卦",
    "紫霄", "青云", "碧落", "黄泉", "昆仑", "蓬莱", "方丈", "瀛洲", "天罡", "地煞"
]

ARTIFACT_NAME_SUFFIXES = [
    "镜", "塔", "鼎", "炉", "珠", "瓶", "葫", "袋", "幡", "钟",
    "印", " ring", "镯", "佩", "符", "卷", "图", "阵", "盘", "匣"
]

ELIXIR_NAME_PREFIXES = [
    "九转", "七彩神", "万年", "千秋", "百炼", "灵虚", "天元", "地灵", "玄武", "朱雀",
    "青龙", "白虎", "麒麟", "凤凰", "应龙", "饕餮", "混沌", "太初", "鸿蒙", "无极"
]

ELIXIR_NAME_SUFFIXES = [
    "丹", "丸", "散", "露", "液", "膏", "霜", "粉", "丸", "酏",
    "酏", "酏", "酏", "酏", "酏", "酏", "酏", "酏", "酏", "酏"
]

SKILL_NAME_PREFIXES = [
    "太虚", "九天", "无极", "混元", "太极", "紫霄", "青云", "碧落", "黄泉", "昆仑",
    "蓬莱", "方丈", "瀛洲", "天罡", "地煞", "五行", "八卦", "阴阳", "乾坤", "玄天"
]

SKILL_NAME_SUFFIXES = [
    "诀", "经", "录", "典", "法", "术", "功", "道", "心法", "秘术",
    "真言", "咒", "印", "章", "篇", "卷", "谱", "诀要", "总纲", "精要"
]


def generate_item_name(item_type: str, level: str) -> str:
    """
    程序生成物品名称
    """
    if item_type == ItemType.WEAPON:
        prefix = random.choice(WEAPON_NAME_PREFIXES)
        suffix = random.choice(WEAPON_NAME_SUFFIXES)
        return f"{prefix}{suffix}"
    elif item_type == ItemType.ARTIFACT:
        prefix = random.choice(ARTIFACT_NAME_PREFIXES)
        suffix = random.choice(ARTIFACT_NAME_SUFFIXES)
        return f"{prefix}{suffix}"
    elif item_type == ItemType.ELIXIR:
        prefix = random.choice(ELIXIR_NAME_PREFIXES)
        suffix = random.choice(ELIXIR_NAME_SUFFIXES)
        return f"{prefix}{suffix}"
    elif item_type == ItemType.SKILL:
        prefix = random.choice(SKILL_NAME_PREFIXES)
        suffix = random.choice(SKILL_NAME_SUFFIXES)
        return f"{prefix}{suffix}"
    else:
        return f"神秘{item_type}"

def generate_item_attributes(item_type: str, level: str) -> dict:
    """
    根据物品类型和等级生成属性
    """
    config = ITEM_ATTRIBUTES_CONFIG.get(item_type, {})
    level_config = config.get(level, {})
    
    attributes = {}
    for attr, (min_val, max_val) in level_config.items():
        # 根据名称霸气程度调整数值
        base_value = random.randint(min_val, max_val)
        # 有小概率生成超越当前境界的属性值
        if random.random() < 0.1:  # 10%概率
            base_value = int(base_value * random.uniform(1.2, 2.0))
        attributes[attr] = base_value
    
    return attributes

def create_item(name: str, item_type: str, level_req: str, description: str = "", attributes: dict = None, materials: dict = None):
    """
    创建新物品并存入数据库
    """
    if attributes is None:
        attributes = {}
    if materials is None:
        materials = {}
        
    # 为丹药添加使用说明
    if item_type == ItemType.ELIXIR and not description:
        description = f"一枚{level_req}境界的丹药，服用后可增加修为并恢复灵力。使用指令：服用 {name}"
        
    sql = """
    INSERT OR IGNORE INTO items (name, type, level_requirement, description, attributes, crafting_materials)
    VALUES (?, ?, ?, ?, ?, ?)
    """
    params = (
        name,
        item_type,
        level_req,
        description,
        json.dumps(attributes),
        json.dumps(materials)
    )
    execute_query(sql, params)

async def generate_random_item(provider, item_type: str, player_level: str) -> dict:
    """
    为玩家生成随机物品
    """
    # 确定物品等级（大多数情况下与玩家等级相同，小概率高一级）
    player_level_index = LEVEL_ORDER.index(player_level)
    max_level_index = min(player_level_index + (1 if random.random() < 0.2 else 0), len(LEVEL_ORDER) - 2)
    item_level_index = random.randint(player_level_index, max_level_index)
    item_level = LEVEL_ORDER[item_level_index]
    
    # 生成物品名称
    item_name = generate_item_name(item_type, item_level)
    
    # 生成物品属性
    attributes = generate_item_attributes(item_type, item_level)
    
    # 生成描述
    description = ""
    if item_type == ItemType.ELIXIR:
        description = f"一枚{item_level}境界的丹药，服用后可增加修为并恢复灵力。使用指令：服用 {item_name}"
    elif item_type == ItemType.SKILL:
        description = f"一种{item_level}境界的功法，可提升修为效率。"
    else:
        description = f"一件{item_level}境界的{item_type}"
    
    # 创建物品（如果不存在）
    create_item(item_name, item_type, item_level, description, attributes)
    
    return {
        "name": item_name,
        "type": item_type,
        "level": item_level,
        "attributes": attributes,
        "description": description
    }

def add_item_to_player(user_id: str, item_name: str, quantity: int = 1):
    """
    将物品添加到玩家背包
    """
    # 获取物品ID
    item_sql = "SELECT id FROM items WHERE name = ?"
    item_result = fetch_query(item_sql, (item_name,), one=True)
    
    if not item_result:
        return False
    
    item_id = item_result[0]
    
    # 检查玩家是否已有该物品
    player_item_sql = "SELECT id, quantity FROM player_items WHERE player_id = ? AND item_id = ?"
    player_item_result = fetch_query(player_item_sql, (user_id, item_id), one=True)
    
    if player_item_result:
        # 更新数量
        update_sql = "UPDATE player_items SET quantity = quantity + ? WHERE id = ?"
        execute_query(update_sql, (quantity, player_item_result[0]))
    else:
        # 插入新记录
        insert_sql = "INSERT INTO player_items (player_id, item_id, quantity) VALUES (?, ?, ?)"
        execute_query(insert_sql, (user_id, item_id, quantity))
    
    return True

def get_player_items(user_id: str) -> list:
    """
    获取玩家所有物品
    """
    sql = """
    SELECT i.name, i.type, i.level_requirement, i.description, i.attributes, pi.quantity, pi.enhancement_level
    FROM player_items pi
    JOIN items i ON pi.item_id = i.id
    WHERE pi.player_id = ?
    """
    results = fetch_query(sql, (user_id,))
    
    items = []
    for result in results:
        items.append({
            "name": result[0],
            "type": result[1],
            "level_requirement": result[2],
            "description": result[3],
            "attributes": json.loads(result[4]) if result[4] else {},
            "quantity": result[5],
            "enhancement_level": result[6]
        })
    
    return items

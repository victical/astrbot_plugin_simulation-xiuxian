# astrbot_xiuxian_plugin/systems/async_monster_generator.py
"""异步怪物生成系统，支持使用大模型生成怪物名称"""

import random
from ..models.monster import Monster
from ..config.cultivation_levels import LEVEL_ORDER

# 怪物类型配置
MONSTER_TYPES = {
    "凡人": {
        "common": ["凶兽", "低阶精怪"],
        "elite": ["强凶兽", "变异精怪"],
        "boss": ["远古凶兽", "精怪王"]
    },
    "炼气": {
        "common": ["妖兽", "二阶灵植"],
        "elite": ["变异妖兽", "三阶灵植"],
        "boss": ["妖王级妖兽", "上古遗种"]
    },
    "筑基": {
        "common": ["妖兽", "三阶灵植"],
        "elite": ["变异妖兽", "四阶灵植"],
        "boss": ["妖王级妖兽", "上古遗种"]
    },
    "金丹": {
        "common": ["大妖级妖兽", "高阶灵植"],
        "elite": ["变异大妖", "五阶灵植"],
        "boss": ["大妖王级", "地灵类"]
    },
    "元婴": {
        "common": ["大妖王级", "地灵类"],
        "elite": ["太古遗种", "变异地灵"],
        "boss": ["太古妖兽", "灵界来客"]
    },
    "化神": {
        "common": ["太古妖兽", "高阶地灵"],
        "elite": ["混沌遗种", "堕落神灵"],
        "boss": ["远古神兽", "天界使者"]
    },
    "炼虚": {
        "common": ["远古神兽", "天界生物"],
        "elite": ["混沌神兽", "虚空生物"],
        "boss": ["太古神王", "天道化身"]
    },
    "合体": {
        "common": ["混沌神兽", "虚空生物"],
        "elite": ["太古神王", "天道化身"],
        "boss": ["天道主宰", "宇宙意志"]
    },
    "大乘": {
        "common": ["天道主宰", "宇宙意志"],
        "elite": ["创世神兽", "混沌主宰"],
        "boss": ["宇宙创世神", "混沌元始神"]
    }
}

# 怪物区域配置
MONSTER_AREAS = {
    "凡人": ["新手村周边", "凡人山脉", "低阶灵矿外围"],
    "炼气": ["中低阶修士历练区", "普通山林", "筑基期宗门后山"],
    "筑基": ["高阶修士试炼地", "灵矿深处", "筑基期宗门内门"],
    "金丹": ["金丹期禁地", "秘境入口", "宗门核心区域"],
    "元婴": ["元婴修士禁地", "深海区域", "上古战场外围"],
    "化神": ["化神期险地", "界域裂缝边缘", "高浓度灵气山谷"],
    "炼虚": ["炼虚修士专属秘境", "灵界通道附近", "星空古路外围"],
    "合体": ["合体期秘境", "仙界裂缝", "混沌虚空"],
    "大乘": ["大乘期禁地", "天界入口", "宇宙边缘"],
    "渡境": ["渡劫期秘境", "天道试炼场", "宇宙核心"],
    "仙人": ["仙界", "天道领域", "宇宙本源"]
}

# 怪物属性配置
MONSTER_CONFIG = {
    "凡人": {"hp_range": (30, 60), "attack_range": (5, 10), "defense_range": (2, 5), "exp_reward": 5, "spirit_stones_reward": (1, 3)},
    "炼气": {"hp_range": (80, 200), "attack_range": (15, 35), "defense_range": (8, 20), "exp_reward": 20, "spirit_stones_reward": (5, 15)},
    "筑基": {"hp_range": (300, 800), "attack_range": (50, 120), "defense_range": (30, 80), "exp_reward": 100, "spirit_stones_reward": (20, 50)},
    "金丹": {"hp_range": (1000, 3000), "attack_range": (150, 400), "defense_range": (100, 250), "exp_reward": 500, "spirit_stones_reward": (100, 200)},
    "元婴": {"hp_range": (5000, 15000), "attack_range": (500, 1500), "defense_range": (300, 800), "exp_reward": 2000, "spirit_stones_reward": (300, 600)},
    "化神": {"hp_range": (20000, 50000), "attack_range": (1500, 4000), "defense_range": (1000, 2500), "exp_reward": 8000, "spirit_stones_reward": (800, 1500)},
    "炼虚": {"hp_range": (80000, 200000), "attack_range": (5000, 15000), "defense_range": (3000, 8000), "exp_reward": 30000, "spirit_stones_reward": (2000, 4000)},
    "合体": {"hp_range": (300000, 800000), "attack_range": (15000, 40000), "defense_range": (10000, 25000), "exp_reward": 100000, "spirit_stones_reward": (5000, 10000)},
    "大乘": {"hp_range": (1000000, 3000000), "attack_range": (50000, 150000), "defense_range": (30000, 80000), "exp_reward": 500000, "spirit_stones_reward": (15000, 30000)},
    "渡境": {"hp_range": (3000000, 10000000), "attack_range": (150000, 500000), "defense_range": (100000, 250000), "exp_reward": 2000000, "spirit_stones_reward": (30000, 60000)},
    "仙人": {"hp_range": (10000000, 30000000), "attack_range": (500000, 1500000), "defense_range": (300000, 800000), "exp_reward": 10000000, "spirit_stones_reward": (100000, 200000)}
}

# 默认怪物名称库
DEFAULT_MONSTER_NAMES = {
    ("凡人", "common"): ["青狼", "赤焰鼠", "草精", "石灵", "土蛇", "风雀", "水蛭", "火蚁", "木妖", "岩怪"],
    ("凡人", "elite"): ["青狼王", "赤焰王鼠", "草精王", "石灵王", "土蛇王"],
    ("凡人", "boss"): ["远古青狼", "赤焰鼠王"],
    ("炼气", "common"): ["黑纹熊", "风翎鸟", "食人花", "迷魂草", "铁甲虫", "雷鼠", "冰蛇", "火狐", "土熊", "水蛇"],
    ("炼气", "elite"): ["黑纹熊王", "风翎鹰", "食人花王", "迷魂草王", "铁甲虫王"],
    ("炼气", "boss"): ["妖王级黑熊", "风翎鸟王"],
    ("筑基", "common"): ["烈焰狮", "玄冰龟", "雷鹰", "火蛇", "土龙", "水豹", "风狼", "木猿", "金鼠", "石虎"],
    ("筑基", "elite"): ["烈焰狮王", "玄冰龟王", "雷鹰王", "火蛇王", "土龙王"],
    ("筑基", "boss"): ["烈焰狮王", "玄冰龟皇"],
    ("金丹", "common"): ["风雷鹏", "幽冥虎", "山神", "土地神", "雷兽", "冰龙", "火狮", "金甲虫", "风狼", "木灵"],
    ("金丹", "elite"): ["风雷鹏王", "幽冥虎王", "山神王", "土地神王", "雷兽王"],
    ("金丹", "boss"): ["风雷鹏皇", "幽冥虎皇"],
    ("元婴", "common"): ["穷奇幼崽", "饕餮后裔", "天魔", "异界凶兽", "混沌兽", "虚空兽", "星兽", "灵兽", "神兽", "圣兽"],
    ("元婴", "elite"): ["穷奇后裔", "饕餮真传", "高阶天魔", "异界霸主", "混沌王兽"],
    ("元婴", "boss"): ["穷奇真身", "饕餮分身"],
    ("化神", "common"): ["太古神兽", "天界生物", "混沌神兽", "虚空生物", "星界神兽", "灵界神兽", "神界神兽", "圣界神兽", "仙界神兽", "道界神兽"],
    ("化神", "elite"): ["太古神王", "天界主宰", "混沌真神", "虚空霸主", "星界帝君"],
    ("化神", "boss"): ["太古神皇", "天界天帝"],
    ("炼虚", "common"): ["混沌神兽", "虚空生物", "星界神兽", "灵界神兽", "神界神兽", "圣界神兽", "仙界神兽", "道界神兽", "天界神兽", "宇宙神兽"],
    ("炼虚", "elite"): ["混沌主宰", "虚空帝王", "星界至尊", "灵界之主", "神界神王"],
    ("炼虚", "boss"): ["混沌元始神", "虚空创世神"],
    ("合体", "common"): ["宇宙创世神", "混沌元始神", "天道主宰", "宇宙意志", "创世神兽", "混沌主宰", "天道化身", "宇宙意识", "本源神兽", "终极神兽"],
    ("合体", "elite"): ["宇宙创世主", "混沌至高神", "天道至圣", "宇宙至意", "本源至神"],
    ("合体", "boss"): ["宇宙至高神", "混沌创世主"],
    ("大乘", "common"): ["宇宙至高神", "混沌创世主", "天道至圣", "宇宙至意", "本源至神", "终极神王", "无限神帝", "永恒神皇", "绝对神尊", "至极神主"],
    ("大乘", "elite"): ["宇宙创世神王", "混沌至高神帝", "天道永恒神皇", "宇宙绝对神尊", "本源至极神主"],
    ("大乘", "boss"): ["宇宙创世神帝", "混沌至高神皇"],
}

def generate_monster(player_level: str) -> Monster:
    """
    根据玩家等级生成合适的怪物
    :param player_level: 玩家当前等级
    :return: 生成的怪物对象
    """
    # 确定怪物等级
    player_level_index = LEVEL_ORDER.index(player_level)
    
    # 确定怪物类型（普通、精英、BOSS）
    monster_type_roll = random.random()
    if monster_type_roll < 0.7:
        monster_type = "common"  # 70%概率生成普通怪物
    elif monster_type_roll < 0.9:
        monster_type = "elite"   # 20%概率生成精英怪物
    else:
        monster_type = "boss"    # 10%概率生成BOSS怪物
    
    # 确定怪物等级
    if monster_type == "boss":
        # BOSS可以超过玩家等级
        max_level_index = min(player_level_index + 2, len(LEVEL_ORDER) - 1)
        monster_level_index = random.randint(player_level_index, max_level_index)
    else:
        # 普通和精英怪物不强于玩家
        max_level_index = player_level_index
        # 有50%概率生成低一级的怪物
        if random.random() < 0.5 and player_level_index > 0:
            max_level_index = player_level_index - 1
        monster_level_index = random.randint(0, max_level_index)
    
    monster_level = LEVEL_ORDER[monster_level_index]
    
    # 获取怪物配置
    config = MONSTER_CONFIG[monster_level]
    
    # 生成怪物属性
    hp = random.randint(*config["hp_range"])
    attack = random.randint(*config["attack_range"])
    defense = random.randint(*config["defense_range"])
    exp_reward = config["exp_reward"]
    
    # 精英怪物和BOSS提供更高奖励
    if monster_type == "elite":
        exp_reward *= 2
        hp = int(hp * 1.5)
        attack = int(attack * 1.3)
        defense = int(defense * 1.2)
    elif monster_type == "boss":
        exp_reward *= 5
        hp = int(hp * 2)
        attack = int(attack * 1.5)
        defense = int(defense * 1.3)
    
    spirit_stones_reward = random.randint(*config["spirit_stones_reward"])
    
    # 生成怪物名称（简化名称，只包含类型和具体名称）
    monster_type_name = MONSTER_TYPES.get(monster_level, {}).get(monster_type, ["未知怪物"])[0]
    
    # 使用默认方式生成具体名称
    key = (monster_level, monster_type)
    if key in DEFAULT_MONSTER_NAMES and DEFAULT_MONSTER_NAMES[key]:
        specific_name = random.choice(DEFAULT_MONSTER_NAMES[key])
    else:
        # 如果找不到对应等级和类型的名称，返回默认名称
        base_names = ["凶兽", "精怪", "妖兽", "灵植", "地灵", "神兽", "天魔"]
        specific_name = random.choice(base_names)
    
    full_name = f"{monster_type_name}{specific_name}"
    
    # 创建怪物对象
    monster = Monster(
        name=full_name,
        level=monster_level,
        hp=hp,
        attack=attack,
        defense=defense,
        exp_reward=exp_reward,
        spirit_stones_reward=spirit_stones_reward
    )
    
    return monster
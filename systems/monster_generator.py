# astrbot_xiuxian_plugin/systems/monster_generator.py
import random
from ..config.cultivation_levels import LEVEL_ORDER

# 定义各等级段的野怪名称列表
MONSTER_NAMES_BY_LEVEL = {
    "1-19": [
        "影魅狸奴", "幽谷灵蛇", "雾隐狐仙", "青面獠牙怪", "赤血蝙蝠",
        "碧水精怪", "断魂草妖", "疾风狼妖", "玄冰蚕", "烈焰鼠"
    ],
    "20-49": [
        "青龙啸天", "白虎破晓", "朱雀焚翼", "玄武镇岳", "麒麟怒啸",
        "凤凰踏云", "蛟龙潜渊", "金乌耀日", "玄豹追风", "灵龟驮山"
    ],
    "50-100": [
        "伏羲天帝", "女娲圣母", "昊天玉皇", "神农炎帝", "轩辕黄帝",
        "东皇太一", "紫薇大帝", "后土娘娘", "帝俊天帝", "勾陈上宫天皇大帝"
    ],
    "100+": [
        "混沌始元尊", "乾坤造物主", "宇宙创生神", "鸿蒙开辟神", "太极衍化尊",
        "虚空造化主", "万象归一神", "时空主宰者", "元炁生成君", "无极混元帝"
    ]
}

def get_monster_level_range(player_level: str) -> str:
    """
    根据玩家境界确定怪物等级范围
    """
    # 定义境界到等级范围的映射
    level_mapping = {
        "凡人": "1-19",
        "筑基初期": "1-19",
        "筑基中期": "1-19",
        "筑基大圆满": "1-19",
        "金丹初期": "20-49",
        "金丹中期": "20-49",
        "金丹大圆满": "20-49",
        "元婴初期": "20-49",
        "元婴中期": "20-49",
        "元婴大圆满": "20-49",
        "出窍初期": "50-100",
        "出窍中期": "50-100",
        "出窍大圆满": "50-100",
        "分神初期": "50-100",
        "分神中期": "50-100",
        "分神大圆满": "50-100",
        "合体初期": "50-100",
        "合体中期": "50-100",
        "合体大圆满": "100+",
        "大乘初期": "100+",
        "大乘中期": "100+",
        "大乘大圆满": "100+",
        "渡劫初期": "100+",
        "渡劫中期": "100+",
        "渡劫大圆满": "100+",
        "地仙初期": "100+",
        "地仙中期": "100+",
        "地仙大圆满": "100+",
        "天仙初期": "100+",
        "天仙中期": "100+",
        "天仙大圆满": "100+",
        "大罗金仙初期": "100+",
        "大罗金仙中期": "100+",
        "大罗金仙大圆满": "100+",
        "九天玄仙初期": "100+",
        "九天玄仙中期": "100+",
        "九天玄仙大圆满": "100+",
        "九天玄仙之上": "100+"
    }
    
    return level_mapping.get(player_level, "1-19")

class Monster:
    def __init__(self, name, level, hp, attack, defense, spirit_stones_drop, exp_drop):
        self.name = name
        self.level = level
        self.hp = hp
        self.attack = attack
        self.defense = defense
        self.spirit_stones_drop = spirit_stones_drop
        self.exp_drop = exp_drop

def generate_monster(player_level: str) -> Monster:
    """
    根据玩家等级生成一个动态属性的怪物，按照规划实现。
    """
    # 获取怪物等级范围
    monster_level_range = get_monster_level_range(player_level)
    
    # 从对应等级范围中随机选择一个怪物名称
    monster_names = MONSTER_NAMES_BY_LEVEL[monster_level_range]
    monster_name = random.choice(monster_names)
    
    # 根据等级范围确定怪物等级数值
    if monster_level_range == "1-19":
        monster_level_num = random.randint(1, 19)
    elif monster_level_range == "20-49":
        monster_level_num = random.randint(20, 49)
    elif monster_level_range == "50-100":
        monster_level_num = random.randint(50, 100)
    else:  # 100+
        # 100级以上怪物等级可以略高于玩家境界对应的等级
        base_level = 100
        monster_level_num = base_level + random.randint(0, 50)
    
    # 根据规划中的公式计算怪物属性
    # 攻击(50-150)*lv、气血(100-500)*lv
    hp = random.randint(100, 500) * monster_level_num
    attack = random.randint(50, 150) * monster_level_num
    defense = random.randint(20, 80) * monster_level_num  # 防御力公式未在规划中明确，这里自定义
    
    # 掉落奖励也根据等级计算
    spirit_stones_drop = random.randint(1, 10) * monster_level_num
    exp_drop = random.randint(5, 20) * monster_level_num
    
    # 生成怪物等级描述
    monster_level_desc = f"{monster_level_num}级"
    
    return Monster(monster_name, monster_level_desc, hp, attack, defense, spirit_stones_drop, exp_drop)
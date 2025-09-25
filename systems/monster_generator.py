# astrbot_xiuxian_plugin/systems/monster_generator.py
import random
from ..config.cultivation_levels import LEVEL_ORDER

# 定义各等级怪物的属性基准
# hp, attack, defense, spirit_stones_drop, exp_drop
MONSTER_STATS_BY_LEVEL = {
    "凡人": (50, 8, 3, (1, 5), (10, 20)),
    "炼气": (200, 20, 10, (5, 15), (50, 100)),
    "筑基": (800, 50, 30, (20, 50), (200, 400)),
    "金丹": (3000, 150, 100, (80, 200), (1000, 2000)),
    "元婴": (15000, 500, 350, (300, 800), (5000, 10000)),
    "化神": (50000, 1500, 1000, (1000, 2500), (20000, 40000)),
    # 更高等级的怪物可以后续添加
}

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
    根据玩家等级生成一个动态属性的怪物。
    """
    level_index = LEVEL_ORDER.index(player_level)
    
    # 为了挑战性，怪物等级可能比玩家高一级或同级
    monster_level_index = min(level_index + random.randint(0, 1), len(LEVEL_ORDER) - 2) # -2 避免渡境和仙人
    monster_level = LEVEL_ORDER[monster_level_index]
    
    base_stats = MONSTER_STATS_BY_LEVEL.get(monster_level, MONSTER_STATS_BY_LEVEL["凡人"])
    
    # 在基准属性上随机浮动 ±20%
    hp = int(base_stats[0] * random.uniform(0.8, 1.2))
    attack = int(base_stats[1] * random.uniform(0.8, 1.2))
    defense = int(base_stats[2] * random.uniform(0.8, 1.2))
    
    stones_min, stones_max = base_stats[3]
    exp_min, exp_max = base_stats[4]
    
    spirit_stones_drop = random.randint(stones_min, stones_max)
    exp_drop = random.randint(exp_min, exp_max)
    
    # 怪物名称暂时硬编码，后续将由 LLM 生成
    monster_name = f"{monster_level}期妖兽"
    
    return Monster(monster_name, monster_level, hp, attack, defense, spirit_stones_drop, exp_drop)

# LLM 生成名称的函数占位
async def generate_monster_name_with_llm(provider) -> str:
    """
    使用 LLM 生成一个符合地域特色的怪物名称。
    """
    if not provider:
        return "未知妖兽"
        
    prompt = "请为一款修仙游戏生成一个独特的怪物名称。这个怪物生活在'东域'的'青木仙宗'附近，具有木系或山林相关的特征。请只返回怪物名称，不要任何多余的解释。"
    
    try:
        llm_resp = await provider.text_chat(prompt=prompt, system_prompt="你是一个富有创意的游戏文案设计师。")
        if llm_resp and llm_resp.content:
            # 清理可能的额外文本，例如引号
            return llm_resp.content.strip().replace('"', '').replace('“', '').replace('”', '')
    except Exception as e:
        # 日志记录错误
        print(f"LLM call failed: {e}")

    return "变异的树妖" # 作为备用名称

# astrbot_xiuxian_plugin/systems/item_generator.py
import random
from ..config.cultivation_levels import LEVEL_ORDER

class Item:
    def __init__(self, name, item_type, description=""):
        self.name = name
        self.item_type = item_type
        self.description = description

class Weapon(Item):
    def __init__(self, name, level, attack_boost, defense_boost=0):
        super().__init__(name, "weapon")
        self.level = level
        self.attack_boost = attack_boost
        self.defense_boost = defense_boost

class Skill(Item):
    def __init__(self, name, level, effect):
        super().__init__(name, "skill")
        self.level = level
        self.effect = effect

# --- Base Stat Definitions ---
WEAPON_STATS_BY_LEVEL = {
    "凡人": {"attack": (1, 5)},
    "炼气": {"attack": (5, 15)},
    "筑基": {"attack": (15, 40)},
    "金丹": {"attack": (40, 100)},
    "元婴": {"attack": (100, 250)},
}

async def analyze_name_epicness(provider, name: str) -> float:
    """
    使用 LLM 分析名称的“霸气”程度，返回一个 0.0 到 1.0 的浮点数。
    """
    if not provider:
        return 0.5 # Default epicness if no provider is available

    prompt = f"请评估修仙物品名称 '{name}' 的霸气程度。请只返回一个0.0到1.0之间的小数，0.0代表毫无气势，1.0代表霸气绝伦。不要任何多余的解释。"
    try:
        llm_resp = await provider.text_chat(prompt=prompt, system_prompt="你是一个精通修仙文学的评论家。")
        if llm_resp and llm_resp.content:
            return float(llm_resp.content.strip())
    except (ValueError, TypeError) as e:
        print(f"LLM epicness analysis failed: {e}")
        return 0.5

async def generate_weapon(provider, player_level: str) -> Weapon:
    """
    生成一把武器，其属性受 LLM 生成的名称影响。
    """
    level_index = LEVEL_ORDER.index(player_level)
    item_level = LEVEL_ORDER[min(level_index, len(WEAPON_STATS_BY_LEVEL) - 1)]
    
    # 1. Generate Name with LLM
    name_prompt = f"为一款修仙游戏生成一个独特的、等级为'{item_level}'的武器名称。请只返回武器名称，不要任何多余的解释。"
    weapon_name = "凡铁剑" # Default name
    if provider:
        try:
            llm_resp = await provider.text_chat(prompt=name_prompt, system_prompt="你是一个富有创意的游戏文案设计师。")
            if llm_resp and llm_resp.content:
                weapon_name = llm_resp.content.strip().replace('"', '')
        except Exception as e:
            print(f"LLM weapon name generation failed: {e}")

    # 2. Analyze Name Epicness
    epicness = await analyze_name_epicness(provider, weapon_name) # 0.0 to 1.0

    # 3. Generate Stats
    base_stats = WEAPON_STATS_BY_LEVEL[item_level]
    base_attack_min, base_attack_max = base_stats["attack"]
    
    # Epicness boosts stats. A super epic name can result in a weapon far above its level.
    # A multiplier of up to 3x for max epicness.
    stat_multiplier = 1 + (epicness * 2) 
    
    attack_boost = int(random.randint(base_attack_min, base_attack_max) * stat_multiplier)
    
    # 10% chance for a super-roll, exceeding current level stats
    if random.random() < 0.10:
        next_level_index = min(level_index + 1, len(WEAPON_STATS_BY_LEVEL) - 1)
        next_level = LEVEL_ORDER[next_level_index]
        next_level_stats = WEAPON_STATS_BY_LEVEL[next_level]
        attack_boost += random.randint(next_level_stats["attack"][0], next_level_stats["attack"][1])

    return Weapon(weapon_name, item_level, attack_boost)

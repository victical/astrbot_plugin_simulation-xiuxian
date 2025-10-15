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


async def generate_weapon(provider, player_level: str) -> Weapon:
    """
    生成一把武器。
    """
    level_index = LEVEL_ORDER.index(player_level)
    item_level = LEVEL_ORDER[min(level_index, len(WEAPON_STATS_BY_LEVEL) - 1)]
    
    # 1. Generate Name
    weapon_name = f"{item_level}凡铁剑" # Default name
    
    # 2. Generate Stats
    base_stats = WEAPON_STATS_BY_LEVEL[item_level]
    base_attack_min, base_attack_max = base_stats["attack"]
    
    attack_boost = int(random.randint(base_attack_min, base_attack_max))
    
    # 10% chance for a super-roll, exceeding current level stats
    if random.random() < 0.10:
        next_level_index = min(level_index + 1, len(WEAPON_STATS_BY_LEVEL) - 1)
        next_level = LEVEL_ORDER[next_level_index]
        next_level_stats = WEAPON_STATS_BY_LEVEL[next_level]
        attack_boost += random.randint(next_level_stats["attack"][0], next_level_stats["attack"][1])

    return Weapon(weapon_name, item_level, attack_boost)

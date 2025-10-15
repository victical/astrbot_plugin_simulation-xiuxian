# astrbot_xiuxian_plugin/models/monster.py
"""怪物模型"""

class Monster:
    """怪物类"""
    
    def __init__(self, name: str, level: str, hp: int, attack: int, defense: int, 
                 exp_reward: int, spirit_stones_reward: int,
                 attack_bonus: int = 0, defense_bonus: int = 0,
                 skills: list = None, drop_items: list = None):
        """
        初始化怪物对象
        :param name: 怪物名称
        :param level: 怪物等级
        :param hp: 怪物气血值
        :param attack: 怪物攻击力
        :param defense: 怪物防御力
        :param exp_reward: 击败怪物获得的经验值奖励
        :param spirit_stones_reward: 击败怪物获得的灵石奖励
        :param attack_bonus: 怪物攻击力加成
        :param defense_bonus: 怪物防御力加成
        :param skills: 怪物拥有的技能列表
        :param drop_items: 击败怪物后可能掉落的物品列表
        """
        self.name = name
        self.level = level
        self.hp = hp
        self.attack = attack
        self.defense = defense
        self.exp_reward = exp_reward
        self.spirit_stones_reward = spirit_stones_reward
        self.attack_bonus = attack_bonus
        self.defense_bonus = defense_bonus
        self.skills = skills or []
        self.drop_items = drop_items or []
    
    def __str__(self):
        return f"Monster(name={self.name}, level={self.level}, hp={self.hp}, attack={self.attack}, defense={self.defense}, exp_reward={self.exp_reward}, spirit_stones_reward={self.spirit_stones_reward})"
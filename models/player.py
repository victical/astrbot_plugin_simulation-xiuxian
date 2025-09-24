# astrbot_xiuxian_plugin/models/player.py

import json

class Player:
    def __init__(self, user_id, user_name, level, experience, spirit_stones, 
                 hp, mp, attack, defense, sect, sect_rank, contribution, 
                 inventory=None, learned_skills=None,current_mission=None, created_at=None, updated_at=None):
        self.user_id = user_id
        self.user_name = user_name
        self.level = level
        self.experience = experience
        self.spirit_stones = spirit_stones
        self.hp = hp
        self.mp = mp
        self.attack = attack
        self.defense = defense
        self.sect = sect
        self.sect_rank = sect_rank
        self.contribution = contribution
        
        # 背包和技能使用 JSON 字符串存储，在这里解析为 Python 对象
        self.inventory = json.loads(inventory) if inventory else {}
        self.learned_skills = json.loads(learned_skills) if learned_skills else []
        self.current_mission = json.loads(current_mission) if current_mission and current_mission != 'null' else None

        self.created_at = created_at
        self.updated_at = updated_at

    def to_dict(self):
        """将玩家对象转换为字典，方便数据库更新"""
        return {
            "user_id": self.user_id,
            "user_name": self.user_name,
            "level": self.level,
            "experience": self.experience,
            "spirit_stones": self.spirit_stones,
            "hp": self.hp,
            "mp": self.mp,
            "attack": self.attack,
            "defense": self.defense,
            "sect": self.sect,
            "sect_rank": self.sect_rank,
            "contribution": self.contribution,
            "inventory": json.dumps(self.inventory, ensure_ascii=False),
            "learned_skills": json.dumps(self.learned_skills, ensure_ascii=False),
            "current_mission": json.dumps(self.current_mission, ensure_ascii=False) if self.current_mission else None
        }

    def __repr__(self):
        return (f"<Player(user_id='{self.user_id}', user_name='{self.user_name}', "
                f"level='{self.level}', exp={self.experience})>")
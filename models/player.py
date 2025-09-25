# astrbot_xiuxian_plugin/models/player.py

import json

class Player:
    def __init__(self, user_id, user_name, level, experience, spirit_stones, 
                 hp, spirit_power, max_spirit_power, attack, defense, meditation_start_time,
                 sect, sect_rank, contribution, 
                 inventory=None, skills=None, equipment=None, current_mission=None, 
                 created_at=None, updated_at=None):
        self.user_id = user_id
        self.user_name = user_name
        self.level = level
        self.experience = experience
        self.spirit_stones = spirit_stones
        self.hp = hp
        self.spirit_power = spirit_power
        self.max_spirit_power = max_spirit_power
        self.attack = attack
        self.defense = defense
        self.meditation_start_time = meditation_start_time
        self.sect = sect
        self.sect_rank = sect_rank
        self.contribution = contribution
        
        self.inventory = json.loads(inventory) if inventory else {}
        self.skills = json.loads(skills) if skills else []
        self.equipment = json.loads(equipment) if equipment else {}
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
            "spirit_power": self.spirit_power,
            "max_spirit_power": self.max_spirit_power,
            "attack": self.attack,
            "defense": self.defense,
            "meditation_start_time": self.meditation_start_time,
            "sect": self.sect,
            "sect_rank": self.sect_rank,
            "contribution": self.contribution,
            "inventory": json.dumps(self.inventory, ensure_ascii=False),
            "skills": json.dumps(self.skills, ensure_ascii=False),
            "equipment": json.dumps(self.equipment, ensure_ascii=False),
            "current_mission": json.dumps(self.current_mission, ensure_ascii=False) if self.current_mission else None
        }

    def __repr__(self):
        return (f"<Player(user_id='{self.user_id}', user_name='{self.user_name}', "
                f"level='{self.level}', exp={self.experience})>")

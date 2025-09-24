# astrbot_xiuxian_plugin/config/monsters_data.py

MONSTERS = {
    "嗜血野狼": {
        "level": "炼气",
        "hp": 50,
        "attack": 12,
        "defense": 5,
        "rewards": {
            "experience": 25,
            "spirit_stones": 10,
            "items": [{"name": "狼皮", "quantity": 1, "chance": 0.5}] # 50% 概率掉落
        }
    },
    "妖化巨蟒": {
        "level": "炼气",
        "hp": 80,
        "attack": 15,
        "defense": 8,
        "rewards": {
            "experience": 40,
            "spirit_stones": 20,
            "items": [{"name": "蛇胆", "quantity": 1, "chance": 0.3}] # 30% 概率掉落
        }
    },
    "黑风熊": {
        "level": "筑基",
        "hp": 150,
        "attack": 25,
        "defense": 15,
        "rewards": {
            "experience": 100,
            "spirit_stones": 50,
            "items": [{"name": "熊掌", "quantity": 1, "chance": 0.6}, {"name": "妖兽内丹", "quantity": 1, "chance": 0.1}]
        }
    }
}

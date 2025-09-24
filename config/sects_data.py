# astrbot_xiuxian_plugin/config/sects_data.py

# 门派静态数据
# 这里的数据是 "模板"，玩家学习或获得后会成为他们自己的动态数据
SECTS_DATA = {
    "青木仙宗": {
        "description": "东域大派，以木系功法和疗伤丹药闻名于世，门中弟子多心怀仁善。",
        "region": "东域",
        "specialty": ["木系", "治疗", "辅助"],
        "ranks": ["外门弟子", "内门弟子", "真传弟子", "长老", "护法"],
        "missions": [
            {
                "id": "qmxz_001",
                "name": "巡逻山门",
                "description": "巡视宗门山门，防范宵小之辈。",
                "rewards": {"contribution": 5, "experience": 20, "spirit_stones": 10}
            },
            {
                "id": "qmxz_002",
                "name": "采集草药",
                "description": "前往后山药圃，采集成熟的灵草。",
                "rewards": {"contribution": 7, "experience": 30, "spirit_stones": 15}
            },
            {
                "id": "qmxz_003",
                "name": "照料灵田",
                "description": "为宗门的灵田施展小回春术，促进灵谷生长。",
                "rewards": {"contribution": 6, "experience": 25, "spirit_stones": 12}
            }
        ],
        "exchange_shop": {
            "外门弟子": [ # 商品按职位等级划分
                {"name": "养气丹", "type": "丹药", "description": "补充灵气，加速炼气期修为增长。", "cost": 10},
                {"name": "小还丹", "type": "丹药", "description": "疗伤圣药，可迅速恢复低阶修士的伤势。", "cost": 15},
                {"name": "护心玉佩", "type": "法器", "description": "可抵挡一次致命攻击。", "cost": 50}
            ],
            "内门弟子": [
                {"name": "筑基丹", "type": "丹药", "description": "辅助筑基期修士稳固道基。", "cost": 200},
                # 未来可以添加更多内门弟子可兑换的物品
            ]
        },
        "skills": {
            "凡人/炼气期": [
                {"name": "青木引气诀", "type": "心法", "description": "青木仙宗的基础吐纳法门，提升灵气吸收效率。"},
                {"name": "小回春术", "type": "法术", "description": "初阶治疗法术，可恢复少量气血。"}
            ],
            "筑基/金丹期": [
                {"name": "万木生发功", "type": "心法", "description": "中阶木系功法，提升生命恢复速度和木系法术威力。"},
                {"name": "藤蔓缠绕术", "type": "法术", "description": "释放坚韧藤蔓束缚敌人。"}
            ]
            # ... 更多等级的功法
        },
        "elixirs": {
            "凡人/炼气期": [
                {"name": "养气丹", "description": "补充灵气，加速炼气期修为增长。"},
                {"name": "小还丹", "description": "疗伤圣药，可迅速恢复低阶修士的伤势。"}
            ]
            # ... 更多等级的丹药
        },
        "artifacts": {
            "凡人/炼气期": [
                {"name": "护心玉佩", "type": "防御法器", "description": "可抵挡一次致命攻击。"},
                {"name": "灵草锄", "type": "辅助法器", "description": "提升采集灵草的成功率。"}
            ]
            # ... 更多等级的法宝
        }
    },
    # 未来可以添加更多门派，如焚天谷, 金刚寺等
    # "焚天谷": { ... }
}
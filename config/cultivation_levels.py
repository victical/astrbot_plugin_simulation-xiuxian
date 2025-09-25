# astrbot_xiuxian_plugin/config/cultivation_levels.py

# 定义修仙等级的属性，包括晋升所需经验和灵力上限
# required_exp: 晋升到下一等级所需的总经验
# max_spirit_power: 该等级的灵力上限
CULTIVATION_LEVELS = {
    "凡人": {"required_exp": 100, "max_spirit_power": 100},
    "炼气": {"required_exp": 1000, "max_spirit_power": 500},
    "筑基": {"required_exp": 5000, "max_spirit_power": 2000},
    "金丹": {"required_exp": 20000, "max_spirit_power": 10000},
    "元婴": {"required_exp": 100000, "max_spirit_power": 50000},
    "化神": {"required_exp": 500000, "max_spirit_power": 200000},
    "炼虚": {"required_exp": 2000000, "max_spirit_power": 1000000},
    "合体": {"required_exp": 8000000, "max_spirit_power": 5000000},
    "大乘": {"required_exp": 25000000, "max_spirit_power": 20000000},
    "渡境": {"required_exp": 100000000, "max_spirit_power": 100000000},
    "仙人": {"required_exp": float('inf'), "max_spirit_power": 999999999}
}

# 等级顺序列表，用于查找下一等级
LEVEL_ORDER = list(CULTIVATION_LEVELS.keys())

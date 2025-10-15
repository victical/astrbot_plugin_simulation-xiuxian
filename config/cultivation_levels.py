# astrbot_xiuxian_plugin/config/cultivation_levels.py

# 定义修仙等级的属性，包括晋升所需经验和灵力上限
# required_exp: 晋升到下一等级所需的总经验
# max_spirit_power: 该等级的灵力上限
CULTIVATION_LEVELS = {
    "凡人": {"required_exp": 100, "max_spirit_power": 100},
    "筑基初期": {"required_exp": 200, "max_spirit_power": 200},
    "筑基中期": {"required_exp": 350, "max_spirit_power": 350},
    "筑基大圆满": {"required_exp": 500, "max_spirit_power": 500},
    "金丹初期": {"required_exp": 700, "max_spirit_power": 700},
    "金丹中期": {"required_exp": 900, "max_spirit_power": 900},
    "金丹大圆满": {"required_exp": 1200, "max_spirit_power": 1200},
    "元婴初期": {"required_exp": 1400, "max_spirit_power": 1400},
    "元婴中期": {"required_exp": 1800, "max_spirit_power": 1800},
    "元婴大圆满": {"required_exp": 2500, "max_spirit_power": 2500},
    "出窍初期": {"required_exp": 3000, "max_spirit_power": 3000},
    "出窍中期": {"required_exp": 4000, "max_spirit_power": 4000},
    "出窍大圆满": {"required_exp": 5000, "max_spirit_power": 5000},
    "分神初期": {"required_exp": 6500, "max_spirit_power": 6500},
    "分神中期": {"required_exp": 8000, "max_spirit_power": 8000},
    "分神大圆满": {"required_exp": 10000, "max_spirit_power": 10000},
    "合体初期": {"required_exp": 12500, "max_spirit_power": 12500},
    "合体中期": {"required_exp": 14000, "max_spirit_power": 14000},
    "合体大圆满": {"required_exp": 15500, "max_spirit_power": 15500},
    "大乘初期": {"required_exp": 18000, "max_spirit_power": 18000},
    "大乘中期": {"required_exp": 22000, "max_spirit_power": 22000},
    "大乘大圆满": {"required_exp": 25000, "max_spirit_power": 25000},
    "渡劫初期": {"required_exp": 28000, "max_spirit_power": 28000},
    "渡劫中期": {"required_exp": 30000, "max_spirit_power": 30000},
    "渡劫大圆满": {"required_exp": 35000, "max_spirit_power": 35000},
    "地仙初期": {"required_exp": 40000, "max_spirit_power": 40000},
    "地仙中期": {"required_exp": 50000, "max_spirit_power": 50000},
    "地仙大圆满": {"required_exp": 60000, "max_spirit_power": 60000},
    "天仙初期": {"required_exp": 70000, "max_spirit_power": 70000},
    "天仙中期": {"required_exp": 80000, "max_spirit_power": 80000},
    "天仙大圆满": {"required_exp": 100000, "max_spirit_power": 100000},
    "大罗金仙初期": {"required_exp": 110000, "max_spirit_power": 110000},
    "大罗金仙中期": {"required_exp": 120000, "max_spirit_power": 120000},
    "大罗金仙大圆满": {"required_exp": 130000, "max_spirit_power": 130000},
    "九天玄仙初期": {"required_exp": 150000, "max_spirit_power": 150000},
    "九天玄仙中期": {"required_exp": 170000, "max_spirit_power": 170000},
    "九天玄仙大圆满": {"required_exp": 200000, "max_spirit_power": 200000},
    "九天玄仙之上": {"required_exp": float('inf'), "max_spirit_power": 999999999}
}

# 等级顺序列表，用于查找下一等级
LEVEL_ORDER = list(CULTIVATION_LEVELS.keys())

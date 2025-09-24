# astrbot_xiuxian_plugin/config/cultivation_levels.py

# 定义修仙等级和晋升所需经验
# key 是当前等级，value 是晋升到下一等级所需的总经验
CULTIVATION_LEVELS = {
    "凡人": 100,
    "炼气": 1000,
    "筑基": 5000,
    "金丹": 20000,
    "元婴": 100000,
    "化神": 500000,
    "炼虚": 2000000,
    "合体": 8000000,
    "大乘": 25000000,
    "渡境": 100000000,
    "仙人": float('inf')  # 仙人等级后经验无限，代表已飞升
}

# 等级顺序列表，用于查找下一等级
LEVEL_ORDER = list(CULTIVATION_LEVELS.keys())
# astrbot_xiuxian_plugin/config/exploration_events.py
# 基础事件（所有玩家可触发）
COMMON_EVENTS = [
    {
        "desc": "你在山林中发现一株一阶灵草，小心采摘后收入囊中。",
        "reward": {"exp": 15, "item": "一阶灵草"}
    },
    {
        "desc": "你发现一只嗜血野狼正在袭击一个商队，你决定出手相助！",
        "type": "combat",
        "monster_name": "嗜血野狼"
    },
    {
        "desc": "路过一个凡人村庄，你出手解决了一只作乱的野兽，村民赠予你一些薄礼以示感谢。",
        "reward": {"stones": 20}
    },
    {
        "desc": "你在溪边打坐，顿悟了天地自然之道，心境修为有所提升。",
        "reward": {"exp": 50}
    },
    {
        "desc": "一阵浓雾袭来，你迷失了方向，耗费了不少灵力才走出来。",
        "penalty": {"mp": 10}
    }
]

# 门派弟子专属事件（对应README的门派区域探索）
SECT_EVENTS = [
    {
        "desc": "在门派后山巡逻时，发现一处隐藏的灵泉，吸收灵气后修为有所精进。",
        "reward": {"exp": 40, "mp": 5}
    },
    {
        "desc": "偶遇门派长老，得到指点后茅塞顿开。",
        "reward": {"exp": 60}
    }
]

# 散修专属事件（对应README的散修奇遇）
WILDERNESS_EVENTS = [
    {
        "desc": "误入一处秘境，获得少量修炼资源，但灵力消耗巨大。",
        "reward": {"stones": 10, "item": "神秘矿石"},
        "penalty": {"mp": 15}
    },
    {
        "desc": "你在一个无名山洞中发现了一位前辈修士的坐化之地，拜祭后获得其留下的部分传承。",
        "reward": {"exp": 100, "stones": 50}
    },
    {
        "desc": "你从一个狡猾的商人手中购得一张藏宝图的残片。",
        "reward": {"item": "藏宝图残片"}
    },
    {
        "desc": "你被卷入一场散修间的冲突，虽然成功脱身，但还是受了点伤。",
        "penalty": {"hp": 20}
    }
]

# 遗迹事件（高阶探索）
RUIN_EVENTS = [
    {
        "desc": "探索上古遗迹时，找到一枚残缺玉简，从中领悟到些许道法。",
        "reward": {"exp": 80, "item": "上古玉简"}
    },
    {
        "desc": "你在遗迹深处发现一个古老的炼丹炉，旁边还散落着几枚丹药。",
        "reward": {"item": "淬体丹"}
    },
    {
        "desc": "触动了遗迹中的上古禁制，你被困其中，耗费九牛二虎之力才得以脱身。",
        "reward": {"exp": 120},
        "penalty": {"hp": 25, "mp": 20}
    },
    {
        "desc": "在一具骸骨旁，你找到了一柄布满尘土的法器。",
        "reward": {"item": "下品法器"}
    }
]

# 高阶事件（金丹期及以上）
HIGH_LEVEL_EVENTS = [
    {
        "desc": "一头狂暴的黑风熊挡住了你的去路！",
        "type": "combat",
        "monster_name": "黑风熊"
    }
]

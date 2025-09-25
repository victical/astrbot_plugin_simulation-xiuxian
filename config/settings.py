# astrbot_xiuxian_plugin/config/settings.py

import os

# 插件根目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 数据库文件路径
# 我们将数据库文件放在插件根目录下的 data 文件夹中
DATA_DIR = os.path.join(BASE_DIR, 'data')
DATABASE_FILE = os.path.join(DATA_DIR, 'xiuxian_data.db')

# 确保 data 文件夹存在
os.makedirs(DATA_DIR, exist_ok=True)

from . import cultivation_levels

# 初始玩家属性
INITIAL_PLAYER_STATS = {
    'level': '凡人',
    'experience': 0,
    'spirit_stones': 10,
    'hp': 100,
    'spirit_power': 50,
    'max_spirit_power': cultivation_levels.CULTIVATION_LEVELS['凡人']['max_spirit_power'],
    'attack': 10,
    'defense': 5,
    'sect': None,
    'sect_rank': None,
    'contribution': 0
}

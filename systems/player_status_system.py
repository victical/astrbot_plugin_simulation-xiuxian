# astrbot_xiuxian_plugin/systems/player_status_system.py

from ..database.repositories import player_repository
from ..config import cultivation_levels

def get_player_status(user_id: str) -> str:
    """
    获取并格式化玩家的状态信息。

    - 从数据库查询玩家数据。
    - 如果玩家存在，则格式化为一个美观的字符串。
    - 如果玩家不存在，则提示他们开始游戏。

    :param user_id: 用户的唯一ID
    :return: 格式化后的状态信息字符串
    """
    # 1. 从数据库获取玩家对象
    player = player_repository.get_player_by_id(user_id)

    # 2. 检查玩家是否存在
    if not player:
        return "道友，你尚未踏入仙途。请输入 `!开始修仙` 开启你的旅程。"

    # 3. 如果存在，格式化输出信息
    # 获取晋升到下一级所需经验
    next_level_exp = cultivation_levels.CULTIVATION_LEVELS.get(player.level, '已达巅峰')

    status_message = (
        f"═══【道友 {player.user_name} 的状态】═══\n"
        f"境界: {player.level}\n"
        f"修为: {player.experience} / {next_level_exp}\n"
        f"灵石: {player.spirit_stones} 颗\n"
        f"═══ 属性 ═══\n"
        f"气血: {player.hp}\n"
        f"灵力: {player.mp}\n"
        f"攻击: {player.attack}\n"
        f"防御: {player.defense}\n"
        f"═══ 身份 ═══\n"
        f"门派: {player.sect or '无'}\n"
        f"职位: {player.sect_rank or '无'}\n"
        f"贡献: {player.contribution}\n"
        f"══════════════════"
    )

    return status_message
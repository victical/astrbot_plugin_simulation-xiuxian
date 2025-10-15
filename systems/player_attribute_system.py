# astrbot_xiuxian_plugin/systems/player_attribute_system.py

import random
from ..database.repositories import player_repository
from ..models.player import Player
from ..config import cultivation_levels

async def allocate_attribute_points(user_id: str, attribute: str, points: int) -> str:
    """
    为玩家分配属性点。
    """
    player = await player_repository.get_player_by_id(user_id)
    if not player:
        return "道友，你尚未踏入仙途。请输入 `开始修仙` 开启你的旅程。"

    if player.attribute_points < points:
        return f"你的属性点不足，当前剩余 {player.attribute_points} 点。"

    if points <= 0:
        return "分配的点数必须大于 0。"

    attribute_mapping = {
        "气血": "hp",
        "攻击": "attack",
        "防御": "defense"
    }

    if attribute not in attribute_mapping:
        return "无效的属性名称。可用属性：气血、攻击、防御。"

    try:
        fenshen_index = cultivation_levels.LEVEL_ORDER.index("分神初期")
        current_index = cultivation_levels.LEVEL_ORDER.index(player.level)
    except ValueError:
        # 如果等级不在列表中，默认使用较低的增益
        fenshen_index = 999
        current_index = 0

    if current_index >= fenshen_index:
        min_gain = 100
        max_gain = 200
    else:
        min_gain = 50
        max_gain = 100
        
    total_gain = 0
    for _ in range(points):
        total_gain += random.randint(min_gain, max_gain)

    attr_name = attribute_mapping[attribute]
    current_value = getattr(player, attr_name)
    setattr(player, attr_name, current_value + total_gain)
    
    player.attribute_points -= points
    await player_repository.update_player(player)

    return f"成功将 {points} 点属性点分配到 {attribute}，{attribute} 增加了 {total_gain}。"

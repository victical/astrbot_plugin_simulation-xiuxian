# astrbot_xiuxian_plugin/systems/inventory_system.py

from ..database.repositories import player_repository

def display_inventory(user_id: str) -> str:
    """
    显示玩家的背包物品。
    :param user_id: 玩家的唯一ID。
    :return: 格式化后的背包列表字符串。
    """
    player = player_repository.get_player_by_id(user_id)

    if not player:
        return "道友，你尚未踏入仙途。"

    if not player.inventory:
        return "你的背包空空如也，宛如你的钱包。"

    message_parts = ["═══【我的背包】═══"]
    for item_name, item_info in player.inventory.items():
        quantity = item_info.get('quantity', 0)
        item_type = item_info.get('type', '未知')
        message_parts.append(f"【{item_name}】x {quantity} ({item_type})")
    
    message_parts.append("══════════════")
    return "\n".join(message_parts)
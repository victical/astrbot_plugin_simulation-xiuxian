# astrbot_xiuxian_plugin/systems/elixir_system.py
"""丹药系统，处理丹药的使用效果"""

import random
from ..database.repositories import player_repository
from ..database.db_manager import fetch_query, execute_query

def use_elixir(user_id: str, elixir_name: str) -> str:
    """
    使用丹药
    :param user_id: 玩家ID
    :param elixir_name: 丹药名称
    :return: 使用结果消息
    """
    player = player_repository.get_player_by_id(user_id)
    if not player:
        return "道友，你尚未踏入仙途。"
    
    # 检查玩家是否拥有该丹药（先检查传统背包系统）
    if player.inventory and elixir_name in player.inventory:
        # 使用传统背包中的丹药
        return _use_traditional_elixir(player, elixir_name)
    
    # 检查新物品系统中的丹药
    item = _get_player_item(user_id, elixir_name)
    if not item:
        return f"你身上没有【{elixir_name}】这味丹药。"
    
    if item["type"] != "elixir":
        return f"【{elixir_name}】不是丹药，无法服用。"
    
    # 使用新物品系统中的丹药
    return _use_new_elixir(player, item)

def _use_traditional_elixir(player, elixir_name: str) -> str:
    """
    使用传统背包系统中的丹药
    """
    # 获取丹药数量
    elixir_info = player.inventory[elixir_name]
    quantity = elixir_info.get("quantity", 0)
    
    if quantity <= 0:
        return f"你身上没有【{elixir_name}】这味丹药。"
    
    # 根据丹药名称确定效果
    exp_bonus = 0
    spirit_power_restore = 0
    
    if elixir_name == "养气丹":
        exp_bonus = random.randint(50, 200)
        spirit_power_restore = random.randint(20, 100)
    elif elixir_name == "小还丹":
        exp_bonus = random.randint(100, 300)
        spirit_power_restore = random.randint(50, 150)
    elif elixir_name == "筑基丹":
        exp_bonus = random.randint(300, 1000)
        spirit_power_restore = random.randint(100, 500)
    else:
        # 默认效果
        exp_bonus = random.randint(50, 200)
        spirit_power_restore = random.randint(20, 100)
    
    # 应用效果
    player.experience += exp_bonus
    player.spirit_power = min(player.spirit_power + spirit_power_restore, player.max_spirit_power)
    
    # 消耗丹药
    player.inventory[elixir_name]["quantity"] -= 1
    if player.inventory[elixir_name]["quantity"] <= 0:
        del player.inventory[elixir_name]
    
    # 保存玩家数据
    player_repository.update_player(player)
    
    # 5%概率触发特殊效果
    special_effect = ""
    if random.random() < 0.05:
        special_exp_bonus = exp_bonus * 2
        player.experience += special_exp_bonus
        player_repository.update_player(player)
        special_effect = f"\n【惊喜】丹药效果翻倍，额外获得 {special_exp_bonus} 修为！"
    
    return f"你服用了【{elixir_name}】，获得了 {exp_bonus} 修为和 {spirit_power_restore} 灵力恢复。{special_effect}"

def _get_player_item(user_id: str, item_name: str) -> dict:
    """
    获取玩家拥有的特定物品信息（新物品系统）
    """
    sql = """
    SELECT i.id, i.name, i.type, i.level_requirement, i.description, i.attributes, pi.quantity
    FROM player_items pi
    JOIN items i ON pi.item_id = i.id
    WHERE pi.player_id = ? AND i.name = ?
    """
    result = fetch_query(sql, (user_id, item_name), one=True)
    
    if result:
        import json
        return {
            "id": result[0],
            "name": result[1],
            "type": result[2],
            "level_requirement": result[3],
            "description": result[4],
            "attributes": json.loads(result[5]) if result[5] else {},
            "quantity": result[6]
        }
    
    return None

def _use_new_elixir(player, item: dict) -> str:
    """
    使用新物品系统中的丹药
    """
    # 获取丹药属性
    attributes = item.get("attributes", {})
    exp_bonus = attributes.get("exp_bonus", random.randint(50, 200))
    spirit_power_restore = attributes.get("spirit_power_restore", random.randint(20, 100))
    
    # 如果属性是范围值，则随机取值
    if isinstance(exp_bonus, list):
        exp_bonus = random.randint(exp_bonus[0], exp_bonus[1])
    
    if isinstance(spirit_power_restore, list):
        spirit_power_restore = random.randint(spirit_power_restore[0], spirit_power_restore[1])
    
    # 应用效果
    player.experience += exp_bonus
    player.spirit_power = min(player.spirit_power + spirit_power_restore, player.max_spirit_power)
    
    # 消耗丹药
    _consume_item(player.user_id, item["id"], 1)
    
    # 保存玩家数据
    player_repository.update_player(player)
    
    # 5%概率触发特殊效果
    special_effect = ""
    if random.random() < 0.05:
        special_exp_bonus = exp_bonus * 2
        player.experience += special_exp_bonus
        player_repository.update_player(player)
        special_effect = f"\n【惊喜】丹药效果翻倍，额外获得 {special_exp_bonus} 修为！"
    
    return f"你服用了【{item['name']}】，获得了 {exp_bonus} 修为和 {spirit_power_restore} 灵力恢复。{special_effect}"

def _consume_item(user_id: str, item_id: int, quantity: int):
    """
    消耗玩家的物品（新物品系统）
    """
    # 检查玩家物品数量
    sql = "SELECT id, quantity FROM player_items WHERE player_id = ? AND item_id = ?"
    result = fetch_query(sql, (user_id, item_id), one=True)
    
    if not result:
        return
    
    player_item_id, current_quantity = result
    
    if current_quantity <= quantity:
        # 删除记录
        delete_sql = "DELETE FROM player_items WHERE id = ?"
        execute_query(delete_sql, (player_item_id,))
    else:
        # 减少数量
        update_sql = "UPDATE player_items SET quantity = quantity - ? WHERE id = ?"
        execute_query(update_sql, (quantity, player_item_id))
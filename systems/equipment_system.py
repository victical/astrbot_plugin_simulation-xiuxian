# astrbot_xiuxian_plugin/systems/equipment_system.py
"""装备系统，处理武器和法宝的装备效果"""

from ..database.db_manager import fetch_query, execute_query
from ..database.repositories import player_repository
import json

def equip_item(user_id: str, item_name: str) -> str:
    """
    装备物品（武器或法宝）
    """
    player = player_repository.get_player_by_id(user_id)
    if not player:
        return "道友，你尚未踏入仙途。"
    
    # 检查玩家是否拥有该物品
    item = _get_player_item(user_id, item_name)
    if not item:
        return f"你身上没有【{item_name}】这件物品。"
    
    item_type = item["type"]
    if item_type not in ["weapon", "artifact"]:
        return f"【{item_name}】不是可装备的物品。"
    
    # 检查修仙等级是否满足要求
    from ..config.cultivation_levels import LEVEL_ORDER
    player_level_index = LEVEL_ORDER.index(player.level)
    item_level_requirement = item.get("level_requirement", "凡人")
    item_level_index = LEVEL_ORDER.index(item_level_requirement)
    
    if player_level_index < item_level_index:
        return f"你的境界【{player.level}】不足以使用【{item_name}】({item_level_requirement})。"
    
    # 卸下当前同类型装备（如果有的话）
    unequipped_items = []
    current_equipment = player.equipment if player.equipment else {}
    if item_type in current_equipment:
        unequipped_items.append(current_equipment[item_type])
    
    # 装备新物品
    current_equipment[item_type] = item_name
    player.equipment = current_equipment
    
    # 应用属性加成
    attributes = item.get("attributes", {})
    _apply_attributes(player, attributes)
    
    # 如果有卸下的装备，移除其属性加成
    for unequipped_item_name in unequipped_items:
        unequipped_item = _get_player_item(user_id, unequipped_item_name)
        if unequipped_item:
            unequipped_attributes = unequipped_item.get("attributes", {})
            _remove_attributes(player, unequipped_attributes)
    
    # 保存玩家数据
    player_repository.update_player(player)
    
    # 生成返回消息
    message_parts = [f"你装备了【{item_name}】"]
    if unequipped_items:
        message_parts.append(f"并卸下了【{', '.join(unequipped_items)}】")
    
    attr_desc = ", ".join([f"{k}+{v}" for k, v in attributes.items()])
    if attr_desc:
        message_parts.append(f"\n获得属性加成: {attr_desc}")
    
    return "\n".join(message_parts)

def unequip_item(user_id: str, item_name: str) -> str:
    """
    卸下装备
    """
    player = player_repository.get_player_by_id(user_id)
    if not player:
        return "道友，你尚未踏入仙途。"
    
    current_equipment = player.equipment if player.equipment else {}
    
    # 查找装备类型
    equipped_item_type = None
    for item_type, equipped_name in current_equipment.items():
        if equipped_name == item_name:
            equipped_item_type = item_type
            break
    
    if not equipped_item_type:
        return f"你没有装备【{item_name}】。"
    
    # 卸下装备
    del current_equipment[equipped_item_type]
    player.equipment = current_equipment
    
    # 移除属性加成
    item = _get_player_item(user_id, item_name)
    if item:
        attributes = item.get("attributes", {})
        _remove_attributes(player, attributes)
    
    # 保存玩家数据
    player_repository.update_player(player)
    
    attr_desc = ", ".join([f"{k}-{v}" for k, v in attributes.items()])
    message = f"你卸下了【{item_name}】"
    if attr_desc:
        message += f"\n失去属性加成: {attr_desc}"
    
    return message

def show_equipment(user_id: str) -> str:
    """
    显示玩家当前装备
    """
    player = player_repository.get_player_by_id(user_id)
    if not player:
        return "道友，你尚未踏入仙途。"
    
    current_equipment = player.equipment if player.equipment else {}
    
    if not current_equipment:
        return "你当前没有装备任何物品。"
    
    message_parts = ["═══【当前装备】═══"]
    
    for item_type, item_name in current_equipment.items():
        item = _get_player_item(user_id, item_name)
        if item:
            item_type_cn = "武器" if item_type == "weapon" else "法宝"
            attrs = item.get("attributes", {})
            attr_desc = ", ".join([f"{k}:{v}" for k, v in attrs.items()])
            message_parts.append(f"{item_type_cn}: 【{item_name}】 [{attr_desc}]")
        else:
            message_parts.append(f"{item_type}: 【{item_name}】 [数据异常]")
    
    message_parts.append("══════════════")
    message_parts.append("【装备指令】")
    message_parts.append("- 装备 <物品名称>")
    message_parts.append("- 卸下 <物品名称>")
    message_parts.append("══════════════")
    return "\n".join(message_parts)

def _get_player_item(user_id: str, item_name: str) -> dict:
    """
    获取玩家拥有的特定物品信息
    """
    sql = """
    SELECT i.name, i.type, i.level_requirement, i.description, i.attributes, pi.quantity
    FROM player_items pi
    JOIN items i ON pi.item_id = i.id
    WHERE pi.player_id = ? AND i.name = ?
    """
    result = fetch_query(sql, (user_id, item_name), one=True)
    
    if result:
        return {
            "name": result[0],
            "type": result[1],
            "level_requirement": result[2],
            "description": result[3],
            "attributes": json.loads(result[4]) if result[4] else {},
            "quantity": result[5]
        }
    
    return None

def _apply_attributes(player, attributes: dict):
    """
    应用属性加成到玩家
    """
    for attr, value in attributes.items():
        if attr == "attack":
            player.attack += value
        elif attr == "defense":
            player.defense += value
        elif attr == "hp":
            player.hp += value
        elif attr == "spirit_power":
            player.spirit_power += value
            player.max_spirit_power += value

def _remove_attributes(player, attributes: dict):
    """
    从玩家身上移除属性加成
    """
    for attr, value in attributes.items():
        if attr == "attack":
            player.attack -= value
        elif attr == "defense":
            player.defense -= value
        elif attr == "hp":
            player.hp -= value
        elif attr == "spirit_power":
            player.spirit_power -= value
            player.max_spirit_power -= value
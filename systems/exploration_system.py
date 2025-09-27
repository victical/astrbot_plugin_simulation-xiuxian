import random
from ..database.repositories import player_repository
from ..config import exploration_events
from . import combat_system, monster_generator

async def explore(user_id: str, provider) -> str:
    """处理玩家探索逻辑"""
    player = await player_repository.get_player_by_id(user_id)
    if not player:
        return "道友，你尚未踏入仙途。请输入 `开始修仙` 开启你的旅程。"

    required_spirit_power = 10
    if player.spirit_power < required_spirit_power:
        return f"灵力不足{required_spirit_power}点，无法探索。请先打坐恢复灵力。"
    
    player.spirit_power -= required_spirit_power
    
    # 70% 概率遭遇战斗，30% 概率触发和平事件
    if random.random() < 0.7:
        # --- 战斗事件 ---
        monster = monster_generator.generate_monster(player.level)
        monster.name = await monster_generator.generate_monster_name_with_llm(provider)
        
        combat_result = combat_system.start_pve_combat(player, monster)
        result_msg = f"你在东域的密林中穿行，突然，一头名为【{monster.name}】（{monster.level}）的妖兽挡住了你的去路！\n{combat_result}"
    else:
        # --- 和平事件 ---
        event = random.choice(exploration_events.COMMON_EVENTS + exploration_events.WILDERNESS_EVENTS)
        result_msg = _process_peaceful_event(player, event)

    await player_repository.update_player(player)
    return result_msg

def _process_peaceful_event(player: "Player", event: dict) -> str:
    """处理非战斗事件的奖励与惩罚"""
    msg_parts = [event["desc"]]
    
    if "reward" in event:
        reward = event["reward"]
        if "exp" in reward:
            player.experience += reward["exp"]
            msg_parts.append(f"获得{reward['exp']}点修为！")
        if "stones" in reward:
            player.spirit_stones += reward["stones"]
            msg_parts.append(f"获得{reward['stones']}颗灵石！")
        if "item" in reward:
            item_name = reward["item"]
            item_type = reward.get("item_type", "material")
            if item_name in player.inventory:
                player.inventory[item_name]["quantity"] += 1
            else:
                player.inventory[item_name] = {"quantity": 1, "type": item_type}
            msg_parts.append(f"获得{item_name}x1！")
            
    if "penalty" in event:
        penalty = event["penalty"]
        if "hp" in penalty:
            player.hp = max(1, player.hp - penalty["hp"])
            msg_parts.append(f"受到{penalty['hp']}点伤害！")
        if "spirit_power" in penalty:
            player.spirit_power = max(0, player.spirit_power - penalty["spirit_power"])
            msg_parts.append(f"灵力损耗{penalty['spirit_power']}点！")
            
    return "\n".join(msg_parts)
# astrbot_xiuxian_plugin/systems/exploration_system.py
import random
from ..database.repositories import player_repository
from ..config import exploration_events  # 事件配置
from ..config.cultivation_levels import LEVEL_ORDER  # 复用等级体系
from . import combat_system

def explore(user_id: str) -> str:
    """处理玩家探索逻辑（类似打坐功能的函数结构）"""
    # 1. 检查玩家是否存在（复用已有逻辑）
    player = player_repository.get_player_by_id(user_id)
    if not player:
        return "道友，你尚未踏入仙途。请输入 `!开始修仙` 开启你的旅程。"

    # 检查并合成藏宝图
    map_piece = "藏宝图残片"
    complete_map = "完整的藏宝图"
    pieces_needed = 3
    synthesis_msg = ""
    if player.inventory.get(map_piece, {}).get("quantity", 0) >= pieces_needed:
        player.inventory[map_piece]["quantity"] -= pieces_needed
        if player.inventory[map_piece]["quantity"] == 0:
            del player.inventory[map_piece]
        
        if complete_map in player.inventory:
            player.inventory[complete_map]["quantity"] += 1
        else:
            player.inventory[complete_map] = {"quantity": 1, "type": "consumable"}
        synthesis_msg = f"\n你将{pieces_needed}张藏宝图残片合成为了一张完整的藏宝图！"
    
    # 2. 检查探索条件（参考打坐的灵力检查）
    required_mp = 10  # 探索消耗10点灵力
    if player.mp < required_mp:
        return f"灵力不足{required_mp}点，无法探索。请先打坐恢复灵力。"
    
    # 3. 消耗资源并获取事件（结合玩家状态动态生成内容）
    player.mp -= required_mp  # 扣减灵力
    
    # 如果持有藏宝图，有概率进入遗迹
    if player.inventory.get(complete_map, {}).get("quantity", 0) > 0 and random.random() < 0.3: # 30%概率
        # 消耗一张藏宝图
        player.inventory[complete_map]["quantity"] -= 1
        if player.inventory[complete_map]["quantity"] == 0:
            del player.inventory[complete_map]
        
        # 进入遗迹探索
        event = random.choice(exploration_events.RUIN_EVENTS)
        result_msg = "你根据藏宝图的指引，找到了一处上古遗迹的入口...\n" + _process_event(player, event)
    else:
        event = _get_random_event(player)  # 根据玩家状态（门派/等级）获取事件
        result_msg = _process_event(player, event)  # 处理事件结果
    
    # 4. 保存状态（与打坐、宗门任务逻辑一致）
    player_repository.update_player(player)
    return result_msg + synthesis_msg

def _get_random_event(player: "Player") -> dict:
    """根据玩家身份/等级返回随机事件（参考宗门任务的分发逻辑）"""
    # 按门派/散修区分事件池（类似宗门弟子和散修的不同逻辑）
    if player.sect:
        # 门派弟子：更多门派周边事件
        event_pool = exploration_events.SECT_EVENTS + exploration_events.COMMON_EVENTS
    else:
        # 散修：更多野外奇遇
        event_pool = exploration_events.WILDERNESS_EVENTS + exploration_events.COMMON_EVENTS
    
    # 按等级调整事件概率（类似打坐收益随等级提升）
    level_index = LEVEL_ORDER.index(player.level)
    if level_index >= 3:  # 金丹期及以上解锁高阶事件
        event_pool += exploration_events.HIGH_LEVEL_EVENTS
    
    return random.choice(event_pool)

def _process_event(player: "Player", event: dict) -> str:
    """处理事件奖励/惩罚或触发战斗"""
    
    # 检查是否为战斗事件
    if event.get("type") == "combat":
        monster_name = event.get("monster_name")
        if monster_name:
            # 调用战斗系统
            combat_result = combat_system.start_pve_combat(player, monster_name)
            return f"{event['desc']}\n{combat_result}"
        else:
            return "遭遇未知妖兽，但它似乎没有敌意。"

    # --- 非战斗事件处理逻辑 ---
    msg_parts = [event["desc"]]
    
    # 处理奖励
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
    
    # 处理惩罚
    if "penalty" in event:
        penalty = event["penalty"]
        if "hp" in penalty:
            player.hp = max(1, player.hp - penalty["hp"])
            msg_parts.append(f"受到{penalty['hp']}点伤害！")
        if "mp" in penalty:
            player.mp = max(0, player.mp - penalty["mp"])
            msg_parts.append(f"灵力损耗{penalty['mp']}点！")
    
    return "\n".join(msg_parts)

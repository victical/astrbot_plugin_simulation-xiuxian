# astrbot_xiuxian_plugin/systems/progression_system.py

import random
import time
from datetime import datetime, timezone
from ..database.repositories import player_repository
from ..config import cultivation_levels
from ..models.player import Player

def _check_and_process_levelup(player: Player) -> str:
    """
    检查并处理玩家升级逻辑。
    如果玩家经验值足够，则提升其等级并增加属性。
    支持连续升级。
    :param player: 玩家对象
    :return: 升级的祝贺消息，如果没有升级则返回空字符串
    """
    levelup_messages = []
    
    while True:
        current_level = player.level
        
        if current_level == cultivation_levels.LEVEL_ORDER[-1]:
            break

        level_info = cultivation_levels.CULTIVATION_LEVELS.get(current_level)
        required_exp = level_info["required_exp"]
        
        if player.experience >= required_exp:
            current_level_index = cultivation_levels.LEVEL_ORDER.index(current_level)
            new_level = cultivation_levels.LEVEL_ORDER[current_level_index + 1]
            
            player.level = new_level
            new_level_info = cultivation_levels.CULTIVATION_LEVELS.get(new_level)
            player.max_spirit_power = new_level_info["max_spirit_power"]
            
            hp_gain = random.randint(50, 100)
            spirit_power_gain = random.randint(20, 50)
            attack_gain = random.randint(5, 10)
            defense_gain = random.randint(3, 8)
            
            player.hp += hp_gain
            player.spirit_power = min(player.spirit_power + spirit_power_gain, player.max_spirit_power)
            player.attack += attack_gain
            player.defense += defense_gain
            
            msg = (f"🎉 恭喜！你成功突破，当前境界提升至【{new_level}】！\n"
                   f"   气血+ {hp_gain}, 灵力上限提升至 {player.max_spirit_power}, 攻击+ {attack_gain}, 防御+ {defense_gain}")
            levelup_messages.append(msg)
        else:
            break
            
    return "\n".join(levelup_messages)

def start_meditation(user_id: str) -> str:
    """
    开始打坐。
    """
    player = player_repository.get_player_by_id(user_id)
    if not player:
        return "道友，你尚未踏入仙途。请输入 `我要修仙` 开启你的旅程。"
    
    if player.meditation_start_time:
        return "你正在打坐中，请先 `结束打坐`。"

    player.meditation_start_time = int(time.time())
    player_repository.update_player(player)
    
    return "你开始了打坐，灵力正在慢慢恢复..."

def stop_meditation(user_id: str) -> str:
    """
    结束打坐并结算收益。
    """
    player = player_repository.get_player_by_id(user_id)
    if not player:
        return "道友，你尚未踏入仙途。请输入 `我要修仙` 开启你的旅程。"

    if not player.meditation_start_time:
        return "你尚未开始打坐。"

    end_time = int(time.time())
    start_time = player.meditation_start_time
    duration_minutes = (end_time - start_time) / 60

    if duration_minutes < 1:
        return "打坐时间不足一分钟，无法获得收益。"

    level_index = cultivation_levels.LEVEL_ORDER.index(player.level)
    
    # 每分钟收益
    exp_per_minute = 5 + level_index * 2
    spirit_power_per_minute = 10 + level_index * 5

    exp_gained = int(duration_minutes * exp_per_minute)
    spirit_power_gained = int(duration_minutes * spirit_power_per_minute)

    player.experience += exp_gained
    player.spirit_power = min(player.spirit_power + spirit_power_gained, player.max_spirit_power)
    player.meditation_start_time = None

    levelup_message = _check_and_process_levelup(player)
    player_repository.update_player(player)

    result_message = (
        f"打坐结束，共持续 {int(duration_minutes)} 分钟。\n"
        f"你获得了 {exp_gained} 点修为，恢复了 {spirit_power_gained} 点灵力。"
    )

    if levelup_message:
        result_message += "\n" + levelup_message

    return result_message

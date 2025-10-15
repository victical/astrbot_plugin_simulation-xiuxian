# astrbot_xiuxian_plugin/systems/progression_system.py

import random
import time
from datetime import datetime, timezone
from ..database.repositories import player_repository
from ..config import cultivation_levels
from ..models.player import Player

async def _check_and_process_levelup(player: Player) -> str:
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
            if "大圆满" in current_level:
                dice = random.randint(1, 100)
                if dice <= 50:
                    player.experience -= int(required_exp * 0.1)
                    msg = "突破失败，修为倒退10%。"
                    levelup_messages.append(msg)
                    break
            
            current_level_index = cultivation_levels.LEVEL_ORDER.index(current_level)
            new_level = cultivation_levels.LEVEL_ORDER[current_level_index + 1]
            
            player.level = new_level
            new_level_info = cultivation_levels.CULTIVATION_LEVELS.get(new_level)
            player.max_spirit_power = new_level_info["max_spirit_power"]
            
            attribute_points_gain = 0
            # 根据新境界确定给予的属性点数
            if "凡人" in current_level:
                # 凡人突破到筑基期
                attribute_points_gain = 20
            elif "筑基" in new_level:
                # 筑基期各阶段突破
                attribute_points_gain = 20
            elif "金丹" in new_level:
                # 金丹期各阶段突破
                attribute_points_gain = 20
            elif "元婴" in new_level:
                # 元婴期各阶段突破
                attribute_points_gain = 40
            elif "出窍" in new_level:
                # 出窍期各阶段突破
                attribute_points_gain = 40
            elif "分神" in new_level:
                # 分神期各阶段突破
                attribute_points_gain = 40
            elif "合体" in new_level:
                # 合体期各阶段突破
                attribute_points_gain = 60
            elif "大乘" in new_level:
                # 大乘期各阶段突破
                attribute_points_gain = 60
            elif "渡劫" in new_level:
                # 渡劫期各阶段突破
                attribute_points_gain = 60
            else:
                # 更高境界突破
                attribute_points_gain = 100
            
            player.attribute_points += attribute_points_gain
            
            msg = (f"🎉 恭喜！你成功突破，当前境界提升至【{new_level}】！\n"
                   f"   获得了 {attribute_points_gain} 点属性点，请使用 `加点` 指令进行分配。")
            levelup_messages.append(msg)
        else:
            break
            
    return "\n".join(levelup_messages)

async def start_meditation(user_id: str) -> str:
    """
    开始打坐。
    """
    player = await player_repository.get_player_by_id(user_id)
    if not player:
        return "道友，你尚未踏入仙途。请输入 `开始修仙` 开启你的旅程。"
    
    if player.meditation_start_time:
        return "你正在打坐中，请先 `结束打坐`。"

    player.meditation_start_time = int(time.time())
    await player_repository.update_player(player)
    
    return "你开始了打坐，灵力正在慢慢恢复..."

async def stop_meditation(user_id: str) -> str:
    """
    结束打坐并结算收益。
    """
    player = await player_repository.get_player_by_id(user_id)
    if not player:
        return "道友，你尚未踏入仙途。请输入 `开始修仙` 开启你的旅程。"

    if not player.meditation_start_time:
        return "你尚未开始打坐。"

    end_time = int(time.time())
    start_time = player.meditation_start_time
    duration_minutes = (end_time - start_time) / 60

    if duration_minutes < 1:
        return "打坐时间不足一分钟，无法获得收益。"

    level_index = cultivation_levels.LEVEL_ORDER.index(player.level)
    
    # 每分钟收益
    spirit_power_per_minute = 10 + level_index * 5
    exp_per_minute= 10 + level_index * 5

    exp_gained = int(duration_minutes * exp_per_minute)
    spirit_power_gained = int(duration_minutes * spirit_power_per_minute)

    player.experience += exp_gained
    player.spirit_power = min(player.spirit_power + spirit_power_gained, player.max_spirit_power)
    player.meditation_start_time = None

    levelup_message = await _check_and_process_levelup(player)
    await player_repository.update_player(player)

    result_message = (
        f"打坐结束，共持续 {int(duration_minutes)} 分钟。\n"
        f"你获得了 {exp_gained} 点修为，恢复了 {spirit_power_gained} 点灵力。"
    )

    if levelup_message:
        result_message += "\n" + levelup_message

    return result_message

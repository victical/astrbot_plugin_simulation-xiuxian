# astrbot_xiuxian_plugin/systems/progression_system.py

import random
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
    
    # 使用 while 循环来处理可能发生的连续升级
    while True:
        current_level = player.level
        
        # 如果已经是最高级，则无法再升级
        if current_level == cultivation_levels.LEVEL_ORDER[-1]:
            break

        required_exp = cultivation_levels.CULTIVATION_LEVELS.get(current_level)
        
        # 检查经验是否足够
        if player.experience >= required_exp:
            # 获取当前等级在等级列表中的索引
            current_level_index = cultivation_levels.LEVEL_ORDER.index(current_level)
            # 新等级就是列表中的下一个
            new_level = cultivation_levels.LEVEL_ORDER[current_level_index + 1]
            
            player.level = new_level
            
            # 升级奖励：增加各项属性
            # 这里的数值可以根据游戏平衡性进行调整
            hp_gain = random.randint(50, 100)
            mp_gain = random.randint(20, 50)
            attack_gain = random.randint(5, 10)
            defense_gain = random.randint(3, 8)
            
            player.hp += hp_gain
            player.mp += mp_gain
            player.attack += attack_gain
            player.defense += defense_gain
            
            msg = (f"🎉 恭喜！你成功突破，当前境界提升至【{new_level}】！\n"
                   f"   气血+ {hp_gain}, 灵力+ {mp_gain}, 攻击+ {attack_gain}, 防御+ {defense_gain}")
            levelup_messages.append(msg)
        else:
            # 经验不足，跳出循环
            break
            
    return "\n".join(levelup_messages)

def meditate(user_id: str) -> str:
    """
    处理玩家打坐的逻辑。
    :param user_id: 玩家的唯一ID
    :return: 打坐结果的消息
    """
    player = player_repository.get_player_by_id(user_id)

    if not player:
        return "道友，你尚未踏入仙途。请输入 `!开始修仙` 开启你的旅程。"
        
    # 根据玩家等级设定收益范围，等级越高，收益越大
    level_index = cultivation_levels.LEVEL_ORDER.index(player.level)
    
    # 基础收益 + 等级加成
    min_exp_gain = 10 + level_index * 5
    max_exp_gain = 20 + level_index * 10
    min_stone_gain = 1 + level_index
    max_stone_gain = 5 + level_index * 2

    # 获得随机奖励
    exp_gained = random.randint(min_exp_gain, max_exp_gain)
    stones_gained = random.randint(min_stone_gain, max_stone_gain)

    player.experience += exp_gained
    player.spirit_stones += stones_gained

    # 检查是否升级
    levelup_message = _check_and_process_levelup(player)

    # 将更新后的玩家数据保存回数据库
    player_repository.update_player(player)

    # 构造最终消息
    result_message = (
        f"打坐结束。\n"
        f"你获得了 {exp_gained} 点修为，{stones_gained} 颗灵石。"
    )

    if levelup_message:
        result_message += "\n" + levelup_message

    return result_message
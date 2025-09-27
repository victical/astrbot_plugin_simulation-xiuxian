# astrbot_xiuxian_plugin/systems/sect_system.py
import random
from ..database.repositories import player_repository
from ..config import sects_data
from ..config.cultivation_levels import LEVEL_ORDER
from . import progression_system
from ..database.db_manager import execute_query, fetch_query
from ..systems.item_system import ItemType
import json

async def _check_and_process_promotion(player: "Player") -> str | None:
    """检查并处理玩家的宗门职位晋升，成功则返回祝贺消息"""
    if not player.sect:
        return None

    sect_info = sects_data.SECTS_DATA.get(player.sect, {})
    ranks = sect_info.get("ranks", [])
    if not ranks:
        return None

    # 查找当前职位和下一个职位
    current_rank_index = -1
    for i, rank_data in enumerate(ranks):
        if rank_data["name"] == player.sect_rank:
            current_rank_index = i
            break
    
    # 如果已是最高职位或未找到当前职位
    if current_rank_index == -1 or current_rank_index + 1 >= len(ranks):
        return None

    next_rank_data = ranks[current_rank_index + 1]
    req = next_rank_data.get("promotion_req")
    if not req:
        return None

    # 检查晋升条件
    req_contribution = req.get("contribution", float('inf'))
    req_level = req.get("level")
    
    # 等级比较
    player_level_index = LEVEL_ORDER.index(player.level)
    req_level_index = LEVEL_ORDER.index(req_level)

    if player.contribution >= req_contribution and player_level_index >= req_level_index:
        # --- 满足条件，执行晋升 ---
        old_rank = player.sect_rank
        new_rank = next_rank_data["name"]
        player.sect_rank = new_rank
        
        promotion_message = [f"恭喜！你在【{player.sect}】的职位从【{old_rank}】提升为【{new_rank}】！"]

        # --- 晋升奖励 ---
        rewards = next_rank_data.get("rewards", {})
        reward_spirit_stones = rewards.get("spirit_stones", 0)
        if reward_spirit_stones > 0:
            player.spirit_stones += reward_spirit_stones
            promotion_message.append(f"获得了 {reward_spirit_stones} 灵石奖励。")

        # 属性提升
        stat_bonuses = rewards.get("stat_bonuses", {})
        hp_bonus = stat_bonuses.get("hp", 0)
        attack_bonus = stat_bonuses.get("attack", 0)
        defense_bonus = stat_bonuses.get("defense", 0)

        if hp_bonus > 0:
            player.hp += hp_bonus
            promotion_message.append(f"气血上限增加 {hp_bonus}。")

        if attack_bonus > 0:
            player.attack += attack_bonus
            promotion_message.append(f"攻击增加 {attack_bonus}。")

        if defense_bonus > 0:
            player.defense += defense_bonus
            promotion_message.append(f"防御增加 {defense_bonus}。")

        return "\n".join(promotion_message)

    return None

async def join_sect(user_id: str, sect_name: str) -> str:
    """
    加入一个宗门。
    :param user_id: 用户ID
    :param sect_name: 宗门名称
    """
    # 1. 验证宗门是否存在
    if sect_name not in sects_data.SECTS_DATA:
        return f"不存在名为【{sect_name}】的宗门。请检查名称是否正确。"

    # 2. 获取玩家信息
    player = await player_repository.get_player_by_id(user_id)
    if not player:
        return "道友，你尚未踏入仙途。请输入 `开始修仙` 开启你的旅程。"

    # 3. 检查玩家是否已经加入了宗门
    if player.sect:
        return f"你已经是【{player.sect}】的弟子了，不可再入他门。"

    # 4. 设置玩家的宗门和初始职位
    player.sect = sect_name
    # 获取宗门的最低职位
    sect_info = sects_data.SECTS_DATA[sect_name]
    initial_rank = sect_info["ranks"][0]["name"] if sect_info.get("ranks") else "外门弟子"
    player.sect_rank = initial_rank
    player.contribution = 0  # 初始化贡献度

    # 5. 保存更新
    await player_repository.update_player(player)

    return f"恭喜你成功加入【{sect_name}】，当前职位为【{initial_rank}】！"

async def get_sect_mission(user_id: str) -> str:
    """
    获取当前宗门任务。
    :param user_id: 用户ID
    """
    player = await player_repository.get_player_by_id(user_id)
    if not player:
        return "道友，你尚未踏入仙途。请输入 `开始修仙` 开启你的旅程。"

    if not player.sect:
        return "你还未加入任何宗门。请先使用 `宗门列表` 和 `加入宗门 <宗门名>` 命令。"

    # 检查是否有正在进行的任务
    if player.current_mission and player.current_mission != 'null':
        mission_data = json.loads(player.current_mission)
        return _format_mission_message(mission_data)

    # 生成新任务
    sect_info = sects_data.SECTS_DATA[player.sect]
    missions = sect_info.get("missions", [])
    if not missions:
        return f"【{player.sect}】暂无任务可接。"

    # 随机分配一个任务
    mission = random.choice(missions)
    mission_data = {
        "type": mission["type"],
        "description": mission["description"],
        "target": mission.get("target", ""),
        "reward": mission["reward"]
    }

    # 保存任务到玩家数据
    player.current_mission = json.dumps(mission_data)
    await player_repository.update_player(player)

    return _format_mission_message(mission_data)

def _format_mission_message(mission_data: dict) -> str:
    """格式化任务信息"""
    reward_info = mission_data["reward"]
    reward_parts = []
    if reward_info.get("contribution"):
        reward_parts.append(f"{reward_info['contribution']} 贡献")
    if reward_info.get("spirit_stones"):
        reward_parts.append(f"{reward_info['spirit_stones']} 灵石")
    if reward_info.get("exp"):
        reward_parts.append(f"{reward_info['exp']} 修为")

    reward_str = "、".join(reward_parts) if reward_parts else "无"

    return (
        f"📜 当前宗门任务：\n"
        f"任务描述: {mission_data['description']}\n"
        f"任务奖励: {reward_str}\n"
        f"使用 `完成任务` 来完成当前任务。"
    )

async def complete_sect_mission(user_id: str) -> str:
    """
    完成当前宗门任务。
    :param user_id: 用户ID
    """
    player = await player_repository.get_player_by_id(user_id)
    if not player:
        return "道友，你尚未踏入仙途。请输入 `开始修仙` 开启你的旅程。"

    if not player.sect:
        return "你还未加入任何宗门。"

    if not player.current_mission or player.current_mission == 'null':
        return "你当前没有进行中的宗门任务。使用 `宗门任务` 来获取一个新任务。"

    # 解析任务数据
    mission_data = json.loads(player.current_mission)
    reward = mission_data["reward"]

    # 发放奖励
    messages = ["🎉 宗门任务完成！"]
    if reward.get("contribution"):
        player.contribution += reward["contribution"]
        messages.append(f"获得 {reward['contribution']} 贡献度。")

    if reward.get("spirit_stones"):
        player.spirit_stones += reward["spirit_stones"]
        messages.append(f"获得 {reward['spirit_stones']} 灵石。")

    if reward.get("exp"):
        player.experience += reward["exp"]
        messages.append(f"获得 {reward['exp']} 修为。")
        
        # 检查是否升级
        levelup_msg = await progression_system._check_and_process_levelup(player)
        if levelup_msg:
            messages.append(levelup_msg)

    # 清除任务
    player.current_mission = 'null'

    # 检查晋升
    promotion_msg = await _check_and_process_promotion(player)
    if promotion_msg:
        messages.append(promotion_msg)

    # 保存更新
    await player_repository.update_player(player)

    return "\n".join(messages)

async def get_sect_status(user_id: str) -> str:
    """
    获取玩家所在宗门的信息。
    :param user_id: 用户ID
    """
    player = await player_repository.get_player_by_id(user_id)
    if not player:
        return "道友，你尚未踏入仙途。请输入 `开始修仙` 开启你的旅程。"

    if not player.sect:
        return "你还未加入任何宗门。请先使用 `宗门列表` 和 `加入宗门 <宗门名>` 命令。"

    sect_info = sects_data.SECTS_DATA[player.sect]
    return (
        f"🏛️ 所在宗门: {player.sect}\n"
        f"道士职业: {player.sect_rank}\n"
        f"道士职业贡献: {player.contribution}\n"
        f"宗门介绍: {sect_info.get('description', '暂无介绍')}"
    )

def list_all_sects() -> str:
    """列出所有可加入的宗门"""
    sect_list = []
    for sect_name, sect_info in sects_data.SECTS_DATA.items():
        sect_list.append(f"🔹 {sect_name}: {sect_info.get('description', '暂无介绍')}")

    if not sect_list:
        return "目前暂无可加入的宗门。"

    return "🏛️ 可加入的宗门列表：\n" + "\n".join(sect_list)

async def list_exchangeable_items(user_id: str) -> str:
    """
    列出宗门商店中可兑换的物品。
    :param user_id: 用户ID
    """
    player = await player_repository.get_player_by_id(user_id)
    if not player:
        return "道友，你尚未踏入仙途。请输入 `开始修仙` 开启你的旅程。"

    if not player.sect:
        return "你还未加入任何宗门。"

    sect_info = sects_data.SECTS_DATA[player.sect]
    shop_items = sect_info.get("shop", [])
    
    if not shop_items:
        return f"【{player.sect}】暂未开放商店。"

    item_lines = []
    for item in shop_items:
        item_lines.append(
            f"🔸 {item['name']} - {item['cost']} 贡献\n"
            f"   {item.get('description', '暂无描述')}"
        )

    return (
        f"🛍️【{player.sect}】宗门商店\n"
        f"你的贡献: {player.contribution}\n"
        f"可兑换物品:\n" + "\n".join(item_lines)
    )

async def exchange_item(user_id: str, item_name: str) -> str:
    """
    在宗门商店兑换物品。
    :param user_id: 用户ID
    :param item_name: 物品名称
    """
    player = await player_repository.get_player_by_id(user_id)
    if not player:
        return "道友，你尚未踏入仙途。请输入 `开始修仙` 开启你的旅程。"

    if not player.sect:
        return "你还未加入任何宗门。"

    sect_info = sects_data.SECTS_DATA[player.sect]
    shop_items = sect_info.get("shop", [])
    
    # 查找物品
    target_item = None
    for item in shop_items:
        if item["name"] == item_name:
            target_item = item
            break

    if not target_item:
        return f"【{player.sect}】的商店中没有名为【{item_name}】的物品。"

    # 检查贡献度是否足够
    cost = target_item["cost"]
    if player.contribution < cost:
        return f"你的贡献度不足。需要 {cost} 贡献，当前只有 {player.contribution} 贡献。"

    # 扣除贡献度
    player.contribution -= cost

    # 将物品添加到玩家背包
    inventory = json.loads(player.inventory) if player.inventory and player.inventory != 'null' else {}
    item_type = target_item.get("type", ItemType.CONSUMABLE.value)
    
    if item_name in inventory:
        inventory[item_name]["quantity"] += 1
    else:
        inventory[item_name] = {
            "type": item_type,
            "quantity": 1
        }

    player.inventory = json.dumps(inventory)

    # 保存更新
    await player_repository.update_player(player)

    return f"成功兑换【{item_name}】，消耗了 {cost} 贡献。物品已放入你的背包。"

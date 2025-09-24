# astrbot_xiuxian_plugin/systems/sect_system.py
import random
from ..database.repositories import player_repository
from ..config import sects_data
from ..config.cultivation_levels import LEVEL_ORDER
from . import progression_system

def _check_and_process_promotion(player: "Player") -> str | None:
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
        
        # 发放晋升奖励
        reward = next_rank_data.get("promotion_reward", {})
        if "spirit_stones" in reward:
            player.spirit_stones += reward["spirit_stones"]
            promotion_message.append(f"获得晋升奖励：灵石 x{reward['spirit_stones']}！")
        
        if "items" in reward:
            for item_info in reward["items"]:
                item_name = item_info["name"]
                quantity = item_info.get("quantity", 1)
                if item_name in player.inventory:
                    player.inventory[item_name]["quantity"] += quantity
                else:
                    # 假设奖励物品都是丹药类型，后续可扩展
                    player.inventory[item_name] = {"quantity": quantity, "type": "丹药"}
                promotion_message.append(f"获得晋升奖励：{item_name} x{quantity}！")

        return "\n".join(promotion_message)

    return None


def list_all_sects() -> str:
    """
    列出所有可用的宗门及其简介。
    :return: 格式化后的宗门列表字符串。
    """
    if not sects_data.SECTS_DATA:
        return "天地初开，混沌一片，暂无宗门创立。"

    message_parts = ["═══ 天下宗门 ═══"]
    for sect_name, data in sects_data.SECTS_DATA.items():
        description = data.get('description', '暂无简介')
        message_parts.append(f"【{sect_name}】: {description}")
    
    message_parts.append("══════════════")
    message_parts.append("使用 `!加入宗门 [名称]` 来加入你心仪的宗门。")
    
    return "\n".join(message_parts)

def join_sect(user_id: str, sect_name_to_join: str) -> str:
    """
    处理玩家加入宗门的逻辑。
    :param user_id: 玩家的唯一ID。
    :param sect_name_to_join: 玩家想要加入的宗门名称。
    :return: 操作结果的消息。
    """
    player = player_repository.get_player_by_id(user_id)

    if not player:
        return "道友，你尚未踏入仙途。请输入 `!开始修仙` 开启你的旅程。"

    # 1. 检查玩家是否已有所属宗门
    if player.sect:
        return f"道友已是【{player.sect}】的弟子，不可背叛师门，加入他派。"

    # 2. 检查想加入的宗门是否存在
    if sect_name_to_join not in sects_data.SECTS_DATA:
        return f"寻遍天下，也未曾听闻名为【{sect_name_to_join}】的宗门。使用 `!宗门列表` 查看所有宗门。"

    # 3. 执行加入宗门的逻辑
    sect_info = sects_data.SECTS_DATA[sect_name_to_join]
    
    # 分配初始职位
    initial_rank_data = sect_info.get('ranks', [{}])[0]
    initial_rank = initial_rank_data.get('name', '外门弟子')
    
    player.sect = sect_name_to_join
    player.sect_rank = initial_rank
    
    # 将更新保存到数据库
    player_repository.update_player(player)

    return f"恭喜道友！你已成功拜入【{sect_name_to_join}】，成为一名光荣的“{initial_rank}”。"


def get_sect_mission(user_id: str) -> str:
    """处理玩家领取宗门任务的逻辑"""
    player = player_repository.get_player_by_id(user_id)

    if not player:
        return "道友，你尚未踏入仙途。"
    
    if not player.sect:
        return "你尚未加入任何宗门，无法领取任务。使用 `!宗门列表` 查看可加入的宗门。"

    if player.current_mission:
        mission_name = player.current_mission.get('name', '未知任务')
        return f"你身上已经有一个任务【{mission_name}】了，请先用 `!完成任务` 复命。"

    # 从配置中获取该宗门的任务列表
    available_missions = sects_data.SECTS_DATA.get(player.sect, {}).get('missions', [])
    if not available_missions:
        return f"你的宗门【{player.sect}】目前无事发生，暂无任务可领。"

    # 随机选择一个任务
    chosen_mission = random.choice(available_missions)
    
    player.current_mission = chosen_mission
    player_repository.update_player(player)

    return f"你领取了新的宗门任务：\n【{chosen_mission['name']}】\n描述：{chosen_mission['description']}"

def complete_sect_mission(user_id: str) -> str:
    """处理玩家完成宗门任务的逻辑"""
    player = player_repository.get_player_by_id(user_id)

    if not player:
        return "道友，你尚未踏入仙途。"

    if not player.current_mission:
        return "你身上没有任务，快去 `!宗门任务` 领取一个吧。"

    mission_data = player.current_mission
    rewards = mission_data.get('rewards', {})
    
    # 发放奖励
    con_gain = rewards.get('contribution', 0)
    exp_gain = rewards.get('experience', 0)
    stone_gain = rewards.get('spirit_stones', 0)

    player.contribution += con_gain
    player.experience += exp_gain
    player.spirit_stones += stone_gain
    
    # 完成后清空任务
    player.current_mission = None
    
    # 检查是否升级（重用 progression_system 的逻辑）
    levelup_message = progression_system._check_and_process_levelup(player)

    # 新增：检查是否晋升
    promotion_message = _check_and_process_promotion(player)
    
    # 保存所有更新
    player_repository.update_player(player)
    
    message = (
        f"你成功完成了任务【{mission_data['name']}】！\n"
        f"获得奖励：\n"
        f" - 宗门贡献 +{con_gain}\n"
        f" - 修为 +{exp_gain}\n"
        f" - 灵石 +{stone_gain}"
    )
    
    if levelup_message:
        message += "\n\n" + levelup_message
    
    if promotion_message:
        message += "\n\n" + promotion_message
        
    return message


def get_sect_status(user_id: str) -> str:
    """获取玩家的宗门状态信息"""
    player = player_repository.get_player_by_id(user_id)

    if not player:
        return "道友，你尚未踏入仙途。"
    
    if not player.sect:
        return "你尚未加入任何宗门。使用 `!宗门列表` 查看可加入的宗门。"

    sect_info = sects_data.SECTS_DATA.get(player.sect, {})
    ranks = sect_info.get("ranks", [])
    
    message_parts = [
        f"═══【{player.sect} - 个人信息】═══",
        f"道号: {player.user_name}",
        f"职位: {player.sect_rank}",
        f"贡献: {player.contribution}",
        "════════════════════"
    ]

    # 显示下一级晋升条件
    current_rank_index = -1
    for i, rank_data in enumerate(ranks):
        if rank_data["name"] == player.sect_rank:
            current_rank_index = i
            break

    if 0 <= current_rank_index < len(ranks) - 1:
        next_rank_data = ranks[current_rank_index + 1]
        req = next_rank_data.get("promotion_req")
        if req:
            req_contribution = req.get("contribution", "无")
            req_level = req.get("level", "无")
            message_parts.append(f"下一职位: 【{next_rank_data['name']}】")
            message_parts.append(f"晋升要求: {req_contribution}贡献, {req_level}境界")

    return "\n".join(message_parts)


def list_exchangeable_items(user_id: str) -> str:
    """列出玩家当前可兑换的宗门物品"""
    player = player_repository.get_player_by_id(user_id)

    if not player or not player.sect:
        return "散修一枚，何谈宗门贡献。快去 `!加入宗门` 吧！"

    sect_shop = sects_data.SECTS_DATA.get(player.sect, {}).get('exchange_shop', {})
    
    message_parts = [
        f"═══【{player.sect} - 宝库】═══",
        f"你当前的贡献为: {player.contribution}",
        f"你的职位为: {player.sect_rank}",
        "----------"
    ]

    # 获取所有低于或等于当前职位的可兑换物品
    player_rank_index = -1
    all_ranks = [r['name'] for r in sects_data.SECTS_DATA.get(player.sect, {}).get('ranks', [])]
    if player.sect_rank in all_ranks:
        player_rank_index = all_ranks.index(player.sect_rank)

    accessible_items = []
    if player_rank_index != -1:
        for i in range(player_rank_index + 1):
            rank_name = all_ranks[i]
            items = sect_shop.get(rank_name, [])
            if items:
                message_parts.append(f"[{rank_name} 可兑换]")
                for item in items:
                    accessible_items.append(item)
                    message_parts.append(f"  【{item['name']}】 - 需要贡献: {item['cost']}")

    if not accessible_items:
        return f"你在【{player.sect}】的职位({player.sect_rank})太低，宝库尚未对你开放。"
    
    message_parts.append("════════════════════")
    message_parts.append("使用 `!兑换 [物品名称]` 来进行兑换。")
    return "\n".join(message_parts)


def exchange_item(user_id: str, item_name_to_buy: str) -> str:
    """处理玩家兑换物品的逻辑"""
    player = player_repository.get_player_by_id(user_id)

    if not player or not player.sect:
        return "散修一枚，何谈宗门贡献。"

    sect_shop = sects_data.SECTS_DATA.get(player.sect, {}).get('exchange_shop', {})
    
    # 查找玩家想兑换的物品，并检查其职位是否足够
    player_rank_index = -1
    all_ranks = [r['name'] for r in sects_data.SECTS_DATA.get(player.sect, {}).get('ranks', [])]
    if player.sect_rank in all_ranks:
        player_rank_index = all_ranks.index(player.sect_rank)

    target_item = None
    can_exchange = False
    
    # 遍历所有职位等级的商店
    for i in range(len(all_ranks)):
        rank_name = all_ranks[i]
        items_in_rank = sect_shop.get(rank_name, [])
        for item in items_in_rank:
            if item['name'] == item_name_to_buy:
                target_item = item
                # 检查玩家职位是否达到兑换要求
                if player_rank_index >= i:
                    can_exchange = True
                break
        if target_item:
            break

    if not target_item or not can_exchange:
        return f"你的职位({player.sect_rank})无法兑换【{item_name_to_buy}】，或者该物品不存在。"

    # 检查贡献度是否足够
    if player.contribution < target_item['cost']:
        return f"贡献不足！兑换【{target_item['name']}】需要 {target_item['cost']} 贡献，你只有 {player.contribution}。"

    # --- 执行兑换 ---
    # 1. 扣除贡献
    player.contribution -= target_item['cost']
    
    # 2. 添加物品到背包
    # 如果背包中已有该物品，则数量+1
    if item_name_to_buy in player.inventory:
        player.inventory[item_name_to_buy]['quantity'] += 1
    # 如果没有，则新增
    else:
        player.inventory[item_name_to_buy] = {
            "quantity": 1,
            "type": target_item['type']
        }
        
    # 3. 保存更新到数据库
    player_repository.update_player(player)

    return f"兑换成功！你花费了 {target_item['cost']} 贡献，获得了【{target_item['name']}】x1。可使用 `!我的背包` 查看。"

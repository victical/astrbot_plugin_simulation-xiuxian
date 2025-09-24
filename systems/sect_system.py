# astrbot_xiuxian_plugin/systems/sect_system.py
import random
from ..database.repositories import player_repository
from ..config import sects_data
from . import progression_system

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
    
    # 分配初始职位（通常是列表中的第一个）
    initial_rank = sect_info.get('ranks', ['弟子'])[0]
    
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
        message += "\n" + levelup_message
        
    return message


def list_exchangeable_items(user_id: str) -> str:
    """列出玩家当前可兑换的宗门物品"""
    player = player_repository.get_player_by_id(user_id)

    if not player or not player.sect:
        return "散修一枚，何谈宗门贡献。快去 `!加入宗门` 吧！"

    sect_shop = sects_data.SECTS_DATA.get(player.sect, {}).get('exchange_shop', {})
    player_rank = player.sect_rank
    
    # 获取当前职位可兑换的物品
    available_items = sect_shop.get(player_rank, [])
    if not available_items:
        return f"你在【{player.sect}】的职位({player_rank})太低，宝库尚未对你开放。"

    message_parts = [
        f"═══【{player.sect} - {player_rank}宝库】═══",
        f"你当前的贡献为: {player.contribution}"
    ]
    for item in available_items:
        message_parts.append(f"【{item['name']}】 - 需要贡献: {item['cost']}")
    
    message_parts.append("════════════════════")
    message_parts.append("使用 `!兑换 [物品名称]` 来进行兑换。")
    return "\n".join(message_parts)


def exchange_item(user_id: str, item_name_to_buy: str) -> str:
    """处理玩家兑换物品的逻辑"""
    player = player_repository.get_player_by_id(user_id)

    if not player or not player.sect:
        return "散修一枚，何谈宗门贡献。"

    sect_shop = sects_data.SECTS_DATA.get(player.sect, {}).get('exchange_shop', {})
    player_rank = player.sect_rank
    available_items = sect_shop.get(player_rank, [])
    
    # 查找玩家想兑换的物品
    target_item = None
    for item in available_items:
        if item['name'] == item_name_to_buy:
            target_item = item
            break
            
    if not target_item:
        return f"你在【{player.sect}】的职位({player_rank})无法兑换【{item_name_to_buy}】，或者该物品不存在。"

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
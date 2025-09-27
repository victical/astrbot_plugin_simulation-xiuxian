# astrbot_xiuxian_plugin/systems/game_start_system.py
from astrbot.api import logger
from ..models.player import Player
from ..database.repositories import player_repository
from ..config import settings

async def start_game(user_id: str, user_name: str) -> str:
    """
    处理用户的游戏开始请求。

    - 检查玩家是否已存在。
    - 如果不存在，则根据初始设置创建一个新角色。
    - 返回一个相应的消息给用户。
    
    :param user_id: 用户的唯一ID
    :param user_name: 用户的昵称
    :return: 一条将要回复给用户的消息字符串
    """
    logger.info(f"进入 start_game 系统, user_id={user_id}")
    # 1. 检查玩家是否已经存在
    logger.info("检查玩家是否存在...")
    if await player_repository.player_exists(user_id):
        logger.info("玩家已存在。")
        player = await player_repository.get_player_by_id(user_id)
        if player:
            return f"道友 {player.user_name}，你已在仙途中，当前境界为【{player.level}】。无需重新开始。使用 `我的状态` 查看详情。"
        else:
            logger.error("严重错误: player_exists 返回 True 但 get_player_by_id 返回 None。")
            # 这是一个理论上的边缘情况，以防万一
            return "系统出现异常，无法获取您的角色信息，请联系管理员。"

    # 2. 如果玩家不存在，创建新角色
    logger.info(f"玩家不存在，准备创建新角色: user_id={user_id}, user_name={user_name}")

    # 从配置文件获取初始属性
    initial_stats = settings.INITIAL_PLAYER_STATS

    # 创建一个新的 Player 对象
    new_player = Player(
        user_id=user_id,
        user_name=user_name,
        level=initial_stats['level'],
        experience=initial_stats['experience'],
        spirit_stones=initial_stats['spirit_stones'],
        hp=initial_stats['hp'],
        spirit_power=initial_stats['spirit_power'],
        max_spirit_power=initial_stats['max_spirit_power'],
        attack=initial_stats['attack'],
        defense=initial_stats['defense'],
        meditation_start_time=None,
        sect=initial_stats['sect'],
        sect_rank=initial_stats.get('sect_rank', '外门弟子'),
        contribution=initial_stats.get('contribution', 0),
        inventory=initial_stats.get('inventory', '{}'),
        skills=initial_stats.get('skills', '{}'),
        equipment=initial_stats.get('equipment', '{}'),
        current_mission=initial_stats.get('current_mission', 'null')
    )

    # 3. 将新玩家存入数据库
    try:
        await player_repository.create_player(new_player)
        logger.info(f"成功为 {user_name} 创建角色。")
        return (f"道友 {user_name}，欢迎踏入修仙之路！\n"
                f"当前境界为【{new_player.level}】，祝你早日飞升仙界！\n"
                f"输入 `我的状态` 查看详情，`打坐` 开始修炼。")
    except Exception as e:
        logger.error(f"创建角色时发生错误: {e}", exc_info=True)
        return "系统异常：无法创建角色，请稍后重试或联系管理员。"
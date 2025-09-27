# astrbot_xiuxian_plugin/database/repositories/player_repository.py
from astrbot.api import logger
from ...models.player import Player
from ...database import db_manager

async def get_player_by_id(user_id: str) -> Player | None:
    """
    通过 user_id 从数据库中异步获取玩家数据
    :param user_id: 玩家的唯一ID
    :return: Player 对象或 None
    """
    logger.info(f"仓库层: 正在通过 ID 查询玩家: {user_id}")
    sql = """
    SELECT user_id, user_name, level, experience, spirit_stones, 
           hp, spirit_power, max_spirit_power, attack, defense, meditation_start_time,
           sect, sect_rank, contribution, inventory, skills, equipment, current_mission, 
           created_at, updated_at
    FROM players 
    WHERE user_id = ?
    """
    row = await db_manager.fetch_query(sql, (user_id,), one=True)
    
    if row:
        logger.info("仓库层: 成功找到玩家。")
        # 将数据库行数据解包以匹配 Player 类的构造函数
        return Player(*row)
    logger.warning("仓库层: 未找到玩家。")
    return None

async def create_player(player: Player):
    """
    在数据库中异步创建一个新玩家
    :param player: Player 对象
    """
    logger.info(f"仓库层: 正在创建新玩家: {player.user_id}")
    sql = """
    INSERT INTO players (user_id, user_name, level, experience, spirit_stones, 
                         hp, spirit_power, max_spirit_power, attack, defense, meditation_start_time,
                         sect, sect_rank, contribution, inventory, skills, equipment, current_mission)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    player_dict = player.to_dict()
    params = (
        player_dict['user_id'], player_dict['user_name'], player_dict['level'],
        player_dict['experience'], player_dict['spirit_stones'], player_dict['hp'],
        player_dict['spirit_power'], player_dict['max_spirit_power'], player_dict['attack'],
        player_dict['defense'], player_dict['meditation_start_time'], player_dict['sect'],
        player_dict['sect_rank'], player_dict['contribution'], player_dict['inventory'],
        player_dict['skills'], player_dict['equipment'], player_dict['current_mission']
    )
    await db_manager.execute_query(sql, params)

async def update_player(player: Player):
    """
    异步更新数据库中的玩家数据
    :param player: Player 对象
    """
    sql = """
    UPDATE players SET
        user_name = ?, level = ?, experience = ?, spirit_stones = ?,
        hp = ?, spirit_power = ?, max_spirit_power = ?, attack = ?, defense = ?,
        meditation_start_time = ?, sect = ?, sect_rank = ?, contribution = ?,
        inventory = ?, skills = ?, equipment = ?, current_mission = ?,
        updated_at = CURRENT_TIMESTAMP
    WHERE user_id = ?
    """
    player_dict = player.to_dict()
    params = (
        player_dict['user_name'], player_dict['level'], player_dict['experience'],
        player_dict['spirit_stones'], player_dict['hp'], player_dict['spirit_power'],
        player_dict['max_spirit_power'], player_dict['attack'], player_dict['defense'],
        player_dict['meditation_start_time'], player_dict['sect'], player_dict['sect_rank'],
        player_dict['contribution'], player_dict['inventory'], player_dict['skills'],
        player_dict['equipment'], player_dict['current_mission'], player_dict['user_id']
    )
    await db_manager.execute_query(sql, params)

async def player_exists(user_id: str) -> bool:
    """
    异步检查玩家是否存在于数据库中
    :param user_id: 玩家的唯一ID
    :return: 如果存在则为 True, 否则为 False
    """
    player = await get_player_by_id(user_id)
    return player is not None
# astrbot_xiuxian_plugin/database/repositories/player_repository.py

from ...models.player import Player
from ...database import db_manager

def get_player_by_id(user_id: str) -> Player | None:
    """
    通过 user_id 从数据库中获取玩家数据
    :param user_id: 玩家的唯一ID
    :return: Player 对象或 None
    """
    sql = "SELECT * FROM players WHERE user_id = ?"
    row = db_manager.fetch_query(sql, (user_id,), one=True)
    
    if row:
        # 将数据库行数据解包以匹配 Player 类的构造函数
        return Player(*row)
    return None

def create_player(player: Player):
    """
    在数据库中创建一个新玩家
    :param player: Player 对象
    """
    # 修正：VALUES 子句中添加了第15个 '?' 来匹配 current_mission
    sql = """
    INSERT INTO players (user_id, user_name, level, experience, spirit_stones, 
                         hp, mp, attack, defense, sect, sect_rank, contribution, 
                         inventory, learned_skills, current_mission)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    player_dict = player.to_dict()
    params = (
        player_dict['user_id'], player_dict['user_name'], player_dict['level'],
        player_dict['experience'], player_dict['spirit_stones'], player_dict['hp'],
        player_dict['mp'], player_dict['attack'], player_dict['defense'],
        player_dict['sect'], player_dict['sect_rank'], player_dict['contribution'],
        player_dict['inventory'], player_dict['learned_skills'],
        player_dict['current_mission']
    )
    db_manager.execute_query(sql, params)

def update_player(player: Player):
    """
    更新数据库中的玩家数据
    :param player: Player 对象
    """
    # 修正：SET 子句中添加了 current_mission = ?
    sql = """
    UPDATE players SET
        user_name = ?, level = ?, experience = ?, spirit_stones = ?,
        hp = ?, mp = ?, attack = ?, defense = ?, sect = ?, sect_rank = ?,
        contribution = ?, inventory = ?, learned_skills = ?, current_mission = ?,
        updated_at = CURRENT_TIMESTAMP
    WHERE user_id = ?
    """
    player_dict = player.to_dict()
    params = (
        player_dict['user_name'], player_dict['level'], player_dict['experience'],
        player_dict['spirit_stones'], player_dict['hp'], player_dict['mp'],
        player_dict['attack'], player_dict['defense'], player_dict['sect'],
        player_dict['sect_rank'], player_dict['contribution'],
        player_dict['inventory'], player_dict['learned_skills'],
        player_dict['current_mission'],
        player_dict['user_id']
    )
    db_manager.execute_query(sql, params)

def player_exists(user_id: str) -> bool:
    """
    检查玩家是否存在于数据库中
    :param user_id: 玩家的唯一ID
    :return: 如果存在则为 True, 否则为 False
    """
    return get_player_by_id(user_id) is not None